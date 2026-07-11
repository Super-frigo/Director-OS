# Knowledge Resolution Specification

Version: 1.0
Status: Draft
Based on: [ADR-008: Knowledge Resolution Architecture](../adr/ADR-008.md)

---

## 1. Overview

Knowledge Resolution is the architectural component responsible for answering the question:

> "When the Engine needs filmmaking knowledge, how does the system provide the best available answer in a deterministic, source-traceable way?"

It replaces the Library-as-storage model (ADR-004) with a multi-provider resolution pipeline.

### 1.1 Core Principle

```text
Director OS does not own filmmaking knowledge.
Director OS defines how knowledge is requested and resolved.
```

### 1.2 Architecture Position

```text
                         Project
                           │
                           ▼
                         Engine
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
         Story Engine  Visual Engine  Shot Engine
              │            │            │
              └────────────┼────────────┘
                           │
                           ▼
                  Knowledge Request
                           │
                           ▼
              ┌────────────────────────┐
              │   Knowledge Resolution │
              │                        │
              │  ┌──────────────────┐  │
              │  │  Local Rules     │  │
              │  │  Provider        │  │
              │  └────────┬─────────┘  │
              │           │            │
              │  ┌────────▼─────────┐  │
              │  │  Cached LLM      │  │
              │  │  Provider        │  │
              │  └────────┬─────────┘  │
              │           │            │
              │  ┌────────▼─────────┐  │
              │  │  Future          │  │
              │  │  Providers       │  │
              │  └────────┬─────────┘  │
              │           │            │
              │  ┌────────▼─────────┐  │
              │  │  Merge & Rank    │  │
              │  └────────┬─────────┘  │
              │           │            │
              └───────────┼────────────┘
                          │
                          ▼
                  Resolved Knowledge
                          │
                          ▼
                   Production Intent
                          │
                          ▼
                       Compiler
```

---

## 2. Lifecycle

Knowledge Resolution follows a strict 6-stage lifecycle. Each stage has defined inputs, outputs, and validation rules.

```
Stage 1: Requirement Analysis
    ↓
Stage 2: Knowledge Request
    ↓
Stage 3: Provider Resolution
    ↓
Stage 4: Structured Knowledge Response
    ↓
Stage 5: Project Enrichment
    ↓
Stage 6: Compiler
```

### Stage 1: Requirement Analysis

**Owner:** Engine

**Purpose:** Engine analyzes the current Project context and determines what knowledge is missing.

```yaml
Input:
  project_context:
    scene: <current scene data>
    shot: <current shot data>
    character: <current character state>
    emotion_target: <desired emotional effect>
    visual_language: <project visual style>

Process:
  1. Engine evaluates current Production Intent completeness
  2. Engine identifies knowledge gaps:
     - Missing composition rules for current emotion
     - Unknown lighting patterns for scene mood
     - Unresolved camera language for character state
  3. Engine forms requirement list

Output:
  requirements:
    - domain: composition
      context: { emotion: "loneliness", scene_type: "interior" }
    - domain: lighting
      context: { mood: "tension", location: "alleyway" }
    - domain: camera
      context: { character_state: "vulnerable", shot_size: "CU" }
```

**Constraints:**
- Engine never guesses knowledge — it requests what it doesn't have
- Requirements must be scoped to the current creative decision
- Each requirement maps to exactly one knowledge domain

### Stage 2: Knowledge Request

**Owner:** Knowledge Resolver (receives)

**Purpose:** Engine submits structured requests to the Resolution layer.

```yaml
Request Schema:
  KnowledgeRequest:
    request_id: string          # unique identifier
    timestamp: datetime
    requirements:
      - domain: string          # e.g., "composition", "lighting", "camera"
        query: string           # natural language query
        context: dict           # structured context
        constraints:            # optional
          max_results: int      # default 5
          min_confidence: float # default 0.0
          prefer_provider: str  # optional
    cache_policy:
      allow_llm: bool           # whether to allow live LLM fallback
      cache_ttl: int            # seconds, 0 = permanent

Example:
  KnowledgeRequest:
    request_id: "req-20260712-001"
    timestamp: "2026-07-12T10:00:00Z"
    requirements:
      - domain: "composition"
        query: "How to frame a lonely character in a confined space?"
        context:
          emotion: "loneliness"
          scene_type: "interior_small_room"
          character_count: 1
        constraints:
          max_results: 3
    cache_policy:
      allow_llm: true
      cache_ttl: 0
```

### Stage 3: Provider Resolution

**Owner:** Knowledge Resolver (executes)

**Purpose:** Route requests to available providers, collect responses, cache results.

```yaml
Resolution Pipeline:

  Step 1: Check Cache
    - Hash: SHA256(request_id + domain + query)
    - If cache hit → return cached entries immediately
    - If cache miss → proceed to providers

  Step 2: Query Providers (in priority order)
    ┌──────────────────────────────────┐
    │ Provider 1: Local Rules          │
    │ - Query: YAML file index         │
    │ - Latency: <1ms                  │
    │ - Deterministic: yes             │
    │ - Coverage: limited by entries   │
    └──────────────┬───────────────────┘
                   │
    ┌──────────────▼───────────────────┐
    │ Provider 2: Cached LLM           │
    │ - Query: LLM with domain prompt  │
    │ - Latency: <2s (if cached 0ms)   │
    │ - Deterministic: yes (via cache) │
    │ - Coverage: broad                │
    │ - Condition: cache_policy.allow_llm=true │
    └──────────────┬───────────────────┘
                   │
    ┌──────────────▼───────────────────┐
    │ Provider N: Future Providers     │
    │ - Reserved for extension         │
    └──────────────────────────────────┘

  Step 3: Collect Results
    - Each provider returns: List[KnowledgeEntry]
    - Entries annotated with provider metadata

  Step 4: Write Cache
    - New LLM results written to cache
    - Cache key: hash(request_id + domain + query)
    - Cache file: knowledge/providers/llm_cache/<hash>.yaml
```

**Provider Interface:**

```python
class KnowledgeProvider:
    """Interface that every knowledge provider must implement."""

    @property
    def name(self) -> str:
        """Unique provider identifier."""

    @property
    def is_deterministic(self) -> bool:
        """Whether this provider always returns the same result for the same input."""

    def resolve(self, request: KnowledgeRequest) -> list[KnowledgeEntry]:
        """Resolve a knowledge request and return matching entries."""

    def can_handle(self, domain: str) -> bool:
        """Whether this provider can handle the given domain."""
```

### Stage 4: Structured Knowledge Response

**Owner:** Knowledge Resolver (produces)

**Purpose:** Merge provider results, rank by relevance, resolve conflicts, produce final structured response.

```yaml
Merge & Rank Algorithm:

  Input:
    provider_results:
      local_rules: [entry_a, entry_b]
      cached_llm: [entry_c, entry_d, entry_e]

  Step 1: Deduplication
    - Compare entries by content similarity (>0.85 cosine → duplicate)
    - Prefer local_rules over cached_llm for identical content
    - Merge overlapping entries (union of fields)

  Step 2: Scoring
    Each entry receives a composite score:

    score = W_SEMANTIC * semantic_score
          + W_CONTEXT * context_match_score
          + W_PROVIDER * provider_confidence
          + W_FRESHNESS * freshness_score

    Default weights:
      W_SEMANTIC = 0.40   # how well content matches query
      W_CONTEXT = 0.30    # how well context fields align
      W_PROVIDER = 0.20   # provider trust level
      W_FRESHNESS = 0.10  # entry age / version

    Provider confidence defaults:
      local_rules: 0.95
      cached_llm: 0.80
      live_llm: 0.70

  Step 3: Ranking
    - Sort by composite score descending
    - Truncate to max_results
    - Filter by min_confidence

  Step 4: Conflict Resolution
    - If two entries contradict, prefer higher provider_confidence
    - If same provider_confidence, prefer local_rules
    - Flag unresolved conflicts as warnings

  Output:
    ResolvedKnowledge:
      request_id: "req-20260712-001"
      entries:
        - content: <KnowledgeEntry>
          score: 0.87
          sources:
            - provider: local_rules
              path: "knowledge/providers/local_rules/composition/comp_negative_space.yaml"
            - provider: cached_llm
              cache_key: "abc123"
              model: "gpt-5"
              timestamp: "2026-07-10T15:00:00Z"
          confidence: 0.87
      warnings: []
      stats:
        total_providers_queried: 2
        cache_hits: 0
        cache_misses: 1
        resolution_time_ms: 1200
```

**Response Schema:**

```yaml
KnowledgeEntry:
  entry_id: string
  domain: string
  content:
    description: string        # human-readable knowledge
    rules: list                # structured rules engine can apply
    examples: list             # reference examples
    constraints: dict          # when this knowledge applies
  metadata:
    provider: string
    source_path: string        # file path for local_rules, cache key for llm
    model: string              # only for LLM entries
    timestamp: datetime
    version: string
  confidence: float            # 0.0 - 1.0

ResolvedKnowledge:
  request_id: string
  entries: list[KnowledgeEntry]
  warnings: list[str]
  stats: dict
```

### Stage 5: Project Enrichment

**Owner:** Engine

**Purpose:** Engine consumes resolved knowledge and applies it to creative decisions, enriching the Production Intent.

```yaml
Process:
  1. Engine receives ResolvedKnowledge
  2. Engine maps knowledge entries to creative decisions:
     - Composition rules → shot framing choices
     - Lighting patterns → lighting setup specifications
     - Camera language → camera movement directives
  3. Engine produces enriched ProductionIntent

Example:
  ResolvedKnowledge:
    entries:
      - domain: composition
        content:
          rules:
            - "Use negative space >60% of frame for isolation"
            - "Position subject at rule-of-thirds intersection opposite gaze"

  Engine applies:
    ProductionIntent:
      shots:
        - shot_id: "S1"
          framing: "MS"
          composition:
            negative_space_ratio: 0.65
            subject_position: "left_third"
            gaze_direction: "right"
```

**Constraints:**
- Engine never stores knowledge back into Project
- Enrichment is per-shot, not global
- All enrichment decisions are recorded in ProductionIntent with source trace

### Stage 6: Compiler

**Owner:** Compiler

**Purpose:** Compiler receives enriched ProductionIntent (with resolved knowledge already baked in) and performs deterministic platform translation.

```yaml
Input to Compiler:
  - Project data (structured, version-controlled)
  - Production Intent (engine output, enriched with resolved knowledge)

Compiler does NOT:
  - Call any knowledge provider
  - Call any LLM
  - Make creative decisions
  - Request additional knowledge

Compiler only:
  - Translates structured intent to platform-specific prompt syntax
  - Applies platform capability constraints
  - Assembles final prompt string

Determinism guarantee:
  Same Project + Same ProductionIntent → Same Prompt (byte-identical)
```

---

## 3. Provider Specifications

### 3.1 Local Rules Provider

```yaml
Provider:
  name: "local_rules"
  is_deterministic: true

Data Source:
  - YAML files under knowledge/providers/local_rules/
  - Each file is one KnowledgeEntry
  - Files organized by domain subdirectories

Directory Structure:
  knowledge/providers/local_rules/
    ├── composition/
    │   ├── comp_negative_space.yaml
    │   ├── comp_rule_of_thirds.yaml
    │   └── ...
    ├── lighting/
    │   ├── light_low_key_noir.yaml
    │   └── ...
    ├── camera/
    │   ├── movement/
    │   │   ├── movement_dolly_in.yaml
    │   │   └── ...
    │   └── ...
    └── ...

Entry Format:
  # comp_negative_space.yaml
  entry_id: "comp_negative_space"
  domain: "composition"
  version: "1.0"
  content:
    description: >
      Negative space composition creates visual isolation by surrounding
      the subject with empty space, emphasizing loneliness or vulnerability.
    rules:
      - "Allocate 60-75% of frame to empty space"
      - "Position subject near frame edge, facing inward"
      - "Use shallow depth of field to separate subject from background"
    examples:
      - "Character standing alone in vast empty room"
      - "Single figure at end of long corridor"
    constraints:
      emotion: ["loneliness", "isolation", "vulnerability"]
      scene_types: ["interior", "exterior_wide"]
      character_count: { max: 1 }
    keywords: ["negative space", "empty", "alone", "void", "isolation"]

Resolution Strategy:
  - Keyword matching via jieba tokenization (ADR-007)
  - Exact match on domain + context fields
  - Rank by composite score (semantic + context match)
```

### 3.2 Cached LLM Provider

```yaml
Provider:
  name: "cached_llm"
  is_deterministic: true  # via caching

Mechanism:
  1. Compute cache key: SHA256(domain + query + model_version)
  2. Check cache directory for matching file
  3. If found → return cached entry (deterministic)
  4. If not found → call LLM → write cache → return entry

Cache Structure:
  knowledge/providers/llm_cache/
    ├── index.yaml           # cache key → file mapping
    ├── a1b2c3d4.yaml        # individual cache entries
    ├── e5f6g7h8.yaml
    └── ...

Cache Entry Format:
  # a1b2c3d4.yaml
  cache_key: "a1b2c3d4e5f6..."
  domain: "composition"
  query: "How to frame a lonely character in a confined space?"
  model: "gpt-5"
  model_version: "2026-07"
  timestamp: "2026-07-12T10:00:00Z"
  ttl: 0  # permanent
  entries:
    - entry_id: "llm_cache_comp_lonely_confined"
      domain: "composition"
      content:
        description: "..."
        rules: [...]
        examples: [...]
      confidence: 0.80
  warmup: false  # true if pre-filled by CI

LLM Prompt Template:
  System:
    "You are a cinematography knowledge provider for Director OS.
     Respond with structured YAML following the KnowledgeEntry schema.
     Be specific, actionable, and domain-focused.
     Do not include general advice — only concrete rules the Engine can apply."

  User:
    "Domain: {domain}
     Query: {query}
     Context: {context}

     Provide up to {max_results} knowledge entries in the following format:
     - entry_id: string
     - description: one paragraph
     - rules: list of concrete, actionable rules
     - examples: list of specific film references
     - constraints: when this knowledge applies (emotions, scene_types, etc.)
     - keywords: list of searchable terms"

Cache Warmup:
  - CI pipeline pre-fills cache for common domains and emotions
  - Warmup queries defined in knowledge/providers/llm_cache/warmup_queries.yaml
  - Prevents cold-start latency in production
  - Ensures baseline determinism from day one
```

---

## 4. Integration Contracts

### 4.1 Engine → Knowledge Resolution

```yaml
Engine responsibility:
  - Analyze project context
  - Identify knowledge gaps
  - Form KnowledgeRequest
  - Submit to Resolver
  - Consume ResolvedKnowledge
  - Apply to ProductionIntent

Engine does NOT:
  - Call providers directly
  - Manage caches
  - Know which provider produced which result
  - Call LLM directly
```

### 4.2 Knowledge Resolution → Compiler

```yaml
Resolution responsibility:
  - Receive KnowledgeRequest from Engine
  - Route to providers
  - Merge, rank, deduplicate
  - Return ResolvedKnowledge (deterministic)
  - All LLM calls happen here, NOT in Compiler

Compiler receives:
  - Project: structured, version-controlled data
  - ProductionIntent: engine output with resolved knowledge baked in

Compiler knows:
  - Nothing about providers
  - Nothing about LLMs
  - Nothing about caches
  - Only: structured input → platform-specific output
```

### 4.3 Determinism Boundary

```text
┌────────────────── Non-Deterministic Zone ──────────────────┐
│                                                             │
│  Engine forms request                                       │
│       │                                                     │
│       ▼                                                     │
│  Knowledge Resolution                                       │
│  ┌──────────────────────────────────────┐                   │
│  │  LLM call (only if cache miss)       │ ← non-deterministic
│  │  Cache write                         │                   │
│  └──────────────────────────────────────┘                   │
│       │                                                     │
│       ▼                                                     │
│  Resolved Knowledge (cached, deterministic)                 │
│                                                             │
├────────────────── Deterministic Zone ───────────────────────┤
│       │                                                     │
│       ▼                                                     │
│  Production Intent                                          │
│       │                                                     │
│       ▼                                                     │
│  Compiler (pure translation)                                │
│       │                                                     │
│       ▼                                                     │
│  Platform Prompt                                            │
└─────────────────────────────────────────────────────────────┘
```

The boundary is drawn at the cache. Everything after the cache is deterministic. The LLM call (when needed) is the only non-deterministic point, and its output is immediately cached to restore determinism for all future identical queries.

---

## 5. Cache Management

### 5.1 Cache Lifecycle

```yaml
Write:
  - On cache miss after LLM call
  - Atomic write (write to temp → rename)
  - Version-tagged: cache entry records model version

Read:
  - SHA256 hash of (domain + query + context_signature)
  - Positive hit if: hash matches AND model_version matches
  - Stale if: model_version changed → treated as miss

Invalidation:
  - Manual: delete cache file or entry from index
  - Version-based: model upgrade invalidates all entries for that model
  - Per-entry: set ttl > 0 for time-based expiry

Distribution:
  - Cache files stored in repository (version controlled)
  - Team members share identical cache via git
  - CI validates cache consistency
```

### 5.2 Cache Index

```yaml
# knowledge/providers/llm_cache/index.yaml
version: 1
entries:
  a1b2c3d4:
    domain: composition
    query_hash: "sha256:..."
    file: "a1b2c3d4.yaml"
    model: "gpt-5"
    created: "2026-07-12T10:00:00Z"
  e5f6g7h8:
    domain: lighting
    query_hash: "sha256:..."
    file: "e5f6g7h8.yaml"
    model: "gpt-5"
    created: "2026-07-12T10:05:00Z"
```

---

## 6. Error Handling

### 6.1 Provider Unavailable

```yaml
Scenario: LLM provider timeout or error
Fallback chain:
  1. Cached LLM (always checked first, no network required)
  2. Local Rules (always available, no external deps)
  3. Empty response with warning (system can still compile)

Engine handles:
  - Missing knowledge entries
  - Falls back to default creative rules
  - Compiler never receives error — only missing optional enrichment
```

### 6.2 Cache Corruption

```yaml
Scenario: Cache file is malformed
Resolution:
  1. Log warning
  2. Skip corrupted entry
  3. Treat as cache miss → re-query LLM → write fresh cache
  4. If LLM also unavailable, fall back to local rules
```

### 6.3 Conflicting Knowledge

```yaml
Scenario: Two providers return contradictory rules
Resolution:
  1. Flag as warning in ResolvedKnowledge
  2. Prefer local_rules (higher provider confidence)
  3. Include both entries with conflict annotation
  4. Engine decides which to apply (or requests human review)
```

---

## 7. Directory Structure

```text
knowledge/
├── providers/
│   ├── local_rules/            # migrated from libraries/
│   │   ├── composition/
│   │   ├── lighting/
│   │   ├── camera/
│   │   ├── color/
│   │   ├── storytelling/
│   │   ├── visual_style/
│   │   └── model_capabilities/
│   │
│   └── llm_cache/
│       ├── index.yaml          # cache key → file mapping
│       ├── warmup_queries.yaml # CI pre-fill queries
│       └── *.yaml              # individual cache entries
│
├── resolver.py                 # Resolution Pipeline (merge, rank, dedup)
├── providers.py                # Provider interface + base class
├── cache.py                    # Cache read/write/invalidation
└── schemas.py                  # KnowledgeRequest, KnowledgeEntry, ResolvedKnowledge
```

---

## 8. Summary

Knowledge Resolution is the mechanism by which Director OS bridges the gap between what local rules can cover and what filmmaking demands.

```text
Requirement Analysis  →  Engine identifies what it doesn't know
Knowledge Request     →  Engine asks Resolution for help
Provider Resolution   →  Resolution queries providers, caches responses
Structured Response   →  Resolution merges, ranks, resolves conflicts
Project Enrichment    →  Engine applies resolved knowledge to Production Intent
Compiler              →  Compiler translates enriched intent (deterministic, no LLM)
```

The Knowledge Resolver is the **only** system component allowed to call LLMs. It does so behind a cache boundary that guarantees determinism for all downstream consumers. The Compiler never sees unresolved knowledge, and the Engine never manages knowledge sources directly.
