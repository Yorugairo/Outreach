"""P72 T14 - THE CAPTIONS READ ON EVERY PLATE (R26-268, R26-292).

R26-268 (P69 T15 / T20 / T21, recurred on row 17's first draft): on a picture plate the caption is either the anchored
strip (a card is up) or stage-centred at 40 % - it crossed the host's collar (row 7), sat low-contrast on the bright
desk (rows 12, 17) and over the viaduct's paper edge (row 13). Owed, and pinned here:

  THE ROOM     `;caption_room=x,y,w,h` - fractions of the stage, the plate's word for where its STAGE caption sits,
               exactly as `;room=` names where a card may stand (R26-221). A PICTURE PLATE option, refused by name on
               a world that computes its own (a page's quiet zone, a vector map, a clip), and when malformed. A plate
               that declares none writes nothing - its caption is where it always was, to the byte.
  THE BACKING  the STAGE caption's ink measured against the plate UNDER it (the engine's own measured ground,
               `groundLumAt` / `ringRgbAt`, as the stamp ring and the ruler read it): where the caption's words hold
               less than the reference's contrast floor against that ground (`caption-squint-floor.v1.json`,
               Wealth Logic's strip, E38 - never a number fitted to ours) the words take a dark backing IN THE TEXT
               SHADOW - the reference's own form (white caps in a black stroke), never a box: doc 29 Part 5 and the
               portable pipeline hold the long form's caption to "transparent glyphs plus text shadow; no pill, no
               panel". A dark plate measures clear and paints exactly what it painted. The anchored / quiet strip is
               P71 T8b's (its size and contrast on every world) and takes none.

R26-292 (P69 T26e review): `exit: morph:prop:<id>` collapses the page of the row before OVER this row's world; the
row's stage caption painted large, mid-stage, over the collapsing page. Owed: the caption keeps the incoming scene's
STRIP (the anchored strip) while the page collapses, and takes the stage from the landing.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import measure_line_bloom as MLB  # noqa: E402
import render_baseline as RB  # noqa: E402
import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE = (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")
FLOOR_FILE = ROOT / "content/video_engine/assets/caption-squint-floor.v1.json"
CROOM = "0.55,0.08,0.40,0.30"
CROOM_FRACTIONS = [0.55, 0.08, 0.40, 0.30]


# ---- the token's grammar ------------------------------------------------------------------------------


def test_caption_room_is_a_plate_option_and_is_parsed_like_room():
    assert "caption_room" in B.PLATE_OPTS
    assert B.split_plate_opts("world-h1-studio-v1;idle=drift;caption_room=" + CROOM)[1] == {
        "idle": "drift", "caption_room": CROOM}
    assert B.plate_room_spec(CROOM, "row", key="caption_room") == CROOM_FRACTIONS


@pytest.mark.parametrize("bad, match", [
    ("0.1,0.2", "caption_room '0.1,0.2' is not x,y,w,h"),
    ("left,top,wide,tall", "caption_room 'left,top,wide,tall' is not four numbers"),
    ("0.1,0.1,nan,0.3", "is not four numbers"),
    ("0.1,0.1,0,0.3", "caption_room '0.1,0.1,0,0.3' is empty"),
    ("0.8,0.1,0.4,0.2", "caption_room '0.8,0.1,0.4,0.2' runs off the stage"),
])
def test_a_malformed_caption_room_is_refused_BY_NAME(bad, match):
    """s106: a key the slice adds is refused by name when malformed - never a silent drop."""
    with pytest.raises(ValueError, match=re.escape(match) if "'" in match else match):
        B.split_plate_opts("world-h1-studio-v1;caption_room=" + bad)


def test_the_caption_room_is_a_picture_plates_word_and_is_refused_on_a_world_that_computes_its_own(tmp_path):
    objects = tmp_path / "evidence/objects"
    objects.mkdir(parents=True)
    (objects / "ev-lines-v1.series.json").write_text(json.dumps(
        {"title": "t", "sub": "s", "src": "the test bed", "unit": "",
         "series": [{"name": "A", "color": "crimson", "pts": [[1, 1], [2, 2], [3, 3]]},
                    {"name": "B", "color": "teal", "pts": [[1, 2], [2, 3], [3, 4]]}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="caption_room= is a PICTURE PLATE option"):
        B.world_for_plate("ledger:ev-lines-v1:line;caption_room=" + CROOM, (0, 0, 0), tmp_path)
    with pytest.raises(ValueError, match="caption_room= is a PICTURE PLATE option"):
        B.world_for_plate("vecmap;caption_room=" + CROOM, (0, 0, 0), Path("."))


def test_a_plate_that_declares_a_caption_room_carries_it_and_one_that_does_not_writes_nothing(tmp_path):
    from PIL import Image
    objects = tmp_path / "evidence/objects"
    objects.mkdir(parents=True)
    Image.new("RGB", (64, 36), (43, 52, 60)).save(objects / "plate-croom-test.png")
    old = B.R.EP
    try:
        B.R.EP = tmp_path
        plain = B.world_for_plate("plate-croom-test;idle=drift;room=0.04,0.1,0.34,0.62", (0.05, -12, 6), tmp_path)
        assert "caption_room" not in plain, "a plate that declares none writes nothing - byte-identity"
        world = B.world_for_plate("plate-croom-test;idle=drift;room=0.04,0.1,0.34,0.62;caption_room=" + CROOM,
                                  (0.05, -12, 6), tmp_path)
        assert world["caption_room"] == CROOM_FRACTIONS
        del world["caption_room"]
        assert world == plain, "the declared caption room is the ONLY difference the token makes"
    finally:
        B.R.EP = old


def test_a_caption_room_too_small_for_the_stage_strip_is_ADVICE_with_its_numbers():
    """s106: the author's room stands; a room that cannot hold the two-line strip at the stage size WARNs, with
    the numbers - never a refusal."""
    assert B.caption_room_advice(CROOM_FRACTIONS, "16:9") == []
    (w,) = B.caption_room_advice([0.1, 0.1, 0.5, 0.05], "16:9")
    assert "caption_room" in w and "54 px" in w and str(B.caption_strip_h()) in w


# ---- R26-292: a page collapsing into a prop keeps the caption in the strip --------------------------------


def _collapse_scenes() -> list[dict]:
    s1 = {"scene_id": "s01", "span": [0.0, 12.0], "world": {"kind": "ledger"}, "docks": [], "species": [],
          "prop_morphs": [{"id": "s02.enter", "way": "out", "prop": "p", "at": 12.0, "dur": 1.6, "mark": "page",
                           "over": True},
                          {"id": "s01.m1", "way": "out", "prop": "p", "at": 6.0, "dur": 2.0, "mark": "page"}]}
    s2 = {"scene_id": "s02", "span": [12.0, 30.0], "world": {"asset_id": "plate-plain"}, "docks": [], "species": []}
    return [s1, s2]


def test_a_page_collapsing_OVER_the_next_world_is_found_at_its_seconds_only():
    sc = _collapse_scenes()
    assert B._prop_collapse_at(sc, 12.0) and B._prop_collapse_at(sc, 13.5)
    assert not B._prop_collapse_at(sc, 11.99) and not B._prop_collapse_at(sc, 13.6)
    assert not B._prop_collapse_at(sc, 7.0), "a mid-page morph on its own page is not a collapse over the next world"


def test_the_caption_page_that_opens_during_the_collapse_is_stamped_ANCHOR():
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    stamp = src[src.index('pages = [{**pg, "cap_mode": "anchor" if ('):]
    assert "_prop_collapse_at(scenes, pg[\"s\"])" in stamp[:600], "the compiler's cap_mode reads the collapse"


# ---- the engine: the frames ---------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

CAP_PROBE = """() => {
  const sb = document.getElementById('stage').getBoundingClientRect(), cap = document.getElementById('caption');
  const R = (r) => [r.left - sb.left, r.top - sb.top, r.right - sb.left, r.bottom - sb.top];
  const ws = [...cap.querySelectorAll('.cw')].filter((w) => w.getBoundingClientRect().width > 0);
  let u = null;
  for (const w of ws) { const r = R(w.getBoundingClientRect());
    u = u ? [Math.min(u[0], r[0]), Math.min(u[1], r[1]), Math.max(u[2], r[2]), Math.max(u[3], r[3])] : r; }
  return { cls: cap.className, box: u, words: ws.map((w) => [R(w.getBoundingClientRect()), w.textContent]),
           style: { left: cap.style.left, right: cap.style.right, top: cap.style.top, bottom: cap.style.bottom,
                    textShadow: cap.style.textShadow },
           shadow: getComputedStyle(cap).textShadow };
}"""

WORDS = ["the", "desk", "is", "bright", "tonight"]
PAGE_S = 2.0


def _pages(at: float = PAGE_S, dur: float = 3.0) -> list[dict]:
    return [{"s": at, "e": at + dur, "cap_mode": "stage",
             "t": [{"w": w, "k": False, "s": round(at + 0.3 * j, 2), "e": round(at + 0.3 * j + 0.28, 2)}
                   for j, w in enumerate(WORDS)]}]


def _plate_tl(rgb: tuple, caption_room: list | None = None, modes: list | None = None) -> tuple[dict, dict]:
    uris = G._base_uris()
    uris["plate-test"] = G.uri("image/png", G.png_solid(64, 36, rgb))
    world = {"asset_id": "plate-test", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    if caption_room is not None:
        world["caption_room"] = caption_room
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": []}]
    tl = G._timeline("plate caption", scenes, {}, "16:9")
    tl["caption_pages"] = _pages()
    tl["captions"] = []
    if modes is not None:
        tl["caption_modes"] = modes
    return json.loads(json.dumps(tl)), uris


class _Player:
    def __init__(self, browser, tl: dict, uris: dict):
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / "p.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.size = RB.STAGE[tl.get("aspect") or "16:9"]
        self._srv, port = RB.serve(html.parent)
        self.page = browser.new_context(viewport={"width": self.size[0], "height": self.size[1]}).new_page()
        self.errors: list[str] = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, *self.size)

    def cap(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                           "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(CAP_PROBE)

    def png(self, t: float) -> bytes:
        return RB.frame_png(self.page, t, self.size)

    def close(self) -> None:
        self.page.context.close(); self._srv.shutdown(); self._td.cleanup()


def _browser():
    return SP.browser()  # R26-351 (P72 T9): the one guarded Playwright start


def _read(br, tl, uris, t: float) -> tuple[dict, bytes, list]:
    pl = _Player(br, tl, uris)
    try:
        png = pl.png(t)
        return pl.cap(t), png, list(pl.errors)
    finally:
        pl.close()


def _contrast(png: bytes, cap: dict) -> float:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "f.png"
        p.write_bytes(png)
        grow = lambda b, k: [b[0] - k, b[1] - k, b[2] + k, b[3] + k]   # noqa: E731 - M48's own _caption_rec grows
        return MLB.caption_read(p, grow(cap["box"], 4), " ".join(WORDS),
                                words=[(grow(b, 3), w) for b, w in cap["words"]])["contrast"]


CREAM = (236, 229, 214)     # a pale cream desk wall - row 17's ground
CHARCOAL = (43, 52, 60)     # the golden plate's own colour (build_golden_sources._base_uris)
T_READ = PAGE_S + 2.0       # every word written, the page still up


def _floor() -> float:
    return json.loads(FLOOR_FILE.read_text(encoding="utf-8"))["lanes"]["16:9"]["contrast"]["min"]


def test_the_engines_floor_is_the_reference_files_never_a_number_typed_for_ours():
    m = re.search(r"CAPTION_BACKING\s*=\s*(?:Object\.freeze\()?\{[^}]*FLOOR:\s*([0-9.]+)", ENGINE)
    assert m, "the engine names its backing floor"
    assert float(m.group(1)) == _floor(), "mirrored from caption-squint-floor.v1.json (16:9 contrast.min)"


@needs_browser
def test_a_declared_caption_room_places_the_stage_caption_inside_it():
    room = [v * s for v, s in zip(CROOM_FRACTIONS, (1920, 1080, 1920, 1080))]
    with _browser() as br:
        got, _png, errs = _read(br, *_plate_tl(CHARCOAL, CROOM_FRACTIONS), T_READ)
        base, _png0, errs0 = _read(br, *_plate_tl(CHARCOAL), T_READ)
    assert errs == [] and errs0 == []
    assert "stage" in got["cls"].split()
    x0, y0, x1, y1 = got["box"]
    assert room[0] - 1 <= x0 and x1 <= room[0] + room[2] + 1, (got["box"], room)
    assert room[1] - 1 <= y0 and y1 <= room[1] + room[3] + 1, (got["box"], room)
    assert got["box"] != base["box"], "the room MOVED the caption off its 40 % home"


@needs_browser
def test_a_plate_with_no_caption_room_captions_where_it_always_did():
    with _browser() as br:
        got, _png, errs = _read(br, *_plate_tl(CHARCOAL), T_READ)
    assert errs == []
    assert got["style"]["left"] == got["style"]["right"] == got["style"]["top"] == "", got["style"]
    assert abs(got["box"][1] - 0.40 * 1080) < 12, ("the template's own 40 % home", got["box"])


@needs_browser
def test_over_a_BRIGHT_plate_the_caption_takes_the_backing_and_holds_the_reference_floor():
    """The acceptance on the frame, read by M48's own caption read at 320 px: the caption over a pale cream ground
    holds the reference's contrast floor; the backing is a text shadow on the strip, never a box."""
    with _browser() as br:
        got, png, errs = _read(br, *_plate_tl(CREAM), T_READ)
    assert errs == []
    assert got["style"]["textShadow"], "the backing is painted inline, measured against the plate"
    assert "background" not in json.dumps(got["style"])
    c = _contrast(png, got)
    assert c >= _floor(), (c, _floor())


@needs_browser
def test_the_anchored_strip_over_a_bright_plate_is_left_to_the_quiet_strips_owner():
    """The seam with P71 T8b: the backing is the STAGE caption's; the anchored / quiet strip (its size and contrast on
    every world) is T8b's, so a strip over the same cream takes none here."""
    with _browser() as br:
        got, _png, errs = _read(br, *_plate_tl(CREAM, modes=["anchor"]), T_READ)
    assert errs == []
    assert "stage" not in got["cls"].split()
    assert got["style"]["textShadow"] == ""


@needs_browser
def test_over_a_DARK_plate_the_caption_paints_exactly_what_it_painted():
    with _browser() as br:
        got, _png, errs = _read(br, *_plate_tl(CHARCOAL), T_READ)
    assert errs == []
    assert got["style"]["textShadow"] == "", "a ground that already holds the floor takes no backing"


@needs_browser
def test_during_a_page_collapse_into_a_prop_the_caption_keeps_the_strip_and_takes_the_stage_on_the_landing():
    """R26-292 on the frames: the row after a `morph:prop` exit opens its caption while the page of the row before
    collapses over its world - the caption sits in the anchored strip (quiet) for the collapse. From the landing the
    row's own rule is back: the standing prop is a live dock (the strip, as under any card), and once it has left the
    caption takes the stage."""
    tl, uris = _exit_timeline()
    with _browser() as br:
        pl = _Player(br, tl, uris)
        try:
            before = pl.cap(EXIT_CUT + 0.12)
            mid = pl.cap(EXIT_CUT + EXIT_S * 0.5)
            gone = pl.cap(PROP_LEAVES + 1.0)
            errors = list(pl.errors)
        finally:
            pl.close()
    assert errors == []
    for got in (before, mid):
        assert "quiet" in got["cls"].split() and "stage" not in got["cls"].split(), got["cls"]
        assert got["box"] and got["box"][1] > 800, ("the strip, not mid-stage", got["box"])
    assert "stage" in gone["cls"].split(), gone["cls"]


EXIT_CUT, EXIT_S = 12.0, 1.6
PROP_LEAVES = EXIT_CUT + EXIT_S + 1.0   # the prop stands a second after its landing, then leaves (the stage returns)
DC = "prop-hyperscale-datacenter-v1"
DC_PATH = ROOT / "content/video_engine/assets/props/cutouts" / f"{DC}.png"


def _exit_timeline() -> tuple[dict, dict]:
    """test_prop_morph's own exit bed (scene 1 the golden's capex page; scene 2 a plain plate whose row names
    `exit: morph:prop:<id>:1.6`), with a caption page opening 0.1 s into the collapse."""
    world1 = G._prop_morph_world()
    s1 = {"scene_id": "s01", "world": world1, "exit": "cut", "span": [0.0, EXIT_CUT], "docks": [], "species": []}
    row2 = [(DC, 0, EXIT_CUT, PROP_LEAVES, {"prop": True, "place": {"x": 0.62, "y": 0.5, "w": 0.24}})]
    r = B.prop_morph_row([], row2, f"morph:prop:{DC}:{EXIT_S}", EXIT_CUT, G.RUNTIME, "t", sid="s02", prev_a=0.0)
    aid, slot, enter, exitt, raw = r["ds"][0]
    opts = {**B.dock_opts(raw), "arrive": "morph"}
    world2 = {"asset_id": "plate-plain", "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    fit = B.prop_place_fit(world2, "16:9", opts, B.painted_box(DC_PATH), None, "t")
    dock = B.dock_entry(aid, slot, enter, exitt, 0, B.DOCK_KIND_PROP, {k: fit[k] for k in ("x", "y", "w", "h", "room")},
                        "morph", None, True, prop=True)
    B.attach_enter_morph(r["enter_morph"], s1, dock, "16:9", "t", lambda a: DC_PATH)
    s2 = {"scene_id": "s02", "world": world2, "exit": r["exit"], "span": [EXIT_CUT, G.RUNTIME], "docks": [dock],
          "species": []}
    ev = {DC: {"title": "A hyperscale data centre", "source": "cutout", "species": "prop",
               "document": {"path": "x", "sha256": "0" * 64}, "badges": [], "kind": B.DOCK_KIND_PROP}}
    uris = G._base_uris()
    uris[DC] = G.uri("image/png", G.png_proxy(DC_PATH, G.PROP_PROXY_PX))
    tl = G._timeline("prop exit caption", [s1, s2], ev, "16:9")
    tl["kinetics"] = {"stop_action": True}
    tl["caption_pages"] = _pages(EXIT_CUT + 0.1, 6.0)
    tl["captions"] = []
    return json.loads(json.dumps(tl)), uris
