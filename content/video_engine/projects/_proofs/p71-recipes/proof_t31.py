"""P71 T31 - the labels PROVED AS BEATS (E99 s60): S5 (the golden's axis-less two clocks and their category pills), R2
`recipe:bar-ladder-to-membership` (then against now as axis-less pilled bars, the now bar filling with its members on
their words) and S6 (a logo under a bar, on a page with its axes and on the axis-less page; a logo heading a line's end
tag, the name in the long form's key) - each a private test-bed beat on a committed Steel and Paper object (values READ
off the series files, never re-typed), served with the repo's own engine and shot at named instants, one contact sheet
per beat.

    python content/video_engine/projects/_proofs/p71-recipes/proof_t31.py              # every beat into build-lab-t31/
    python content/video_engine/projects/_proofs/p71-recipes/proof_t31.py --out <dir> r2 s6-line

THE LOGO IS A STAND-IN DRAWN HERE: no committed object names a company the operator's catalogue carries a mark for, and
a real mark on the wrong bar would read as a claim - so the S6 beats catalogue a plain disc this script draws into a
temporary icon catalogue (operator_approved, render_eligible, as the compiler's permission test asks), exactly as
`tests/test_story_bar_labels.py` does. No logo image is written into the repo. It writes only inside `build-lab-t31/`
beside this file (gitignored) or the named --out; nothing in the project moves. The beats are test-bed beats (their
words are placed on a test clock after the page's build, not a take's): no approved cut carries the recipe, so it stays
a candidate with a zero count."""
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
import test_story_bar_labels as TL  # noqa: E402 - the drawn stand-in mark and its temporary catalogue
from PIL import Image, ImageDraw  # noqa: E402

OBJS = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects"
LF = ";readability=longform"
BUILT = 4.4 + 3.0   # the default enter's roll, savor, field and punch, then the page's build


def world(oid: str, obj: dict, species: list, tmp: Path, variant: str = "bars", opt: str = "") -> tuple[dict, str]:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    plate = f"ledger:{oid}:{variant}{opt}"
    errs = B.validate_species(species, (0, 0, 0), plate)
    if errs:
        raise SystemExit(f"{oid}: {errs}")
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        w = B.world_for_plate(plate, (0, 0, 0), tmp)
        B.stamp_full_stage(w["page"])
    finally:
        B.ASPECT = saved
    return w, plate


def beat_golden(tmp: Path):
    """S5 on H row 19's two clocks: no axis, each name in its pill over its written value - the golden's own page."""
    tl, _ = G.story_bars_pills()
    w = tl["scenes"][0]["world"]
    return w, "golden", [], [0.3, 0.8, 1.4, 2.0, 2.6, 3.2, 4.0, G.FRAME_T["story-bars-pills"]]


def capex_ladder() -> dict:
    """R2's then and now, READ off `ev-capex-funding-v1`'s CASH CAPEX line: its first quarter against its last, the last
    filled with the five builders its source names (MSFT, AMZN, GOOGL, META, ORCL - T45's membership golden's five)."""
    src = json.loads((OBJS / "ev-capex-funding-v1.series.json").read_text(encoding="utf-8"))
    capex = next(s for s in src["series"] if s.get("name") == "CASH CAPEX")
    (x0, v0), (x1, v1) = capex["pts"][0], capex["pts"][-1]
    q = lambda x: f"Q{int(round((x % 1) * 4 + 0.5))} {int(x)}"   # noqa: E731 - 2023.375 -> Q2 2023 (the quarter's midpoint)
    assert "MSFT, AMZN, GOOGL, META, ORCL" in src["src"]
    return {"title": "Five builders, one quarter's bill", "sub": "Cash capital spending, US$ billions a quarter - then and now",
            "src": src["src"].split("; dashed")[0], "unit": "$", "unit_suffix": "B", "axes": "none", "member_noun": "company",
            "bars": [{"label": q(x0), "value": v0, "color": "deemph", "pill": True},
                     {"label": q(x1), "value": v1, "color": "crimson", "pill": True,
                      "members": [{"name": n} for n in ("Microsoft", "Amazon", "Alphabet", "Meta", "Oracle")]}]}


def beat_r2(tmp: Path):
    """R2: then against now, axis-less and pilled; the now bar's five members land on their words, then one is lit."""
    words = [BUILT + 0.6 + 0.9 * j for j in range(5)]
    species = [{"kind": "member", "at": round(t, 2), "dur": 0.45, "tile": j} for j, t in enumerate(words)]
    species.append({"kind": "member", "at": round(words[-1] + 1.4, 2), "dur": 0.45, "tile": 0, "light": True})
    w, _ = world("fx-capex-ladder", capex_ladder(), species, tmp, opt=":1" + LF)
    return w, "r2", species, [5.0, 6.2, BUILT + 0.2, words[0] + 0.5, words[2] + 0.5, words[4] + 0.5, words[4] + 1.9, words[4] + 2.6]


def beat_s6_bar(tmp: Path):
    """S6 under a bar: the two clocks WITH their axes and a (stand-in) mark under compute, its name written under it."""
    obj = json.loads((OBJS / "ev-two-clocks-bars-v1.series.json").read_text(encoding="utf-8"))
    obj["bars"][1]["logo"] = TL.LOGO_OK
    w, _ = world("fx-clocks-logo", obj, [], tmp, opt=":1" + LF)
    return w, "s6-bar", [], [5.5, 6.5, BUILT + 0.5]


def beat_s6_pill(tmp: Path):
    """S6 on the axis-less page: the mark under compute, its name in its pill over the bar."""
    obj = G.clocks_axisless()
    obj["bars"][1]["logo"] = TL.LOGO_OK
    w, _ = world("fx-clocks-pill-logo", obj, [], tmp, opt=":1" + LF)
    return w, "s6-pill", [], [5.5, 6.5, BUILT + 0.5]


def beat_s6_line(tmp: Path):
    """S6 at a line's end: the builders' two cash lines (`ev-capex-funding-v1`, its fitted trend left out), the (stand-in)
    mark heading CASH CAPEX's end tag in the long form, its name on the key rail."""
    src = json.loads((OBJS / "ev-capex-funding-v1.series.json").read_text(encoding="utf-8"))
    obj = {k: src[k] for k in ("title", "sub", "unit") if k in src}
    obj["src"] = src["src"].split("; dashed")[0]
    obj["series"] = [dict(s) for s in src["series"] if s.get("name")]
    obj["series"][1]["logo"] = TL.LOGO_OK
    w, _ = world("fx-capex-lines-logo", obj, [], tmp, variant="line", opt="::right" + LF)
    return w, "s6-line", [], [5.5, 7.0, BUILT + 1.0, BUILT + 4.5]


BEATS = {"golden": beat_golden, "r2": beat_r2, "s6-bar": beat_s6_bar, "s6-pill": beat_s6_pill, "s6-line": beat_s6_line}


def sheet(out: Path, name: str, shots: list) -> Path:
    tile_w = 640
    tiles = [Image.open(io.BytesIO(p)).convert("RGB").resize((tile_w, tile_w * 9 // 16)) for _, p in shots]
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    im = Image.new("RGB", (cols * tile_w, rows * (tile_w * 9 // 16 + 24)), (20, 20, 20))
    d = ImageDraw.Draw(im)
    for i, (tile, (t, _)) in enumerate(zip(tiles, shots)):
        x, y = (i % cols) * tile_w, (i // cols) * (tile_w * 9 // 16 + 24)
        im.paste(tile, (x, y + 24))
        d.text((x + 6, y + 5), f"{name} t={t:.2f}", fill=(255, 255, 255))
    path = out / f"SHEET-{name}.png"
    im.save(path)
    return path


def main() -> int:
    args = sys.argv[1:]
    out = HERE / "build-lab-t31"
    if args[:1] == ["--out"]:
        out, args = Path(args[1]), args[2:]
    unknown = [a for a in args if a not in BEATS]
    if unknown:
        raise SystemExit(f"unknown beat(s) {unknown}; known: {sorted(BEATS)}")
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as cat_td:
        saved = (B.ICON_CATALOG, B._CATALOG_CACHE)
        B.ICON_CATALOG, B._CATALOG_CACHE = TL._catalogue(Path(cat_td)), None   # the stand-in mark's temporary catalogue
        try:
            for name in args or list(BEATS):
                with tempfile.TemporaryDirectory() as td:
                    tmp = Path(td)
                    w, _, species, ts = BEATS[name](tmp / "ep")
                    print(name, "warnings:", (w.get("page") or {}).get("warnings"))
                    scenes = [{"scene_id": "s01", "world": dict(w, ken_burns={"scale": 0, "x": 0, "y": 0}),
                               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
                    tl = G._timeline(f"P71 T31 proof: {name}", scenes, {}, "16:9")
                    uris = dict(G._base_uris(), **B.longform_assets(tl), **B.member_assets(tl), **B.label_logo_assets(tl))
                    html = tmp / "beat.html"
                    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
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
                    print(name, "sheet:", sheet(out, name, shots))
        finally:
            B.ICON_CATALOG, B._CATALOG_CACHE = saved
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
