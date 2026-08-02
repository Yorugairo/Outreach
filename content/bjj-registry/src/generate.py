"""generate.py — BJJ Registry pSEO article generator.

Usage:
    python generate.py                 # generates all sample facts -> output/
    python generate.py --slug austin-tx
    python generate.py --tier city
    python generate.py --out my_output

Each article is written as:
    output/<slug>/index.md        (article body)
    output/<slug>/meta.json       (title, meta, slug, verified flag)
    output/<slug>/article.jsonld  (structured data)

The generator is deterministic: same facts -> same output. It never invents
facts; it only renders what LocationFacts provides.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from article_template import build_article, build_blog_row  # noqa: E402
from sample_facts import ALL_SAMPLE_FACTS  # noqa: E402

BRAND = "National BJJ Registry"


def load_facts(args) -> list:
    """Resolve the fact list from sample data or a real source (axis-aware)."""
    axis = getattr(args, "axis", "location")
    if axis == "technique":
        import corpus_loader
        from validate_corpus import validate_corpus

        src = getattr(args, "corpus", None) or (HERE.parent / "corpus")
        readiness = validate_corpus(src)
        if not readiness["valid"]:
            details = [
                f"{item['path']}: {error}"
                for item in readiness["records"]
                for error in item["errors"]
            ]
            details.extend(readiness["errors"])
            raise ValueError(
                "technique corpus is not production-ready:\n  - "
                + "\n  - ".join(details)
            )
        return corpus_loader.load_corpus(str(src))
    # location axis
    if getattr(args, "source", None):
        import db_loader
        src = args.source
        kwargs = {}
        if args.state_names:
            import json as _json
            kwargs["state_names"] = _json.loads(Path(args.state_names).read_text(encoding="utf-8"))
        if src.startswith("postgres://") or src.startswith("postgresql://"):
            return db_loader.load_from_postgres(src, **kwargs)
        if src.endswith(".db") or src.endswith(".sqlite") or src.endswith(".sqlite3"):
            return db_loader.load_from_sqlite(src, **kwargs)
        return db_loader.load_from_csv(src, **kwargs)
    return ALL_SAMPLE_FACTS


def generate_one(facts, out_root: Path, brand: str = BRAND, writer: str = "template",
                 axis: str = "location") -> dict:
    article = _render(facts, brand, writer, axis)
    slug_dir = out_root / facts.slug
    slug_dir.mkdir(parents=True, exist_ok=True)
    (slug_dir / "index.md").write_text(article["markdown"], encoding="utf-8")
    (slug_dir / "meta.json").write_text(json.dumps({
        "axis": article.get("axis", axis),
        "tier": article.get("tier"),
        "slug": article["slug"],
        "title_tag": article["title_tag"],
        "meta_description": article["meta_description"],
        "verified": article["verified"],
        "writer": article.get("writer", writer),
    }, indent=2), encoding="utf-8")
    (slug_dir / "article.jsonld").write_text(json.dumps(article["jsonld"], indent=2), encoding="utf-8")
    return article


def _render(facts, brand: str, writer: str, axis: str) -> dict:
    """Render an article, choosing the writer with safe fallback (axis-aware)."""
    if axis == "technique":
        if writer == "llm":
            try:
                from technique_template import build_technique_llm
                art = build_technique_llm(facts, brand=brand)
                art["writer"] = "llm"
                return art
            except Exception as e:  # noqa: BLE001
                print(f"  [llm-fallback] {facts.slug}: {e}; using template")
        from technique_template import build_article
        art = build_article(facts, brand=brand)
        art["writer"] = "template"
        return art
    # location axis
    if writer == "llm":
        try:
            from article_template import build_article_llm
            art = build_article_llm(facts, brand=brand)
            art["writer"] = "llm"
            return art
        except Exception as e:  # noqa: BLE001
            print(f"  [llm-fallback] {facts.slug}: {e}; using template")
    from article_template import build_article
    art = build_article(facts, brand=brand)
    art["writer"] = "template"
    return art


def _blog_row(facts, brand: str, axis: str) -> dict:
    if axis == "technique":
        from technique_template import build_article as _ta
        art = _ta(facts, brand=brand)
        return {
            "slug": facts.slug,
            "title": art["title_tag"],
            "excerpt": art["meta_description"],
            "content_md": art["markdown"],
            "cover_image": "",
            "tenant_id": brand,
            "metadata": {
                "distribution": {"scope_type": "gym", "technique_slug": facts.slug},
                "axis": "technique",
                "position": facts.position,
                "belt": facts.belt,
            },
        }
    return build_blog_row(facts, brand=brand)


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate BJJ Registry pSEO articles")
    ap.add_argument("--slug")
    ap.add_argument("--tier")
    ap.add_argument("--out", default=str(HERE.parent / "output"))
    ap.add_argument("--brand", default=BRAND)
    ap.add_argument("--axis", choices=["location", "technique"], default="location",
                    help="location = academy/region pages; technique = corpus video pages")
    ap.add_argument("--source", help="registry source: CSV/SQLite file, or postgres:// DSN")
    ap.add_argument("--corpus", help="technique corpus: dir or json/jsonl of video+transcript records")
    ap.add_argument("--state-names", help="optional JSON file mapping state code -> full name")
    ap.add_argument("--format", choices=["md", "jsonl"], default="md",
                    help="md = per-slug files (default); jsonl = registry blog_posts import rows")
    ap.add_argument("--writer", choices=["template", "llm"], default="template",
                    help="template = deterministic (default); llm = flash-model prose w/ guard + fallback")
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    try:
        facts_list = load_facts(args)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.slug:
        facts_list = [f for f in facts_list if f.slug == args.slug]
    if args.tier:
        facts_list = [f for f in facts_list if getattr(f, "tier", None) == args.tier]
    if not facts_list:
        print("No matching facts found.")
        return 1

    if args.format == "jsonl":
        out_root.mkdir(parents=True, exist_ok=True)
        out_file = out_root / "blog_posts.jsonl"
        rows = [_blog_row(f, args.brand, args.axis) for f in facts_list]
        out_file.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
        print(f"Done. {len(rows)} registry blog_posts row(s) -> {out_file} (axis={args.axis})")
        return 0

    print(f"Generating {len(facts_list)} article(s) -> {out_root}  (axis={args.axis})")
    count = 0
    for facts in facts_list:
        generate_one(facts, out_root, brand=args.brand, writer=args.writer, axis=args.axis)
        count += 1
        tag = getattr(facts, "tier", args.axis)
        print(f"  [ok] /{facts.slug}  ({tag})")
    print(f"Done. {count} article(s) written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
