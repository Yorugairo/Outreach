"""Register a review-only finance semantic asset wave and build its contact sheet."""

from __future__ import annotations

import argparse
import hashlib
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
EDIT_ROOT = PILOT / "edit/sentence-native-v1"
WAVE_ROOT = PILOT / "assets/quarantine/sentence-native-wave-01"
MANIFEST = WAVE_ROOT / "wave-01a-review-manifest.v1.json"
CONTACT_SHEET = WAVE_ROOT / "wave-01a-review-contact-sheet.png"

ACCEPTED = [
    {
        "beat_id": "cbm-semantic-beat-01-002",
        "filename": "beat-01-002-memory-stocks-vertical-v1.png",
        "provider_output_filename": "exec-ddeee425-c70a-49d4-a01f-347efbe8ed94.png",
        "semantic_job": "Memory-chip modules become a steep physical skyline while an analyst confronts apparently unbelievable performance.",
    },
    {
        "beat_id": "cbm-semantic-beat-01-003",
        "filename": "beat-01-003-bubble-reflex-v1.png",
        "provider_output_filename": "exec-edd4ea64-3831-4e8d-91c7-cc6aa0625494.png",
        "semantic_job": "Rational investors visibly step backward from a memory-stock bubble before the narration complicates that reflex.",
    },
    {
        "beat_id": "cbm-semantic-beat-01-004",
        "filename": "beat-01-004-factory-capacity-v1.png",
        "provider_output_filename": "exec-43f53b53-1b23-49a3-8b5e-9338a8de6ded.png",
        "semantic_job": "Customers continue arriving while an already-full semiconductor factory cannot expand fast enough.",
    },
    {
        "beat_id": "cbm-semantic-beat-01-006",
        "filename": "beat-01-006-index-safe-default-v2.png",
        "provider_output_filename": "exec-5f2b18a6-777e-43c7-a047-379dc35e275f.png",
        "semantic_job": "Retirement savers calmly feed recurring contributions into a broad multi-sector basket marketed as the safe default.",
    },
]

REJECTED = [
    {
        "beat_id": "cbm-semantic-beat-01-006",
        "filename": "beat-01-006-index-safe-default-rejected-v1.png",
        "provider_output_filename": "exec-b2a2ec53-f789-4e45-a077-3aee7dfd7daa.png",
        "rejection_reasons": [
            "leisure landscape weakens the finance mechanism",
            "certificate markings are not clean deterministic compositor text",
            "the basket is less legible as a multi-sector index than the corrected candidate",
        ],
    }
]

WAVE_DEFINITIONS = {
    "01a": {
        "wave_id": "current-bubble-mechanism-hook-wave-01a",
        "accepted": ACCEPTED,
        "rejected": REJECTED,
    },
    "01b": {
        "wave_id": "current-bubble-mechanism-hook-wave-01b",
        "accepted": [
            {
                "beat_id": "cbm-semantic-beat-01-008",
                "filename": "beat-01-008-automatic-inflow-feedback-v1.png",
                "provider_output_filename": "exec-64ee8ac2-f9af-42a7-96d8-79f94f8b98be.png",
                "semantic_job": "Automatic contributions enter an index basket whose widest pipes route the most capital to the already-largest companies.",
            },
            {
                "beat_id": "cbm-semantic-beat-01-009",
                "filename": "beat-01-009-memory-correction-v1.png",
                "provider_output_filename": "exec-1b574abc-7178-4214-8ca5-ddabf52d2e22.png",
                "semantic_job": "The market price of memory pulls back while the physical factory and outbound shipments remain intact.",
            },
            {
                "beat_id": "cbm-semantic-beat-01-010",
                "filename": "beat-01-010-memory-overpriced-v1.png",
                "provider_output_filename": "exec-5cffde10-de73-4876-9ac9-aa2d139f72ed.png",
                "semantic_job": "Excess bidding raises a memory module on a valuation pedestal far above its underlying productive base.",
            },
            {
                "beat_id": "cbm-semantic-beat-01-011",
                "filename": "beat-01-011-memory-cycle-v1.png",
                "provider_output_filename": "exec-9fda9599-4aef-4915-9882-15a93f04aab9.png",
                "semantic_job": "Memory modules move through a recurring industrial loop of orders, inventory, idle capacity, and restart.",
            },
        ],
        "rejected": [],
    },
    "01c": {
        "wave_id": "current-bubble-mechanism-semantic-wave-01c",
        "accepted": [
            {
                "beat_id": "cbm-semantic-beat-01-012",
                "filename": "beat-01-012-physical-bottleneck-repriced-v1.png",
                "provider_output_filename": "exec-ffd68fa2-a2d9-4838-9deb-a6885f6e072a.png",
                "semantic_job": "Real server demand converges on a narrow physical memory bottleneck where scarce output is repriced.",
            },
            {
                "beat_id": "cbm-semantic-beat-01-013",
                "filename": "beat-01-013-hidden-safe-index-loop-v1.png",
                "provider_output_filename": "exec-63b9d7d1-537a-4f6a-bea3-b1dd12c8ef73.png",
                "semantic_job": "A respectable diversified exterior conceals automatic feedback gears that investors have stopped examining.",
            },
            {
                "beat_id": "cbm-semantic-beat-02-002",
                "filename": "beat-02-002-symptom-not-diagnosis-v1.png",
                "provider_output_filename": "exec-7f94511e-6e44-4352-96b8-69aefe6ad830.png",
                "semantic_job": "A rising price line is separated from the analyst's inspection of the economic mechanism underneath it.",
            },
            {
                "beat_id": "cbm-semantic-beat-02-003",
                "filename": "beat-02-003-next-buyer-belief-v1.png",
                "provider_output_filename": "exec-e4adf70c-429a-4dcc-aee3-73aac7cf2714.png",
                "semantic_job": "A chain of buyers carries the same asset up a fragile staircase because each expects a still-higher buyer.",
            },
        ],
        "rejected": [],
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _review_text(value: str) -> str:
    return (
        value.replace("—", " - ")
        .replace("–", "-")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )


def _make_contact_sheet(rows: list[dict], contact_sheet: Path, wave_name: str) -> None:
    panel_w, panel_h, footer_h = 960, 548, 112
    header_h = 86
    sheet = Image.new("RGB", (panel_w * 2, header_h + (panel_h + footer_h) * 2), "#071827")
    draw = ImageDraw.Draw(sheet)
    title_font = ImageFont.load_default(size=30)
    label_font = ImageFont.load_default(size=22)
    body_font = ImageFont.load_default(size=17)
    draw.text((28, 22), f"P21 SEMANTIC WAVE {wave_name.upper()} - SENTENCE-NATIVE REVIEW", font=title_font, fill="#F5D27A")
    for index, row in enumerate(rows):
        x = (index % 2) * panel_w
        y = header_h + (index // 2) * (panel_h + footer_h)
        with Image.open(ROOT / row["path"]) as source:
            image = ImageOps.fit(source.convert("RGB"), (panel_w, panel_h), method=Image.Resampling.LANCZOS)
        sheet.paste(image, (x, y))
        draw.rectangle((x, y + panel_h, x + panel_w, y + panel_h + footer_h), fill="#0A2033")
        draw.text((x + 22, y + panel_h + 12), row["beat_id"], font=label_font, fill="#F5D27A")
        excerpt = " ".join(textwrap.wrap(_review_text(row["narration_excerpt"]), width=82)[:2])
        timing = f'{row["start_s"]:.3f} to {row["end_s"]:.3f}s  {excerpt}'
        draw.text((x + 22, y + panel_h + 53), timing, font=body_font, fill="#F2E9D2")
    contact_sheet.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(contact_sheet, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", choices=sorted(WAVE_DEFINITIONS), default="01a")
    parser.add_argument("--approve", action="store_true", help="Record operator approval for composition use.")
    args = parser.parse_args()
    definition = WAVE_DEFINITIONS[args.wave]
    manifest_path = WAVE_ROOT / f"wave-{args.wave}-review-manifest.v1.json"
    contact_sheet = WAVE_ROOT / f"wave-{args.wave}-review-contact-sheet.png"
    accepted_review_state = (
        "operator_approved_for_composition" if args.approve else "quarantined_operator_review"
    )
    ledger = json.loads((EDIT_ROOT / "semantic-beat-ledger.v1.json").read_text(encoding="utf-8"))
    prompt_spine = json.loads((EDIT_ROOT / "generation-prompt-spine.v1.json").read_text(encoding="utf-8"))
    beats = {item["beat_id"]: item for item in ledger["beats"]}
    prompts = {item["beat_id"]: item for item in prompt_spine["prompts"]}

    accepted_rows: list[dict] = []
    for asset_definition in definition["accepted"]:
        beat = beats[asset_definition["beat_id"]]
        prompt = prompts[asset_definition["beat_id"]]
        path = WAVE_ROOT / asset_definition["filename"]
        if not path.is_file():
            raise FileNotFoundError(path)
        with Image.open(path) as image:
            width, height = image.size
        accepted_rows.append(
            {
                **asset_definition,
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": _sha256(path),
                "width": width,
                "height": height,
                "prompt_id": prompt["prompt_id"],
                "prompt_spine_artifact_hash": prompt_spine["artifact_hash"],
                "prompt_sha256": hashlib.sha256(prompt["prompt"].encode("utf-8")).hexdigest(),
                "start_word_index": beat["start_word_index"],
                "end_word_index": beat["end_word_index"],
                "start_s": beat["start_s"],
                "end_s": beat["end_s"],
                "narration_excerpt": beat["excerpt"],
                "review_state": accepted_review_state,
                "qa": {
                    "semantic_fit": "pass",
                    "anatomy_and_objects": "pass",
                    "readable_generated_text": "none_observed",
                    "depth_separability": "pass",
                    "adjacent_visual_difference": "pass",
                },
                "render_eligible": args.approve,
                "promotion_eligible": False,
            }
        )

    rejected_rows: list[dict] = []
    for asset_definition in definition["rejected"]:
        path = WAVE_ROOT / asset_definition["filename"]
        if not path.is_file():
            raise FileNotFoundError(path)
        rejected_rows.append(
            {
                **asset_definition,
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": _sha256(path),
                "review_state": "rejected_internal_qa",
                "render_eligible": False,
                "promotion_eligible": False,
            }
        )

    _make_contact_sheet(accepted_rows, contact_sheet, args.wave)
    payload = {
        "schema_version": "finance_sentence_native_asset_wave_review.v1",
        "episode_id": ledger["episode_id"],
        "wave_id": definition["wave_id"],
        "review_state": accepted_review_state,
        "operator_decision": "approved_for_composition" if args.approve else "pending",
        "semantic_beat_ledger_artifact_hash": ledger["artifact_hash"],
        "prompt_spine_artifact_hash": prompt_spine["artifact_hash"],
        "selection_policy": "exact spoken nouns and causal relationship before style; no convenient reuse or filler",
        "contact_sheet_path": contact_sheet.relative_to(ROOT).as_posix(),
        "contact_sheet_sha256": _sha256(contact_sheet),
        "accepted_candidates": accepted_rows,
        "rejected_candidates": rejected_rows,
        "next_wave_authorized": args.approve,
    }
    payload["artifact_hash"] = _artifact_hash(payload)
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(manifest_path.relative_to(ROOT).as_posix())
    print(contact_sheet.relative_to(ROOT).as_posix())
    print(payload["artifact_hash"])


if __name__ == "__main__":
    main()
