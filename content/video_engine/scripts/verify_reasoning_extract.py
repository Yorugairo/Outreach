"""The gate an extraction order proves itself against (P54 T11 retest, 2026-09-13).

The operator, after the ungated reasoning run came back with 13 of 14 invented paths and copied counts: "it's probably
because we didn't force it to gate and proof itself." This is that gate. The extract is JSON lines with three kinds:

    {"kind": "coverage", "id": "<exchange id>", "status": "kept" | "nothing" | "recorded", "anchor": "<path:heading>"}
    {"kind": "item", "rid": "R-001", "title": "...", "logic": "...",
     "evidence": [{"id": "<exchange id>", "quote": "<verbatim, <= 25 words>"}],
     "repo_check": {"terms": ["t1", "t2"], "found": "none" | "partial", "anchor": "<path:heading>"},
     "home": "<existing path[:heading]> | NEW: <proposed path> | ruling candidate | gate candidate | agent memory",
     "confidence": "high" | "medium" | "low"}
    {"kind": "counts", "read": N, "kept": k, "nothing": n, "recorded": r, "items": i}

    python verify_reasoning_extract.py --extract <extract.jsonl> --input <exchanges.jsonl> [--repo-root <dir>] [--no-docs-find]

Exit 0 and a PASS line when every check holds; exit 1 listing each failure. Checks: every input id has exactly one
coverage row and no unknown id appears; `recorded` and `partial` anchors name an existing file whose text contains the
heading's lead; every evidence id is in the input and every quote occurs verbatim (whitespace- and case-folded) in that
exchange, at most 25 words; `found: none` means each of >= 2 terms returns 0 docs_find hits; a home that names a repo
path exists unless it says NEW:; nothing cites the operator-ledger triage or an earlier reasoning run; the counts equal
the rows; every `kept` coverage id is evidence for at least one item.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FORBIDDEN = ("docs/operator-ledger/TRIAGE", "docs/research/runs/operator-reasoning/REASONING-EXTRACT",
             "docs/research/runs/operator-reasoning/REVIEW")
STATUSES = ("kept", "nothing", "recorded")
HITS = re.compile(r"(\d+) hit\(s\)")


def fold(s: str) -> str:
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def anchor_ok(anchor: str, root: Path) -> str:
    """'' when `path[:heading]` names an existing file containing the heading's lead, else why not."""
    a = str(anchor or "").strip()
    if not a:
        return "empty anchor"
    path, _, head = a.partition(":")
    p = root / path.strip()
    if not path.strip() or not p.is_file():
        return f"path does not exist: {path.strip()!r}"
    lead = re.split(r"\s[(—-]\s?|\s\(", head.strip(), maxsplit=1)[0].strip().lstrip("#").strip()
    if lead and fold(lead)[:40] not in fold(p.read_text(encoding="utf-8", errors="ignore")):
        return f"heading {lead[:50]!r} not found in {path.strip()}"
    return ""


def docs_find_hits(term: str, root: Path) -> int:
    r = subprocess.run([sys.executable, str(root / "content/video_engine/scripts/docs_find.py"), term],
                       cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = HITS.search(r.stdout + r.stderr)
    return int(m.group(1)) if m else -1


def verify(extract: Path, inp: Path, root: Path, use_docs_find: bool = True) -> list[str]:
    ex = {}
    for line in inp.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            ex[r["id"]] = fold(str(r.get("operator", "")) + " \n " + str(r.get("agent", "")))
    rows = []
    fails: list[str] = []
    for n, line in enumerate(extract.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except ValueError as exc:
            fails.append(f"line {n}: not JSON ({exc})")
    raw = extract.read_text(encoding="utf-8")
    for bad in FORBIDDEN:
        if bad in raw:
            fails.append(f"cites a forbidden source: {bad}")
    cov = [r for r in rows if r.get("kind") == "coverage"]
    items = [r for r in rows if r.get("kind") == "item"]
    counts = [r for r in rows if r.get("kind") == "counts"]
    # coverage
    seen: dict[str, int] = {}
    for r in cov:
        seen[r.get("id")] = seen.get(r.get("id"), 0) + 1
        if r.get("id") not in ex:
            fails.append(f"coverage: unknown id {r.get('id')!r}")
        if r.get("status") not in STATUSES:
            fails.append(f"coverage {r.get('id')}: bad status {r.get('status')!r}")
        if r.get("status") == "recorded":
            why = anchor_ok(r.get("anchor", ""), root)
            if why:
                fails.append(f"coverage {r.get('id')} recorded: {why}")
    missing = [i for i in ex if i not in seen]
    if missing:
        fails.append(f"coverage: {len(missing)} input id(s) have no coverage row (first: {missing[:5]})")
    dup = [i for i, c in seen.items() if c > 1]
    if dup:
        fails.append(f"coverage: {len(dup)} id(s) covered more than once (first: {dup[:5]})")
    # items
    evidence_ids: set[str] = set()
    for it in items:
        rid = it.get("rid", "?")
        ev = it.get("evidence") or []
        if not ev:
            fails.append(f"{rid}: no evidence")
        for e in ev:
            eid, q = e.get("id"), str(e.get("quote", ""))
            evidence_ids.add(eid)
            if eid not in ex:
                fails.append(f"{rid}: evidence id {eid!r} not in the input")
                continue
            if len(q.split()) > 25:
                fails.append(f"{rid}: quote over 25 words")
            if not q.strip() or fold(q) not in ex[eid]:
                fails.append(f"{rid}: quote not verbatim in exchange {eid}: {q[:60]!r}")
        rc = it.get("repo_check") or {}
        terms = [t for t in rc.get("terms") or [] if str(t).strip()]
        if len(terms) < 2:
            fails.append(f"{rid}: repo_check needs >= 2 terms")
        if rc.get("found") == "none":
            if use_docs_find:
                for t in terms:
                    h = docs_find_hits(t, root)
                    if h != 0:
                        fails.append(f"{rid}: repo_check says not found but docs_find {t!r} returns {h} hit(s)")
        elif rc.get("found") == "partial":
            why = anchor_ok(rc.get("anchor", ""), root)
            if why:
                fails.append(f"{rid}: partial anchor: {why}")
        else:
            fails.append(f"{rid}: repo_check.found must be 'none' or 'partial'")
        home = str(it.get("home", "")).strip()
        if re.match(r"^(docs|content|\.agents|\.claude)/", home):
            why = anchor_ok(home if ":" in home else home + ":", root)
            if why.startswith("path does not exist"):
                fails.append(f"{rid}: home {why} (prefix a proposed new file with 'NEW: ')")
        if it.get("confidence") not in ("high", "medium", "low"):
            fails.append(f"{rid}: confidence must be high|medium|low")
    kept_ids = [r.get("id") for r in cov if r.get("status") == "kept"]
    orphan = [i for i in kept_ids if i not in evidence_ids]
    if orphan:
        fails.append(f"coverage: {len(orphan)} 'kept' id(s) are evidence for no item (first: {orphan[:5]})")
    # counts
    if len(counts) != 1:
        fails.append(f"expected exactly one counts row, found {len(counts)}")
    else:
        c = counts[0]
        want = {"read": len(cov), "kept": len(kept_ids), "items": len(items),
                "nothing": sum(1 for r in cov if r.get("status") == "nothing"),
                "recorded": sum(1 for r in cov if r.get("status") == "recorded")}
        for k, v in want.items():
            if c.get(k) != v:
                fails.append(f"counts.{k} = {c.get(k)} but the rows give {v}")
        if want["read"] != len(ex):
            fails.append(f"read {want['read']} of {len(ex)} input exchanges")
    return fails


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--extract", type=Path, required=True)
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    ap.add_argument("--no-docs-find", action="store_true", help="skip the docs_find calls (tests)")
    a = ap.parse_args(argv)
    fails = verify(a.extract, a.input, a.repo_root, not a.no_docs_find)
    for f in fails[:60]:
        print("FAIL", f)
    if fails:
        print(f"verify_reasoning_extract: FAIL - {len(fails)} problem(s)")
        return 1
    print("verify_reasoning_extract: PASS - coverage complete, every quote verbatim, every path real, counts match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
