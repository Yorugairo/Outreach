"""P71 T21 - the fills to a level PROVED AS BEATS (E99 s60): R29 `recipe:the-glowing-trough` (the dip filled to its
rule, its edge lit, a ring on the trough) on two pages, and A45's underwater fill with its edge lit - each a private
test-bed beat on a COMMITTED object (values READ off the series files, never re-typed), served with the repo's own
engine and shot at named instants, with one contact sheet per beat.

    python content/video_engine/projects/_proofs/p71-recipes/proof_t21.py              # all three into build-lab-t21/
    python content/video_engine/projects/_proofs/p71-recipes/proof_t21.py --out <dir> trough

  trough      the fed reserves' change since June 2022 (fed-liquidity-pressure's DERIVED object): the spring 2025 dip
              below zero - the fill kept below the zero rule, the stretch's edge lit, a dashed ring on the trough
              (-$0.357T, datum 152) - D40 12:46-13:08's glowing trough on a signed series
  soft-month  Steel and Paper H row 22's memory monitor and its sentence "one soft month in June": the fill under May's
              print (the prior high, datum 40, the rule READ off it) until July regains it, June's edge lit, a ring on
              June - R29's USE-WHEN names this row; the page is a level, so the "zero" is the prior print (A45's form)
  underwater  H row 5's railway index: the fall drawn, the fill under the October 1845 high to the record's end with its
              time under water computed ("4+ years below the peak"), and the light down the fall (BOOM 02:49.5's lit
              edge)

It writes only inside `build-lab-t21/` beside this file (gitignored) or the named --out; nothing in the project moves.
The beats are test-bed beats on the page's own build clock (no take's words): no approved cut carries the recipe, so
it stays a candidate with a zero count."""
from __future__ import annotations

import io
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

SNP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
MEM_PLATE = "ledger:ev-memory-monitor-v1:line:42:right;idle=live"


def _datum(i: int, s: int = 0) -> dict:
    return {"kind": "datum", "index": i, "series": s}


def beat_trough():
    """R29 on the fed page: the dip from the last print over zero (149) back over it (157); the trough at 152."""
    w = G._fill_world(G.FILL_FED_PLATE, G.FILL_FED_PROJECT)
    w["page"].setdefault("axes", {})["hlines"] = [{"y": 0, "color": "deemph"}]
    species = [{"kind": "build_to", "at": 0.0, "dur": 0.4, "series": s, "target": _datum(0, s)} for s in (0, 1)]
    species += [{"kind": "build_to", "at": 0.6, "dur": 2.4, "series": 1, "target": _datum(158, 1)},
                {"kind": "spread", "at": 9.0, "dur": 1.2, "from": 1, "to_rule": 0, "side": "below", "from_index": 149},
                {"kind": "lit_stretch", "at": 9.2, "dur": 1.2, "series": 1, "from": 149, "to": 157},
                {"kind": "ring", "at": 10.2, "dur": 2.4, "form": "dashed", "target": _datum(152, 1)}]   # after the page has built (its own clock)
    return w, G.FILL_FED_PLATE, species, [8.9, 9.4, 9.8, 10.3, 10.8, 11.4, 12.2, 13.5]


def beat_soft_month():
    """R29 on H row 22: under May's print from May (40) until July (42) regains it; June (41) is the soft month."""
    w = G._fill_world(MEM_PLATE, SNP)
    may = float(w["page"]["series"][0]["pts"][40][1])   # 77,558 - READ off the datum
    w["page"].setdefault("axes", {})["hlines"] = [{"y": may, "color": "deemph"}]
    species = [{"kind": "build_to", "at": 0.0, "dur": 0.4, "series": s, "target": _datum(42, s)} for s in (0, 1, 2)]
    species += [{"kind": "spread", "at": 12.69, "dur": 1.04, "from": 0, "to_rule": 0, "side": "below", "peak": True, "from_index": 40},
                {"kind": "lit_stretch", "at": 12.8, "dur": 1.0, "series": 0, "from": 40, "to": 42},
                {"kind": "ring", "at": 13.89, "dur": 2.4, "form": "dashed", "target": _datum(41)}]   # "June" 653.89 - 640
    assert B.check_spread_levels(w, species) == []
    return w, MEM_PLATE, species, [12.6, 13.0, 13.4, 13.8, 14.2, 14.8, 15.6, 16.5]


def beat_underwater():
    """A45 + the lit edge on H row 5's railway index (the golden's page and clock, the light added)."""
    tl, _uris = G.fill_underwater()
    scene = tl["scenes"][0]
    species = [dict(e) for e in scene["species"]] + [
        {"kind": "lit_stretch", "at": G.FILL_WATER_AT + 0.2, "dur": 1.56, "from": 53, "to": 139, "comet": True}]
    return scene["world"], G.LIT_PLATE, species, [11.2, 11.8, 12.3, 12.8, 13.3, 13.8, 14.5, 16.0]


BEATS = {"trough": beat_trough, "soft-month": beat_soft_month, "underwater": beat_underwater}


def main() -> int:
    args = sys.argv[1:]
    out = HERE / "build-lab-t21"
    if args[:1] == ["--out"]:
        out, args = Path(args[1]), args[2:]
    unknown = [a for a in args if a not in BEATS]
    if unknown:
        raise SystemExit(f"unknown beat(s) {unknown}; known: {sorted(BEATS)}")
    out.mkdir(parents=True, exist_ok=True)
    for name in args or list(BEATS):
        w, plate, species, ts = BEATS[name]()
        errs = B.validate_species(species, (0, 0, 0), plate)
        print(name, "validate:", errs or "clean")
        if errs:
            continue
        scenes = [{"scene_id": "s01", "world": dict(w, ken_burns={"scale": 0, "x": 0, "y": 0}),
                   "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
        tl = G._timeline(f"P71 T21 proof: {name}", scenes, {}, "16:9")
        with tempfile.TemporaryDirectory() as td:
            html = Path(td) / "beat.html"
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
