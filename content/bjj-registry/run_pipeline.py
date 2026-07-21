"""run_pipeline.py — one-command pSEO workstream for the National BJJ Registry.

Wires the fact layer -> article generator -> registry blog_posts JSONL, then
(optionally) invokes the registry's own importer. Designed to be run on a
schedule (cron / CI) so content regenerates as registry scores refresh.

Usage:
  # Generate from the live registry DB (directory spine + insight aggregates):
  python run_pipeline.py --source "postgres://user@host:5432/registry" \
      --state-names state_names.json --format jsonl --out ../output

  # Then push to the registry (dry-run by default; add --publish to write):
  python run_pipeline.py --source ... --import-to ../../WA\ JiuJitsu\ Registry-.../scripts/import-programmatic-blog-posts.mjs

Behavior:
  - Reads academies (directory) + registry_region_score_aggregates_v1 (insights)
  - Emits output/blog_posts.jsonl shaped for import-programmatic-blog-posts.mjs
  - NEVER writes to the registry unless --import-to is passed AND --publish given
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
sys.path.insert(0, str(SRC))

from generate import BRAND, load_facts, build_blog_row  # noqa: E402
from article_template import build_article, build_article_llm  # noqa: E402


def _render_content_md(facts, brand, writer, only_priority):
    """Render the article body. LLM only on priority tiers unless forced."""
    use_llm = writer == "llm" and (not only_priority or facts.tier in ("state", "city"))
    if use_llm:
        try:
            art = build_article_llm(facts, brand=brand)
            return art["markdown"]
        except Exception as e:  # noqa: BLE001
            print(f"  [llm-fallback] {facts.slug}: {e}; template")
    return build_article(facts, brand=brand)["markdown"]


def main() -> int:
    ap = argparse.ArgumentParser(description="BJJ Registry pSEO pipeline")
    ap.add_argument("--source", help="CSV / SQLite / postgres:// DSN for the registry")
    ap.add_argument("--state-names", help="JSON: state code -> full name")
    ap.add_argument("--out", default=str(HERE.parent / "output"))
    ap.add_argument("--brand", default=BRAND)
    ap.add_argument("--slug")
    ap.add_argument("--tier")
    ap.add_argument("--writer", choices=["template", "llm"], default="template",
                    help="template (default) or llm (flash-model prose, guarded)")
    ap.add_argument("--only-priority", action="store_true",
                    help="with --writer llm, use LLM only on state/city; template elsewhere")
    ap.add_argument("--import-to", help="path to registry import-programmatic-blog-posts.mjs")
    ap.add_argument("--publish", action="store_true", help="actually write to registry DB")
    ap.add_argument("--batch-id", default=f"bjj-registry-pseo")
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    facts_list = load_facts(args)
    if args.slug:
        facts_list = [f for f in facts_list if f.slug == args.slug]
    if args.tier:
        facts_list = [f for f in facts_list if f.tier == args.tier]
    if not facts_list:
        print("No matching facts found.")
        return 1

    # Emit registry blog_posts JSONL (prose rendered via chosen writer)
    rows = []
    for f in facts_list:
        content_md = _render_content_md(f, args.brand, args.writer, args.only_priority)
        row = build_blog_row(f, brand=args.brand)
        row["content_md"] = content_md
        rows.append(row)
    jsonl_path = out_root / "blog_posts.jsonl"
    jsonl_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8"
    )
    with_insights = sum(1 for f in facts_list if f.insights)
    print(f"Generated {len(rows)} blog rows -> {jsonl_path}")
    print(f"  with market-insight layer: {with_insights}/{len(rows)}  writer={args.writer}")

    # Optional: hand off to the registry importer
    if args.import_to:
        importer = Path(args.import_to)
        if not importer.exists():
            print(f"ERROR: importer not found: {importer}", file=sys.stderr)
            return 1
        cmd = [
            "node", str(importer),
            f"--input={jsonl_path}",
            f"--batch-id={args.batch_id}",
        ]
        if args.publish:
            cmd += ["--confirm-write", "--approve", "--publish", "--enqueue-refresh"]
        print("Running importer" + (" (PUBLISH)" if args.publish else " (dry-run):"))
        print("  " + " ".join(cmd))
        res = subprocess.run(cmd)
        return res.returncode

    print("Dry-run only. Add --import-to <path> to hand off to the registry importer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
