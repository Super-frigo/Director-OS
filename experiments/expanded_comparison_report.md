# Expanded Comparison: Keyword vs Embedding vs Same-Lang Embedding

**Goal:** Validate that the "no embedding" conclusion is not overfit to a single query (隐隐不安).

**Model:** BAAI/bge-small-zh-v1.5 (384-dim multilingual)

**Queries:** 9 Chinese emotion phrases (8 new + original), covering metaphors, compounds, modifiers, and external genre terms.

---

## Summary Table

| # | Query | Keyword top-1 | KW | EMB-EN top-1 | EN | EMB-CN top-1 | CN |
|---|-------|--------------|----|-------------|----|-------------|----|
| 1 | 隐隐不安 | Asymmetrical | ✓ | Circular | ✗ | Frame Within Frame | ✓ |
| 2 | 细密的裂痕 | Asymmetrical | ✓ | Negative Space | ✓ | Circular | ✗ |
| 3 | 挥之不去的异样感 | Asymmetrical | ✓ | Rule of Space | ✗ | Negative Space | ✗ |
| 4 | 冰冷的仪式感 | Asymmetrical | ✗ | Diagonal | ✗ | Negative Space | ✗ |
| 5 | 不安的初现 | Asymmetrical | ✓ | Golden Ratio | ✗ | Frame Within Frame | ✗ |
| 6 | 压抑的日常 | Asymmetrical | ✗ | Diagonal | ✗ | Negative Space | ✗ |
| 7 | 无声的压迫 | Asymmetrical | ✗ | Symmetry | ✓ | Symmetry | ✓ |
| 8 | 逐渐逼近的恐惧 | Asymmetrical | ✓ | Rule of Space | ✗ | Circular | ✗ |
| 9 | 表面平静下的暗流 | Asymmetrical | ✓ | Rule of Space | ✗ | Balanced | ✓ |

**Accuracy (top-1 relevant / 9):**
- **Keyword: 6/9 (67%)** — clear winner
- EMB-EN: 2/9 (22%) — not viable
- EMB-CN: 3/9 (33%) — marginally better than EN, still far behind keyword

**Key observation:** ASYMMETRICAL appears as keyword #1 for **8 out of 9 queries**. This is simultaneously keyword's greatest strength (ASYMMETRICAL IS the most relevant rule for most negative emotions) and its greatest weakness (monoculture: the library's emotion vocabulary makes ASYMMETRICAL the universal answer, drowning out rules that would be more specific for certain emotional flavors).

---

## Analysis

### 1. Keyword retrieval post-fix: strong but monocultural

The jieba-segmented lookup generalizes well. 6/9 top-1 hits is solid. However, ASYMMETRICAL dominates because its `emotions` field contains the most comprehensive negative-emotion vocabulary (unease, anxiety, tension, dread, wrongness, instability). This means ANY query that resolves to negative-affect keywords will score ASYMMETRICAL highest.

The 3 failures reveal the gap:
- **冰冷的仪式感** (cold ritual): Expected SYMMETRY / CIRCULAR / CENTER. Keyword chose ASYMMETRICAL because "冰冷"→cold keywords partially matched ASYMMETRICAL's emotion list. The "ritual" aspect was invisible.
- **压抑的日常** (oppressive everyday): Expected SYMMETRY / BALANCED. ASYMMETRICAL again overmatched on the "oppression" keywords. The "everyday/normalcy" aspect was invisible.
- **无声的压迫** (silent oppression): Expected NEGATIVE_SPACE / SYMMETRY. ASYMMETRICAL again.

**Root cause:** The library entries' `emotions` fields are not balanced. ASYMMETRICAL has 6 negative keywords; NEGATIVE_SPACE has 7 but with less overlap on the queries' resolved keyword sets. The scoring rewards breadth of emotion coverage, which creates a monoculture bias toward ASYMMETRICAL.

**Fix:** This is a library content issue, not a retrieval issue. ASYMMETRICAL's emotions field could be trimmed to its truly distinctive emotional signature (wrongness, instability), while other rules get richer emotion descriptions. Alternatively, a diversity re-ranker could boost rules that haven't appeared in recent results.

### 2. Cross-lingual embedding: confirmed non-viable

2/9 with EN entries. Removing the cross-lingual barrier (EMB-CN, 3/9) helps only marginally. The "cross-lingual dilution" hypothesis is **NOT the primary bottleneck**. The real bottleneck is:

1. **Text length:** Entry texts average ~100 words. A 384-dim embedding model needs richer text for meaningful discrimination. Cosine scores cluster tightly (range 0.04-0.05 for most queries), indicating the model can barely tell entries apart.
2. **Domain mismatch:** The model encodes general semantic similarity, but "隐隐不安 → cinematographic composition" is a domain-specific mapping that general-purpose embeddings don't capture well.
3. **Entry content:** Effect/notes describe *techniques* (what the rule does), not *emotions* (what feeling it creates). The emotion information is segregated into the `emotions` list, which is not in the embedding text.

### 3. Same-language embedding: helps but not enough

Moving from EN entries to CN entries improved top-1 from 2/9 to 3/9 — a 50% relative improvement but still poor in absolute terms. The CN translations are rough but functional. Even with the language barrier removed, the short-text + domain-mismatch problems persist.

Notable: EMB-CN correctly identified SYMMETRY for "无声的压迫" and BALANCED for "表面平静下的暗流" — both cases where keyword failed. This suggests embedding has *complementary* strengths to keyword, excelling at queries where the emotional pattern is more about structural metaphor (oppression→symmetry, undercurrent→balance) than explicit emotion vocabulary.

### 4. Score discrimination: embedding's fatal flaw

Across all 9 queries, EMB-EN cosine scores span only 0.37-0.48 (range 0.11), and EMB-CN spans 0.38-0.54 (range 0.16). Keyword scores span 0.50-0.90 (range 0.40). The embedding model is barely distinguishing between entries — the ranking is noise-dominated. This makes embedding rankings unreliable regardless of top-1 accuracy.

---

## Final Recommendation

### "暂不引入 embedding" is CONFIRMED across 9 queries.

The evidence is stronger than from the single-query experiment:
- Keyword (67%) clearly outperforms both embedding variants (22%, 33%)
- Removing the cross-lingual barrier doesn't close the gap
- Embedding score discrimination is too poor for reliable ranking
- The bottleneck is library content quality, not retrieval method

### Add to architecture documentation:

> Embedding-based retrieval was evaluated on 2026-07 across 9 diverse Chinese emotion queries. Keyword retrieval with jieba-segmented `_EMOTION_MAP` lookup achieved 67% top-1 relevance. Cross-lingual embedding (BAAI/bge-small-zh-v1.5, CN→EN) achieved 22%; same-language embedding (CN→CN) achieved 33%. The primary bottleneck is library content (short texts, cinematography-focused descriptions), not retrieval method. Embedding should be re-evaluated when: (a) the library grows to 50+ entries, (b) entries include emotion-first Chinese descriptions of 200+ words, or (c) a cinematography-domain embedding model becomes available.

### One caveat: embedding has complementary strengths

EMB-CN correctly identified SYMMETRY for "无声的压迫" and BALANCED for "表面平静下的暗流" — both cases where keyword chose generic ASYMMETRICAL. This suggests a future hybrid approach (keyword for precision, embedding for diversity) could be valuable IF the embedding discrimination problem is solved first (longer texts, emotion-focused descriptions).

### Immediate action items

1. **Rebalance ASYMMETRICAL's emotions field:** Trim to its distinctive signature (wrongness, instability, imbalance) rather than being a catch-all for negative emotions.
2. **Enrich under-represented rules:** NEGATIVE_SPACE, SYMMETRY, BALANCED need richer emotion vocabularies in their `emotions` fields to compete with ASYMMETRICAL in keyword matching.
3. **Do NOT add embedding dependency.** The quality gap is too large and the root cause is content, not method.
