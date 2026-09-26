"""P71 T24 - the re-value's beats PROVED AS BEATS (E99 s60): A48 (the golden's then -> now), R28
`recipe:revalue-then-the-ratio` (the re-value, then the bracket to its neighbour with the multiple) and R30
`recipe:ranked-dim-the-rest` (the ranked field rises and holds, one bar keeps its ink while the rest dim, its pill, then
a second pill) - each a private test-bed beat on a committed Steel and Paper object (values READ off the series files,
never re-typed), served with the repo's own engine and shot at named instants, with one contact sheet per beat.

    python content/video_engine/projects/_proofs/p71-recipes/proof_t24.py              # all three into build-lab-t24/
    python content/video_engine/projects/_proofs/p71-recipes/proof_t24.py --out <dir> r28 r30

It writes only inside `build-lab-t24/` beside this file (gitignored) or the named --out; nothing in the project moves.
The beats are test-bed beats (their timing is the page's own build clock, not a take's words): no approved cut
carries either recipe, so both stay candidates with a zero count."""
from __future__ import annotations

import copy
import io
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import render_baseline as RB  # noqa: E402
import served_player as SP  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

OBJS = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects"


def world(oid: str, obj: dict, tmp: Path, tail: str = "bars") -> tuple[dict, str]:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    plate = f"ledger:{oid}:{tail}"
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        w = B.world_for_plate(plate, (0, 0, 0), tmp)
        B.stamp_full_stage(w["page"])
    finally:
        B.ASPECT = saved
    return w, plate


def beat_golden(tmp: Path):
    obj, species = G.revalue_issuance()
    w, plate = world("fx-debt-issuance-bars", obj, tmp)
    return w, plate, species, [10.8, 11.2, 11.5, 11.9, 13.5, 16.35, 16.55, 16.75, 17.0, 17.8]


def beat_r28(tmp: Path):
    """R28 on H row 16's issuance: 2025's actual beside the 2026E top of the range; the 2026E bar re-valued to the
    2020-24 average and back; then the bracket to its neighbour with the multiple (computed, never typed)."""
    obj, species = G.revalue_issuance()
    debt = json.loads((OBJS / "ev-debt-issuance-line-v1.series.json").read_text(encoding="utf-8"))
    by = {s["label"]: s["pts"] for s in debt["series"]}
    last = by["issuance"][-1][1]                      # 121: 2025 actual
    now = obj["bars"][0]["value"]
    obj = dict(obj, bars=[{"label": "2025, actual", "value": last, "color": "deemph"}, dict(obj["bars"][0])])
    species = copy.deepcopy(species)
    species[0]["target"]["index"] = 1
    pct = round((now / last - 1) * 100)
    species.append({"kind": "bracket", "at": 18.0, "dur": 1.6, "from": 0, "to": 1, "label": f"+{pct}%",
                    "sub": "this year on last"})
    w, plate = world("fx-debt-issuance-two-bars", obj, tmp)
    return w, plate, species, [10.8, 11.9, 14.0, 16.7, 17.4, 18.4, 18.9, 19.8]


def beat_r30(tmp: Path):
    """R30 on H row 21's memory contract prices, RANKED (sorted by value, the rank read off the sort): the field rises
    and holds, the steepest keeps its ink while the rest dim, its pill; then a second pill on the next."""
    src = json.loads((OBJS / "ev-dram-contract-v1.series.json").read_text(encoding="utf-8"))
    bars = sorted(src["bars"], key=lambda b: -b["value"])
    obj = dict(src, unit="%", bars=[dict(b, color="crimson") for b in bars])
    species = [
        {"kind": "solo", "at": 9.0, "dur": 0.6, "bar": 0},
        {"kind": "callout", "at": 9.6, "dur": 6.0, "label": "the steepest", "target": {"kind": "datum", "index": 0, "part": "value"}},
        {"kind": "callout", "at": 13.0, "dur": 4.0, "label": "servers next", "target": {"kind": "datum", "index": 1, "part": "value"}},
    ]
    w, plate = world("fx-dram-ranked", obj, tmp)
    return w, plate, species, [5.0, 7.6, 8.8, 9.3, 9.9, 11.0, 13.4, 14.5]


BEATS = {"golden": beat_golden, "r28": beat_r28, "r30": beat_r30}


def main() -> int:
    args = sys.argv[1:]
    out = HERE / "build-lab-t24"
    if args[:1] == ["--out"]:
        out, args = Path(args[1]), args[2:]
    unknown = [a for a in args if a not in BEATS]
    if unknown:
        raise SystemExit(f"unknown beat(s) {unknown}; known: {sorted(BEATS)}")
    out.mkdir(parents=True, exist_ok=True)
    names = args or list(BEATS)
    for name in names:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            w, plate, species, ts = BEATS[name](tmp / "ep")
            errs = B.validate_species(species, (0, 0, 0), plate)
            print(name, "validate:", errs or "clean")
            if errs:
                continue
            scenes = [{"scene_id": "s01", "world": dict(w, ken_burns={"scale": 0, "x": 0, "y": 0}),
                       "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
            tl = G._timeline(f"P71 T24 proof: {name}", scenes, {}, "16:9")
            html = tmp / "beat.html"
            html.write_text(RB.instantiate(tl, G._base_uris()), encoding="utf-8")
            W_, H_ = RB.STAGE["16:9"]
            shots = []
            with SP.served(html, W_, H_) as (page, perrs):
                for t in ts:
                    RB.frame_png(page, t, (W_, H_))
                    page.wait_for_timeout(120)
                    png = RB.frame_png(page, t, (W_, H_))
                    (out / f"{name}-{t:06.2f}.png").write_bytes(png)
                    shots.append((t, png))
                print(name, "page errors:", perrs[:3])
            tile_w = 640
            tiles = [Image.open(io.BytesIO(p)).convert("RGB").resize((tile_w, tile_w * 9 // 16)) for _, p in shots]
            cols = 4
            rows = (len(tiles) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * tile_w, rows * (tile_w * 9 // 16 + 24)), (20, 20, 20))
            d = ImageDraw.Draw(sheet)
            for i, (im, (t, _)) in enumerate(zip(tiles, shots)):
                x, y = (i % cols) * tile_w, (i // cols) * (tile_w * 9 // 16 + 24)
                sheet.paste(im, (x, y + 24))
                d.text((x + 6, y + 5), f"{name} t={t:.2f}", fill=(255, 255, 255))
            sheet.save(out / f"SHEET-{name}.png")
            print(name, "sheet:", out / f"SHEET-{name}.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
