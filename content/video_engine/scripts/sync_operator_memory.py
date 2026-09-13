"""Promote the Claude operator memories into the repo (P54 T4).

The Claude-only memory folder links memories as ``[[slug]]`` where slug is another
file's frontmatter ``name:``. The repo copy under ``docs/agent-memory/operator/``
rewrites those links as relative Markdown links so any agent can follow them;
everything else is copied byte-for-byte.

    --export          write the transformed copies (reports extras, never deletes)
    --export --prune  also delete destination files that no longer exist in the source
    --check           exit 1 listing drifted / missing / extra files, else 0

A source file with a secret-looking string is never written; the file and the
pattern name are printed (never the value) and the run exits 2.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SRC = Path.home() / ".claude/projects/C--Users-Snipe-Downloads-Outreach-Program/memory"
DEFAULT_DST = ROOT / "docs/agent-memory/operator"
EXTRA_EXEMPT = frozenset({"README.md"})  # repo-owned files, not copies

EXIT_OK, EXIT_DRIFT, EXIT_SECRET = 0, 1, 2

WIKI_LINK = re.compile(r"\[\[([^\[\]\r\n]+)\]\]")
FRONTMATTER_NAME = re.compile(r"\A---\r?\n(?:[^\r\n]*\r?\n)*?name:[ \t]*(\S[^\r\n]*?)[ \t]*\r?\n")
SECRET_PATTERNS = {
    "openai_key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "github_token": re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    "google_api_key": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    "slack_token": re.compile(r"xox[bap]-"),
    "assigned_secret_run": re.compile(
        r"(?i)(?:token|key|secret)\w*[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9+/_=-]{40,}"
    ),
}


def slug_of(text: str) -> str | None:
    match = FRONTMATTER_NAME.match(text)
    return match.group(1).strip("\"'") if match else None


def secret_hits(text: str) -> list[str]:
    return [name for name, pattern in SECRET_PATTERNS.items() if pattern.search(text)]


def transform(text: str, slug_to_file: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        slug = match.group(1)
        target = slug_to_file.get(slug)
        return f"[{slug}]({target})" if target else f"`{slug}` (not yet written)"

    return WIKI_LINK.sub(replace, text)


def build_copies(src: Path) -> tuple[dict[str, bytes], dict[str, list[str]]]:
    """Return (file name -> transformed bytes, blocked file name -> pattern names)."""
    texts = {p.name: p.read_bytes().decode("utf-8") for p in sorted(src.glob("*.md"))}
    slug_to_file = {slug: name for name, text in texts.items() if (slug := slug_of(text))}
    copies: dict[str, bytes] = {}
    blocked: dict[str, list[str]] = {}
    for name, text in texts.items():
        hits = secret_hits(text)
        if hits:
            blocked[name] = hits
            continue
        copies[name] = transform(text, slug_to_file).encode("utf-8")
    return copies, blocked


def extras_in(dst: Path, src: Path) -> list[str]:
    if not dst.is_dir():
        return []
    source_names = {p.name for p in src.glob("*.md")}
    return sorted(
        p.name for p in dst.glob("*.md") if p.name not in source_names and p.name not in EXTRA_EXEMPT
    )


def report_blocked(blocked: dict[str, list[str]]) -> None:
    for name, hits in blocked.items():
        print(f"secret-scan blocked: {name} ({', '.join(hits)})")


def run_export(src: Path, dst: Path, prune: bool) -> int:
    copies, blocked = build_copies(src)
    dst.mkdir(parents=True, exist_ok=True)
    written = unchanged = 0
    for name, data in copies.items():
        target = dst / name
        if target.is_file() and target.read_bytes() == data:
            unchanged += 1
            continue
        target.write_bytes(data)
        written += 1
    for name in extras_in(dst, src):
        if prune:
            (dst / name).unlink()
            print(f"pruned: {name}")
        else:
            print(f"extra: {name} (kept; --prune deletes)")
    report_blocked(blocked)
    print(f"export: {written} written, {unchanged} unchanged, {len(blocked)} blocked -> {dst}")
    return EXIT_SECRET if blocked else EXIT_OK


def run_check(src: Path, dst: Path) -> int:
    copies, blocked = build_copies(src)
    problems: list[str] = []
    for name, data in copies.items():
        target = dst / name
        if not target.is_file():
            problems.append(f"missing: {name}")
        elif target.read_bytes() != data:
            problems.append(f"drifted: {name}")
    problems.extend(f"extra: {name}" for name in extras_in(dst, src))
    for line in problems:
        print(line)
    report_blocked(blocked)
    if blocked:
        return EXIT_SECRET
    if problems:
        return EXIT_DRIFT
    print(f"in sync ({len(copies)} files)")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--export", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--prune", action="store_true", help="with --export, delete extra destination files")
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC)
    parser.add_argument("--dst", type=Path, default=DEFAULT_DST)
    args = parser.parse_args(argv)
    if not args.src.is_dir():
        print(f"source not found: {args.src}", file=sys.stderr)
        return EXIT_DRIFT
    if args.export:
        return run_export(args.src, args.dst, args.prune)
    return run_check(args.src, args.dst)


if __name__ == "__main__":
    sys.exit(main())
