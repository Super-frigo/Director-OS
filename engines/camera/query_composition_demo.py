"""End-to-end demo: Project context -> Composition Library -> Engine decision.

Validates the ADR-004 pipeline with v2 query (token-based matching, balanced weights).

SHOT_03 context:
  - emotion: unease
  - framing: CU (close-up)
  - lens: 85mm
  - lighting.position: SIDE_90 (side light -- half face in shadow)
  - composition.rule: CENTER_COMPOSITION
  - scene_type: psychological

Usage:
    python engines/camera/query_composition_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libraries.composition.query import (
    query_compositions_detailed,
    set_weights,
)


SHOT_03_CONTEXT = {
    "shot_id": "SHOT_03",
    "beat_ref": "THE_FACE",
    "duration": 4.0,
    "emotion": "unease",
    "emotion_intensity": 6,
    "framing": "CU",
    "lens": "85mm",
    "angle": "EYE_LEVEL",
    "movement": "STATIC",
    "focus": "SHALLOW_FOCUS",
    "scene_type": "psychological",
    "current_rule": "CENTER_COMPOSITION",
    "lighting_position": "SIDE_90",
    "lighting_mood": "side light reveals cheekbone and eye socket shadows",
}

RULE_TO_ADVICE = {
    "CENTER_COMPOSITION": {
        "desc": "Keep CENTER_COMPOSITION -- unease + direct face-on = maximum confrontation",
        "changes": [
            "No rule change needed; ensure side light further breaks symmetry",
            "Shift eyes slightly above center for subliminal imbalance",
        ],
    },
    "ASYMMETRICAL": {
        "desc": "Switch to ASYMMETRICAL -- break center, push detective off-axis",
        "changes": [
            "Move face to left 1/3, large negative space (mist) on right",
            "Side light: lit half faces frame edge, dark half faces void",
            "Frame imbalance signals inner collapse",
        ],
    },
    "DIAGONAL": {
        "desc": "Incorporate DIAGONAL -- tilted axis amplifies instability",
        "changes": [
            "Side light top-left to bottom-right = diagonal face split",
            "Subtle DUTCH_ANGLE (2-3 deg) -- barely visible, viscerally felt",
            "Diagonal + CU + 85mm = face as tilted mask about to topple",
        ],
    },
}


def run_query(label: str, w_sem: float, w_shot: float) -> list:
    """Run a query with given weights and return results."""
    set_weights(w_sem, w_shot)
    return query_compositions_detailed(
        {
            "emotion": SHOT_03_CONTEXT["emotion"],
            "scene_type": SHOT_03_CONTEXT["scene_type"],
            "framing": SHOT_03_CONTEXT["framing"],
            "lens": SHOT_03_CONTEXT["lens"],
            "angle": SHOT_03_CONTEXT["angle"],
            "focus": SHOT_03_CONTEXT["focus"],
        },
        min_score=0.05,
        max_results=8,
    )


def print_results(results: list) -> None:
    for r in results:
        bar = "#" * int(r.score * 20) + "-" * (20 - int(r.score * 20))
        print(f"  [{r.rank}] {r.entry['name']:<35} [{bar}] {r.score:.3f}")
        print(f"      Rule: {r.entry['rule']}  "
              f"semantic={r.semantic_score:.3f}  shot_param={r.shot_param_score:.3f}")
        print(f"      Matched: {', '.join(r.matched_on[:6])}")
        print()


def main() -> None:
    print("=" * 72)
    print("Composition Library Retrieval Demo -- v2 (token matching, balanced weights)")
    print("=" * 72)
    print()

    print("Shot context:")
    for k in ("emotion", "framing", "lens", "scene_type", "current_rule", "lighting_position"):
        print(f"  {k}: {SHOT_03_CONTEXT[k]}")
    print()

    # -- BEFORE: v1 style (W_semantic=0.85, W_shot=0.15, mimicking old weights) --
    print("-" * 72)
    print("BEFORE (old-style weights: semantic=0.85, shot=0.15)")
    print("-" * 72)
    results_before = run_query("before", 0.85, 0.15)
    print_results(results_before)

    # -- AFTER: balanced (W_semantic=0.50, W_shot=0.50) --
    print("-" * 72)
    print("AFTER (balanced weights: semantic=0.50, shot=0.50)")
    print("-" * 72)
    results_after = run_query("after", 0.50, 0.50)
    print_results(results_after)

    # -- Comparison summary --
    print("-" * 72)
    print("Ranking Comparison: BEFORE vs AFTER")
    print("-" * 72)
    print()
    print(f"  {'Rank':<6} {'BEFORE (W_sem=0.85)':<38} {'AFTER (W_sem=0.50)':<38}")
    print(f"  {'-'*6} {'-'*38} {'-'*38}")
    for i in range(max(len(results_before), len(results_after))):
        b_name = results_before[i].entry['name'] if i < len(results_before) else "--"
        b_score = results_before[i].score if i < len(results_before) else 0
        a_name = results_after[i].entry['name'] if i < len(results_after) else "--"
        a_score = results_after[i].score if i < len(results_after) else 0
        marker = " <--" if b_name != a_name else ""
        print(f"  {i+1:<6} {b_name:<30} ({b_score:.3f})     {a_name:<30} ({a_score:.3f}){marker}")
    print()

    # -- What changed? --
    print("-" * 72)
    print("Key Changes")
    print("-" * 72)
    print()

    # Find entries that moved significantly
    before_map = {r.entry["id"]: r for r in results_before}
    after_map = {r.entry["id"]: r for r in results_after}

    all_ids = set(before_map.keys()) | set(after_map.keys())
    moved = []
    for eid in all_ids:
        b = before_map.get(eid)
        a = after_map.get(eid)
        b_rank = b.rank if b else 99
        a_rank = a.rank if a else 99
        if abs(b_rank - a_rank) >= 1:
            moved.append((eid, b_rank, a_rank, abs(b_rank - a_rank)))
    moved.sort(key=lambda x: -x[3])

    if moved:
        print("  Entries that changed rank significantly:")
        for eid, old_r, new_r, delta in moved[:8]:
            name = (before_map.get(eid) or after_map.get(eid)).entry["name"]
            direction = "UP" if new_r < old_r else "DOWN" if new_r > old_r else "--"
            old_s = before_map[eid].semantic_score if eid in before_map else 0
            old_p = before_map[eid].shot_param_score if eid in before_map else 0
            new_s = after_map[eid].semantic_score if eid in after_map else 0
            new_p = after_map[eid].shot_param_score if eid in after_map else 0
            print(f"    {direction} {name}: rank {old_r} -> {new_r} "
                  f"(sem {old_s:.2f}/{new_s:.2f}, shot {old_p:.2f}/{new_p:.2f})")
    print()

    # -- Substring fix confirmation --
    print("-" * 72)
    print("Substring False-Positive Fix Verification")
    print("-" * 72)
    print()
    print("  Previously, 'instability' substring-matched 'stability',")
    print("  causing TRIANGULAR and BALANCED to appear with inflated scores.")
    print()

    # Check: no matched_on contains "substr"
    for r in results_after:
        for m in r.matched_on:
            assert "substr" not in m, f"substring match still present: {m}"

    # Check: TRIANGULAR not present or has honest score
    tri = next((r for r in results_after if r.entry["id"] == "comp_triangular"), None)
    bal = next((r for r in results_after if r.entry["id"] == "comp_balanced"), None)

    if tri:
        print(f"  TRIANGULAR: score={tri.score:.3f}, matched_on={tri.matched_on[:4]}")
    else:
        print("  TRIANGULAR: NOT in results (previously scored 0.468 via substring)")
    if bal:
        print(f"  BALANCED: score={bal.score:.3f}, matched_on={bal.matched_on[:4]}")
    else:
        print("  BALANCED: NOT in results (previously scored 0.275 via substring)")
    print()

    # -- What-if Engine adopts suggestions --
    print("-" * 72)
    print("What if Engine adopts the top 3 suggestions?")
    print("-" * 72)
    print()
    for r in results_after[:3]:
        rule = r.entry["rule"]
        advice = RULE_TO_ADVICE.get(rule)
        print(f"  [#{r.rank}] {r.entry['name']} (score={r.score:.3f})")
        if advice:
            print(f"       {advice['desc']}")
            for ch in advice["changes"]:
                print(f"         * {ch}")
        print()

    # Reset weights
    set_weights(0.50, 0.50)


if __name__ == "__main__":
    main()
