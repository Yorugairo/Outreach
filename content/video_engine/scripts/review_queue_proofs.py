"""THE REVIEW QUEUE'S PROOFS - a clip of the seconds that matter, a crop on what changed (E99 s14).

An item reaches the operator only with a proof framed for a viewer. This file makes the two proofs the page cannot copy:

  (a) CLIPS - an mp4 of a window of a player, captured the way render_baseline captures a golden frame (headless
      Chromium seeks #scrub to t and screenshots #stage) but in ONE browser across the window, piped to ffmpeg. The
      source is either a golden surface (`surface` + `flags`, instantiated from tests/golden/sources/) or a served-form
      build directory (`build` + `page`). Silent; written to `content/video_engine/review/queue/clips/` (gitignored).
  (b) CROPS - the bounding box of the pixels that differ between a before and an after frame, plus a margin, with the
      caption strip excluded: a pair that differs only inside the caption box is refused (it proves nothing).

    python content/video_engine/scripts/review_queue_proofs.py --clips [--only ITEM_ID] [--force]
    python content/video_engine/scripts/review_queue_proofs.py --confirm      # GET every player proof, print the codes

Clip rendering is slow (seconds per clip-second), so the builder never renders; it shows a rendered clip and marks a
missing one. Crops are cheap and deterministic, so the builder writes them at every --write.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

DATA_REL = "docs/content-video-engine/review-queue.v1.json"
CLIPS_REL = "content/video_engine/review/queue/clips"
CLIP_FPS = 15
CLIP_WIDTH = {"16:9": 960, "9:16": 720}   # the page shows a clip at card width; the full stage costs only bytes
DIFF_THRESHOLD = 16                        # a channel difference below this is encoder / antialias noise
CROP_MARGIN = 32


class NoVisibleChange(ValueError):
    """A before / after pair whose only difference is inside the caption box (or nowhere): not a proof."""


# ---------------------------------------------------------------- crops

def diff_box(before, after, caption_box=None, margin: int = CROP_MARGIN, threshold: int = DIFF_THRESHOLD):
    """The (x0, y0, x1, y1) box, grown by `margin` and clamped to the frame, holding every pixel that differs between
    two same-size images outside `caption_box` ([x0, y0, x1, y1] or None). Refuses a pair with no such pixel."""
    from PIL import Image, ImageChops, ImageDraw
    a = before if isinstance(before, Image.Image) else Image.open(before)
    b = after if isinstance(after, Image.Image) else Image.open(after)
    a, b = a.convert("RGB"), b.convert("RGB")
    if a.size != b.size:
        raise ValueError(f"the pair is not the same size: {a.size} vs {b.size}")
    diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v >= threshold else 0)
    if caption_box:
        ImageDraw.Draw(diff).rectangle([caption_box[0], caption_box[1], caption_box[2] - 1, caption_box[3] - 1], fill=0)
    box = diff.getbbox()
    if box is None:
        where = "outside the caption box" if caption_box else "anywhere"
        raise NoVisibleChange(f"the frames do not differ {where}: not a proof")
    w, h = a.size
    return (max(0, box[0] - margin), max(0, box[1] - margin), min(w, box[2] + margin), min(h, box[3] + margin))


def crop_names(item_id: str, n: int) -> tuple[str, str]:
    return f"{item_id}-{n}-before.png", f"{item_id}-{n}-after.png"


def crop_box(proof: dict, root: Path) -> tuple[int, int, int, int]:
    """The box of one crop proof. Raises NoVisibleChange for a caption-only pair."""
    return diff_box(root / proof["before"], root / proof["after"], proof.get("caption_box"))


def write_crop(proof: dict, item_id: str, n: int, root: Path, crops_dir: Path) -> tuple[int, int, int, int]:
    """Write the before / after crops of one crop proof; return the box."""
    from PIL import Image
    box = crop_box(proof, root)
    crops_dir.mkdir(parents=True, exist_ok=True)
    for rel, name in zip((proof["before"], proof["after"]), crop_names(item_id, n)):
        Image.open(root / rel).convert("RGB").crop(box).save(crops_dir / name, format="PNG", optimize=False)
    return box


# ---------------------------------------------------------------- clips

def clip_name(item_id: str, n: int) -> str:
    return f"{item_id}-{n}.mp4"


def clip_proofs(data: dict, only: str | None = None) -> list[tuple[dict, int, dict]]:
    out = []
    for item in data["items"]:
        if only and item["id"] != only:
            continue
        for n, proof in enumerate(item.get("proofs") or []):
            if proof.get("type") == "clip":
                out.append((item, n, proof))
    return out


def _clip_source(proof: dict, tmp: Path) -> tuple[Path, str, str]:
    """(the directory to serve, the page name, the aspect) for a golden surface or a built player."""
    import render_baseline as RB
    if proof.get("surface"):
        tl, uris, _t, aspect = RB.load_surface(proof["surface"])
        if proof.get("flags"):
            tl = dict(tl, kinetics=proof["flags"])
        page = "surface.html"
        (tmp / page).write_text(RB.instantiate(tl, uris), encoding="utf-8")
        return tmp, page, aspect
    return ROOT / proof["build"], proof.get("page", "player.html"), proof.get("aspect", "16:9")


CLIP_KEYS = ("surface", "build", "page", "aspect", "t0", "t1", "flags", "mp4")


def clip_source_sha(proof: dict, root: Path = ROOT) -> str | None:
    """The bytes the clip is rendered FROM: a golden surface's base frame, or a build's player page. An engine change
    re-lays the same surface under the same window - 2026-09-16 the verdict card's clip kept the old rails - so the sha of
    the rendered source is part of what a clip is. None when the source is not on disk (the fixture's surfaces)."""
    import hashlib
    if proof.get("mp4"):
        p = root / proof["mp4"]                      # an mp4 already on disk - a composed comparison, an ambient-lane render
    elif proof.get("surface"):
        p = root / "content/video_engine/tests/golden/frames" / f"{proof['surface']}.png"
        # a surface's MOTION lives in the engine, not in its base frame: T7c's gather left verdict-stack-9x16.png
        # byte-identical and the old clip was served as current - so the engine's bytes are part of the key too
        engine = root / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
        if p.is_file() and engine.is_file():
            h = hashlib.sha256(p.read_bytes()); h.update(engine.read_bytes())
            return h.hexdigest()
    elif proof.get("build"):
        p = root / proof["build"] / (proof.get("page") or "player.html")
    else:
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def clip_key(proof: dict, root: Path = ROOT) -> dict:
    """What a clip IS: its source, its window, and the bytes of the source it was rendered from. A clip on disk is
    current only if its sidecar carries this key - 2026-09-16 a card's proofs were rewritten and the old clip kept
    serving under the same name; the same night a re-laid surface kept its old clip under the same window."""
    key = {k: proof.get(k) for k in CLIP_KEYS if proof.get(k) is not None}
    sha = clip_source_sha(proof, root)
    if sha:
        key["source_sha256"] = sha
    return key


def clip_sidecar(out_mp4: Path) -> Path:
    return out_mp4.with_suffix(out_mp4.suffix + ".json")


def clip_is_current(proof: dict, out_mp4: Path) -> bool:
    """The mp4 exists AND its sidecar names the same source and window."""
    side = clip_sidecar(out_mp4)
    if not out_mp4.is_file() or not side.is_file():
        return False
    try:
        return json.loads(side.read_text(encoding="utf-8")) == clip_key(proof)
    except ValueError:
        return False


def render_clip(proof: dict, out_mp4: Path) -> Path:
    """Capture [t0, t1) at CLIP_FPS from one browser and encode a silent H.264 mp4 at card width."""
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    t0, t1 = float(proof["t0"]), float(proof["t1"])
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    if proof.get("mp4"):   # already rendered elsewhere (E99 s38's three-way proof): the queue carries it as it is
        import shutil
        src = ROOT / proof["mp4"]
        if not src.is_file():
            raise FileNotFoundError(f"clip proof names an mp4 that is not on disk: {proof['mp4']}")
        shutil.copyfile(src, out_mp4)
        return out_mp4
    with tempfile.TemporaryDirectory() as td:
        directory, page_name, aspect = _clip_source(proof, Path(td))
        w, h = RB.STAGE[aspect]
        srv, port = RB.serve(directory)
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(CLIP_FPS),
                               "-c:v", "png", "-i", "-", "-vf", f"scale={CLIP_WIDTH[aspect]}:-2:flags=lanczos",
                               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24", "-preset", "medium",
                               "-movflags", "+faststart", str(out_mp4)], stdin=subprocess.PIPE)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/{page_name}", wait_until="networkidle", timeout=180000)
                RB.prepare_page(page, w, h)
                for i in range(int(round((t1 - t0) * CLIP_FPS))):
                    ff.stdin.write(RB.frame_png(page, round(t0 + i / CLIP_FPS, 4), (w, h)))
                browser.close()
        finally:
            ff.stdin.close()
            code = ff.wait()
            srv.shutdown()
        if code != 0:
            raise RuntimeError(f"ffmpeg failed ({code}) writing {out_mp4}")
    return out_mp4


# ---------------------------------------------------------------- players

def url_answers(url: str, timeout: float = 3.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as res:
            return 200 <= res.status < 400
    except (urllib.error.URLError, OSError, ValueError):
        return False


def player_urls(data: dict) -> list[str]:
    return sorted({p["url"] for i in data["items"] for p in (i.get("proofs") or []) if p.get("type") == "player"})


# ---------------------------------------------------------------- cli

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--clips", action="store_true", help="render every clip proof that is not on disk")
    mode.add_argument("--confirm", action="store_true", help="GET every player proof and print whether it answers")
    ap.add_argument("--only", help="one item id")
    ap.add_argument("--force", action="store_true", help="re-render clips that exist")
    ap.add_argument("--data", type=Path, default=ROOT / DATA_REL)
    ap.add_argument("--clips-dir", type=Path, default=ROOT / CLIPS_REL)
    args = ap.parse_args(argv)
    data = json.loads(args.data.read_text(encoding="utf-8"))
    if args.confirm:
        bad = 0
        for url in player_urls(data):
            ok = url_answers(url)
            bad += not ok
            print(f"{'answers' if ok else 'NO ANSWER'}: {url}")
        return 1 if bad else 0
    for item, n, proof in clip_proofs(data, args.only):
        out = args.clips_dir / clip_name(item["id"], n)
        if clip_is_current(proof, out) and not args.force:
            print(f"have  {out.name}")
            continue
        why = "stale" if out.is_file() else "clip"
        print(f"{why:5s} {out.name}: {proof.get('surface') or proof.get('build') or proof.get('mp4')} {proof['t0']}-{proof['t1']} s", flush=True)
        render_clip(proof, out)
        clip_sidecar(out).write_text(json.dumps(clip_key(proof), sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
