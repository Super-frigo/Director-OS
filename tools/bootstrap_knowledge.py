#!/usr/bin/env python3
"""Knowledge Library Bootstrap CLI.

Four-layer generation pipeline with quality gates:
  Layer 1 (Taxonomy)    — List all entries per category
  Layer 2 (Skeleton)    — Generate full schema-compliant YAML
  Layer 3 (Relationship)— Annotate cross-entry relationships
  Layer 4 (Deepening)   — Add examples and extra depth to priority entries

Quality Gates:
  Gate 1 (Schema)       — YAML structure validation
  Gate 2 (Consistency)  — LLM-based accuracy/completeness/practicality review
  Gate 3 (Crossref)     — Bidirectional relationship validation + auto-fix
  Gate 4 (Spotcheck)    — Human spot-check report generation

Usage:
    python tools/bootstrap_knowledge.py --category lens --layer skeleton
    python tools/bootstrap_knowledge.py --category all --layer full
    python tools/bootstrap_knowledge.py --category color --layer skeleton --dry-run
    python tools/bootstrap_knowledge.py --gate schema --category all
    python tools/bootstrap_knowledge.py --gate crossref --category all --fix
    python tools/bootstrap_knowledge.py --gate spotcheck --category all

Environment variables:
    OPENAI_API_KEY   — API key for LLM
    OPENAI_BASE_URL  — Base URL (for DeepSeek etc.)
    BOOTSTRAP_MODEL  — Model name (default: deepseek-chat)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import textwrap
from datetime import date
from pathlib import Path
from typing import Any

import yaml

# Ensure project root is on sys.path for director_os imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from director_os.knowledge.llm_client import LLMClient, OpenAIClient

from tools.bootstrap_config import (
    ALLOWED_CATEGORIES,
    CATEGORIES,
    DEEPENING_PRIORITY,
    EMOTION_VOCABULARY,
    GENRE_VOCABULARY,
    LOCAL_RULES_DIR,
    PROMPTS_DIR,
    REPORTS_DIR,
    SCHEMA_PATH,
    get_category_dir,
    get_all_existing_ids,
)
from tools.quality_gates.schema_gate import SchemaGate, SchemaGateResult
from tools.quality_gates.consistency_gate import ConsistencyGate, ConsistencyGateResult
from tools.quality_gates.crossref_gate import CrossrefGate
from tools.quality_gates.spotcheck_report import SpotcheckReportGenerator


# ════════════════════════════════════════════════════════════════════════
# LLM Client Factory
# ════════════════════════════════════════════════════════════════════════

def make_llm_client(max_tokens: int = 4000) -> LLMClient:
    """Create an LLM client from environment variables."""
    return OpenAIClient(
        api_key=os.environ.get("OPENAI_API_KEY", ""),
        model=os.environ.get("BOOTSTRAP_MODEL", "deepseek-chat"),
        base_url=os.environ.get("OPENAI_BASE_URL", ""),
        temperature=0.4,
        max_tokens=max_tokens,
        timeout=60.0,
    )


# ════════════════════════════════════════════════════════════════════════
# Prompt Loading & Rendering
# ════════════════════════════════════════════════════════════════════════

_prompt_cache: dict[str, dict] = {}


def load_prompt(name: str) -> dict:
    """Load a prompt template YAML from tools/prompts/."""
    if name not in _prompt_cache:
        path = PROMPTS_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            _prompt_cache[name] = yaml.safe_load(f)
    return _prompt_cache[name]


def render_template(template: str, variables: dict[str, str]) -> str:
    """Replace {{variable}} placeholders."""
    for key, value in variables.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    return template


def extract_yaml_from_response(text: str) -> str:
    """Strip markdown code fences from LLM response."""
    cleaned = re.sub(r"```ya?ml\s*\n?", "", text)
    cleaned = re.sub(r"```\s*$", "", cleaned)
    return cleaned.strip()


# ════════════════════════════════════════════════════════════════════════
# Few-Shot Example Loading
# ════════════════════════════════════════════════════════════════════════

def load_existing_entry(entry_id: str, category_dir: Path) -> dict | None:
    """Load an existing YAML entry by ID (searches directory for matching file)."""
    # Try common filename patterns
    candidates = [
        category_dir / f"{entry_id}.yaml",
        category_dir / f"{entry_id.replace('-', '_')}.yaml",
    ]
    # Also search by id field inside files
    for yaml_file in category_dir.glob("*.yaml"):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and data.get("library", {}).get("metadata", {}).get("id") == entry_id:
                return data
        except (yaml.YAMLError, OSError):
            continue
    for c in candidates:
        if c.exists():
            with open(c, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
    return None


def format_few_shot_examples(cat_config: dict, category_dir: Path) -> str:
    """Format few-shot examples as YAML text."""
    parts: list[str] = []
    for entry_id in cat_config["few_shot"]:
        data = load_existing_entry(entry_id, category_dir)
        if data:
            parts.append(yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False))
    if not parts:
        return "(No few-shot examples available for this category)"
    return "\n---\n".join(parts)


# ════════════════════════════════════════════════════════════════════════
# Layer 1: Taxonomy Generation
# ════════════════════════════════════════════════════════════════════════

def generate_taxonomy(
    category_key: str,
    client: LLMClient,
    dry_run: bool = False,
) -> list[dict]:
    """Layer 1: Generate taxonomy (entry checklist) for a category."""
    cat = CATEGORIES[category_key]
    prompt = load_prompt("taxonomy.yaml")

    existing_text = "\n".join(f"- {eid}" for eid in cat["existing"]) or "(none)"

    variables = {
        "category": category_key,
        "category_definition": cat["definition"],
        "existing_entries": existing_text,
        "id_prefix": cat["id_prefix"],
        "id_examples": ", ".join(cat["existing"][:3]),
        "target_count": str(len(cat["new_ids"]) + len(cat["existing"])),
    }

    system_msg = prompt["system"].strip()
    user_msg = render_template(prompt["user"].strip(), variables)

    print(f"\n{'═' * 60}")
    print(f"Layer 1 (Taxonomy) — {category_key}")
    print(f"{'═' * 60}")

    response = client.chat(system_msg, user_msg)
    cleaned = extract_yaml_from_response(response)

    if dry_run:
        print(f"\n[DRY RUN] Taxonomy output for {category_key}:")
        print(cleaned)
        return []

    try:
        entries = yaml.safe_load(cleaned)
        if not isinstance(entries, list):
            print(f"  ⚠️  Expected list, got {type(entries).__name__}")
            return []
    except yaml.YAMLError as e:
        print(f"  ❌ YAML parse error: {e}")
        return []

    print(f"  ✅ Generated {len(entries)} taxonomy entries")
    for entry in entries:
        print(f"     • {entry.get('id', '?')}: {entry.get('one_line_description', '')[:60]}")

    return entries


# ════════════════════════════════════════════════════════════════════════
# Layer 2: Skeleton Generation
# ════════════════════════════════════════════════════════════════════════

def generate_skeleton(
    entry_id: str,
    category_key: str,
    client: LLMClient,
    dry_run: bool = False,
) -> dict | None:
    """Layer 2: Generate full schema-compliant YAML for a single entry."""
    cat = CATEGORIES[category_key]
    category_dir = get_category_dir(category_key)
    prompt = load_prompt("skeleton.yaml")

    # Build entry description (from new_ids list or taxonomy)
    entry_name = entry_id.replace(cat["id_prefix"], "").replace("_", " ").title()
    entry_description = f"{entry_name} — see category definition for guidance."

    few_shot_text = format_few_shot_examples(cat, category_dir)

    variables = {
        "entry_id": entry_id,
        "entry_description": entry_description,
        "allowed_categories": "\n".join(f"  - {c}" for c in ALLOWED_CATEGORIES),
        "emotion_vocabulary": "\n".join(f"  - {e}" for e in EMOTION_VOCABULARY),
        "genre_vocabulary": "\n".join(f"  - {g}" for g in GENRE_VOCABULARY),
        "few_shot_examples": few_shot_text,
        "today": date.today().isoformat(),
    }

    system_msg = prompt["system"].strip()
    user_msg = render_template(prompt["user"].strip(), variables)

    print(f"\n  📝 Generating skeleton: {entry_id}")

    response = client.chat(system_msg, user_msg)
    cleaned = extract_yaml_from_response(response)

    try:
        data = yaml.safe_load(cleaned)
    except yaml.YAMLError as e:
        print(f"     ❌ YAML parse error: {e}")
        return None

    if not data or "library" not in data:
        print(f"     ❌ Missing 'library' key in response")
        return None

    if dry_run:
        print(f"\n     [DRY RUN] Skeleton for {entry_id}:")
        print(textwrap.indent(cleaned, "     "))
        return data

    # Write to disk
    output_path = category_dir / f"{entry_id}.yaml"
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"     ✅ Written to {output_path.relative_to(PROJECT_ROOT)}")
    return data


# ════════════════════════════════════════════════════════════════════════
# Layer 3: Relationship Graph Generation
# ════════════════════════════════════════════════════════════════════════

def generate_relationships(
    category_key: str,
    client: LLMClient,
    dry_run: bool = False,
) -> bool:
    """Layer 3: Generate relationship graph for all entries in a category."""
    cat = CATEGORIES[category_key]
    category_dir = get_category_dir(category_key)
    prompt = load_prompt("relationship.yaml")

    # Build entry matrix
    all_ids = cat["existing"] + cat["new_ids"]
    matrix_parts: list[str] = []
    entries_data: dict[str, dict] = {}

    for entry_id in all_ids:
        data = load_existing_entry(entry_id, category_dir)
        if data and "library" in data:
            entries_data[entry_id] = data
            lib = data["library"]
            concept = lib.get("knowledge", {}).get("concept", "")[:100]
            matrix_parts.append(f"- {entry_id}: {concept}")

    if not entries_data:
        print(f"\n  ⚠️  No entries found for {category_key} relationship generation")
        return False

    # Existing relationships
    existing_rels: list[str] = []
    for eid, data in entries_data.items():
        rels = data.get("library", {}).get("relationships", {})
        related = rels.get("related", []) or []
        if related:
            existing_rels.append(f"  {eid}.related: {related}")

    variables = {
        "category": category_key,
        "entry_matrix": "\n".join(matrix_parts),
        "existing_relationships": "\n".join(existing_rels) or "(none)",
    }

    system_msg = prompt["system"].strip()
    user_msg = render_template(prompt["user"].strip(), variables)

    print(f"\n{'═' * 60}")
    print(f"Layer 3 (Relationship) — {category_key}")
    print(f"{'═' * 60}")

    response = client.chat(system_msg, user_msg)
    cleaned = extract_yaml_from_response(response)

    try:
        rel_data = yaml.safe_load(cleaned)
    except yaml.YAMLError as e:
        print(f"  ❌ YAML parse error: {e}")
        return False

    if not isinstance(rel_data, dict):
        print(f"  ⚠️  Expected dict mapping, got {type(rel_data).__name__}")
        return False

    if dry_run:
        print(f"\n  [DRY RUN] Relationship data for {category_key}:")
        print(textwrap.indent(yaml.dump(rel_data, default_flow_style=False), "  "))
        return True

    # Merge relationship data into entries
    updated = 0
    for entry_id, rels in rel_data.items():
        if entry_id not in entries_data:
            print(f"  ⚠️  Unknown entry ID in relationships: {entry_id}")
            continue

        data = entries_data[entry_id]
        lib = data.setdefault("library", {})
        rel_section = lib.setdefault("relationships", {})

        # Only update if values are provided
        if isinstance(rels, dict):
            if "related" in rels and rels["related"] is not None:
                rel_section["related"] = rels["related"]
            if "conflicts" in rels and rels["conflicts"] is not None:
                rel_section["conflicts"] = rels["conflicts"]
            if "extensions" in rels and rels["extensions"] is not None:
                rel_section["extensions"] = rels["extensions"]

        # Write back
        # Find the file path
        entry_path = category_dir / f"{entry_id}.yaml"
        if entry_path.exists():
            with open(entry_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            updated += 1

    print(f"  ✅ Updated relationships for {updated} entries")
    return True


# ════════════════════════════════════════════════════════════════════════
# Layer 4: Deepening
# ════════════════════════════════════════════════════════════════════════

def deepen_entry(
    entry_id: str,
    client: LLMClient,
    dry_run: bool = False,
) -> bool:
    """Layer 4: Deepen a high-priority entry with examples and extra depth."""
    prompt = load_prompt("deepening.yaml")

    # Find the entry across all category directories
    entry_data = None
    entry_path = None
    for cat_key, cat in CATEGORIES.items():
        cat_dir = get_category_dir(cat_key)
        p = cat_dir / f"{entry_id}.yaml"
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                entry_data = yaml.safe_load(f)
            entry_path = p
            break

    if entry_data is None:
        print(f"  ⚠️  Entry not found: {entry_id}")
        return False

    current_content = yaml.dump(entry_data, default_flow_style=False, allow_unicode=True, sort_keys=False)

    variables = {
        "entry_id": entry_id,
        "current_content": current_content,
    }

    system_msg = prompt["system"].strip()
    user_msg = render_template(prompt["user"].strip(), variables)

    print(f"\n  🔍 Deepening: {entry_id}")

    response = client.chat(system_msg, user_msg)
    cleaned = extract_yaml_from_response(response)

    try:
        deepened = yaml.safe_load(cleaned)
    except yaml.YAMLError as e:
        print(f"     ❌ YAML parse error: {e}")
        return False

    if not isinstance(deepened, dict):
        print(f"     ⚠️  Expected dict, got {type(deepened).__name__}")
        return False

    if dry_run:
        print(f"\n     [DRY RUN] Deepening data for {entry_id}:")
        print(textwrap.indent(yaml.dump(deepened, default_flow_style=False), "     "))
        return True

    # Merge deepened content
    lib = entry_data.setdefault("library", {})

    # Merge examples
    if "examples" in deepened:
        ex = lib.setdefault("examples", {})
        if "successful" in deepened["examples"]:
            ex["successful"] = deepened["examples"]["successful"]
        if "failure" in deepened["examples"]:
            ex["failure"] = deepened["examples"]["failure"]

    # Merge knowledge.techniques and constraints
    if "knowledge" in deepened:
        knowledge = lib.setdefault("knowledge", {})
        existing_techniques = set(knowledge.get("techniques", []) or [])
        for t in deepened["knowledge"].get("techniques", []) or []:
            if t not in existing_techniques:
                knowledge.setdefault("techniques", []).append(t)
                existing_techniques.add(t)

        existing_constraints = set(knowledge.get("constraints", []) or [])
        for c in deepened["knowledge"].get("constraints", []) or []:
            if c not in existing_constraints:
                knowledge.setdefault("constraints", []).append(c)
                existing_constraints.add(c)

    # Write back
    with open(entry_path, "w", encoding="utf-8") as f:
        yaml.dump(entry_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"     ✅ Deepened and saved: {entry_path.relative_to(PROJECT_ROOT)}")
    return True


# ════════════════════════════════════════════════════════════════════════
# Gate Runners
# ════════════════════════════════════════════════════════════════════════

def run_schema_gate(category_key: str) -> bool:
    """Gate 1: Validate schema compliance."""
    category_dir = get_category_dir(category_key)
    gate = SchemaGate()
    result = gate.validate_directory(category_dir)

    print(f"\n{'─' * 50}")
    print(f"Gate 1 (Schema) — {category_key}")
    print(f"{'─' * 50}")

    if result.passed:
        print(f"  ✅ PASSED — {len(result.entry_ids)} entries valid")
    else:
        print(f"  ❌ FAILED — {sum(1 for i in result.issues if i.severity == 'error')} errors")

    for issue in result.issues:
        icon = {"error": "🔴", "warning": "🟡"}.get(issue.severity, "⚪")
        print(f"  {icon} [{issue.severity.upper()}] {issue.entry_id}.{issue.field}")
        print(f"      {issue.description}")
        if issue.suggestion:
            print(f"      💡 {issue.suggestion}")

    return result.passed


def run_consistency_gate(
    category_key: str,
    client: LLMClient,
    skip: bool = False,
) -> ConsistencyGateResult | None:
    """Gate 2: LLM-based consistency review."""
    if skip:
        print(f"\n  ⏭️  Skipping Gate 2 (Consistency) for {category_key}")
        return None

    category_dir = get_category_dir(category_key)

    # Load only NEW entries for review
    cat = CATEGORIES[category_key]
    new_entries: list[dict] = []
    for entry_id in cat["new_ids"]:
        data = load_existing_entry(entry_id, category_dir)
        if data:
            new_entries.append(data)

    if not new_entries:
        print(f"\n  ⚠️  No new entries to review for {category_key}")
        return None

    print(f"\n{'─' * 50}")
    print(f"Gate 2 (Consistency) — {category_key}")
    print(f"{'─' * 50}")

    gate = ConsistencyGate(client=client)
    result = gate.review_entries(new_entries)

    if result.passed:
        print(f"  ✅ PASSED — no errors found")
    else:
        print(f"  ❌ FAILED — {len(result.entries_needing_regeneration)} entries need regeneration")

    for issue in result.issues:
        icon = {"error": "🔴", "warning": "🟡", "suggestion": "🔵"}.get(issue.severity, "⚪")
        print(f"  {icon} [{issue.severity.upper()}] ({issue.review_round}) {issue.entry_id}.{issue.field}")
        print(f"      {issue.description}")
        if issue.suggestion:
            print(f"      💡 {issue.suggestion}")

    return result


def run_crossref_gate(category_key: str, fix: bool = False) -> bool:
    """Gate 3: Cross-reference validation."""
    print(f"\n{'─' * 50}")
    print(f"Gate 3 (Crossref) — {category_key}")
    print(f"{'─' * 50}")

    category_dir = get_category_dir(category_key)
    gate = CrossrefGate()
    gate.load_directory(category_dir)

    if fix:
        result = gate.fix_bidirectional()
        if result.auto_fixes_applied:
            print(f"  🔧 Auto-fixed {len(result.auto_fixes_applied)} relationships:")
            for fix_msg in result.auto_fixes_applied:
                print(f"     • {fix_msg}")
    else:
        result = gate.validate()

    if result.passed:
        print(f"  ✅ PASSED — all relationships bidirectional")
    else:
        n_warn = sum(1 for i in result.issues if i.severity == "warning")
        if n_warn:
            print(f"  ⚠️  {n_warn} warnings (non-blocking)")
        n_err = sum(1 for i in result.issues if i.severity == "error")
        if n_err:
            print(f"  ❌ {n_err} errors")

    for issue in result.issues:
        if issue.severity == "auto_fixed":
            continue
        icon = {"error": "🔴", "warning": "🟡", "suggestion": "🔵"}.get(issue.severity, "⚪")
        print(f"  {icon} [{issue.severity.upper()}] {issue.entry_id}.{issue.field}")
        print(f"      {issue.description}")

    return result.passed


def run_spotcheck_gate(category_key: str) -> bool:
    """Gate 4: Generate spot-check report."""
    print(f"\n{'─' * 50}")
    print(f"Gate 4 (Spotcheck) — {category_key}")
    print(f"{'─' * 50}")

    category_dir = get_category_dir(category_key)
    generator = SpotcheckReportGenerator(output_dir=REPORTS_DIR, sample_count=3, seed=42)
    report = generator.generate(category_key, category_dir)

    if report.entries:
        print(f"  📄 Report: {REPORTS_DIR.relative_to(PROJECT_ROOT)}/{category_key}_spotcheck.md")
        print(f"     Sampled {len(report.entries)} entries, pass rate: {report.pass_rate:.0%}")
        return report.pass_rate >= 0.9
    else:
        print(f"  ⚠️  No entries to sample")
        return False


# ════════════════════════════════════════════════════════════════════════
# Pipeline Orchestration
# ════════════════════════════════════════════════════════════════════════

def run_full_pipeline(
    category_key: str,
    client: LLMClient,
    dry_run: bool = False,
    skip_gates: bool = False,
) -> bool:
    """Run all layers + gates for a single category."""
    cat = CATEGORIES[category_key]
    print(f"\n{'═' * 60}")
    print(f"FULL PIPELINE — {category_key} ({len(cat['new_ids'])} new entries)")
    print(f"{'═' * 60}")

    # Layer 1: Taxonomy (informational, validates target list)
    generate_taxonomy(category_key, client, dry_run=dry_run)

    # Layer 2: Skeleton
    print(f"\n{'═' * 60}")
    print(f"Layer 2 (Skeleton) — {category_key}")
    print(f"{'═' * 60}")
    generated: list[str] = []
    for entry_id in cat["new_ids"]:
        data = generate_skeleton(entry_id, category_key, client, dry_run=dry_run)
        if data:
            generated.append(entry_id)

    if dry_run:
        print(f"\n  [DRY RUN] Would have generated {len(generated)} entries")
        return True

    if not generated:
        print(f"\n  ⚠️  No entries generated, skipping remaining layers")
        return False

    # Gate 1: Schema
    if not skip_gates:
        schema_ok = run_schema_gate(category_key)
        if not schema_ok:
            print(f"\n  ⚠️  Schema gate failed — fix issues before proceeding")

    # Gate 2: Consistency
    if not skip_gates:
        run_consistency_gate(category_key, client)

    # Layer 3: Relationships
    generate_relationships(category_key, client, dry_run=dry_run)

    # Gate 3: Crossref
    if not skip_gates:
        run_crossref_gate(category_key, fix=True)

    return True


def run_deepening_pipeline(client: LLMClient, dry_run: bool = False) -> None:
    """Run Layer 4 deepening on priority entries."""
    print(f"\n{'═' * 60}")
    print(f"Layer 4 (Deepening) — {len(DEEPENING_PRIORITY)} priority entries")
    print(f"{'═' * 60}")

    for entry_id in DEEPENING_PRIORITY:
        deepen_entry(entry_id, client, dry_run=dry_run)


# ════════════════════════════════════════════════════════════════════════
# CLI Argument Parsing
# ════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Knowledge Library Bootstrap — generate + validate knowledge entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              # Generate skeletons for all lens entries
              python tools/bootstrap_knowledge.py --category lens --layer skeleton

              # Full pipeline for all categories
              python tools/bootstrap_knowledge.py --category all --layer full

              # Validate schema only
              python tools/bootstrap_knowledge.py --gate schema --category all

              # Fix relationship cross-references
              python tools/bootstrap_knowledge.py --gate crossref --category all --fix

              # Generate spot-check reports
              python tools/bootstrap_knowledge.py --gate spotcheck --category all
        """),
    )

    parser.add_argument(
        "--category",
        choices=list(CATEGORIES.keys()) + ["all"],
        default="all",
        help="Knowledge category to process (default: all)",
    )
    parser.add_argument(
        "--layer",
        choices=["taxonomy", "skeleton", "relationship", "deepening", "full"],
        help="Generation layer to run",
    )
    parser.add_argument(
        "--gate",
        choices=["schema", "consistency", "crossref", "spotcheck"],
        help="Quality gate to run (alternative to --layer)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="LLM model name (overrides BOOTSTRAP_MODEL env var)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print LLM output without writing files",
    )
    parser.add_argument(
        "--skip-gates",
        action="store_true",
        help="Skip quality gates (only applies to --layer full)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix issues (applies to --gate crossref)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all target entry IDs and exit",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # ── List mode ──
    if args.list:
        print("\nKnowledge Library Bootstrap — Target Entries\n")
        for cat_key, cat in CATEGORIES.items():
            print(f"  {cat_key}:")
            print(f"    Directory: {cat['directory']}/")
            print(f"    Existing:  {len(cat['existing'])} entries")
            print(f"    New:       {len(cat['new_ids'])} entries")
            for eid in cat["new_ids"]:
                print(f"      + {eid}")
            print()
        print(f"  Deepening priority: {len(DEEPENING_PRIORITY)} entries")
        return 0

    # ── Determine categories to process ──
    if args.category == "all":
        cat_keys = list(CATEGORIES.keys())
    else:
        cat_keys = [args.category]

    # ── Gate-only mode ──
    if args.gate and not args.layer:
        if args.gate == "consistency":
            client = make_llm_client()
            for ck in cat_keys:
                run_consistency_gate(ck, client)
        elif args.gate == "schema":
            for ck in cat_keys:
                run_schema_gate(ck)
        elif args.gate == "crossref":
            for ck in cat_keys:
                run_crossref_gate(ck, fix=args.fix)
        elif args.gate == "spotcheck":
            for ck in cat_keys:
                run_spotcheck_gate(ck)
        return 0

    # ── Layer / full pipeline mode ──
    if not args.layer:
        parser.error("--layer or --gate is required (unless --list)")

    # Gate-only modes that don't need LLM
    if args.layer in ("taxonomy", "skeleton", "relationship", "full"):
        client = make_llm_client()
    elif args.layer == "deepening":
        client = make_llm_client()
    else:
        client = None

    if args.layer == "full":
        for ck in cat_keys:
            run_full_pipeline(ck, client, dry_run=args.dry_run, skip_gates=args.skip_gates)
        # Deepening for priority entries
        if not args.dry_run:
            run_deepening_pipeline(client, dry_run=args.dry_run)
        # Spot-check reports
        if not args.skip_gates:
            for ck in cat_keys:
                run_spotcheck_gate(ck)

    elif args.layer == "taxonomy":
        for ck in cat_keys:
            generate_taxonomy(ck, client, dry_run=args.dry_run)

    elif args.layer == "skeleton":
        for ck in cat_keys:
            cat = CATEGORIES[ck]
            print(f"\n{'═' * 60}")
            print(f"Layer 2 (Skeleton) — {ck}")
            print(f"{'═' * 60}")
            for eid in cat["new_ids"]:
                generate_skeleton(eid, ck, client, dry_run=args.dry_run)

    elif args.layer == "relationship":
        for ck in cat_keys:
            generate_relationships(ck, client, dry_run=args.dry_run)

    elif args.layer == "deepening":
        run_deepening_pipeline(client, dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
