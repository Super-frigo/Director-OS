#!/usr/bin/env python3
"""Cache warmup script — pre-fill LLM cache for common domain queries.

Run this once after setting up an LLM client to pre-populate the cache.
After warmup, Engine queries that match these combinations hit cache
without calling the LLM.

Usage:
    # With OpenAI (default)
    python scripts/warmup_cache.py --api-key sk-... --model gpt-4o

    # With DeepSeek or any OpenAI-compatible API
    python scripts/warmup_cache.py --api-key sk-... --base-url https://api.deepseek.com/v1 --model deepseek-chat

    # Dry run (shows what would be queried without calling LLM)
    python scripts/warmup_cache.py --dry-run

    # Warmup specific domains only
    python scripts/warmup_cache.py --api-key sk-... --domains composition,lighting
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml

from director_os.knowledge import (
    KnowledgeRequest,
    KnowledgeResolver,
    LocalRulesProvider,
    LLMProvider,
    CacheManager,
)
from director_os.knowledge.llm_client import OpenAIClient


def load_warmup_queries(path: Path) -> dict[str, list[dict]]:
    """Load warmup query definitions."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("domains", {})


def warmup(
    client: OpenAIClient,
    domains: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """Run warmup for specified domains (or all if None)."""
    queries_path = ROOT / "knowledge" / "providers" / "llm_cache" / "warmup_queries.yaml"
    all_queries = load_warmup_queries(queries_path)

    cache = CacheManager()
    resolver = KnowledgeResolver()
    resolver.register(LocalRulesProvider())
    resolver.set_cache(cache)
    provider = LLMProvider(client=client, cache_manager=cache)
    resolver.register(provider)

    target_domains = domains or list(all_queries.keys())
    stats = {"total": 0, "cached": 0, "queried": 0, "errors": 0, "domains": {}}

    for domain in target_domains:
        queries = all_queries.get(domain, [])
        if not queries:
            print(f"  [{domain}] No queries defined — skipping")
            continue

        domain_stats = {"total": len(queries), "cached": 0, "queried": 0, "errors": 0}
        print(f"\n[{domain}] {len(queries)} queries")

        for i, ctx in enumerate(queries):
            query_parts = []
            for k, v in ctx.items():
                if v:
                    query_parts.append(f"{k}={v}")
            query_str = ", ".join(query_parts) if query_parts else domain

            request = KnowledgeRequest(
                request_id=f"warmup_{domain}_{i}",
                domain=domain,
                query=query_str,
                context=ctx,
                allow_llm=not dry_run,
            )

            if dry_run:
                print(f"  [{i+1}/{len(queries)}] WOULD query: {query_str[:80]}")
                continue

            # Check if already cached
            cached = cache.get(request)
            if cached:
                print(f"  [{i+1}/{len(queries)}] CACHED: {query_str[:60]}")
                domain_stats["cached"] += 1
                stats["cached"] += 1
                continue

            # Query LLM
            print(f"  [{i+1}/{len(queries)}] QUERYING: {query_str[:60]} ...", end=" ", flush=True)
            try:
                result = resolver.resolve(request)
                if result.entries:
                    print(f"OK ({len(result.entries)} entries)")
                    domain_stats["queried"] += 1
                    stats["queried"] += 1
                else:
                    print("EMPTY (no entries returned)")
                    domain_stats["errors"] += 1
                    stats["errors"] += 1
            except Exception as e:
                print(f"ERROR: {e}")
                domain_stats["errors"] += 1
                stats["errors"] += 1

            time.sleep(0.5)  # Rate limit courtesy

        stats["domains"][domain] = domain_stats
        stats["total"] += domain_stats["total"]

    return stats


def main():
    parser = argparse.ArgumentParser(description="Pre-fill LLM knowledge cache")
    parser.add_argument("--api-key", default="", help="API key")
    parser.add_argument("--model", default="gpt-4o", help="Model name")
    parser.add_argument("--base-url", default="", help="API base URL (for non-OpenAI providers)")
    parser.add_argument("--domains", default="", help="Comma-separated domain list (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show queries without calling LLM")
    args = parser.parse_args()

    if args.dry_run:
        print("=== DRY RUN (no LLM calls) ===\n")
        warmup(client=None, dry_run=True)
        return

    if not args.api_key:
        print("Error: --api-key is required (or use OPENAI_API_KEY env var)", file=sys.stderr)
        sys.exit(1)

    client = OpenAIClient(
        api_key=args.api_key,
        model=args.model,
        base_url=args.base_url,
        temperature=0.3,
        max_tokens=2000,
    )

    domains = [d.strip() for d in args.domains.split(",") if d.strip()] if args.domains else None

    print(f"Model: {args.model}")
    print(f"Domains: {domains or 'all'}")
    print(f"Cache dir: {ROOT / 'knowledge' / 'providers' / 'llm_cache'}")

    stats = warmup(client=client, domains=domains)

    print(f"\n{'='*50}")
    print(f"Warmup complete:")
    print(f"  Total queries: {stats['total']}")
    print(f"  Already cached: {stats['cached']}")
    print(f"  Newly queried: {stats['queried']}")
    print(f"  Errors: {stats['errors']}")
    for domain, ds in stats.get("domains", {}).items():
        print(f"  [{domain}] {ds['cached']} cached, {ds['queried']} queried, {ds['errors']} errors")


if __name__ == "__main__":
    main()
