"""Build the isolated P27 code-assisted whiteboard proof.

The proof keeps the P24 audio clock and P26 hand calibration, but generates
finished isolated PNG artblocks locally with Pillow. HyperFrames only controls
when each finished element appears through the whiteboard reveal masks.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from PIL import Image, ImageDraw, ImageOps


REPO = Path(__file__).resolve().parents[3]
PILOT = REPO / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
PROOF_ID = "finance-whiteboard-code-drawn-proof-v1"
PROOF_ROOT = PILOT / PROOF_ID
ASSET_ROOT = PROOF_ROOT / "assets"
ART_ROOT = ASSET_ROOT / "art"
SOURCE_ROOT = PROOF_ROOT / "source"
REVIEW_ROOT = PROOF_ROOT / "review"
RENDER_ROOT = PROOF_ROOT / "render"

CANONICAL_AUDIO = PILOT / "audio/canonical/history_episode_1_master.mp3"
CANONICAL_WORDS = PILOT / "audio/canonical/history_episode_1_master.words.json"
P24_WORDS = PILOT / "finance-stealth-wealth-proof-v1/source/canonical.words.json"
P24_NARRATION = PILOT / "finance-stealth-wealth-proof-v1/source/narration.locked.md"
P24_LEDGER = PILOT / "finance-stealth-wealth-proof-v1/source/claim-ledger.v1.json"
HAND_SOURCE = PILOT / "finance-whiteboard-asset-blend-proof-v1/assets/draw-hand-a-v1.png"
HAND_ASSET = ASSET_ROOT / "draw-hand-a-v1.png"
HAND_B_ASSET = ASSET_ROOT / "draw-hand-b-v1.png"

DURATION_S = 18.0
DELIVERY_FPS = 24
AUTHORING = {"width": 1920, "height": 1080, "fps": DELIVERY_FPS}
REVIEW = {"width": 1280, "height": 720, "fps": DELIVERY_FPS, "label": "review"}
HAND_NIB = {
    "a": {"x": 135, "y": 428},
    "b": {"x": 185, "y": 428},
    "display_size_px": {"width": 320, "height": 480},
    "asset": "P26 draw-A mirrored deterministically for draw-B",
}


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
    for path in (CANONICAL_AUDIO, CANONICAL_WORDS, P24_WORDS, P24_NARRATION, P24_LEDGER, HAND_SOURCE):
        require_file(path)
    words_payload = json.loads(P24_WORDS.read_text(encoding="utf-8"))
    canonical_words_payload = json.loads(CANONICAL_WORDS.read_text(encoding="utf-8"))
    if words_payload.get("duration_s") != 105.0 or words_payload.get("source_word_start") != 0:
        raise RuntimeError("P24 canonical word window is not the approved 105-second source")
    if words_payload.get("source_sha256") != sha256(CANONICAL_WORDS):
        raise RuntimeError("P24 word-map source hash does not match canonical words")
    if not canonical_words_payload.get("words"):
        raise RuntimeError("canonical words receipt is empty")
    ledger_payload = json.loads(P24_LEDGER.read_text(encoding="utf-8"))
    if not ledger_payload.get("source_of_record") or not ledger_payload.get("claims"):
        raise RuntimeError("P24 claim ledger is missing its source-of-record contract")
    return {
        "audio_sha256": sha256(CANONICAL_AUDIO),
        "canonical_words_sha256": sha256(CANONICAL_WORDS),
        "p24_words_sha256": sha256(P24_WORDS),
        "p24_narration_sha256": sha256(P24_NARRATION),
        "p24_claim_ledger_sha256": sha256(P24_LEDGER),
        "hand_source_sha256": sha256(HAND_SOURCE),
        "source_window": {
            "start_s": 0.0,
            "end_s": DURATION_S,
            "duration_s": DURATION_S,
            "word_start_index": 0,
            "word_end_index": next(
                (i for i, word in enumerate(canonical_words_payload["words"]) if word["end_s"] > DURATION_S),
                len(canonical_words_payload["words"]) - 1,
            ),
        },
    }


def line(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], fill: str, width: int = 10) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")


def hatch(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, step: int = 18, width: int = 3) -> None:
    left, top, right, bottom = box
    for offset in range(-bottom, right - left, step):
        draw.line((left + max(0, offset), top + max(0, -offset), min(right, left + offset + (bottom - top)), bottom - max(0, offset)), fill=fill, width=width)


def bubble_art() -> Image.Image:
    image = Image.new("RGBA", (900, 560), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((155, 72, 665, 478), fill="#c94f47", outline="#252525", width=12)
    draw.ellipse((182, 103, 638, 447), outline="#e88776", width=5)
    hatch(draw, (180, 98, 640, 455), "#8f3736", 24, 3)
    draw.arc((215, 118, 330, 220), 198, 315, fill="#f4b099", width=9)
    draw.arc((235, 130, 350, 232), 198, 315, fill="#f4b099", width=4)
    line(draw, [(405, 474), (404, 520), (376, 544), (435, 544), (404, 520)], "#252525", 8)
    draw.ellipse((386, 515, 422, 547), fill="#c94f47", outline="#252525", width=6)
    line(draw, [(670, 230), (768, 182), (822, 212)], "#252525", 9)
    line(draw, [(802, 195), (825, 212), (797, 226)], "#252525", 9)
    return image


def valuation_tag_art() -> Image.Image:
    image = Image.new("RGBA", (520, 300), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    points = [(55, 80), (430, 35), (470, 230), (95, 270)]
    draw.polygon(points, fill="#f1d48a", outline="#252525")
    line(draw, [(70, 96), (432, 53)], "#d1a65d", 4)
    hatch(draw, (85, 78, 436, 242), "#c99c59", 22, 2)
    draw.ellipse((83, 128, 122, 167), fill="white", outline="#252525", width=6)
    return image


def arrow_art() -> Image.Image:
    image = Image.new("RGBA", (520, 280), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    points = [(55, 120), (330, 120), (330, 72), (460, 140), (330, 208), (330, 160), (55, 160)]
    draw.polygon(points, fill="#d26455", outline="#252525")
    line(draw, [(76, 145), (318, 145)], "#f3aa87", 5)
    return image


def memory_stack_art() -> Image.Image:
    image = Image.new("RGBA", (980, 580), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for x in (80, 310, 540):
        draw.rounded_rectangle((x, 100, x + 190, 210), radius=18, fill="#6f9ebd", outline="#252525", width=9)
        draw.rectangle((x + 24, 126, x + 64, 185), fill="#314f68", outline="#252525", width=4)
        draw.rectangle((x + 86, 126, x + 164, 185), fill="#4f728d", outline="#252525", width=4)
        for pad in range(0, 6):
            draw.rectangle((x + 12 + pad * 28, 204, x + 25 + pad * 28, 232), fill="#c99c59", outline="#252525", width=2)
    draw.rounded_rectangle((170, 300, 810, 480), radius=22, fill="#7898ad", outline="#252525", width=12)
    for y in (325, 370, 415):
        line(draw, [(205, y), (775, y)], "#b6d0d5", 7)
    for x in range(230, 780, 58):
        line(draw, [(x, 310), (x, 470)], "#476b7d", 4)
    draw.rectangle((355, 268, 625, 305), fill="#d26455", outline="#252525", width=8)
    line(draw, [(375, 286), (602, 286)], "#f4b099", 5)
    return image


def capacity_arrow_art() -> Image.Image:
    image = Image.new("RGBA", (540, 300), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    points = [(40, 130), (330, 130), (330, 75), (500, 150), (330, 225), (330, 170), (40, 170)]
    draw.polygon(points, fill="#6f9ebd", outline="#252525")
    line(draw, [(70, 150), (314, 150)], "#b6d0d5", 6)
    return image


def price_spike_art() -> Image.Image:
    image = Image.new("RGBA", (820, 500), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    line(draw, [(105, 420), (105, 80)], "#252525", 10)
    line(draw, [(105, 420), (735, 420)], "#252525", 10)
    bars = [(170, 330, 255, 420), (300, 275, 385, 420), (430, 196, 515, 420), (560, 110, 645, 420)]
    for index, box in enumerate(bars):
        color = "#6f9ebd" if index < 2 else "#d26455"
        draw.rectangle(box, fill=color, outline="#252525", width=8)
        hatch(draw, box, "#334f61" if index < 2 else "#8f3736", 20, 3)
    line(draw, [(130, 350), (220, 310), (340, 270), (470, 200), (610, 112), (720, 78)], "#252525", 12)
    line(draw, [(680, 92), (720, 78), (700, 122)], "#252525", 10)
    return image


def magnifier_art() -> Image.Image:
    image = Image.new("RGBA", (760, 560), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((70, 65, 480, 475), fill="#c94f47", outline="#252525", width=12)
    hatch(draw, (92, 88, 457, 455), "#8f3736", 22, 3)
    draw.ellipse((250, 110, 585, 445), fill="#d8e6e3", outline="#252525", width=14)
    draw.ellipse((283, 143, 552, 412), fill="#80b6c2", outline="#314f68", width=10)
    draw.ellipse((318, 178, 517, 377), fill="#fffdf8", outline="#252525", width=7)
    hatch(draw, (322, 182, 514, 374), "#9db9bc", 20, 2)
    line(draw, [(510, 405), (700, 520)], "#252525", 30)
    line(draw, [(523, 418), (700, 520)], "#c99c59", 9)
    return image


def memory_lock_art() -> Image.Image:
    image = Image.new("RGBA", (760, 540), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((120, 120, 645, 460), radius=28, fill="#4e9a78", outline="#252525", width=14)
    draw.ellipse((205, 180, 560, 535), fill="#68b58e", outline="#252525", width=10)
    draw.ellipse((280, 255, 485, 460), fill="#2f725d", outline="#252525", width=9)
    draw.arc((322, 176, 443, 330), 180, 360, fill="#252525", width=22)
    draw.rectangle((300, 280, 465, 412), fill="#f1d48a", outline="#252525", width=9)
    draw.ellipse((372, 323, 394, 350), fill="#252525")
    line(draw, [(383, 350), (383, 385)], "#252525", 8)
    for x, y in ((150, 155), (615, 155), (150, 425), (615, 425)):
        draw.ellipse((x - 16, y - 16, x + 16, y + 16), fill="#f1d48a", outline="#252525", width=5)
    hatch(draw, (136, 136, 630, 444), "#2f725d", 28, 3)
    return image


def factory_art() -> Image.Image:
    image = Image.new("RGBA", (700, 380), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((75, 160, 625, 320), fill="#d9c8a2", outline="#252525", width=10)
    draw.polygon([(75, 160), (220, 75), (365, 160)], fill="#c99c59", outline="#252525")
    draw.rectangle((130, 65, 178, 160), fill="#7c8e8d", outline="#252525", width=8)
    draw.rectangle((470, 95, 522, 160), fill="#7c8e8d", outline="#252525", width=8)
    for x in (125, 260, 395, 530):
        draw.rectangle((x, 210, x + 58, 320), fill="#6f9ebd", outline="#252525", width=7)
        draw.rectangle((x + 15, 235, x + 43, 266), fill="#fffdf8", outline="#252525", width=4)
    hatch(draw, (85, 170, 615, 309), "#a98d64", 22, 3)
    return image


ART_BUILDERS: dict[str, Callable[[], Image.Image]] = {
    "bubble": bubble_art,
    "valuation-tag": valuation_tag_art,
    "arrow": arrow_art,
    "memory-stack": memory_stack_art,
    "capacity-arrow": capacity_arrow_art,
    "price-spike": price_spike_art,
    "magnifier": magnifier_art,
    "memory-lock": memory_lock_art,
    "factories": factory_art,
}

ART_LAYOUT = [
    {"id": "bubble", "file": "bubble.png", "width": 900, "height": 560, "x": 560, "y": 315, "rect": [-90, -90, 990, 650], "sw": 180, "start_s": 0.22, "duration_s": 0.78},
    {"id": "valuation-tag", "file": "valuation-tag.png", "width": 520, "height": 300, "x": 1290, "y": 350, "rect": [-80, -80, 600, 380], "sw": 150, "start_s": 0.92, "duration_s": 0.42},
    {"id": "arrow", "file": "arrow.png", "width": 520, "height": 280, "x": 760, "y": 640, "rect": [-80, -80, 600, 360], "sw": 150, "start_s": 1.43, "duration_s": 0.38},
    {"id": "memory-stack", "file": "memory-stack.png", "width": 980, "height": 580, "x": 270, "y": 310, "rect": [-90, -90, 1070, 670], "sw": 180, "start_s": 2.58, "duration_s": 1.2},
    {"id": "capacity-arrow", "file": "capacity-arrow.png", "width": 540, "height": 300, "x": 1040, "y": 520, "rect": [-80, -80, 620, 380], "sw": 160, "start_s": 4.06, "duration_s": 0.45},
    {"id": "price-spike", "file": "price-spike.png", "width": 820, "height": 500, "x": 865, "y": 290, "rect": [-90, -90, 910, 590], "sw": 180, "start_s": 5.05, "duration_s": 1.18},
    {"id": "factories", "file": "factories.png", "width": 700, "height": 380, "x": 375, "y": 645, "rect": [-80, -80, 780, 460], "sw": 150, "start_s": 8.5, "duration_s": 0.95},
    {"id": "magnifier", "file": "magnifier.png", "width": 760, "height": 560, "x": 335, "y": 325, "rect": [-90, -90, 850, 650], "sw": 180, "start_s": 11.88, "duration_s": 0.98},
    {"id": "memory-lock", "file": "memory-lock.png", "width": 760, "height": 540, "x": 1080, "y": 355, "rect": [-90, -90, 850, 630], "sw": 180, "start_s": 13.78, "duration_s": 1.18},
]


def stage_art() -> list[dict[str, Any]]:
    ART_ROOT.mkdir(parents=True, exist_ok=True)
    coverage_root = REVIEW_ROOT / "coverage"
    coverage_root.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    for spec in ART_LAYOUT:
        output = ART_ROOT / spec["file"]
        image = ART_BUILDERS[spec["id"]]()
        image.save(output, optimize=True)
        coverage_image = Image.new("RGBA", image.size, "white")
        coverage_image.alpha_composite(image.convert("RGBA"))
        coverage_image.convert("RGB").save(coverage_root / spec["file"], optimize=True)
        entries.append({**spec, "path": f"assets/art/{spec['file']}", "sha256": sha256(output), "art_mode": "code-assisted detailed raster with transparent surround"})
    chunks = [
        {
            "image": str(coverage_root / spec["file"]),
            "rect": [-spec["sw"], -80, spec["width"] + spec["sw"], spec["height"] + 80],
            "sw": spec["sw"],
        }
        for spec in ART_LAYOUT
    ]
    write_json(REVIEW_ROOT / "chunks.json", chunks)
    return entries


def stage_hand() -> None:
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HAND_SOURCE, HAND_ASSET)
    with Image.open(HAND_ASSET) as source:
        ImageOps.mirror(source).save(HAND_B_ASSET, optimize=True)


def write_contact_sheet(arts: list[dict[str, Any]]) -> None:
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    cards = []
    for art in arts:
        cards.append(f'<figure><img src="../{html.escape(art["path"])}" alt="{html.escape(art["id"])} artblock"><figcaption>{html.escape(art["id"])}</figcaption></figure>')
    REVIEW_ROOT.joinpath("contact-sheet.html").write_text(
        "<!doctype html><meta charset=\"utf-8\"><title>P27 art contact sheet</title>"
        "<style>body{margin:0;padding:32px;background:#f5efe2;color:#252525;font:16px Georgia,serif}main{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}figure{margin:0;background:#fffdf8;border:2px solid #252525;padding:12px}img{width:100%;height:190px;object-fit:contain;background:white}figcaption{padding-top:8px;text-transform:uppercase;letter-spacing:.12em;font:12px Segoe Print, sans-serif}</style>"
        f"<main>{''.join(cards)}</main>\n",
        encoding="utf-8",
    )


def stage_project(source_receipts: dict[str, Any]) -> dict[str, Any]:
    for directory in (SOURCE_ROOT, REVIEW_ROOT, RENDER_ROOT):
        directory.mkdir(parents=True, exist_ok=True)
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CANONICAL_AUDIO, ASSET_ROOT / "history_episode_1_master.mp3")
    shutil.copy2(P24_WORDS, SOURCE_ROOT / "canonical.words.json")
    shutil.copy2(P24_NARRATION, SOURCE_ROOT / "narration.locked.md")
    shutil.copy2(P24_LEDGER, SOURCE_ROOT / "claim-ledger.v1.json")
    stage_hand()
    arts = stage_art()
    write_contact_sheet(arts)
    manifest = {
        "schema_version": "finance_whiteboard_code_drawn_manifest.v1",
        "proof_id": PROOF_ID,
        "renderer": "hyperframes:html-gsap",
        "duration_s": DURATION_S,
        "delivery_fps": DELIVERY_FPS,
        "authoring_profile": AUTHORING,
        "render_profile": REVIEW,
        "canonical_audio": {"path": "assets/history_episode_1_master.mp3", "start_s": 0.0, "duration_s": DURATION_S, "volume": 1.0},
        "word_map": {"path": "source/canonical.words.json", "source_sha256": source_receipts["canonical_words_sha256"], "timing_source": "verified P24 Whisper word receipt"},
        "hand": {"a_path": "assets/draw-hand-a-v1.png", "b_path": "assets/draw-hand-b-v1.png", "source_sha256": source_receipts["hand_source_sha256"], "nib": HAND_NIB},
        "art": arts,
        "provider_calls": 0,
        "pdf_assets": [],
        "source_window": source_receipts["source_window"],
        "status": "inputs_staged",
    }
    write_json(PROOF_ROOT / "source-binding.v1.json", {"schema_version": "finance_whiteboard_code_drawn_binding.v1", "proof_id": PROOF_ID, "source_receipts": source_receipts, "art": arts, "asset_policy": "one finished isolated local artblock per semantic drawable"})
    write_json(PROOF_ROOT / "proof-manifest.v1.json", manifest)
    return manifest


def command(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(list(args), cwd=cwd, check=True)


def render_project(manifest: dict[str, Any]) -> None:
    coverage = Path("C:/Users/Snipe/.codex/skills/whiteboard-explainer/scripts/coverage-check.py")
    command(sys.executable, str(coverage), str(REVIEW_ROOT / "chunks.json"))
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for HyperFrames rendering")
    command(npx, "--yes", "hyperframes@0.7.104", "check", cwd=PROOF_ROOT)
    authoring_output = RENDER_ROOT / "hf-authoring.mp4"
    output = RENDER_ROOT / "finance-whiteboard-code-drawn-proof.mp4"
    command(npx, "--yes", "hyperframes@0.7.104", "render", "-o", str(authoring_output), cwd=PROOF_ROOT)
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        raise RuntimeError("ffprobe and ffmpeg are required for the review packet")
    command(ffmpeg, "-y", "-i", str(authoring_output), "-vf", "scale=1280:720:flags=lanczos", "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output))
    probe = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output)], check=True, capture_output=True, text=True)
    metadata = json.loads(probe.stdout)
    boundaries = REVIEW_ROOT / "boundaries"
    boundaries.mkdir(parents=True, exist_ok=True)
    for index, timestamp in enumerate((0.0, 0.5, 5.9, 6.0, 6.5, 11.9, 12.0, 12.5, 17.9)):
        target = boundaries / f"boundary-{index + 1:02d}-{timestamp:05.1f}s.png"
        command(ffmpeg, "-y", "-ss", f"{timestamp:.3f}", "-i", str(output), "-frames:v", "1", "-update", "1", str(target))
    manifest["status"] = "review_render_complete"
    manifest["render"] = {"path": str(output.relative_to(PROOF_ROOT)).replace("\\", "/"), "authoring_path": str(authoring_output.relative_to(PROOF_ROOT)).replace("\\", "/"), "sha256": sha256(output), "ffprobe": metadata, "boundary_dir": str(boundaries.relative_to(PROOF_ROOT)).replace("\\", "/")}
    write_json(PROOF_ROOT / "proof-manifest.v1.json", manifest)
    write_json(REVIEW_ROOT / "watch-review-draft.v1.json", {"schema_version": "watch_review_draft.v1", "proof_id": PROOF_ID, "status": "draft", "review_required": True, "render_path": str(output.relative_to(PROOF_ROOT)).replace("\\", "/"), "checks": ["each artblock is isolated and fully covered", "hand writes labels and rides every active reveal", "plate remains stable with no camera drift", "no PDF/card image is visible in the composition", "the result reads as drawn whiteboard art rather than a pasted print"]})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", action="store_true", help="run HyperFrames check/render and create audit artifacts")
    args = parser.parse_args()
    receipts = verify_source_inputs()
    manifest = stage_project(receipts)
    if args.render:
        render_project(manifest)
    print(json.dumps({"proof_root": str(PROOF_ROOT), "status": manifest.get("status", "inputs_staged"), "duration_s": DURATION_S}, indent=2))


if __name__ == "__main__":
    main()
