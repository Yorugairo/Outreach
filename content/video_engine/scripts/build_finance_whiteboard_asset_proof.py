"""Stage and render the isolated HyperFrames whiteboard asset proof.

The builder owns only deterministic local inputs: the approved P24 narration
window, its word map/claim ledger, and two operator-supplied PDFs. It does not
call a provider or rewrite factual text inside a source card.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image


REPO = Path(__file__).resolve().parents[3]
PILOT = REPO / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
PROOF_ID = "finance-whiteboard-asset-blend-proof-v1"
PROOF_ROOT = PILOT / PROOF_ID
ASSET_ROOT = PROOF_ROOT / "assets"
SOURCE_ROOT = PROOF_ROOT / "source"
REVIEW_ROOT = PROOF_ROOT / "review"
RENDER_ROOT = PROOF_ROOT / "render"

REALITY_PDF = Path("C:/Users/Snipe/Downloads/The_Silicon_Reality_Gap.pdf")
ANTIDOTE_PDF = Path("C:/Users/Snipe/Downloads/The_Silicon_Antidote.pdf")
CANONICAL_AUDIO = PILOT / "audio/canonical/history_episode_1_master.mp3"
CANONICAL_WORDS = PILOT / "audio/canonical/history_episode_1_master.words.json"
P24_WORDS = PILOT / "finance-stealth-wealth-proof-v1/source/canonical.words.json"
P24_NARRATION = PILOT / "finance-stealth-wealth-proof-v1/source/narration.locked.md"
P24_LEDGER = PILOT / "finance-stealth-wealth-proof-v1/source/claim-ledger.v1.json"
HAND_ASSET = PROOF_ROOT / "assets/draw-hand-a-v1.png"

DURATION_S = 18.0
SOURCE_START_S = 0.0
SOURCE_END_S = 18.0
DELIVERY_FPS = 24
AUTHORING = {"width": 1920, "height": 1080, "fps": DELIVERY_FPS}
REVIEW = {"width": 1280, "height": 720, "fps": DELIVERY_FPS, "label": "review"}
HAND_NIB = {
    "source_px": {"x": 432, "y": 1369},
    "display_px": {"x": 135, "y": 428},
    "display_size_px": {"width": 320, "height": 480},
    "asset": "generated hand cutout; chroma-key removed",
}

EXPECTED_PDF_HASHES = {
    REALITY_PDF.name: "157cdfa87fd58bc92f84a479ba617033df7923c7297e0a6741e813e46744d5fb",
    ANTIDOTE_PDF.name: "f77536dd8123f9c5ff3cc4cc674a6e65117ecbdb0bf1982e8593098bf6ba244f",
}

# Crop coordinates are normalized to the source PDF page. Keeping these in the
# manifest makes every staged card reproducible and reviewable.
SOURCE_CARDS = [
    {
        "id": "valuation-paradox",
        "pdf": REALITY_PDF,
        "page": 1,
        "crop": (0.02, 0.05, 0.52, 0.94),
        "asset_name": "valuation-paradox.png",
        "start_s": 0.0,
        "end_s": 2.4,
        "caption": "The market may be labeling the wrong bubble.",
        "locator": "The Silicon Reality Gap.pdf, p.1, left valuation-paradox panel",
    },
    {
        "id": "capacity-penalty",
        "pdf": REALITY_PDF,
        "page": 9,
        "crop": (0.02, 0.04, 0.98, 0.96),
        "asset_name": "capacity-penalty.png",
        "start_s": 2.4,
        "end_s": 11.6,
        "caption": "AI memory stocks have gone vertical. That is normally where sensible people step back and say: bubble.",
        "locator": "The Silicon Reality Gap.pdf, p.9, three-to-one capacity penalty panel",
    },
    {
        "id": "physical-antidote",
        "pdf": ANTIDOTE_PDF,
        "page": 15,
        "crop": (0.02, 0.05, 0.98, 0.94),
        "asset_name": "physical-antidote.png",
        "start_s": 11.6,
        "end_s": 18.0,
        "caption": "But underneath the chart is a product customers cannot get enough of.",
        "locator": "The Silicon Antidote.pdf, p.15, physical-antidote closing panel",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)


def verify_source_inputs() -> dict[str, Any]:
    for path in (REALITY_PDF, ANTIDOTE_PDF, CANONICAL_AUDIO, CANONICAL_WORDS, P24_WORDS, P24_NARRATION, P24_LEDGER, HAND_ASSET):
        require_file(path)

    pdf_hashes = {path.name: sha256(path) for path in (REALITY_PDF, ANTIDOTE_PDF)}
    if pdf_hashes != EXPECTED_PDF_HASHES:
        raise RuntimeError(f"PDF hash mismatch: {pdf_hashes}")

    words_payload = json.loads(P24_WORDS.read_text(encoding="utf-8"))
    if words_payload.get("duration_s") != 105.0 or words_payload.get("source_word_start") != 0:
        raise RuntimeError("P24 canonical word window is not the approved 105-second source")
    if words_payload.get("source_sha256") != sha256(CANONICAL_WORDS):
        raise RuntimeError("P24 word-map source hash does not match canonical words")

    ledger_payload = json.loads(P24_LEDGER.read_text(encoding="utf-8"))
    if not ledger_payload.get("source_of_record") or not ledger_payload.get("claims"):
        raise RuntimeError("P24 claim ledger is missing its source-of-record contract")

    return {
        "pdf_hashes": pdf_hashes,
        "audio_sha256": sha256(CANONICAL_AUDIO),
        "canonical_words_sha256": sha256(CANONICAL_WORDS),
        "p24_words_sha256": sha256(P24_WORDS),
        "p24_narration_sha256": sha256(P24_NARRATION),
        "p24_claim_ledger_sha256": sha256(P24_LEDGER),
        "hand_asset_sha256": sha256(HAND_ASSET),
        "source_window": {
            "start_s": SOURCE_START_S,
            "end_s": SOURCE_END_S,
            "duration_s": DURATION_S,
            "word_start_index": 0,
            "word_end_index": next(
                (index for index, word in enumerate(words_payload["words"]) if word["end_s"] > SOURCE_END_S),
                len(words_payload["words"]) - 1,
            ),
        },
    }


def pdftoppm_path() -> Path:
    candidates = [
        Path("C:/Users/Snipe/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe"),
        Path(shutil.which("pdftoppm") or ""),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("pdftoppm.exe is required to stage PDF-derived cards")


def render_page(pdf: Path, page: int, staging_dir: Path) -> Path:
    staging_dir.mkdir(parents=True, exist_ok=True)
    output_prefix = staging_dir / f"{pdf.stem}-p{page}"
    output_path = output_prefix.with_suffix(".png")
    if not output_path.is_file():
        subprocess.run(
            [str(pdftoppm_path()), "-png", "-r", "144", "-f", str(page), "-l", str(page), "-singlefile", str(pdf), str(output_prefix)],
            check=True,
            capture_output=True,
            text=True,
        )
    return output_path


def stage_cards() -> list[dict[str, Any]]:
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    staging_dir = PROOF_ROOT / ".pdf-pages"
    staged: list[dict[str, Any]] = []
    for card in SOURCE_CARDS:
        page_path = render_page(card["pdf"], card["page"], staging_dir)
        with Image.open(page_path) as source:
            left, top, right, bottom = card["crop"]
            crop_box = (
                round(source.width * left),
                round(source.height * top),
                round(source.width * right),
                round(source.height * bottom),
            )
            output_path = ASSET_ROOT / card["asset_name"]
            source.crop(crop_box).convert("RGB").save(output_path, optimize=True)
            staged.append(
                {
                    "id": card["id"],
                    "path": f"assets/{card['asset_name']}",
                    "sha256": sha256(output_path),
                    "source_pdf": card["pdf"].name,
                    "source_pdf_sha256": EXPECTED_PDF_HASHES[card["pdf"].name],
                    "page": card["page"],
                    "crop_normalized": list(card["crop"]),
                    "crop_px": list(crop_box),
                    "source_locator": card["locator"],
                    "text_owner": "supplied source card",
                    "render_state": "proof_only",
                    "start_s": card["start_s"],
                    "end_s": card["end_s"],
                    "caption": card["caption"],
                }
            )
    return staged


def stage_project(source_receipts: dict[str, Any]) -> dict[str, Any]:
    for directory in (SOURCE_ROOT, REVIEW_ROOT, RENDER_ROOT):
        directory.mkdir(parents=True, exist_ok=True)
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CANONICAL_AUDIO, ASSET_ROOT / "history_episode_1_master.mp3")
    shutil.copy2(P24_WORDS, SOURCE_ROOT / "canonical.words.json")
    shutil.copy2(P24_NARRATION, SOURCE_ROOT / "narration.locked.md")
    shutil.copy2(P24_LEDGER, SOURCE_ROOT / "claim-ledger.v1.json")
    cards = stage_cards()

    write_json(PROOF_ROOT / "source-binding.v1.json", {
        "schema_version": "finance_whiteboard_source_binding.v1",
        "proof_id": PROOF_ID,
        "source_receipts": source_receipts,
        "cards": cards,
        "asset_policy": "source-bound cards retain page/crop context; no factual text rewritten",
    })
    manifest = {
        "schema_version": "finance_whiteboard_asset_blend_manifest.v1",
        "proof_id": PROOF_ID,
        "renderer": "hyperframes:html-gsap",
        "duration_s": DURATION_S,
        "delivery_fps": DELIVERY_FPS,
        "authoring_profile": AUTHORING,
        "render_profile": REVIEW,
        "canonical_audio": {"path": "assets/history_episode_1_master.mp3", "start_s": 0.0, "duration_s": DURATION_S, "volume": 1.0},
        "hand": {"path": "assets/draw-hand-a-v1.png", "sha256": source_receipts["hand_asset_sha256"], "nib": HAND_NIB},
        "source_window": source_receipts["source_window"],
        "cards": cards,
        "provider_calls": 0,
        "generated_assets": [],
        "status": "inputs_staged",
    }
    write_json(PROOF_ROOT / "proof-manifest.v1.json", manifest)
    return manifest


def command(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(list(args), cwd=cwd, check=True)


def render_project(manifest: dict[str, Any]) -> None:
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for HyperFrames rendering")
    command(npx, "--yes", "hyperframes@0.7.104", "check", cwd=PROOF_ROOT)
    authoring_output = RENDER_ROOT / "hf-authoring.mp4"
    output = RENDER_ROOT / "finance-whiteboard-asset-blend-proof.mp4"
    command(npx, "--yes", "hyperframes@0.7.104", "render", "-o", str(authoring_output), cwd=PROOF_ROOT)
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        raise RuntimeError("ffprobe and ffmpeg are required for the review packet")
    command(
        ffmpeg,
        "-y",
        "-i",
        str(authoring_output),
        "-vf",
        "scale=1280:720:flags=lanczos",
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(output),
    )
    probe = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output)], check=True, capture_output=True, text=True)
    metadata = json.loads(probe.stdout)
    boundaries = REVIEW_ROOT / "boundaries"
    boundaries.mkdir(parents=True, exist_ok=True)
    for index, timestamp in enumerate((0.0, 0.5, 5.9, 6.0, 6.5, 11.9, 12.0, 12.5, 17.9)):
        target = boundaries / f"boundary-{index + 1:02d}-{timestamp:05.1f}s.png"
        command(ffmpeg, "-y", "-ss", f"{timestamp:.3f}", "-i", str(output), "-frames:v", "1", "-update", "1", str(target))
    manifest["status"] = "review_render_complete"
    manifest["render"] = {
        "path": str(output.relative_to(PROOF_ROOT)).replace("\\", "/"),
        "authoring_path": str(authoring_output.relative_to(PROOF_ROOT)).replace("\\", "/"),
        "sha256": sha256(output),
        "ffprobe": metadata,
        "boundary_dir": str(boundaries.relative_to(PROOF_ROOT)).replace("\\", "/"),
    }
    write_json(PROOF_ROOT / "proof-manifest.v1.json", manifest)
    write_json(REVIEW_ROOT / "watch-review-draft.v1.json", {
        "schema_version": "watch_review_draft.v1",
        "proof_id": PROOF_ID,
        "status": "draft",
        "review_required": True,
        "render_path": str(output.relative_to(PROOF_ROOT)).replace("\\", "/"),
        "checks": [
            "source card text remains readable",
            "one semantic asset is active at a time",
            "marker reveal does not expose later cards early",
            "recurring character remains face-readable",
            "the result reads as whiteboard/2D rather than a static infographic",
        ],
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", action="store_true", help="run HyperFrames check/render and create boundary frames")
    args = parser.parse_args()
    receipts = verify_source_inputs()
    manifest = stage_project(receipts)
    if args.render:
        render_project(manifest)
    print(json.dumps({"proof_root": str(PROOF_ROOT), "status": manifest.get("status", "inputs_staged"), "duration_s": DURATION_S}, indent=2))


if __name__ == "__main__":
    main()
