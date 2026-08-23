"""Build P32 Gate B crops and explanatory-illustration review packet.

The script derives crops from immutable teacher-stamped parent slides.  It
intentionally does not register them as production evidence: Gate B is the
operator's context/crop decision, and generated items remain explanatory only.
"""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
DECK_ROOT = ROOT / "content/video_engine/projects/systems-and-blowups/sources/decks"
SOURCES_PATH = DECK_ROOT / "deck-sources.v2.json"
COVERAGE_PATH = PROJECT / "edit/evidence-coverage-v1/full-episode-evidence-coverage.v1.json"
OUTPUT_DIR = PROJECT / "edit/evidence-coverage-v1/gate-b-review-v1"
CROP_DIR = OUTPUT_DIR / "crops"
GENERATED_DIR = OUTPUT_DIR / "generated"

GENERATED_CANDIDATES = (
    {
        "asset_id": "passive-index-feedback-loop-illustration-candidate-v1",
        "path": "generated/passive-index-feedback-loop-illustration-candidate-v1.png",
        "story_need": "Illustrate automatic capital-flow feedback while the index-concentration mechanism is discussed.",
        "permitted_use": "Explanatory illustration only; it carries no factual claim, metric, source citation, or literal evidence status.",
        "target_range": "S&P 500 mechanism scenes, subject to later semantic-binding review.",
    },
    {
        "asset_id": "capacity-reservations-illustration-candidate-v1",
        "path": "generated/capacity-reservations-illustration-candidate-v1.png",
        "story_need": "Illustrate buyer commitments consuming open capacity while contracts/reservations are discussed.",
        "permitted_use": "Explanatory illustration only; it carries no factual claim, metric, source citation, or literal evidence status.",
        "target_range": "Contracts and capacity scenes, subject to later semantic-binding review.",
    },
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _crop_parent(deck_id: str, slide_number: int) -> Path:
    path = DECK_ROOT / "teacher-stamped-production-visuals" / deck_id / "slides" / f"slide-{slide_number:03d}.png"
    if not path.is_file():
        raise FileNotFoundError(f"Missing approved parent slide: {path}")
    return path


def _cue_candidates(coverage: dict[str, Any], asset_id: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for cue in coverage["cues"]:
        for candidate in cue.get("candidate_evidence", []):
            if candidate["asset_id"] == asset_id:
                matches.append({
                    "cue_id": cue["cue_id"],
                    "scene_id": cue["scene_id"],
                    "start_s": cue["start_s"],
                    "end_s": cue["end_s"],
                    "excerpt": cue["excerpt"],
                    "match_basis": candidate["match_basis"],
                })
    return matches


def _crop(source: Path, bbox_norm: list[float], target: Path) -> dict[str, int]:
    with Image.open(source) as image:
        width, height = image.size
        x, y, crop_width, crop_height = bbox_norm
        left = max(0, min(width - 1, round(x * width)))
        top = max(0, min(height - 1, round(y * height)))
        right = max(left + 1, min(width, round((x + crop_width) * width)))
        bottom = max(top + 1, min(height, round((y + crop_height) * height)))
        target.parent.mkdir(parents=True, exist_ok=True)
        image.crop((left, top, right, bottom)).save(target, format="PNG", optimize=True)
    return {"left": left, "top": top, "right": right, "bottom": bottom, "width": right - left, "height": bottom - top}


def _render_html(crops: list[dict[str, Any]], generated: list[dict[str, Any]]) -> str:
    def crop_card(item: dict[str, Any]) -> str:
        cue_text = "<br>".join(
            f"{html.escape(candidate['cue_id'])} · {candidate['start_s']:.1f}s — {html.escape(candidate['excerpt'])}"
            for candidate in item["cue_candidates"][:4]
        ) or "No direct current candidate; manual semantic review required."
        return f"""<article class=\"card source\">
<img src=\"{html.escape(item['path'])}\" alt=\"{html.escape(item['asset_id'])}\">
<h2>{html.escape(item['asset_id'])}</h2>
<p><strong>Source:</strong> {html.escape(item['deck_id'])} · slide {item['slide_number']}</p>
<p><strong>What it is:</strong> {html.escape(item['what_it_is'])}</p>
<p><strong>Does not prove:</strong> {html.escape(' '.join(item['not_what_it_means']))}</p>
<p><strong>Candidate cues:</strong><br>{cue_text}</p>
<p class=\"status\">REVIEW CROP — NOT YET RENDER-ELIGIBLE</p>
</article>"""

    def generated_card(item: dict[str, Any]) -> str:
        return f"""<article class=\"card generated\">
<img src=\"{html.escape(item['path'])}\" alt=\"{html.escape(item['asset_id'])}\">
<h2>{html.escape(item['asset_id'])}</h2>
<p><strong>Story use:</strong> {html.escape(item['story_need'])}</p>
<p><strong>Permitted use:</strong> {html.escape(item['permitted_use'])}</p>
<p><strong>Target:</strong> {html.escape(item['target_range'])}</p>
<p class=\"status\">GENERATED EXPLANATORY ILLUSTRATION — NOT LITERAL EVIDENCE</p>
</article>"""

    return f"""<!doctype html><html><head><meta charset=\"utf-8\"><title>P32 Gate B crop and illustration review</title>
<style>body{{background:#101922;color:#f5f1e7;font-family:Inter,Arial,sans-serif;margin:0;padding:32px}}h1{{margin:0 0 8px}}.lead{{max-width:1000px;color:#c7d2d7;line-height:1.5}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:20px;margin-top:20px}}.card{{background:#172532;border:1px solid #335062;border-radius:12px;overflow:hidden;padding:14px}}.card.generated{{border-color:#9b6b35}}img{{width:100%;height:220px;object-fit:contain;background:#f4ecdc;border-radius:7px}}h2{{font-size:16px;overflow-wrap:anywhere}}p{{font-size:14px;line-height:1.42;color:#d6dfdf}}.status{{font-weight:700;color:#ffcc82;font-size:12px;letter-spacing:.04em}}</style></head><body>
<h1>P32 — Gate B: Crop + explanatory illustration review</h1>
<p class=\"lead\">Approve a crop only for its stated parent slide, context, and cue range. Generated items below are explanatory visual candidates only; they do not substantiate narration or replace source evidence.</p>
<h2>Existing deck crops ({len(crops)})</h2><section class=\"grid\">{''.join(crop_card(item) for item in crops)}</section>
<h2>Generated explanatory candidates ({len(generated)})</h2><section class=\"grid\">{''.join(generated_card(item) for item in generated)}</section>
</body></html>"""


def main() -> None:
    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    deck_titles = {deck["deck_id"]: deck["title"] for deck in sources["decks"]}
    crops: list[dict[str, Any]] = []
    for crop in sources["crops"]:
        parent = _crop_parent(crop["deck_id"], crop["slide_number"])
        output = CROP_DIR / f"{crop['asset_id']}.png"
        pixels = _crop(parent, list(crop["bbox_norm"]), output)
        crops.append({
            **crop,
            "deck_title": deck_titles[crop["deck_id"]],
            "path": output.relative_to(OUTPUT_DIR).as_posix(),
            "parent_path": parent.relative_to(ROOT).as_posix(),
            "parent_sha256": _sha256(parent),
            "crop_sha256": _sha256(output),
            "pixel_bounds": pixels,
            "cue_candidates": _cue_candidates(coverage, crop["asset_id"]),
        })
    generated: list[dict[str, Any]] = []
    for candidate in GENERATED_CANDIDATES:
        path = OUTPUT_DIR / candidate["path"]
        if not path.is_file():
            raise FileNotFoundError(f"Generated candidate was not staged: {path}")
        generated.append({**candidate, "sha256": _sha256(path), "evidence_state": "illustration_candidate", "render_eligible": False})
    manifest = {
        "schema_version": "p32_gate_b_review.v1", "coverage_hash": coverage["artifact_hash"],
        "approval_boundary": "Review only. No item is promoted or render-eligible from this packet.",
        "crops": crops, "generated_illustration_candidates": generated,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "review-manifest.v1.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "crop-and-illustration-review.html").write_text(_render_html(crops, generated), encoding="utf-8")
    print(OUTPUT_DIR / "crop-and-illustration-review.html")
    print(f"crops={len(crops)} generated={len(generated)}")


if __name__ == "__main__":
    main()
