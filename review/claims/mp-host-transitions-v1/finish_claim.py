"""Stages B-D of the work order, on whatever clips landed: derive exits by reversal, cut
first/mid/last frames, tile the contact sheet, write the manifest and the approvals
skeleton. Judging is left as a column for the operator; `approved` stays EMPTY.

    python review/claims/mp-host-transitions-v1/finish_claim.py
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw

CLAIM = Path(r"C:/Users/Snipe/Downloads/Outreach Program/review/claims/mp-host-transitions-v1")
CLIPS = CLAIM / "clips"
FRAMES = CLAIM / "frames"
CREDITS_PER_CLIP = 10          # measured: Omni 1.1 Flash, x1, 6s, 720p (2026-09-03)
CHANNEL = "money-physics"

PLATE_BY_ID = {
    "host-enter-signal-box-dusk": ("world-signal-box-dusk-v1", "actor-host-point-right-v1"),
    "host-enter-korea-port": ("world-korea-port-v1", "actor-host-present-open-v1"),
    "host-enter-memory-fab-floor": ("world-memory-fab-floor-v1", "actor-host-explain-both-hands-v1"),
    "host-enter-seoul-fab-skyline": ("world-seoul-fab-skyline-v1", "actor-host-arms-crossed-v1"),
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def duration_s(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.0


def frame(src: Path, t: float, dst: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1", str(dst)], check=True)


def main() -> int:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("ffmpeg/ffprobe not on PATH"); return 2
    enters = sorted(p for p in CLIPS.glob("host-enter-*.mp4") if "-raw" not in p.stem and "-reversed" not in p.stem)
    if not enters:
        print("no host-enter-*.mp4 in clips/ yet"); return 1
    FRAMES.mkdir(exist_ok=True)

    assets, rows = [], []
    for enter in enters:
        world = enter.stem.replace("host-enter-", "")
        exit_ = CLIPS / f"host-exit-{world}.mp4"
        if not exit_.exists():   # Stage B: one generation -> two assets
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(enter), "-vf", "reverse", "-af", "areverse", str(exit_)], check=True)
        for clip, kind_tag, handoff in ((enter, "host-enter", "first"), (exit_, "host-exit", "last")):
            d = duration_s(clip)
            trio = []
            for tag, t in (("first", 0.05), ("mid", d / 2), ("last", max(d - 0.08, 0))):
                f = FRAMES / f"{clip.stem}-{tag}.png"
                frame(clip, t, f)
                trio.append(f)
            rows.append((clip.stem, trio))
            plate, pose = PLATE_BY_ID.get(enter.stem, ("?", "?"))
            assets.append({
                "asset_id": clip.stem, "path": f"clips/{clip.name}", "sha256": sha(clip),
                "kind": "transition_clip", "semantic": f"{kind_tag}:{world}", "channel": CHANNEL,
                "duration_s": round(d, 2), "handoff_frame": handoff, "derived": kind_tag == "host-exit",
                "generated_from": {"plate": plate, "pose": pose, "model": "Omni 1.1 Flash", "count": 1,
                                   "resolution": "720p", "credits": 0 if kind_tag == "host-exit" else CREDITS_PER_CLIP},
                "judge": {"verdict": "", "note": ""},
            })

    # Stage C: contact sheet - one row per clip, first | mid | last, labelled
    W, H, PAD, LBL = 480, 270, 12, 28
    sheet = Image.new("RGB", (3 * W + 4 * PAD, len(rows) * (H + LBL + PAD) + PAD), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    for r, (name, trio) in enumerate(rows):
        y = PAD + r * (H + LBL + PAD)
        draw.text((PAD, y + 6), name, fill=(235, 225, 200))
        for c, f in enumerate(trio):
            im = Image.open(f).convert("RGB").resize((W, H))
            sheet.paste(im, (PAD + c * (W + PAD), y + LBL))
    sheet_path = CLAIM / "contact-sheet.png"
    sheet.save(sheet_path)

    # Stage D: manifest + approvals skeleton
    (CLAIM / "mp-host-transitions-v1.manifest.json").write_text(json.dumps({
        "schema_version": "review_manifest.v1", "status": "review_only", "render_eligible": False,
        "channel": CHANNEL, "style_family": "woodblock-vox-newsprint-v2", "source_prompt": "claim:mp-host-transitions-v1",
        "generated_on": str(date.today()), "assets": assets,
    }, indent=2), encoding="utf-8")
    ap = CLAIM / "approvals.json"
    if not ap.exists():
        ap.write_text(json.dumps({
            "judge": "", "credits_per_clip": CREDITS_PER_CLIP, "generations": len(enters),
            "credits_spent": CREDITS_PER_CLIP * len(enters), "approved": [], "rejected": [], "notes": "",
        }, indent=2), encoding="utf-8")
    print(f"clips: {len(enters)} enters + {len(enters)} derived exits | sheet: {sheet_path} | manifest written | approved: [] (operator)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
