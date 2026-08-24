"""Validate returned slide-registration documents before ingest.

Structural checks only — it cannot confirm that a transcribed numeral really
appears in an image. What it CAN do is reject every failure mode that would
silently corrupt the join: invented claim ids, altered join keys, semantic ids
that do not encode their own claim, duplicate aliases, missing slides.

Run:  python content/video_engine/scripts/validate_slide_registration.py <pack_dir>
Exit 0 = ingestible. Exit 1 = one or more documents rejected.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

SEMANTIC_ID = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*\.(evidence|context|countercase)"
    r"\.(chart|table|diagram|timeline|quote|photo|composite)-v\d+$")
NUMERIC = re.compile(r"\d")


def validate(pack: Path) -> int:
    index = json.loads((pack / "slide-index.json").read_text(encoding="utf-8"))
    vocab = json.loads((pack / "claim-vocabulary.json").read_text(encoding="utf-8"))
    taxonomy = json.loads((pack / "taxonomy.json").read_text(encoding="utf-8"))

    by_id = {s["slide_id"]: s for s in index["slides"]}
    claim_ids = {c["claim_id"] for c in vocab["claims"]}
    tax_terms = {axis: set(vals) for axis, vals in taxonomy.items()}

    docs = sorted(pack.glob("registration.*.json"))
    if not docs:
        print("FAIL: no registration.*.json documents found")
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    seen_semantic: Counter = Counter()
    registered: set[str] = set()
    figure_count = 0
    unmatched = 0
    low_conf: list[str] = []

    for doc_path in docs:
        doc = json.loads(doc_path.read_text(encoding="utf-8"))
        tag = doc_path.name
        if doc.get("schema_version") != "slide_semantic_registration.v1":
            errors.append(f"{tag}: wrong schema_version {doc.get('schema_version')!r}")
        deck = doc.get("deck_id", "")

        for row in doc.get("slides", []):
            sid = row.get("slide_id", "<missing>")
            ref = by_id.get(sid)
            where = f"{tag}/{sid}"

            if ref is None:
                errors.append(f"{where}: slide_id not in slide-index.json")
                continue
            registered.add(sid)
            if ref["deck_id"] != deck:
                errors.append(f"{where}: belongs to deck {ref['deck_id']}, filed under {deck}")
            if row.get("sha256") != ref["sha256"]:
                errors.append(f"{where}: sha256 altered — the wrong image was read")

            refs = row.get("claim_refs", [])
            bad = [c for c in refs if c not in claim_ids]
            if bad:
                errors.append(f"{where}: claim ids outside the closed set: {bad}")
            if not refs:
                unmatched += 1
                if not row.get("unmatched_reason"):
                    errors.append(f"{where}: empty claim_refs without unmatched_reason")

            sem = row.get("semantic_id", "")
            if not SEMANTIC_ID.match(sem):
                errors.append(f"{where}: semantic_id malformed: {sem!r}")
            else:
                head = sem.split(".", 1)[0]
                expect = refs[0] if refs else "unregistered"
                if head != expect:
                    errors.append(
                        f"{where}: semantic_id claim segment {head!r} != claim_refs[0] {expect!r}")
                seen_semantic[sem] += 1

            for axis, vals in (row.get("taxonomy") or {}).items():
                unknown = [v for v in vals if v not in tax_terms.get(axis, set())]
                if unknown:
                    errors.append(f"{where}: taxonomy.{axis} terms not in vocabulary: {unknown}")

            for fig in row.get("figures", []):
                figure_count += 1
                val = fig.get("value", "")
                if not NUMERIC.search(val):
                    errors.append(f"{where}: figure value has no digits: {val!r}")
                if val != val.strip():
                    errors.append(f"{where}: figure value has surrounding whitespace: {val!r}")
                if re.fullmatch(r"0\.\d+", val):
                    warnings.append(f"{where}: {val!r} looks normalised from a percentage")
                if fig.get("is_headline") and not fig.get("label"):
                    errors.append(f"{where}: headline figure without a label")

            if row.get("confidence") == "low":
                low_conf.append(sid)

    for sem, n in seen_semantic.items():
        if n > 1:
            errors.append(f"duplicate semantic_id used {n}x: {sem}")

    missing = sorted(set(by_id) - registered)
    if missing:
        errors.append(f"{len(missing)} slide(s) never registered: {missing[:6]}"
                      + (" ..." if len(missing) > 6 else ""))

    print(f"documents      : {len(docs)}")
    print(f"slides         : {len(registered)}/{len(by_id)}")
    print(f"figures        : {figure_count}")
    print(f"unmatched      : {unmatched} (empty claim_refs with a stated reason)")
    print(f"low confidence : {len(low_conf)}{' -> ' + ', '.join(low_conf[:8]) if low_conf else ''}")
    for w in warnings:
        print(f"  warn: {w}")
    if errors:
        print(f"\nREJECTED — {len(errors)} error(s):")
        for e in errors[:40]:
            print(f"  {e}")
        if len(errors) > 40:
            print(f"  ... and {len(errors) - 40} more")
        return 1
    print("\nPASS — ingestible")
    return 0


if __name__ == "__main__":
    sys.exit(validate(Path(sys.argv[1] if len(sys.argv) > 1 else "registration-pack")))
