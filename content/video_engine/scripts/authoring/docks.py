"""The authoring kit - DOCKS: what arrives OVER the world, and the assets it is cut from.

E44: the page is the constant and the pictures arrive over it. A dock is registered by ID with the
render resolver (`build_render_f.STAMPED`, which `find_asset` checks first) and then named in the
shot row. Everything here writes into the BUILD directory the episode hands it, so a side build
never touches the watched one.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

KEYFRAME_EVERY = 12   # frames (0.5 s at 24 fps): a seek decodes at most half a second, never the whole clip
STAGE = (1080, 1920)  # the portrait stage the centred placements are measured on

_X264 = ["-c:v", "libx264", "-profile:v", "high", "-crf", "17", "-preset", "slow"]


def register(aid: str, path: Path | str) -> str:
    """Register an asset id with the render resolver and give the id back, so a shot row can say
    ``register(...)`` inline and stay readable."""
    import build_render_f as R
    R.STAMPED[aid] = str(path)
    return aid


def _keyframed(src: Path, out: Path, extra_vf: str | None, keyframe_every: int) -> Path:
    """One encode, one rule: a keyframe every `keyframe_every` frames so a seek never decodes from
    frame 0 (the originals carry one keyframe in 240 and live playback fell behind and held)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        vf = ["-vf", extra_vf] if extra_vf else []
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-an", *vf, *_X264,
                        "-g", str(keyframe_every), "-keyint_min", str(keyframe_every), "-sc_threshold", "0", "-bf", "0",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], check=True)
    return out


def seekable_clip(name: str, src: Path, build: Path, keyframe_every: int = KEYFRAME_EVERY) -> Path:
    """The source clip re-encoded seekable into ``<build>/clips/<name>``. Same frames, same length;
    written once and reused while the source is unchanged."""
    return _keyframed(Path(src), build / "clips" / name, None, keyframe_every)


def zoom_clip(name: str, src: Path, crop: tuple[int, int, int, int], build: Path,
              keyframe_every: int = KEYFRAME_EVERY) -> Path:
    """A clip ZOOMED on a region (x, y, w, h) of another clip's frame: ffmpeg crops the region and
    scales it back up, keyframed like every other dock clip, so the card is live footage (E49 - the
    steam keeps moving) and not a still lifted out of it."""
    x, y, w, h = crop
    return _keyframed(Path(src), build / "clips" / name,
                      f"crop={w}:{h}:{x}:{y},scale={w * 2}:{h * 2}:flags=lanczos", keyframe_every)


def dock_clip(aid: str, src: Path) -> str:
    """A CLIP as a dock (the video dock, E44): an asset that resolves to an .mp4 becomes a video
    dock in the compiler, so the clip itself is what gets registered."""
    return register(aid, src)


def dock_zoom(aid: str, src: Path, crop: tuple[int, int, int, int], build: Path) -> str:
    """Register a zoomed clip as a VIDEO dock asset."""
    return register(aid, zoom_clip(f"{aid}.mp4", src, crop, build))


def dock_still(aid: str, src: Path, build: Path, still: bool = False,
               frame_crop: tuple[int, int, int, int] | None = None) -> str:
    """A clip docked as itself (the video dock, the default) or - with `still` - as its first frame
    cropped to `frame_crop` (w, h, x, y) and written to ``<build>/docks/``. The still is the
    fallback the video dock replaced; it is kept because a build may still ask for it."""
    src = Path(src)
    if not still:
        return register(aid, src)
    if frame_crop is None:
        raise ValueError(f"{aid}: a still dock needs a frame crop (w, h, x, y)")
    w, h, x, y = frame_crop
    out = build / "docks" / f"{aid}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-frames:v", "1",
                        "-vf", f"crop={w}:{h}:{x}:{y}", str(out)], check=True)
    return register(aid, out)


def still_card(aid: str, src: Path, crop: tuple[float, float], build: Path) -> Path:
    """A still PNG cropped to a CARD - (top, height) as fractions of the still - written to
    ``<build>/docks/<aid>.png``. The card remembers its source and crop in a `.src` stamp beside
    it, so a swapped still or a new crop re-cuts it and nothing else does."""
    src = Path(src)
    out = build / "docks" / f"{aid}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    stamp = out.with_suffix(".src")
    key = f"{src.resolve()}|{crop}"
    if (not out.exists() or out.stat().st_mtime < src.stat().st_mtime
            or (stamp.read_text(encoding="utf-8") if stamp.exists() else "") != key):
        top, h = crop
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", f"crop=iw:ih*{h}:0:ih*{top}", str(out)], check=True)
        stamp.write_text(key, encoding="utf-8")
    return out


def dock_png(aid: str, src: Path, crop: tuple[float, float], build: Path) -> str:
    """`still_card` registered as a dock asset in one call."""
    return register(aid, still_card(aid, src, crop, build))


def chart_card(aid: str, series_file: Path, build: Path, variant: str = "line", aspect: str | None = None) -> str:
    """A CHART CARD (R26-19 / E50): the series object's ledger page rendered once, at its landing,
    by `chart_card.render_card` and registered as a dock still - so a 2-3 s beat can carry a chart
    a fresh page could never land in time, and a page can then grow out of the landed card.
    Rebuilt when the object or the renderer is newer than the card."""
    import chart_card as CC
    series_file = Path(series_file)
    out = build / "docks" / f"{aid}.png"
    if not out.exists() or out.stat().st_mtime < max(series_file.stat().st_mtime, Path(CC.__file__).stat().st_mtime):
        CC.render_card(series_file, out, variant, aspect=aspect)
    return register(aid, out)


def card_aspect(aid: str, build: Path) -> float:
    """The rendered card's h / w, for a centred placement sized to the card (the card must exist)."""
    from PIL import Image
    w, h = Image.open(build / "docks" / f"{aid}.png").size
    return round(h / w, 4)


def still_card_aspect(src: Path, crop: tuple[float, float]) -> float:
    """h / w of a still's card crop, from the still's own size - readable before the card is cut."""
    from PIL import Image
    top_h = crop[1]
    w, h = Image.open(src).size
    return round(top_h * h / w, 4)


def centred_card_point(card_aspect: float, centre_y: float, fx: float, fy: float,
                       centre_w: float | None = None, centre_x: float | None = None,
                       stage: tuple[int, int] = STAGE) -> dict:
    """A POINT target inside a CENTRED dock card. The compiler's `centred_place` with an authored
    centre is deterministic (width `centre_w` of the stage, height by the card's aspect, capped at
    CENTRE_MAX_H), so a fraction (fx, fy) of the card maps to a stage fraction here - a light aims
    at the card the compiler will draw, not at a guess."""
    import build_scene_timeline_f as C
    sw, sh = stage
    w = round((centre_w or C.CENTRE_W) * sw)
    h = round(w * card_aspect)
    if h > C.CENTRE_MAX_H * sh:
        h = round(C.CENTRE_MAX_H * sh)
        w = round(h / card_aspect)
    cx = (centre_x if centre_x is not None else 0.5) * sw
    x0, y0 = max(0, cx - w / 2), max(0, centre_y * sh - h / 2)
    return {"kind": "point", "x": round((x0 + fx * w) / sw, 4), "y": round((y0 + fy * h) / sh, 4)}


def record_words(text: str, t0: float, ws: list[dict], anchor_phrase: str, sync: dict, hl: tuple,
                 per: float = 0.1, tail_per: float = 0.07) -> tuple[list, list, float]:
    """[[word, t], ...] for a RECORD dock (live type on paper, never an image): the words before the
    highlighted phrase type from t0 at `per`, the phrase's own words LAND on the narrator's (the
    take's word starts after `anchor_phrase`, mapped through `sync`), the rest type at `tail_per`.
    Returns the typed words, the highlight range [k0, k1] and the end time."""
    from . import words as W
    toks = text.split()
    i0, _ = W.phrase_start(ws, anchor_phrase)
    narr: dict[str, float] = {}
    for w in ws[i0:i0 + 12]:
        k = w["w"].strip(".,;:!?").lower()
        if k in sync.values() and k not in narr:
            narr[k] = round(float(w["start_s"]), 2)
    out: list = []
    t = t0
    k0 = next(i for i in range(len(toks)) if [x.strip(".,;:!?()").lower() for x in toks[i:i + len(hl)]] == [x.lower() for x in hl])
    k1 = k0 + len(hl) - 1
    for i, w in enumerate(toks):
        key = w.strip(".,;:!?()").lower()
        if k0 <= i <= k1 and key in sync and sync[key] in narr:
            t = max(t, narr[sync[key]])
        out.append([w, round(t, 2)])
        t += per if i < k1 else tail_per
    return out, [k0, k1], round(out[-1][1] + 0.05, 2)


def record_asset(aid: str, build: Path, rgb: tuple[int, int, int] = (22, 24, 28)) -> str:
    """A record dock's placeholder asset: a real 1x1 PNG, because a record is LIVE TYPE and the
    image behind it is never drawn."""
    out = build / "docks" / f"{aid}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        from PIL import Image
        Image.new("RGB", (1, 1), rgb).save(out)
    return register(aid, out)


def meta_set(meta: list[dict], aid: str, key: str, value) -> None:
    """Fill a field on the evidence-dock META entry for `aid` (the record's typed words, a badge)."""
    for m in meta:
        if m["asset"] == aid:
            m[key] = value
