# Embedding vs Keyword Retrieval — Controlled Experiment

**Query:** `隐隐不安` (raw Chinese from `the_hanging.md` emotional arc, meaning "faint, lingering unease")

**Query context:**
```
  emotion:     隐隐不安
  scene_type:  psychological
  framing:     CU
  lens:        85mm
```

**Model:** `BAAI/bge-small-zh-v1.5` (384-dim multilingual, cross-lingual CN→EN)

---

## Method A: Keyword Retrieval

### How the query was processed

1. `_resolve_emotion_keywords("隐隐不安")` — not found in `_EMOTION_MAP` (only `不安` is mapped, not `隐隐不安`)
2. Falls through to `_tokenize("隐隐不安")` — jieba segments to `["隐隐", "不安"]`
3. These Chinese tokens are matched against English entry emotion keywords like `["unease", "anxiety", "tension", ...]`
4. No match — `"隐隐"` and `"不安"` are Chinese, entry keywords are English
5. **semantic_score = 0.000 for all 14 entries**

### How the scores were actually produced

Every score above baseline is driven **entirely by shot-param matching**:
- framing=CU matches entries with `framings: [CU, ...]`
- lens=85mm matches entries with `lenses: [85mm, ...]`
- W_SEMANTIC × 0.000 + W_SHOT × shot_param_score = actual score

| Rank | Entry | Score | Semantic | Shot-param | Why? |
|------|-------|-------|----------|------------|------|
| 1 | ASYMMETRICAL | 0.650 | 0.000 | 0.500 | CU + 85mm (bonus: also matched via scene_type) |
| 2 | RULE_OF_SPACE | 0.550 | 0.000 | 0.500 | CU + 85mm |
| 3 | CENTER_COMPOSITION | 0.500 | 0.000 | 0.500 | CU + 85mm |
| 4 | GOLDEN_RATIO | 0.250 | 0.000 | 0.250 | 85mm only |
| 5 | FRAME_WITHIN_FRAME | 0.250 | 0.000 | 0.250 | 85mm only |
| 6 | DIAGONAL | 0.100 | 0.000 | 0.000 | scene_type match only |
| 7 | SYMMETRY | 0.050 | 0.000 | 0.000 | scene_type match only |

**Verdict: The keyword system is BLIND to the emotional content of `隐隐不安`.**
The ranking is a coincidental byproduct of shot-param compatibility, not emotional relevance.
If we stripped the shot-param context (querying with emotion only), keyword would return **zero results**.

---

## Method B: Embedding Retrieval

### How the query was processed

1. `隐隐不安` encoded via `BAAI/bge-small-zh-v1.5` → 384-dim vector
2. Cosine similarity against 14 entry vectors (built from `effect + notes` fields)
3. Cross-lingual: Chinese query → English entry texts

| Rank | Entry | Cosine | Assessment |
|------|-------|--------|------------|
| 1 | CIRCULAR | 0.478 | Tangential — "claustrophobic, enclosure, obsession" shares anxiety valence with "unease" |
| 2 | FRAME_WITHIN_FRAME | 0.478 | Relevant — "voyeurism, observation, separation" fits the detective's detached gaze |
| 3 | SYMMETRY | 0.471 | Marginal — "oppressive perfection, unease through order" is a stretch |
| 4 | ASYMMETRICAL | 0.461 | **Most relevant** — "unease, tension, instability" is exactly the emotion — but ranked #4 |
| 5 | RULE_OF_SPACE | 0.457 | Marginal — "anxiety through tight framing" is tangentially related |
| 6 | NEGATIVE_SPACE | 0.449 | Relevant — "isolation, emptiness, despair" — should rank higher |
| 7 | DIAGONAL | 0.443 | Relevant — "instability, tension, danger" |

**Verdict: Embedding ENGAGES with the semantic content**, but the ranking quality is mediocre.
- ASYMMETRICAL (the most relevant) is at #4, not #1
- CIRCULAR at #1 is a head-scratcher — "隐隐不安" is not about circularity
- All cosine scores cluster tightly (0.478–0.426, range = 0.052) — poor discrimination

---

## Head-to-Head: Which method is better for this query?

| Criterion | Keyword | Embedding | Winner |
|-----------|---------|-----------|--------|
| Understands "隐隐不安" semantically? | No (blind, semantic=0) | Yes (cross-lingual) | Embedding |
| Top-3 contains ASYMMETRICAL? | Yes (#1) — but coincidental | Yes (#4) — but buried | Neither convincingly |
| Top-3 free of irrelevant entries? | No (RULE_OF_SPACE, CENTER_* are irrelevant to 隐隐不安) | No (CIRCULAR is irrelevant) | Neither |
| Produces results without shot-param crutch? | No (0 results without shot context) | Yes (10 results) | Embedding |
| Score discrimination? | Good (0.65→0.05 spread) | Poor (0.48→0.43, tight cluster) | Keyword |
| Debuggable? | Yes (exact token matches visible) | No (opaque cosine) | Keyword |

**Neither method is clearly superior for this specific query.** Both have significant weaknesses:
- Keyword is structurally incapable of handling out-of-vocabulary Chinese phrases
- Embedding can represent them but produces noisy rankings with poor score discrimination

---

## Root cause analysis

### Why embedding underperforms here

The embedding model compares a 4-character Chinese query against ~100-word English composition descriptions. The semantic signal is diluted:
- "隐隐不安" is a highly specific, culturally nuanced emotion phrase
- The entry texts describe cinematographic techniques, not emotions directly
- The model must do cross-lingual mapping (CN→EN) AND domain translation (emotion→cinematography) simultaneously
- Result: all entries look similarly "anxiety-adjacent" to the model

### Why keyword fails

`_EMOTION_MAP` has `不安` → `["unease", "anxiety", "tension", ...]` but not `隐隐不安`.
This is a **prefix/modifier problem**: `隐隐` (faint, lingering) modifies `不安` (unease) but
the mapping system only does exact-key lookups, not partial-key decomposition.

A simple fix: in `_resolve_emotion_keywords`, try jieba-segmenting the query and
looking up each segment in `_EMOTION_MAP`.  This would split `隐隐不安` into
`["隐隐", "不安"]`, find `不安` in the map, and resolve to the English keywords.
This is a 5-line change that would close this specific gap.

---

## Decision Recommendation

### Do NOT introduce embedding dependencies at this stage.

**Reasoning:**

1. **The embedding model's ranking quality does not justify the dependency cost.**
   With cosine scores tightly clustered (0.478–0.426), the model barely discriminates
   between relevant and irrelevant entries.  CIRCULAR at #1 is not an improvement
   over keyword's coincidental ASYMMETRICAL at #1.

2. **The keyword system's gap is fixable with a targeted vocabulary change.**
   Jieba-segmenting the query before map lookup would resolve `隐隐不安` → `不安` →
   English keywords.  This is a 5-line fix to `_resolve_emotion_keywords`, not a
   system architecture change.

3. **Hybrid retrieval adds complexity without clear benefit.**  With the current
   embedding model, a hybrid system would be "keyword for precision, embedding for
   recall" — but embedding's recall is noisy, and keyword's precision is already
   compromised for OOV queries.  Hybrid would give us the worst of both: keyword
   misses + embedding noise.

### Path forward

1. **Immediate: Fix `_resolve_emotion_keywords` to jieba-segment before map lookup.**
   This closes the `隐隐不安` and similar `修饰词+基础情绪词` gap.

2. **Short-term: Expand `_EMOTION_MAP` with common modifiers.**
   Add entries for: 隐隐+X, 淡淡+X, 微微+X, 逐渐+X where X is a base emotion.
   Or, more sustainably, add a modifier-stripping preprocessor.

3. **Medium-term: Revisit embedding when:**
   - The composition library has 50+ entries (better score discrimination through volume)
   - Entry texts are enriched with emotion-first descriptions (currently cinematography-first)
   - A Chinese-native embedding model is evaluated (the BGE model is multilingual but EN-optimized)
   - A dedicated cross-encoder re-ranker can provide sharper discrimination on top of embedding recall

4. **Long-term: If embedding is adopted, use it as a recall layer only.**
   - Embedding: recall top-10 candidates from the full library
   - Keyword: re-rank the top-10 with exact emotion/scene matching
   - This combines embedding's OOV tolerance with keyword's transparency

---

## Experimental Data

### Keyword retrieval trace

```
Query tokens (jieba): ["隐隐", "不安"]
Entry emotion tokens: [all English, e.g. "unease", "anxiety", "tension", ...]
Semantic matches: 0 (Chinese tokens ≠ English tokens)
Shot-param provided: framing=CU, lens=85mm → 2 params
Shot-param matches: ASYMMETRICAL (2/2), RULE_OF_SPACE (2/2), CENTER_COMPOSITION (2/2), etc.
```

### Embedding model info

```
Model: BAAI/bge-small-zh-v1.5
Dimension: 512 (output) / 384 (internal)
Language: Multilingual (CN/EN, trained on C-MTEB)
Entry text length: ~100 words avg (effect + notes)
Score range: 0.478 (CIRCULAR) to 0.426 (RULE_OF_THIRDS)
Score spread: 0.052 (poor discrimination)
```
