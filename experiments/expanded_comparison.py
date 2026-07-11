"""Expanded controlled experiment: Keyword vs Embedding vs Same-Lang Embedding.

Queries (9 total, 8 new + original "隐隐不安"):
  1. 隐隐不安         (original, faint unease)
  2. 细密的裂痕       (metaphorical, no direct emotion word)
  3. 挥之不去的异样感  (compound modifier)
  4. 冰冷的仪式感     (compound: cold + ritual)
  5. 不安的初现       (modifier + emotion)
  6. 压抑的日常       (emotion + context)
  7. 无声的压迫       (metaphorical, atmosphere)
  8. 逐渐逼近的恐惧   (external, mounting dread)
  9. 表面平静下的暗流  (external, calm surface + undercurrent)

Methods:
  A. Keyword (post-fix, jieba-segmented lookup)
  B. Embedding (cross-lingual: CN query -> EN entries, BAAI/bge-small-zh-v1.5)
  C. Embedding same-lang (CN query -> CN entries, same model)

Output: experiments/expanded_comparison_report.md
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
# Queries under test
# ============================================================================

QUERIES = [
    ("隐隐不安",             "original: faint unease"),
    ("细密的裂痕",           "metaphorical: fine cracks"),
    ("挥之不去的异样感",     "compound: lingering wrongness"),
    ("冰冷的仪式感",         "compound: cold ritual feeling"),
    ("不安的初现",           "modifier: first appearance of unease"),
    ("压抑的日常",           "contextual: oppressive everyday"),
    ("无声的压迫",           "metaphorical: silent oppression"),
    ("逐渐逼近的恐惧",       "external: mounting dread"),
    ("表面平静下的暗流",     "external: undercurrent beneath calm"),
]

# Minimal shot context for keyword retrieval
QUERY_CONTEXT = {
    "scene_type": "psychological",
    "framing": "CU",
    "lens": "85mm",
}


# ============================================================================
# Chinese translations of entry effect+notes (rough, for same-lang experiment)
# ============================================================================

CN_TRANSLATIONS: Dict[str, str] = {
    "comp_rule_of_thirds": (
        "创造平衡但动态的构图。偏离中心的主体产生视觉张力，同时保持自然感——"
        "视线被吸引到交叉点而非中心。最广泛教授的构图规则，灵活性是其优势。"
    ),
    "comp_golden_ratio": (
        "产生潜意识层面感到和谐的构图。黄金螺旋引导视线沿自然曲线走向主体，"
        "创造必然性和秩序感。适合哲学沉思场景、自然景观、文艺复兴风格时期片。"
    ),
    "comp_center_composition": (
        "直接、对抗、权威。居中的主体占据画面，要求观众全神贯注。没有歧义——"
        "这是最宣言式的构图。适度使用，每次居中都应该感觉是应得的。适合角色顿悟时刻。"
    ),
    "comp_symmetry": (
        "强加秩序、控制，有时是压迫性的完美。对称构图感觉被设计过的、刻意的，"
        "根据语境可以是美丽的或令人不安的。在恐怖或惊悚类型中，完美对称暗示表面之下有问题。"
    ),
    "comp_leading_lines": (
        "引导观众视线沿预定路径走向主体或消失点。创造深度、叙事方向感和旅程感。"
        "最强的引导线是环境性的——道路、栏杆、河流——感觉是被发现而非强加的。"
    ),
    "comp_frame_within_frame": (
        "创造偷窥感——观众感觉自己从隐藏位置观看。通过前景层次增加深度，"
        "通常带有主题重量：囚禁、观察或情感分离。每一层框架都是与真相的一层隔离。"
    ),
    "comp_diagonal": (
        "注入能量、不稳定和前进动力。对角线构图感觉活跃且未解决——"
        "视线不断沿倾斜轴线移动，永不静止。比引导线更强烈、更具攻击性。"
    ),
    "comp_triangular": (
        "通过最稳定的几何形状创造视觉稳定性。三角形构图锚定画面并建立层次结构——"
        "顶点吸引视线而底部提供基础。适合群体动态和权力层次。"
    ),
    "comp_circular": (
        "封闭和包容。圆形构图感觉完整、自给自足，有时令人幽闭恐惧。"
        "视线在画面内循环而非退出——适合关于循环、执念或封闭的场景。"
    ),
    "comp_negative_space": (
        "将主体放在画面的一小部分，其余留空。这种视觉沉默通过缺席放大情感——"
        "孤独、敬畏、沉思或渺小。空虚成为主动的故事元素，不只是背景。"
    ),
    "comp_rule_of_space": (
        "在主体面对或移动的方向提供呼吸空间。没有视线空间，画面感觉紧张、焦虑或幽闭。"
        "留有适当的视线空间，观众潜意识中感知主体与画外空间的关系。"
    ),
    "comp_dynamic_symmetry": (
        "比简单对称更复杂。使用相交对角线网格创造既有序又生动的构图。"
        "网格提供多个锚点，创造引导视线沿编排路径移动的视觉节奏。"
    ),
    "comp_balanced": (
        "将视觉重量均匀分布在画面中，创造平衡和宁静。不像对称那样镜像，"
        "平衡通过配重实现：一侧的大暗色物体被另一侧的小亮色物体平衡。感觉自然、从容、稳定。"
    ),
    "comp_asymmetrical": (
        "创造不安、紧张和视觉不稳定。画面重量倾斜到一侧，让观众身体上感到不适。"
        "不对称构图是武器而非工具。适度使用，力量来自于与前面平衡构图的对比。"
    ),
}


# ============================================================================
# Load entries and models
# ============================================================================

def load_entries() -> List[Dict[str, Any]]:
    from libraries.composition.query import load_entries as _load
    return _load()


def build_embeddings(entries, texts_fn, model_name="BAAI/bge-small-zh-v1.5"):
    """Build normalized embedding index from entry texts."""
    from fastembed import TextEmbedding
    model = TextEmbedding(model_name=model_name)
    entry_ids = [e["id"] for e in entries]
    raw_texts = [texts_fn(e) for e in entries]
    emb_list = list(model.embed(raw_texts))
    emb = np.array(emb_list, dtype=np.float32)
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    emb = emb / norms
    return emb, entry_ids, model


def embed_query(model, query: str) -> np.ndarray:
    q = np.array(list(model.embed([query])), dtype=np.float32)
    return q / np.linalg.norm(q, axis=1, keepdims=True)


def retrieve_embedding(query, embeddings, entry_ids, model, entries, top_k=5):
    q_emb = embed_query(model, query)
    scores = (embeddings @ q_emb.T).flatten()
    top = np.argsort(scores)[::-1][:top_k]
    entry_map = {e["id"]: e for e in entries}
    results = []
    for idx in top:
        eid = entry_ids[idx]
        if eid in entry_map:
            results.append((entry_map[eid], round(float(scores[idx]), 4)))
    return results


def retrieve_keyword(emotion: str):
    from libraries.composition.query import query_compositions_detailed
    ctx = dict(QUERY_CONTEXT)
    ctx["emotion"] = emotion
    return query_compositions_detailed(ctx, min_score=0.02, max_results=5)


# ============================================================================
# Human relevance judgment
# ============================================================================

def judge_relevance(entry_name: str, query_desc: str) -> str:
    """Crude relevance judgment: does this entry's rule match the query's emotion?"""
    rule = entry_name.split("(")[0].strip().lower() if "(" in entry_name else entry_name.lower()

    # Expected mappings based on cinematographic knowledge
    # "隐隐不安" (faint unease): ASYMMETRICAL, DIAGONAL, NEGATIVE_SPACE, FRAME_WITHIN_FRAME
    # "细密的裂痕" (fine cracks): ASYMMETRICAL, DIAGONAL, NEGATIVE_SPACE
    # "挥之不去的异样感" (lingering wrongness): ASYMMETRICAL, FRAME_WITHIN_FRAME, DIAGONAL
    # "冰冷的仪式感" (cold ritual): SYMMETRY, CENTER_COMPOSITION, CIRCULAR
    # "不安的初现" (first unease): ASYMMETRICAL, CENTER_COMPOSITION, DIAGONAL
    # "压抑的日常" (oppressive everyday): SYMMETRY, BALANCED, FRAME_WITHIN_FRAME
    # "无声的压迫" (silent oppression): NEGATIVE_SPACE, SYMMETRY, FRAME_WITHIN_FRAME
    # "逐渐逼近的恐惧" (mounting dread): DIAGONAL, ASYMMETRICAL, LEADING_LINES
    # "表面平静下的暗流" (undercurrent): ASYMMETRICAL, BALANCED, DIAGONAL

    relevant_map = {
        "隐隐不安": {"asymmetrical", "diagonal", "negative space", "frame within frame"},
        "细密的裂痕": {"asymmetrical", "diagonal", "negative space"},
        "挥之不去的异样感": {"asymmetrical", "frame within frame", "diagonal"},
        "冰冷的仪式感": {"symmetry", "center composition", "circular"},
        "不安的初现": {"asymmetrical", "center composition", "diagonal"},
        "压抑的日常": {"symmetry", "balanced", "frame within frame"},
        "无声的压迫": {"negative space", "symmetry", "frame within frame"},
        "逐渐逼近的恐惧": {"diagonal", "asymmetrical", "leading lines"},
        "表面平静下的暗流": {"asymmetrical", "balanced", "diagonal"},
    }

    # Match query_desc (first token is the query text)
    query_text = query_desc.split(":")[0].strip()
    expected = relevant_map.get(query_text, set())

    for keyword in expected:
        if keyword in rule:
            return "relevant"
    return "marginal"


# ============================================================================
# Main experiment
# ============================================================================

def main():
    print("=" * 72)
    print("Expanded Experiment: Keyword vs Embedding vs Same-Lang Embedding")
    print("=" * 72)
    print()

    # Load
    print("[1/5] Loading entries ...")
    entries = load_entries()
    print("      %d entries" % len(entries))

    # Keyword
    print("[2/5] Running keyword retrieval on %d queries ..." % len(QUERIES))
    kw_results = {}
    for query_text, query_desc in QUERIES:
        kw_results[query_text] = retrieve_keyword(query_text)

    # Embedding (cross-lingual)
    print("[3/5] Building cross-lingual embedding index (EN entries) ...")
    en_texts_fn = lambda e: (e.get("effect", "") + " " + e.get("notes", ""))
    emb_en, eids_en, model = build_embeddings(entries, en_texts_fn)

    emb_en_results = {}
    for query_text, query_desc in QUERIES:
        emb_en_results[query_text] = retrieve_embedding(
            query_text, emb_en, eids_en, model, entries,
        )

    # Embedding (same-language: CN entries)
    print("[4/5] Building same-language embedding index (CN entries) ...")
    cn_texts_fn = lambda e: CN_TRANSLATIONS.get(e["id"], e.get("effect", ""))
    emb_cn, eids_cn, _ = build_embeddings(entries, cn_texts_fn)

    emb_cn_results = {}
    for query_text, query_desc in QUERIES:
        emb_cn_results[query_text] = retrieve_embedding(
            query_text, emb_cn, eids_cn, model, entries,
        )

    # Report
    print("[5/5] Generating report ...")
    lines = []
    lines.append("# Expanded Comparison: Keyword vs Embedding vs Same-Lang Embedding")
    lines.append("")
    lines.append("**Goal:** Validate that the 'no embedding' conclusion is not overfit to a single query.")
    lines.append("")
    lines.append("**Model:** BAAI/bge-small-zh-v1.5 (384-dim multilingual)")
    lines.append("")

    # Summary table
    lines.append("## Summary Table")
    lines.append("")
    lines.append("| # | Query | Description | KW top-1 | KW rel | EMB-EN top-1 | EMB-EN rel | EMB-CN top-1 | EMB-CN rel |")
    lines.append("|---|-------|-------------|----------|--------|--------------|-----------|--------------|-----------|")

    kw_good = 0
    emb_en_good = 0
    emb_cn_good = 0

    for i, (query_text, query_desc) in enumerate(QUERIES, 1):
        kw_top1 = kw_results[query_text][0].entry["name"] if kw_results[query_text] else "(none)"
        emb_en_top1 = emb_en_results[query_text][0][0]["name"] if emb_en_results[query_text] else "(none)"
        emb_cn_top1 = emb_cn_results[query_text][0][0]["name"] if emb_cn_results[query_text] else "(none)"

        kw_rel = judge_relevance(kw_top1, query_text)
        emb_en_rel = judge_relevance(emb_en_top1, query_text)
        emb_cn_rel = judge_relevance(emb_cn_top1, query_text)

        if kw_rel == "relevant": kw_good += 1
        if emb_en_rel == "relevant": emb_en_good += 1
        if emb_cn_rel == "relevant": emb_cn_good += 1

        lines.append(
            "| %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                i, query_text, query_desc,
                kw_top1, kw_rel,
                emb_en_top1, emb_en_rel,
                emb_cn_top1, emb_cn_rel,
            )
        )

    lines.append("")
    lines.append("**Accuracy (top-1 relevant / 9):**")
    lines.append("- Keyword: %d/9 (%.0f%%)" % (kw_good, kw_good/9*100))
    lines.append("- Embedding cross-lingual: %d/9 (%.0f%%)" % (emb_en_good, emb_en_good/9*100))
    lines.append("- Embedding same-lang: %d/9 (%.0f%%)" % (emb_cn_good, emb_cn_good/9*100))
    lines.append("")

    # Detailed per-query tables
    lines.append("## Per-Query Top-3 Details")
    lines.append("")

    for query_text, query_desc in QUERIES:
        lines.append("### %s  (%s)" % (query_text, query_desc))
        lines.append("")

        lines.append("| Rank | Method | Entry | Score | Relevant? |")
        lines.append("|------|--------|-------|-------|-----------|")

        for rank, (method, results) in enumerate([
            ("Keyword", kw_results[query_text]),
            ("EMB-EN", emb_en_results[query_text]),
            ("EMB-CN", emb_cn_results[query_text]),
        ]):
            for j, r in enumerate(results[:3]):
                if method == "Keyword":
                    name = r.entry["name"]
                    score = r.score
                else:
                    name = r[0]["name"]
                    score = r[1]
                rel = judge_relevance(name, query_text)
                lines.append(
                    "| %d | %s | %s | %.4f | %s |" % (
                        j + 1, method, name, score, rel,
                    )
                )
        lines.append("")

    # Analysis
    lines.append("## Analysis")
    lines.append("")

    lines.append("### 1. Keyword post-fix stability")
    lines.append("")
    lines.append("Keyword retrieval with jieba-segmented lookup achieves %d/9 top-1 relevant." % kw_good)
    if kw_good >= 7:
        lines.append("This is a strong result — the fix generalizes well beyond the original '隐隐不安' query.")
    elif kw_good >= 5:
        lines.append("This is acceptable but shows gaps for metaphorical/compound expressions.")
    else:
        lines.append("This is poor — the fix does not generalize. More vocabulary work needed.")
    lines.append("")

    lines.append("### 2. Cross-lingual embedding quality")
    lines.append("")
    lines.append("Cross-lingual embedding achieves %d/9 top-1 relevant." % emb_en_good)
    if emb_en_good >= emb_cn_good - 1:
        lines.append("Cross-lingual performance is comparable to same-language — the 'cross-lingual dilution'")
        lines.append("hypothesis is NOT confirmed. The bottleneck is elsewhere (short texts, domain mismatch).")
    else:
        lines.append("Cross-lingual performs significantly worse than same-language — confirming that")
        lines.append("the CN->EN mapping is a significant quality bottleneck for embedding retrieval.")
    lines.append("")

    lines.append("### 3. Same-language embedding quality")
    lines.append("")
    lines.append("Same-language embedding achieves %d/9 top-1 relevant." % emb_cn_good)
    if emb_cn_good >= 7:
        lines.append("With the cross-lingual barrier removed, embedding quality is strong. If the library")
        lines.append("were to add Chinese versions of entry texts, embedding would become competitive.")
    elif emb_cn_good >= 5:
        lines.append("Same-language embedding is acceptable but not dominant. The short text length")
        lines.append("and domain mismatch (emotion->cinematography) remain bottlenecks.")
    else:
        lines.append("Even same-language embedding performs poorly. The root cause is likely the")
        lines.append("entry text content (cinematography-focused, not emotion-focused).")
    lines.append("")

    lines.append("### 4. Final recommendation")
    lines.append("")

    if kw_good >= 7 and emb_cn_good <= kw_good + 1:
        lines.append("**The 'no embedding' conclusion holds across %d queries.**" % len(QUERIES))
        lines.append("Keyword retrieval post-fix is stable. Embedding does not clearly outperform it")
        lines.append("even with the cross-lingual barrier removed. The bottleneck is the library content")
        lines.append("(short cinematography descriptions), not the retrieval method.")
        lines.append("")
        lines.append("Add to architecture docs: 'Embedding-based retrieval was evaluated (2026-07),")
        lines.append("and keyword matching with jieba-segmented map lookup was found sufficient.")
        lines.append("Embedding should be re-evaluated if: (a) the library grows to 50+ entries,")
        lines.append("(b) entries are rewritten with emotion-first Chinese descriptions, or")
        lines.append("(c) a dedicated cinematography-domain embedding model becomes available.'")
    elif emb_cn_good >= kw_good + 2:
        lines.append("**The 'no embedding' conclusion needs revision.** Same-language embedding")
        lines.append("outperforms keyword by a clear margin. If the library were translated to Chinese,")
        lines.append("embedding retrieval would be the better choice.")
        lines.append("")
        lines.append("Recommendation: add a conditional to the architecture docs: 'Embedding is not")
        lines.append("recommended for v0, but should be adopted if and when library entries are")
        lines.append("translated to Chinese with emotion-rich descriptions.'")
    else:
        lines.append("**Both methods are comparable — neither dominates.** The library content")
        lines.append("quality is the bottleneck. Before investing in retrieval method changes,")
        lines.append("improve entry texts: longer descriptions, emotion-first framing,")
        lines.append("and more diverse vocabulary (synonyms for each emotion concept).")

    out_path = ROOT / "experiments" / "expanded_comparison_report.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print("      Report saved to: %s" % out_path)

    # Quick summary
    print()
    print("-" * 72)
    print("Quick Summary")
    print("-" * 72)
    print("Keyword top-1 relevant:     %d/9" % kw_good)
    print("Embedding EN top-1 relevant: %d/9" % emb_en_good)
    print("Embedding CN top-1 relevant: %d/9" % emb_cn_good)


if __name__ == "__main__":
    main()
