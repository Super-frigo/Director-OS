"""Apply structured AgentProposals onto a Project dataclass tree.

AgentProposal.field uses dotted path notation relative to a Project module:
    "story.premise"                       → project.story.premise = value
    "shots[0].framing"                    → project.shots[0].framing = value
    "visual_language.style"               → project.visual_language.style = value
    "shots[1].lighting.mood"              → project.shots[1].lighting.mood = value

Supported actions (AgentProposal.action):
    "set"     — assign value at the path (overwrite if present)
    "append"  — append value to a list-typed target (create if absent)
    "remove"  — remove value from a list, or delete a key/attr if scalar
    "suggest" — never writes; recorded but not applied (returns in skipped)

The resolver handles dataclasses, dicts, and lists interchangeably so it
works regardless of whether a Project section is a dataclass instance or a
plain dict (the loader produces dataclasses, but some downstream code uses dicts).
"""

from __future__ import annotations

import re
from dataclasses import fields, is_dataclass
from typing import Any

# Matches "name", "name[3]", and chained ".name[3].sub"
_TOKEN_RE = re.compile(r"([^\.\[\]]+)|\[(\d+)\]")
_APPEND_ACTIONS: frozenset[str] = frozenset({"append"})
_REMOVE_ACTIONS: frozenset[str] = frozenset({"remove"})
_SKIP_ACTIONS: frozenset[str] = frozenset({"suggest"})


class ApplyError(Exception):
    """Raised when a proposal path cannot be resolved on the Project tree."""


def apply_proposal(root: Any, module: str, field: str, action: str, value: Any) -> bool:
    """Apply one proposal onto *root* (a Project or equivalent dict).

    Returns True if applied, False if skipped (e.g. action == "suggest").
    Raises ApplyError on an unresolvable path.

    The *module* selects the top-level node (e.g. "story", "shots"). The
    *field* is a dotted/indexed path relative to that node. When *field*
    is empty, the action applies directly to the module-level collection
    (used by StoryAgent's "story_beats" append proposals).
    """
    if action in _SKIP_ACTIONS:
        return False

    # Resolve the module-level node.
    node = _get_attr(root, module)
    if node is None:
        raise ApplyError(
            f"module '{module}' not found on {type(root).__name__}"
        )

    tokens = _parse_path(field) if field else []

    # Strip leading module name if field duplicates it (CameraAgent convention:
    # module="shots", field="shots[0].framing" — strip the "shots" label but
    # keep its index so we navigate into the correct list element).
    if tokens and tokens[0][0] == module:
        _, idx = tokens.pop(0)
        if idx is not None:
            if not isinstance(node, list):
                raise ApplyError(
                    f"module '{module}' has index [{idx}] but is not a list"
                )
            _ensure_list_capacity(node, idx)
            node = node[idx]

    if action in _APPEND_ACTIONS:
        _apply_append(root, module, node, tokens, value)
    elif action in _REMOVE_ACTIONS:
        _apply_remove(node, tokens, value)
    else:
        # "set" (default)
        if not tokens:
            raise ApplyError(
                f"cannot 'set' module '{module}' with empty field path"
            )
        _apply_set(node, tokens, value)
    return True


# ---------------------------------------------------------------------------
# Path parsing & resolution
# ---------------------------------------------------------------------------

def _parse_path(path: str) -> list[tuple[str, int | None]]:
    """Parse "shots[0].lighting.mood" into [("shots", 0), ("lighting", None), ("mood", None)].

    Each token is (name, index) where index is None for plain attributes.
    """
    tokens: list[tuple[str, int | None]] = []
    pos = 0
    expect_name = True
    while pos < len(path):
        m = _TOKEN_RE.match(path, pos)
        if not m:
            # Skip a stray separator rather than crash.
            pos += 1
            continue
        pos = m.end()
        if m.group(1) is not None:
            # Attribute name
            tokens.append((m.group(1), None))
            expect_name = False
        else:
            # [index]
            if not tokens:
                raise ApplyError(f"path '{path}' starts with an index")
            name, _ = tokens[-1]
            tokens[-1] = (name, int(m.group(2)))
            expect_name = True
        # Allow a '.' separator between tokens; consumed implicitly by re.match
    return tokens


def _apply_set(node: Any, tokens: list[tuple[str, int | None]], value: Any) -> None:
    """Walk *node* along *tokens* and set the final attribute/index."""
    # Navigate to the parent of the final token.
    for name, idx in tokens[:-1]:
        node = _resolve_step(node, name, idx, create_missing=True)

    last_name, last_idx = tokens[-1]
    if last_idx is None:
        _set_attr(node, last_name, value)
    else:
        container = _get_attr(node, last_name)
        if container is None:
            raise ApplyError(f"cannot index into missing list '{last_name}'")
        _ensure_list_capacity(container, last_idx)
        container[last_idx] = value


def _apply_append(
    root: Any, module: str, node: Any,
    tokens: list[tuple[str, int | None]], value: Any,
) -> None:
    """Append *value* to a list at the resolved path.

    Special case: when module is a list-typed field (e.g. "shots",
    "story_beats") and tokens is empty or names the module itself,
    append directly to that top-level list.
    """
    if not tokens:
        # Append to the module-level list directly.
        target = _get_attr(root, module)
        if not isinstance(target, list):
            raise ApplyError(f"module '{module}' is not a list, cannot append")
        target.append(_coerce_to_dataclass(target, value, parent=root, field_name=module))
        return

    # Navigate to the container holding the final list.
    for name, idx in tokens[:-1]:
        node = _resolve_step(node, name, idx, create_missing=True)

    last_name, last_idx = tokens[-1]
    container = _get_attr(node, last_name)
    if container is None:
        # Create the list if the attribute exists but is empty/unset.
        _set_attr(node, last_name, [])
        container = _get_attr(node, last_name)
    if not isinstance(container, list):
        raise ApplyError(f"field '{last_name}' is not a list, cannot append")
    container.append(_coerce_to_dataclass(container, value, parent=node, field_name=last_name))


def _apply_remove(node: Any, tokens: list[tuple[str, int | None]], value: Any) -> None:
    """Remove *value* from a list at the resolved path."""
    if not tokens:
        raise ApplyError("cannot 'remove' with empty field path")
    for name, idx in tokens[:-1]:
        node = _resolve_step(node, name, idx, create_missing=False)
    last_name, _ = tokens[-1]
    container = _get_attr(node, last_name)
    if isinstance(container, list) and value in container:
        container.remove(value)


def _resolve_step(
    node: Any, name: str, idx: int | None, create_missing: bool = False,
) -> Any:
    """Resolve one (name, index) step from *node*, returning the child."""
    child = _get_attr(node, name)
    if child is None and create_missing:
        # Auto-create a missing dict/dataclass slot so deep paths work.
        if _is_dataclass_instance(node):
            if name in {f.name for f in fields(node)}:
                _set_attr(node, name, {})
        child = _get_attr(node, name)
    if idx is not None:
        if not isinstance(child, list):
            raise ApplyError(f"cannot index [{idx}] into non-list '{name}'")
        _ensure_list_capacity(child, idx)
        child = child[idx]
    return child


# ---------------------------------------------------------------------------
# Dataclass / dict / list polymorphic accessors
# ---------------------------------------------------------------------------

def _get_attr(obj: Any, name: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _set_attr(obj: Any, name: str, value: Any) -> None:
    if isinstance(obj, dict):
        obj[name] = value
    else:
        setattr(obj, name, value)


def _is_dataclass_instance(obj: Any) -> bool:
    return is_dataclass(obj) and not isinstance(obj, type)


def _ensure_list_capacity(lst: list, idx: int) -> None:
    """Pad *lst* with None until idx is a valid index."""
    while len(lst) <= idx:
        lst.append(None)


def _coerce_to_dataclass(
    lst: list, value: Any, parent: Any = None, field_name: str = "",
) -> Any:
    """If *lst* holds dataclass instances and *value* is a dict, coerce it.

    Uses three strategies (in order):
        1. Sample an existing element from *lst*.
        2. Inspect parent's ``list[X]`` type annotation via ``typing.get_args``.
        3. Fallback: return dict as-is.
    """
    if not isinstance(value, dict):
        return value

    # Strategy 1: sample existing element
    sample = next((x for x in lst if x is not None), None)
    target_cls: type | None = None
    if _is_dataclass_instance(sample):
        target_cls = type(sample)

    # Strategy 2: type annotation on parent dataclass field
    if target_cls is None and parent is not None and field_name:
        from typing import get_args, get_origin
        try:
            type_hint = parent.__class__.__annotations__.get(field_name)
            if get_origin(type_hint) is list:
                args = get_args(type_hint)
                if args and is_dataclass(args[0]):
                    target_cls = args[0]
        except Exception:
            pass

    if target_cls is None:
        return value  # cannot determine element type

    field_names = {f.name for f in fields(target_cls)}
    kwargs = {k: v for k, v in value.items() if k in field_names}
    try:
        return target_cls(**kwargs)
    except TypeError:
        return value
