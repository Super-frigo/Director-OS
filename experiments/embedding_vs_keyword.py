"""Controlled experiment: Keyword retrieval vs Embedding semantic retrieval.

Query: "隐隐不安" (raw Chinese from the_hanging.md creative.objective emotional_arc)
       — a nuanced phrase meaning "faint, lingering unease."

This experiment does NOT modify query.py.  It runs both retrieval methods side by
side on the same query and compares the top-3 results.

Method A: Keyword retrieval (query.py v2, token-based, _EMOTION_MAP lookup)
Method B: Embedding retrieval (fastembed multilingual model, cosine similarity)

Output: a comparison report saved to experiments/embedding_vs_keyword_report.md

Usage:
    python experiments/embedding_vs_keyword.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================================
# Query under test
# ============================================================================

QUERY = "隐隐不安"  # from the_hanging.md creative emotional_arc
QUERY_CONTEXT = {
    "emotion": QUERY,
    "scene_type": "psychological",
    "framing": "CU",
    "lens": "85mm",
}


# ============================================================================
# Load composition entries
# ============================================================================

def load_entries() -> List[Dict[str, Any]]:
    from libraries.composition.query import load_entries as _load
    return _load()


# ============================================================================
# Method A: Keyword retrieval
# ============================================================================

def run_keyword_retrieval(entries: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], float]]:
    """Run keyword-based retrieval on QUERY_CONTEXT."""
    from libraries.composition.query import query_compositions
    return query_compositions(QUERY_CONTEXT, min_score=0.02, max_results=10)


# ============================================================================
# Method B: Embedding retrieval
# ============================================================================

def build_embedding_index(
    entries: List[Dict[str, Any]],
    model_name: str = "BAAI/bge-small-zh-v1.5",
) -> Tuple[np.ndarray, List[str], Any]:
    """Build a simple numpy cosine-similarity index from entry effect+notes fields.

    Args:
        entries: Composition entry dicts.
        model_name: fastembed model name.  Uses a Chinese-optimized small model.

    Returns:
        (embeddings_matrix [N x D], entry_ids, model_instance)
    """
    from fastembed import TextEmbedding

    print(f"  Loading embedding model: {model_name} ...")
    model = TextEmbedding(model_name=model_name)

    # Build texts: effect + notes concatenated
    texts: List[str] = []
    entry_ids: List[str] = []
    for entry in entries:
        eid = entry["id"]
        effect = entry.get("effect", "")
        notes = entry.get("notes", "")
        text = f"{effect} {notes}"
        texts.append(text)
        entry_ids.append(eid)

    print(f"  Encoding {len(texts)} entries ...")
    embeddings_list = list(model.embed(texts))
    embeddings = np.array(embeddings_list, dtype=np.float32)

    # Normalize for cosine similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embeddings = embeddings / norms

    print(f"  Embedding shape: {embeddings.shape}")
    return embeddings, entry_ids, model


def run_embedding_retrieval(
    query: str,
    embeddings: np.ndarray,
    entry_ids: List[str],
    model: Any,
    entries: List[Dict[str, Any]],
    top_k: int = 10,
) -> List[Tuple[Dict[str, Any], float]]:
    """Run embedding-based semantic retrieval.

    Args:
        query: Chinese query text.
        embeddings: Normalized [N x D] embedding matrix.
        entry_ids: List of entry ids matching embedding rows.
        model: fastembed TextEmbedding instance.
        entries: Full entry dicts.
        top_k: Number of results.

    Returns:
        List of (entry_dict, cosine_similarity) sorted descending.
    """
    # Encode query
    query_emb = np.array(list(model.embed([query])), dtype=np.float32)
    query_emb = query_emb / np.linalg.norm(query_emb, axis=1, keepdims=True)

    # Cosine similarity (dot product on normalized vectors)
    scores = (embeddings @ query_emb.T).flatten()

    # Sort descending
    top_indices = np.argsort(scores)[::-1][:top_k]

    # Build id -> entry map
    entry_map = {e["id"]: e for e in entries}

    results: List[Tuple[Dict[str, Any], float]] = []
    for idx in top_indices:
        eid = entry_ids[idx]
        score = float(scores[idx])
        if eid in entry_map:
            results.append((entry_map[eid], round(score, 4)))

    return results


# ============================================================================
# Comparison & reporting
# ============================================================================

def analyze(
    kw_results: List[Tuple[Dict[str, Any], float]],
    emb_results: List[Tuple[Dict[str, Any], float]],
) -> str:
    """Produce a comparison analysis as a Markdown string."""
    lines: List[str] = []

    lines.append("# Embedding vs Keyword Retrieval — Controlled Experiment")
    lines.append("")
    lines.append(f"**Query:** `{QUERY}` (raw Chinese from `the_hanging.md` emotional arc)")
    lines.append("")
    lines.append("**Query context:**")
    lines.append(f"```")
    lines.append(f"  emotion:     {QUERY}")
    lines.append(f"  scene_type:  psychological")
    lines.append(f"  framing:     CU")
    lines.append(f"  lens:        85mm")
    lines.append(f"```")
    lines.append("")

    # ── Top-3 comparison ──
    lines.append("## Top-3 Comparison")
    lines.append("")
    lines.append("| Rank | Keyword Retrieval | Score | Embedding Retrieval | Score |")
    lines.append("|------|-------------------|-------|---------------------|-------|")

    for i in range(3):
        kw_name = kw_results[i][0]["name"] if i < len(kw_results) else "(none)"
        kw_score = kw_results[i][1] if i < len(kw_results) else 0.0
        emb_name = emb_results[i][0]["name"] if i < len(emb_results) else "(none)"
        emb_score = emb_results[i][1] if i < len(emb_results) else 0.0
        lines.append(f"| {i+1} | {kw_name} | {kw_score:.3f} | {emb_name} | {emb_score:.3f} |")

    lines.append("")

    # ── Full keyword results ──
    lines.append("## Method A: Keyword Retrieval (full results)")
    lines.append("")
    for i, (entry, score) in enumerate(kw_results):
        rule = entry["rule"]
        effect = entry.get("effect", "").replace("\n", " ")[:120]
        lines.append(f"{i+1}. **{entry['name']}** ({rule}) — score={score:.3f}")
        lines.append(f"   > {effect}...")
        lines.append("")

    # ── Full embedding results ──
    lines.append("## Method B: Embedding Retrieval (full results)")
    lines.append("")
    for i, (entry, score) in enumerate(emb_results):
        rule = entry["rule"]
        effect = entry.get("effect", "").replace("\n", " ")[:120]
        lines.append(f"{i+1}. **{entry['name']}** ({rule}) — cosine={score:.4f}")
        lines.append(f"   > {effect}...")
        lines.append("")

    # ── Analysis ──
    lines.append("## Analysis")
    lines.append("")

    # Did keyword retrieval return anything?
    if len(kw_results) == 0:
        lines.append("### Keyword retrieval: FAILED")
        lines.append("")
        lines.append(f"The query `{QUERY}` produced **zero results** from keyword retrieval.")
        lines.append(f"This is because `{QUERY}` is not in `_EMOTION_MAP` (which only has `不安`, not `隐隐不安`),")
        lines.append(f"and after falling through the map lookup, the raw token `隐隐不安` has no English")
        lines.append(f"token overlap with any entry's `emotions` or `keywords` fields.")
        lines.append("")
        lines.append("**This is the semantic ceiling of keyword matching**: any Chinese phrase that")
        lines.append("falls outside the controlled vocabulary is invisible to the system.  Expanding")
        lines.append("`_EMOTION_MAP` can fix this specific case, but there are infinitely many")
        lines.append("possible Chinese emotion phrases — the vocabulary gap is unbounded.")
    elif len(kw_results) <= 2:
        lines.append("### Keyword retrieval: MARGINAL")
        lines.append("")
        lines.append(f"Keyword retrieval returned only {len(kw_results)} result(s).  The query")
        lines.append(f"`{QUERY}` partially matched via token overlap but could not surface a")
        lines.append(f"meaningful set of candidates.")
        lines.append("")

    # Overlap analysis
    kw_ids = {r[0]["id"] for r in kw_results[:5]}
    emb_ids = {r[0]["id"] for r in emb_results[:5]}
    overlap = kw_ids & emb_ids
    kw_only = kw_ids - emb_ids
    emb_only = emb_ids - kw_ids

    lines.append("### Top-5 Overlap")
    lines.append("")
    lines.append(f"- Both methods agree on: {len(overlap)} entries")
    if overlap:
        names = [next(r[0]["name"] for r in kw_results if r[0]["id"] == oid) for oid in overlap]
        lines.append(f"  - {', '.join(names)}")
    lines.append(f"- Keyword-only: {len(kw_only)} entries")
    lines.append(f"- Embedding-only: {len(emb_only)} entries")
    if emb_only:
        names = [next(r[0]["name"] for r in emb_results if r[0]["id"] == eid) for eid in emb_only]
        lines.append(f"  - {', '.join(names)}")
    lines.append("")

    # Quality assessment
    lines.append("### Relevance Assessment (Human Judgment)")
    lines.append("")
    lines.append(f"Query `{QUERY}` means 'faint, lingering unease' — a subtle, growing")
    lines.append(f"disquiet that hasn't fully surfaced.  In the context of the_hanging.md,")
    lines.append(f"it describes the detective's dawning suspicion during a close-up shot.")
    lines.append("")
    lines.append("Expected relevant composition rules for this emotion in a CU:")
    lines.append("- **ASYMMETRICAL**: unease, imbalance, 'something feels wrong'")
    lines.append("- **CENTER_COMPOSITION**: direct confrontation, the face as mask")
    lines.append("- **NEGATIVE_SPACE**: isolation, emotional void")
    lines.append("- **DIAGONAL**: instability, tilted perspective")
    lines.append("- **FRAME_WITHIN_FRAME**: voyeurism, distance, observation")
    lines.append("")

    # Score each method
    kw_hits = sum(1 for r in kw_results[:3] if r[0]["rule"] in {
        "ASYMMETRICAL", "CENTER_COMPOSITION", "NEGATIVE_SPACE", "DIAGONAL", "FRAME_WITHIN_FRAME"
    })
    emb_hits = sum(1 for r in emb_results[:3] if r[0]["rule"] in {
        "ASYMMETRICAL", "CENTER_COMPOSITION", "NEGATIVE_SPACE", "DIAGONAL", "FRAME_WITHIN_FRAME"
    })

    lines.append(f"- Keyword top-3 relevant hits: {kw_hits}/3")
    lines.append(f"- Embedding top-3 relevant hits: {emb_hits}/3")
    lines.append("")

    # ── Recommendation ──
    lines.append("## Recommendation")
    lines.append("")

    if len(kw_results) == 0:
        lines.append("### Verdict: Keyword retrieval is BROKEN for this query.")
        lines.append("")
        lines.append(f"The phrase `{QUERY}` — a perfectly natural Chinese expression — is")
        lines.append(f"invisible to keyword matching.  This is not fixable by expanding")
        lines.append(f"`_EMOTION_MAP` alone, because the space of possible Chinese emotion")
        lines.append(f"phrases is unbounded.  Every new Project can introduce novel phrasing.")
        lines.append("")
        if emb_hits >= 2:
            lines.append("Embedding retrieval handles this gracefully — it maps `隐隐不安` to")
            lines.append("relevant composition rules without any vocabulary mapping.  A hybrid")
            lines.append("approach is clearly warranted: keyword for high-confidence exact matches,")
            lines.append("embedding for semantic fallback on out-of-vocabulary queries.")
        else:
            lines.append("Embedding retrieval also struggled with this query.  This may indicate")
            lines.append("that the embedding model's Chinese semantic understanding is insufficient")
            lines.append("for nuanced emotional vocabulary, or that the composition entry texts")
            lines.append("don't describe emotions at the right granularity.")
    else:
        lines.append("### Verdict: Keyword retrieval PARTIALLY WORKS for this query.")
        lines.append("")
        lines.append(f"Keyword retrieval found {len(kw_results)} results.  The question is")
        lines.append("whether these results are *relevant* to the nuanced meaning of `隐隐不安`,")
        lines.append("or merely surface-level matches on component tokens.")
        lines.append("")
        if emb_hits > kw_hits:
            lines.append("Embedding retrieval found MORE relevant results.  A hybrid approach")
            lines.append("would improve recall for nuanced emotional queries.")
        elif emb_hits == kw_hits and emb_hits >= 2:
            lines.append("Both methods perform comparably.  Embedding is a nice-to-have but")
            lines.append("not urgent.  Expanding `_EMOTION_MAP` may be sufficient for now.")
        else:
            lines.append("Both methods produce limited results.  The composition library may")
            lines.append("need richer emotion descriptions in entry texts to improve either method.")

    lines.append("")
    lines.append("### Decision Framework")
    lines.append("")
    lines.append("| Factor | Keyword-only | Hybrid (keyword + embedding) |")
    lines.append("|--------|-------------|------------------------------|")
    lines.append("| OOV phrase handling | Requires manual _EMOTION_MAP entry | Automatic via semantic similarity |")
    lines.append("| Determinism | 100% deterministic | Model-dependent (same model = same output) |")
    lines.append("| Dependency weight | 0 extra deps | +fastembed (~50MB model) |")
    lines.append("| Chinese nuance | Lossy (map to English keywords) | Direct Chinese semantic understanding |")
    lines.append("| Debuggability | Transparent (exact token matches visible) | Opaque (cosine scores) |")
    lines.append("| Maintenance cost | Ongoing vocabulary curation | Model updates, embedding drift |")
    lines.append("")

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    print("=" * 72)
    print("Embedding vs Keyword Retrieval — Controlled Experiment")
    print(f"Query: '{QUERY}'")
    print("=" * 72)
    print()

    # Load
    print("[1/4] Loading composition entries ...")
    entries = load_entries()
    print(f"      {len(entries)} entries loaded.")
    print()

    # Method A: Keyword
    print("[2/4] Method A: Keyword retrieval ...")
    kw_results = run_keyword_retrieval(entries)
    print(f"      {len(kw_results)} results.")
    for i, (entry, score) in enumerate(kw_results[:5]):
        print(f"        {i+1}. {entry['name']} ({entry['rule']}) — {score:.3f}")
    if len(kw_results) == 0:
        print("        (no results — out-of-vocabulary query)")
    print()

    # Method B: Embedding
    print("[3/4] Method B: Embedding retrieval ...")
    try:
        embeddings, entry_ids, model = build_embedding_index(entries)
        emb_results = run_embedding_retrieval(QUERY, embeddings, entry_ids, model, entries)
        print(f"      {len(emb_results)} results.")
        for i, (entry, score) in enumerate(emb_results[:5]):
            print(f"        {i+1}. {entry['name']} ({entry['rule']}) — {score:.4f}")
    except Exception as e:
        print(f"      Embedding retrieval FAILED: {e}")
        print("      Falling back to dummy results for report generation.")
        emb_results = []
    print()

    # Report
    print("[4/4] Generating comparison report ...")
    report = analyze(kw_results, emb_results)

    out_path = ROOT / "experiments" / "embedding_vs_keyword_report.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"      Report saved to: {out_path}")
    print()

    # Quick summary to stdout
    print("-" * 72)
    print("Quick Summary")
    print("-" * 72)
    print(f"  Keyword top-3:   {[(r[0]['name'], round(r[1],3)) for r in kw_results[:3]]}")
    print(f"  Embedding top-3: {[(r[0]['name'], round(r[1],3)) for r in emb_results[:3]]}")
    kw_ids_top3 = {r[0]["id"] for r in kw_results[:3]}
    emb_ids_top3 = {r[0]["id"] for r in emb_results[:3]}
    print(f"  Overlap: {kw_ids_top3 & emb_ids_top3}")
    print(f"  Keyword hit count: {len(kw_results)}")
    print(f"  Embedding hit count: {len(emb_results)}")


if __name__ == "__main__":
    main()
