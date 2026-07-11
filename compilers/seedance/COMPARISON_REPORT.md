# Seedance Compiler vs Reference Output — Comparison Report

**Source project:** `projects/the_hanging.md`
**Compiler output:** `compilers/seedance/output_the_hanging.txt` (auto-generated)
**Reference output:** `compilers/seedance_the_hanging.md` (human/LLM authored)

---

## Summary

The compiler produces a **structured, technical blueprint** — every field from the Project YAML is faithfully translated through deterministic lookup tables. The reference produces a **narrative-optimized prompt** — fields are synthesized into flowing prose with creative interpretation.

Both are valid outputs for different purposes. The compiler version is what you'd feed to a downstream tool or pipeline; the reference version is what a human might paste directly into a video generation UI.

**The compiler is NOT meant to replicate the reference output.** It's designed to be:
1. Deterministic (identical output every run)
2. Complete (no field dropped silently)
3. Auditable (every translation traceable to a specific rule in `rules.py`)

---

## Structural Differences

| Aspect | Compiler Output | Reference Output |
|--------|----------------|-----------------|
| **Format** | Markdown sections with bullet lists | Narrative prose with code blocks |
| **Global Settings** | Enumerated key-value pairs (Style, Setting, Color palette, etc.) | A single prose paragraph |
| **Character Descriptions** | Full technical description per character (appearance, wardrobe, accessories, personality) | Characters described inline within shots |
| **Shot Breakdown** | Per-field decomposition (Camera, Composition, Lighting, Color, Audio, Emotion, Transitions) | Narrative paragraph per shot blending all fields |
| **Audio Design** | Separate section with Music, Ambience, Dialogue, Silence, Rhythm | One line at end: "Sound design: ambient wind, one breath, one mechanical thud, one cello note" |
| **Tone & Theme** | Separate enumerated section | One line at end: "Tone: Cold, restrained, heavy with unseen dread." |
| **Continuous Prompt** | Not generated (structured output only) | Included as "Full Continuous Prompt (Seedance-optimized)" |

---

## Content Differences — Field by Field

### 1. Global Style / Setting
- **Compiler:** Preserves Chinese text from the project YAML verbatim (e.g. Style: Republican Noir, Color palette: 低饱和度冷灰...)
- **Reference:** Translates everything to English (e.g. "Desaturated cold gray with muted green undertones")
- **Root cause:** The compiler does not translate Chinese → English; it passes through the `creative`, `visual_language`, and other fields as-is. Adding a language translation layer would be a new pipeline stage.

### 2. Framing Translation
- **Compiler:** Uses `rules.FRAMING_MAP` → "ELS" becomes "extreme wide shot", "MS" becomes "medium shot", "CU" becomes "close-up"
- **Reference:** Uses the same terminology consistently
- **Judgment:** The FRAMING_MAP fully covers this. No gap.

### 3. Lens Translation
- **Compiler:** "35mm standard wide lens", "50mm standard lens", "85mm portrait lens" (from `rules.LENS_MAP`)
- **Reference:** "35mm lens", "50mm lens", "85mm lens"  — simpler, no qualifier
- **Root cause:** The reference uses shorter lens descriptors. The compiler's LENS_MAP includes additional context (e.g. "standard wide", "portrait"). This is a stylistic choice, not a gap — the map can be tuned by editing `rules.py`.

### 4. Camera Movement
- **Compiler:** "static camera" (from `rules.MOVEMENT_MAP`)
- **Reference:** "Static camera" or "Static." with no qualifier
- **Judgment:** Fully covered.

### 5. Focus
- **Compiler:** "deep focus", "shallow focus" (from `rules.FOCUS_MAP`)
- **Reference:** "Deep focus", "Shallow focus"
- **Judgment:** Fully covered.

### 6. Lighting
- **Compiler:** Translates `key_light`, `position`, `intensity`, `temperature`, `mood` as separate fields
- **Reference:** Blends these into prose (e.g. "Side light cuts across his cheekbone, leaving half his face in shadow")
- **Root cause:** The reference interprets lighting creatively — combining position, intensity, and mood into expressive prose. The compiler keeps them as structured metadata. This is a fundamental design difference, not a gap in the rules.

### 7. Composition
- **Compiler:** Translates `rule`, `depth`, `foreground`, `midground`, `background` separately
- **Reference:** Integrates composition into the shot narrative
- **Root cause:** Same as lighting — creative synthesis vs structured translation.

### 8. Character Descriptions
- **Compiler:** Lists all characters with full technical descriptions at the top
- **Reference:** Introduces characters inline as they appear in shots, with selective detail
- **Root cause:** The "context insertion rules" from COMPILER_SPEC (first-appearance = full, later = state change only) are **not yet implemented**. The compiler currently dumps all character info upfront. This is an enhancement for a future iteration.

### 9. Emotion & Notes
- **Compiler:** Includes `Emotion` field and `Note` field per shot, preserving Chinese notes verbatim
- **Reference:** The notes are synthesized into the shot description prose
- **Judgment:** The compiler preserves all data; the reference selectively uses it. The compiler approach is more complete.

### 10. Audio Design
- **Compiler:** Full structured section
- **Reference:** A single compact line
- **Judgment:** Both contain the same information in different formats.

### 11. Transition Handling
- **Compiler:** `transition_in` and `transition_out` listed per shot
- **Reference:** Transitions implied by narrative flow (or mentioned inline)
- **Judgment:** The compiler explicitly preserves transitions; the reference trusts the narrative to imply them.

### 12. Beat References
- **Compiler:** Shows beat_ref in shot headers (e.g. `[OPENING]`, `[THE_RITUAL]`)
- **Reference:** Does not show beat references
- **Judgment:** The compiler provides more metadata traceability.

### 13. Absent from Compiler: "Full Continuous Prompt"
- The reference includes a third section: "Full Continuous Prompt (Seedance-optimized)" — a tight narrative form that's closer to what the AI platform actually wants.
- The compiler does not generate this format.
- **Root cause:** This is a Stage 4 enhancement — `prompt_assembler` could support a `style` parameter (`structured` vs `continuous`) to produce both formats. The underlying data is all present.

---

## Gaps in Rules Coverage

After verifying all rule coverage tests pass (29/29), the following gaps exist **in what the rules produce vs what the reference shows**:

| Gap | Severity | Explanation |
|-----|----------|-------------|
| No Chinese → English translation | Medium | Project YAML has Chinese text; Seedance may prefer English. This is a pre-processing concern. |
| No "context insertion" optimization | Medium | Characters introduced at first appearance instead of all upfront (COMPILER_SPEC §5.2) |
| No continuous/summary prompt mode | Low | Reference has a prose "full continuous prompt"; compiler only does structured output |
| Shot descriptions are technical, not narrative | Low | Design choice — the structured format is better for pipeline consumption |
| Lighting/Composition → prose synthesis | Low | The reference creatively interprets technical fields into narrative; the compiler keeps them separate |

---

## Conclusion

The Seedance Compiler successfully implements a deterministic, rules-based translation from Project YAML to structured prompt output. All 29 tests pass, including the core determinism test (identical output across multiple runs).

The differences from the human/LLM-authored reference fall into two categories:

1. **Intentional design differences** — The compiler is a pipeline tool producing structured, auditable output. The reference is a narrative-optimized prompt for direct human use. Both are valid.

2. **Enhancement opportunities** — Context insertion rules, continuous prompt mode, and language translation could be added as future pipeline stages or assembler options without changing the existing architecture.

The four-stage pipeline (project_reader → context_builder → platform_adapter → prompt_assembler) is faithfully implemented and the rule tables in `rules.py` provide complete coverage of every valid enum in the Project schema.
