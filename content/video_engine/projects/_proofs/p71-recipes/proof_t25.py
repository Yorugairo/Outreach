"""P71 T25 - the scale-out and the projected overtake PROVED AS BEATS (E99 s60): A51 (the golden's overtake), R31
`recipe:scale-out-then-the-overtake` (the page born on one bar alone, the field on its word with the computed rank, then
the projection surging past the leader) and A50 on its own (a second field, the memory contract prices) - each a private
test-bed beat on a committed Steel and Paper object (values READ off the series files, never re-typed), served with the
repo's own engine and shot at named instants, with one contact sheet per beat.

    python content/video_engine/projects/_proofs/p71-recipes/proof_t25.py              # all three into build-lab-t25/
    python content/video_engine/projects/_proofs/p71-recipes/proof_t25.py --out <dir> r31

It writes only inside `build-lab-t25/` beside this file (gitignored) or the named --out; nothing in the project moves.
The beats are test-bed beats (their words are placed on a test clock after the page's build, not a take's): no approved cut carries the recipe,
so it stays a candidate with a zero count."""
from __future__ import annotations

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


def world(oid: str, obj: dict, species: list, tmp: Path) -> tuple[dict, str]:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    plate = f"ledger:{oid}:bars"
    errs = B.validate_species(species, (0, 0, 0), plate)   # the row as authored - before the compiler stamps each state
    if errs:
        raise SystemExit(f"{oid}: {errs}")
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        w = B.world_for_plate(plate, (0, 0, 0), tmp)
        B.stamp_full_stage(w["page"])
        B.derive_rescale_states(w, species, plate, tmp)
    finally:
        B.ASPECT = saved
    return w, plate


def beat_golden(tmp: Path):
    """A51 on H row 16's capex: the field stands; on its word the 2027 consensus surges dashed past the $690B."""
    species = [{"kind": "chart_to", "to": "extend", "at": 11.0, "dur": 2.5, "bar": 2}]
    w, plate = world("fx-capex-overtake", G.overtake_capex(), species, tmp)
    return w, plate, species, [10.5, 11.15, 11.4, 11.6, 11.8, 12.1, 12.6, 13.0, 13.5, 14.2]


def beat_r31(tmp: Path):
    """R31 on the same field: born on the year's opening estimate alone ('four hundred and eighty'), the field on its
    word with the rank written, then the 2027 projection passes the leader."""
    species = [{"kind": "chart_to", "to": "extend", "at": 9.0, "dur": 2.0, "field": True},
               {"kind": "chart_to", "to": "extend", "at": 14.0, "dur": 2.5, "bar": 2}]
    w, plate = world("fx-capex-scale-out", G.overtake_capex(opens_on=True), species, tmp)
    return w, plate, species, [8.6, 9.2, 9.45, 9.7, 10.0, 10.6, 11.2, 13.5, 14.5, 14.9, 15.6, 17.2]


def beat_a50(tmp: Path):
    """A50 alone on H row 21's memory contract prices: Server DRAM's +60% read alone, then the field and its rank."""
    src = json.loads((OBJS / "ev-dram-contract-v1.series.json").read_text(encoding="utf-8"))
    obj = dict(src, unit="%", opens_on={"bar": "Server DRAM", "rank": "largest rise"})
    species = [{"kind": "chart_to", "to": "extend", "at": 9.0, "dur": 2.0, "field": True}]
    w, plate = world("fx-dram-scale-out", obj, species, tmp)
    return w, plate, species, [8.6, 9.2, 9.45, 9.7, 10.0, 10.6, 11.2, 12.0]


BEATS = {"golden": beat_golden, "r31": beat_r31, "a50": beat_a50}


def main() -> int:
    args = sys.argv[1:]
    out = HERE / "build-lab-t25"
    if args[:1] == ["--out"]:
        out, args = Path(args[1]), args[2:]
    unknown = [a for a in args if a not in BEATS]
    if unknown:
        raise SystemExit(f"unknown beat(s) {unknown}; known: {sorted(BEATS)}")
    out.mkdir(parents=True, exist_ok=True)
    for name in args or list(BEATS):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            w, plate, species, ts = BEATS[name](tmp / "ep")
            print(name, "validate: clean; states", len(w.get("page_states") or []))
            scenes = [{"scene_id": "s01", "world": dict(w, ken_burns={"scale": 0, "x": 0, "y": 0}),
                       "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
            tl = G._timeline(f"P71 T25 proof: {name}", scenes, {}, "16:9")
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
