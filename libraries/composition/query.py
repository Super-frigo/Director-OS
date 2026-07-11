"""Composition Library query -- keyword-based retrieval for Engine consumption.

Implements the ADR-004 pipeline:  Project context -> Library retrieval -> Engine decision.

Token-based matching (v2):
  - English: whitespace/punctuation-split, exact token comparison
  - Chinese: jieba segmentation, exact token comparison
  - No substring matching -- "instability" will NOT match "stability"

Weight-balanced scoring (v2):
  - semantic_score: normalized 0-1 from emotion + scene_type matches
  - shot_param_score: normalized 0-1 from framing/lens/angle/focus/movement matches
  - final = W_semantic * semantic_score + W_shot * shot_param_score
  - W_semantic and W_shot are tunable (default 0.5 each)

Usage:
    from libraries.composition.query import query_compositions

    matches = query_compositions({
        "emotion": "unease",
        "scene_type": "tension",
        "framing": "CU",
    })
    for entry, score in matches:
        print(f"{entry['name']} (score={score})")
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable

import yaml

try:
    import jieba
    _JIEBA_AVAILABLE = True
except ImportError:
    _JIEBA_AVAILABLE = False


# ============================================================================
# Tunable scoring weights (public API)
# ============================================================================

W_SEMANTIC: float = 0.50   # weight for emotion + scene_type matching
W_SHOT: float = 0.50       # weight for framing/lens/angle/focus/movement matching


def set_weights(semantic: float, shot: float) -> None:
    """Set the scoring weights. Must sum to 1.0."""
    if abs(semantic + shot - 1.0) > 0.001:
        raise ValueError(f"Weights must sum to 1.0, got semantic={semantic} + shot={shot}")
    global W_SEMANTIC, W_SHOT
    W_SEMANTIC = semantic
    W_SHOT = shot


# ============================================================================
# Tokenizer -- word-boundary aware, no substring matching
# ============================================================================

# English: split on non-alphanumeric (preserving hyphens within tokens like "rule_of_thirds")
_EN_TOKEN_RE = re.compile(r"[^a-zA-Z0-9_]+$")


def _tokenize_english(text: str) -> List[str]:
    """Tokenize English text into lowercase tokens by splitting on whitespace.

    Multi-word keyword fields (like "rule_of_thirds") are split on underscores
    too, so each component becomes an independent token.
    """
    if not text:
        return []
    # Replace underscores and hyphens with spaces, then split
    cleaned = text.lower().replace("_", " ").replace("-", " ")
    tokens = cleaned.split()
    # Filter out very short tokens (< 2 chars) unless they're meaningful
    return [t for t in tokens if len(t) >= 2]


def _tokenize_chinese(text: str) -> List[str]:
    """Tokenize Chinese text using jieba, with character-bigram fallback."""
    if not text:
        return []
    if _JIEBA_AVAILABLE:
        tokens = list(jieba.cut(text))
        # Filter out pure whitespace/punctuation tokens
        return [t.strip().lower() for t in tokens if t.strip() and len(t.strip()) >= 1]
    # Fallback: character bigrams
    cleaned = re.sub(r"[^\u4e00-\u9fff]", "", text)
    if len(cleaned) <= 1:
        return [cleaned] if cleaned else []
    bigrams = []
    for i in range(len(cleaned) - 1):
        bigrams.append(cleaned[i:i+2])
    return bigrams


def _tokenize(text: str) -> List[str]:
    """Tokenize mixed English/Chinese text into lowercase tokens."""
    if not text:
        return []
    # Separate Chinese and English portions
    has_chinese = bool(re.search(r"[\u4e00-\u9fff]", text))
    has_english = bool(re.search(r"[a-zA-Z]", text))

    tokens: List[str] = []
    if has_chinese:
        tokens.extend(_tokenize_chinese(text))
    if has_english or not has_chinese:
        tokens.extend(_tokenize_english(text))

    # Deduplicate while preserving order
    seen: set = set()
    result: List[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result


# ============================================================================
# Token-set matching -- exact token equality only, no substrings
# ============================================================================

def _token_match(
    query_tokens: List[str],
    entry_tokens: List[str],
) -> Tuple[float, List[str]]:
    """Compute match score between query tokens and entry tokens.

    Each query token that has an exact match in entry tokens contributes
    1 / len(query_tokens) to the score.  This normalizes to 0-1.

    No substring matching -- "instability" will NOT match "stability".

    Returns (score 0.0-1.0, list of matched token descriptors).
    """
    if not query_tokens or not entry_tokens:
        return 0.0, []

    entry_set: set = set(entry_tokens)
    matched: List[str] = []
    hits = 0

    for qt in query_tokens:
        if qt in entry_set:
            matched.append(f"token:{qt}")
            hits += 1

    if hits == 0:
        return 0.0, []

    score = hits / len(query_tokens)
    return score, matched


# ============================================================================
# Emotion keyword mapping (unchanged from v1)
# ============================================================================

_EMOTION_MAP: Dict[str, List[str]] = {
    "unease":        ["unease", "anxiety", "tension", "dread", "wrongness", "instability"],
    "anxiety":       ["anxiety", "unease", "dread", "tension", "instability", "nervous"],
    "tension":       ["tension", "unease", "anxiety", "dread", "instability"],
    "loneliness":    ["loneliness", "isolation", "alone", "emptiness", "despair", "void"],
    "isolation":     ["isolation", "loneliness", "alone", "separation", "distance"],
    "fear":          ["fear", "dread", "unease", "anxiety", "horror"],
    "calm":          ["calm", "peace", "stability", "balance", "normalcy"],
    "contemplation": ["contemplation", "reflection", "awe", "harmony", "order"],
    "power":         ["power", "authority", "hierarchy", "confrontation", "strength"],
    "confrontation": ["confrontation", "power", "intensity", "direct", "face_on"],
    "voyeurism":     ["voyeurism", "observation", "watch", "distance"],
    "entrapment":    ["entrapment", "confinement", "enclosure", "trap"],
    "romance":       ["warmth", "intimacy", "closeness", "soft"],
    "despair":       ["despair", "emptiness", "void", "loneliness", "isolation"],
    "awe":           ["awe", "scale", "vastness", "grandeur"],
    "order":         ["order", "stability", "harmony", "symmetry", "control"],
    "energy":        ["energy", "dynamism", "kinetic", "momentum", "active"],
    "oppression":    ["oppression", "control", "confinement", "authority", "fear"],
    "cold":          ["cold", "distance", "isolation", "clinical", "emotionless"],
    "silence":       ["silence", "stillness", "emptiness", "contemplation"],
    "stillness":     ["stillness", "silence", "static", "quiet"],

    "\u4e0d\u5b89":    ["unease", "anxiety", "tension", "dread", "instability", "wrongness"],
    "\u7126\u616e":    ["anxiety", "unease", "tension", "dread", "nervous"],
    "\u7dca\u5f35":    ["tension", "anxiety", "unease"],
    # Simplified Chinese variants of the above (jieba outputs simplified)
    "\u7d27\u5f20":    ["tension", "anxiety", "unease"],
    "\u5b64\u72ec":    ["loneliness", "isolation", "alone", "emptiness"],
    "\u6050\u60e7":    ["fear", "dread", "unease", "horror"],
    "\u6743\u529b":    ["power", "authority", "hierarchy"],
    "\u538b\u6291":    ["oppression", "control", "tension", "dread", "entrapment"],
    "\u7edd\u671b":    ["despair", "emptiness", "void", "isolation"],
    "\u7126\u8651":    ["anxiety", "unease", "tension", "dread", "nervous"],
    "\u5b64\u7368":    ["loneliness", "isolation", "alone", "emptiness"],
    "\u5bc2\u5bde":    ["loneliness", "isolation", "emptiness"],
    "\u5b64\u5bc2":    ["loneliness", "isolation", "silence", "emptiness"],
    "\u6050\u61fc":    ["fear", "dread", "unease", "horror"],
    "\u5e73\u975c":    ["calm", "peace", "stability", "balance", "stillness"],
    "\u6c89\u601d":    ["contemplation", "reflection", "harmony"],
    "\u6b0a\u529b":    ["power", "authority", "hierarchy"],
    "\u58d3\u6291":    ["oppression", "control", "tension", "dread", "entrapment"],
    "\u514b\u5236":    ["control", "restraint", "order", "stillness"],
    "\u51b7\u5cfb":    ["cold", "distance", "clinical", "order"],
    "\u5bd2\u51b7":    ["cold", "isolation", "distance"],
    "\u6c89\u91cd":    ["despair", "heaviness", "weight", "oppression"],
    "\u51b0\u51b7":    ["cold", "distance", "isolation", "clinical", "emotionless"],
    "\u7d55\u671b":    ["despair", "emptiness", "void", "isolation"],
    "\u656c\u754f":    ["awe", "scale", "contemplation"],
    "\u5026\u6020":    ["fatigue", "emptiness", "reflection"],
    "\u6728\u7136":    ["stillness", "emptiness", "distance", "cold"],
}

# --- Emotion modifiers (jieba-compatible): these allow "\u9690\u9690\u4e0d\u5b89"
# to be segmented into ["\u9690\u9690", "\u4e0d\u5b89"] and BOTH tokens contribute keywords.
# Modifier words map to intensifier/quality keywords rather than base emotions.

_EMOTION_MODIFIER_MAP: Dict[str, List[str]] = {
    "\u9690\u9690":  ["subdued", "suppressed", "unease", "brewing"],      # faint, hidden
    "\u6de1\u6de1":  ["subdued", "mild", "understated"],                # light, faint
    "\u5fae\u5fae":  ["subtle", "slight", "trembling"],                 # slight, trembling
    "\u9010\u6e10":  ["growing", "mounting", "escalating"],               # gradually
    "\u4e00\u4e1d":  ["trace", "hint", "sliver"],                        # a trace of
    "\u4e9b\u8bb8":  ["slight", "moderate", "faint"],                    # a bit of
    "\u7ec6\u5bc6":  ["fine", "subtle", "intricate"],                    # fine-grained
    "\u88c2\u75d5":  ["fracture", "crack", "instability", "wrongness"],   # cracks
}

# Merge modifiers into main map so _resolve_emotion_keywords finds them
_EMOTION_MAP.update(_EMOTION_MODIFIER_MAP)

_SCENE_MAP: Dict[str, List[str]] = {
    "isolation":       ["isolation", "loneliness", "contemplation", "despair"],
    "tension":         ["tension", "anxiety", "psychological", "conflict", "horror"],
    "romance":         ["romance", "intimacy", "peace", "warmth"],
    "confrontation":   ["confrontation", "power", "authority"],
    "dialogue":        ["dialogue", "conversation"],
    "action":          ["action", "energy", "kinetic"],
    "revelation":      ["revelation", "realization", "epiphany"],
    "institution":     ["institution", "power", "authority", "order"],
    "ritual":          ["ritual", "ceremony", "order", "community"],
    "journey":         ["journey", "travel", "direction"],
    "establishing":    ["establishing", "scale", "context"],
    "contemplation":   ["contemplation", "reflection", "existential"],
    "psychological":   ["psychological", "tension", "anxiety", "unease", "instability"],
    "horror":          ["horror", "fear", "dread", "anxiety"],
    "peace":           ["peace", "calm", "stability", "resolution"],
}


# ============================================================================
# Data types
# ============================================================================

@dataclass
class QueryResult:
    """A single library retrieval result with relevance metadata."""
    entry: Dict[str, Any]
    score: float
    semantic_score: float = 0.0
    shot_param_score: float = 0.0
    matched_on: List[str] = field(default_factory=list)
    rank: int = 0


# ============================================================================
# Loader
# ============================================================================

def load_entries(entries_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load composition entries from the YAML knowledge base."""
    if entries_path is None:
        entries_path = Path(__file__).resolve().parent / "entries" / "compositions.yaml"
    if not entries_path.exists():
        raise FileNotFoundError(f"Composition entries not found: {entries_path}")
    with open(entries_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "entries" not in data:
        raise ValueError("Invalid compositions YAML: expected top-level 'entries' key")
    return data["entries"]


# ============================================================================
# Semantic scoring -- emotion + scene_type, normalized 0-1
# ============================================================================

def _semantic_score(
    emotion_keywords: List[str],
    scene_keywords: List[str],
    entry: Dict[str, Any],
) -> Tuple[float, List[str]]:
    """Compute semantic relevance score for an entry.

    Combines emotion and scene_type matching, both normalized to 0-1
    by dividing hits by query keyword count.

    Returns (score 0.0-1.0, list of matched descriptors).
    """
    matched: List[str] = []

    # Tokenize entry fields
    entry_emotions_raw = entry.get("emotions", [])
    if isinstance(entry_emotions_raw, str):
        entry_emotions_raw = [entry_emotions_raw]
    entry_emotion_tokens: List[str] = []
    for e in entry_emotions_raw:
        entry_emotion_tokens.extend(_tokenize(str(e)))

    entry_scenes_raw = entry.get("scene_types", [])
    if isinstance(entry_scenes_raw, str):
        entry_scenes_raw = [entry_scenes_raw]
    entry_scene_tokens: List[str] = []
    for s in entry_scenes_raw:
        entry_scene_tokens.extend(_tokenize(str(s)))

    # Emotion match -- normalized by query keyword count
    emotion_score = 0.0
    if emotion_keywords:
        e_score, e_matched = _token_match(emotion_keywords, entry_emotion_tokens)
        emotion_score = e_score
        matched.extend(e_matched)

    # Scene type match -- normalized by query keyword count
    scene_score = 0.0
    if scene_keywords:
        s_score, s_matched = _token_match(scene_keywords, entry_scene_tokens)
        scene_score = s_score
        matched.extend(s_matched)

    # Combine: average of the two sub-scores (each already 0-1)
    sub_scores = []
    sub_weights = []
    if emotion_keywords:
        sub_scores.append(emotion_score)
        sub_weights.append(1.0)
    if scene_keywords:
        sub_scores.append(scene_score)
        sub_weights.append(1.0)

    if not sub_scores:
        return 0.0, []

    total = sum(s * w for s, w in zip(sub_scores, sub_weights))
    total_weight = sum(sub_weights)
    semantic = total / total_weight if total_weight > 0 else 0.0

    return semantic, matched


# ============================================================================
# Shot-param scoring -- framing/lens/angle/focus/movement, normalized 0-1
# ============================================================================

# Shot parameters that each entry declares compatibility with
_SHOT_PARAM_ENTRY_KEYS: Dict[str, str] = {
    "framing":  "framings",
    "lens":     "lenses",
    "angle":    "angles",
    "focus":    "focus_types",
    "movement": "movements",
}


def _shot_param_score(context: Dict[str, Any], entry: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Compute how well the entry's declared shot-param compatibility
    matches the shot context.

    Each provided shot param contributes equally.  If framing=CU and the entry
    lists CU in its framings, that's one hit.  Score = hits / params_provided.

    Returns (score 0.0-1.0, list of matched descriptors).
    """
    matched: List[str] = []
    hits = 0
    params_provided = 0

    for context_key, entry_key in _SHOT_PARAM_ENTRY_KEYS.items():
        context_val = context.get(context_key, "")
        if not context_val:
            continue
        params_provided += 1

        entry_vals = entry.get(entry_key, [])
        if isinstance(entry_vals, str):
            entry_vals = [entry_vals]

        if context_val in entry_vals:
            hits += 1
            matched.append(f"shot:{context_key}={context_val}")

    if params_provided == 0:
        return 0.0, []

    return hits / params_provided, matched


# ============================================================================
# Unified scoring -- combines semantic + shot-param
# ============================================================================

def _compute_entry_score(
    emotion_keywords: List[str],
    scene_keywords: List[str],
    context: Dict[str, Any],
    entry: Dict[str, Any],
) -> QueryResult:
    """Compute the combined relevance score for one entry.

    final = W_SEMANTIC * semantic_score + W_SHOT * shot_param_score

    Each sub-score is independently normalized to 0-1, ensuring that no
    single dimension can dominate through raw keyword count.
    """
    sem_score, sem_matched = _semantic_score(emotion_keywords, scene_keywords, entry)
    shot_score, shot_matched = _shot_param_score(context, entry)

    final = W_SEMANTIC * sem_score + W_SHOT * shot_score
    all_matched = sem_matched + shot_matched

    return QueryResult(
        entry=entry,
        score=round(final, 4),
        semantic_score=round(sem_score, 4),
        shot_param_score=round(shot_score, 4),
        matched_on=all_matched,
    )


# ============================================================================
# Public query API
# ============================================================================

def _resolve_emotion_keywords(raw_emotion: str) -> List[str]:
    """Resolve an emotion string (English or Chinese) to normalized keyword tokens."""
    if not raw_emotion:
        return []

    # 1. Direct full-string lookup (preserves existing exact-match behavior)
    mapped = _EMOTION_MAP.get(raw_emotion, [])
    if mapped:
        return mapped

    # 2. Case-insensitive English lookup
    eng_key = raw_emotion.strip().lower()
    mapped = _EMOTION_MAP.get(eng_key, [])
    if mapped:
        return mapped

    # 3. Jieba-segment, then union token lookups in _EMOTION_MAP.
    #    This handles modifier+base combos like "隐隐不安" -> ["隐隐", "不安"]
    #    where "不安" is in the map but the full phrase is not.
    tokens = _tokenize(raw_emotion)
    if tokens:
        keywords: List[str] = []
        seen: set = set()
        for token in tokens:
            mapped_token = _EMOTION_MAP.get(token, [])
            if not mapped_token:
                # Try case-insensitive
                mapped_token = _EMOTION_MAP.get(token.lower(), [])
            for kw in mapped_token:
                if kw not in seen:
                    seen.add(kw)
                    keywords.append(kw)
        if keywords:
            return keywords

    # 4. Last resort: use raw tokens as-is
    return tokens if tokens else [raw_emotion.strip().lower()]


def _resolve_scene_keywords(raw_scene: str) -> List[str]:
    """Resolve a scene_type string to normalized keyword tokens."""
    if not raw_scene:
        return []
    mapped = _SCENE_MAP.get(raw_scene.strip().lower(), [])
    if mapped:
        return mapped
    return _tokenize(raw_scene)


def query_compositions(
    context: Dict[str, Any],
    *,
    entries_path: Optional[Path] = None,
    min_score: float = 0.05,
    max_results: int = 10,
) -> List[Tuple[Dict[str, Any], float]]:
    """Retrieve composition entries relevant to the given shot context.

    Token-based matching (v2): exact token equality, no substring matching.
    Scoring (v2): W_SEMANTIC * semantic_score + W_SHOT * shot_param_score.

    Args:
        context: Dict with optional keys:
            emotion, scene_type, framing, lens, angle, focus, movement
        entries_path: Override path to compositions.yaml.
        min_score: Minimum combined score to include.
        max_results: Max results to return.

    Returns:
        List of (entry_dict, score) sorted by score descending.
    """
    results = query_compositions_detailed(
        context,
        entries_path=entries_path,
        min_score=min_score,
        max_results=max_results,
    )
    return [(r.entry, r.score) for r in results]


def query_compositions_detailed(
    context: Dict[str, Any],
    **kwargs: Any,
) -> List[QueryResult]:
    """Like query_compositions() but returns full QueryResult objects."""
    entries = load_entries(kwargs.pop("entries_path", None))
    min_score = kwargs.get("min_score", 0.05)
    max_results = kwargs.get("max_results", 10)

    raw_emotion = context.get("emotion", "")
    raw_scene = context.get("scene_type", "")

    emotion_keywords = _resolve_emotion_keywords(raw_emotion)
    scene_keywords = _resolve_scene_keywords(raw_scene)

    results: List[QueryResult] = []

    for entry in entries:
        qr = _compute_entry_score(emotion_keywords, scene_keywords, context, entry)
        if qr.score >= min_score:
            results.append(qr)

    results.sort(key=lambda r: r.score, reverse=True)
    for i, r in enumerate(results[:max_results]):
        r.rank = i + 1

    return results[:max_results]
