"""Assemble the slide semantic-registration pack for an external model.

Writes a self-contained delivery directory: the slides at full resolution, the
closed claim vocabulary, the taxonomy, a per-slide index carrying the frozen
join keys, and the work order. Nothing in the pack requires repo access.

Run:  python content/video_engine/scripts/build_registration_pack.py <out_dir>
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

P29 = Path(r"C:/Users/Snipe/.codex/worktrees/p29-remotion-console/Outreach Program")
PROJ = P29 / "content/video_engine/projects/systems-and-blowups"
DECKS = PROJ / "sources/decks/teacher-stamped-production-visuals"
LEDGER = PROJ / "pilots/current-bubble-mechanism/claim-ledger.v1.json"
TAXONOMY = PROJ / "asset-taxonomy.v1.json"


def build(out: Path) -> None:
    slides_dir = out / "slides"
    slides_dir.mkdir(parents=True, exist_ok=True)

    manifest = json.loads(
        (DECKS / "teacher-stamped-production-visuals-manifest.v1.json").read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))

    # closed claim vocabulary — id + text so a match is on meaning, not on the slug
    claims = [{"claim_id": c["claim_id"], "text": c["text"],
               "classification": c.get("classification"),
               "as_of": c.get("as_of"),
               "publisher": (c.get("source_locators") or [{}])[0].get("publisher"),
               "source_title": (c.get("source_locators") or [{}])[0].get("title")}
              for c in ledger["claims"]]
    (out / "claim-vocabulary.json").write_text(
        json.dumps({"closed_set": True, "count": len(claims), "claims": claims}, indent=1),
        encoding="utf-8")

    (out / "taxonomy.json").write_text(
        json.dumps({k: v for k, v in taxonomy.items() if isinstance(v, list)}, indent=1),
        encoding="utf-8")

    # per-slide index: frozen join keys the model must copy through untouched
    index, by_deck = [], {}
    for v in manifest["visuals"]:
        if not v.get("evidence_render_eligible"):
            continue
        src = DECKS / v["extracted_path"]
        dst = slides_dir / f'{v["slide_id"]}.png'
        if not dst.exists():
            shutil.copy2(src, dst)
        row = {
            "slide_id": v["slide_id"],
            "deck_id": v["deck_id"],
            "slide_number": v["slide_number"],
            "sha256": v["sha256"],
            "image_file": f'slides/{v["slide_id"]}.png',
            "existing_label": v["context"]["label"],
            "existing_summary": v["context"]["summary"],
        }
        index.append(row)
        by_deck.setdefault(v["deck_id"], []).append(v["slide_id"])

    (out / "slide-index.json").write_text(
        json.dumps({"count": len(index), "decks": {k: len(x) for k, x in by_deck.items()},
                    "slides": index}, indent=1), encoding="utf-8")

    schema = Path(__file__).resolve().parents[1] / "configs/slide_semantic_registration.schema.json"
    shutil.copy2(schema, out / "slide_semantic_registration.schema.json")

    print(f"pack: {out}")
    print(f"  slides    : {len(index)} across {len(by_deck)} decks")
    for d, ids in sorted(by_deck.items()):
        print(f"    {d:36} {len(ids)}")
    print(f"  claims    : {len(claims)} (closed set)")
    print(f"  taxonomy  : {', '.join(f'{k}={len(v)}' for k, v in taxonomy.items() if isinstance(v, list))}")


if __name__ == "__main__":
    build(Path(sys.argv[1] if len(sys.argv) > 1 else "registration-pack"))
