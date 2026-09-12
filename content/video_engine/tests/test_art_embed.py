"""P50 T7 - THE ART-EMBED SURFACE as code: a plate declares a NAMED SET of flat surfaces beside itself, a dock
names the one it lands on, and the compiler refuses every way that can be wrong before a frame is rendered.

The grammar (the approved plate order, 2026-09-11): `<plate>.layers.json` carries
`{"embed": {"poster": {"quad": [[x, y] x 4], "darken": "<word>"}, "paper": {...}}}` - stage fractions, the
corners in TL TR BR BL order - and a dock row says `{"embed": "poster"}`. The compiler validates the quad
(four corners on the stage, convex and in order, at least a quarter of the stage wide so a card can be read on
a phone), refuses a name the plate does not declare, refuses a CHART card and a ledger page outright (B1: the
argument's own charts never embed), resolves `darken` to a second against the build's words, and writes the
surface onto the dock entry with the card picture's aspect - everything the player needs to project the card
without measuring anything that decodes asynchronously.

Pure functions and committed files only - no episode build.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402

GOLDEN = ROOT / "content/video_engine/tests/golden/sources"
# the poster measured off the approved plate still (768 x 1376): vertical sides at x = 283 / 638 px, the top
# edge rising to the right, the bottom falling - as stage fractions, TL TR BR BL
POSTER = [[0.3685, 0.1941], [0.8307, 0.1560], [0.8307, 0.6247], [0.3685, 0.6106]]
PAPER = [[0.1800, 0.7200], [0.8600, 0.7400], [0.9400, 0.9300], [0.0600, 0.9100]]
PLATE_WORLD = {"asset_id": "plate-study", "sha256": "0" * 64}
WHERE = "shot row 3 (12-20s) dock ev-quote"


def _plate_with_embeds(tmp_path: Path, embeds: dict, foreground: dict | None = None) -> Path:
    plate = tmp_path / "plate-study.png"
    plate.write_bytes(b"\x89PNG\r\n\x1a\n")
    side = {"embed": embeds}
    if foreground:
        side["foreground"] = foreground
    (tmp_path / "plate-study.layers.json").write_text(json.dumps(side), encoding="utf-8")
    return plate


# ---- the manifest: a NAMED SET of surfaces, read off the plate's own sidecar ---------------------------

def test_a_plate_declares_its_surfaces_by_name_beside_itself(tmp_path):
    plate = _plate_with_embeds(tmp_path, {"poster": {"quad": POSTER, "darken": "the wall"},
                                          "paper": {"quad": PAPER}},
                               foreground={"desk": "plate-study.front.png"})
    got = B.plate_embeds(plate)
    assert sorted(got) == ["paper", "poster"], "a plate carries a named SET, not one quad"
    assert got["poster"]["darken"] == "the wall"
    assert B.plate_layers(plate) == {"desk": tmp_path / "plate-study.front.png"}, "the two sidecar keys coexist"
    assert B.plate_embeds(tmp_path / "nothing.png") == {}, "a plate is not required to carry a surface"
    (tmp_path / "plate-study.layers.json").write_text("not json", encoding="utf-8")
    assert B.plate_embeds(plate) == {}, "a malformed sidecar is no surfaces, never a crash"


def test_embed_is_a_dock_option_and_names_one_surface():
    assert B.EMBED_KEY in B.DOCK_OPTS
    assert B.dock_opts({"embed": "poster"}) == {"embed": "poster"}
    for bad in ("", "   ", 3, True, None, ["poster"]):
        with pytest.raises(ValueError) as e:
            B.dock_opts({"embed": bad})
        assert "must NAME a surface" in str(e.value)
    with pytest.raises(ValueError) as e:
        B.dock_opts({"embed": "poster", "press": {"source": "THE HERALD", "phrase": {"x0": 0.1, "y0": 0.2, "x1": 0.6, "y1": 0.4}},
                     "stack": True})
    assert "embed and stack" in str(e.value), "a card on a surface has no pile - the surface is the park"


# ---- the quad's law ------------------------------------------------------------------------------------

def test_the_measured_poster_and_the_desk_paper_are_both_lawful_surfaces():
    assert B.embed_quad_error("poster", {"quad": POSTER}, WHERE) is None
    assert B.embed_quad_error("paper", {"quad": PAPER, "darken": "the desk"}, WHERE) is None


@pytest.mark.parametrize("quad,needle", [
    ([[0.3, 0.2], [0.8, 0.2], [0.8, 0.6]], "four [x, y] corners"),
    ([[0.3, 0.2], [0.8, 0.2], [0.8, 0.6], [0.3, "x"]], "four [x, y] corners"),
    ([[0.3, 0.2], [1.4, 0.2], [1.4, 0.6], [0.3, 0.6]], "off the stage"),
    ([[0.3, 0.2], [0.3, 0.6], [0.8, 0.6], [0.8, 0.2]], "the wrong way"),          # wound anticlockwise
    ([[0.1, 0.2], [0.9, 0.2], [0.1, 0.6], [0.9, 0.6]], "both ways"),              # a bow tie: BR and BL swapped
])
def test_a_quad_that_is_not_a_surface_is_refused_by_name(quad, needle):
    err = B.embed_quad_error("poster", {"quad": quad}, WHERE)
    assert err and needle in err and "poster" in err, err


def test_a_surface_under_a_quarter_of_the_stage_is_refused_because_a_card_must_read_on_a_phone():
    narrow = [[0.40, 0.20], [0.58, 0.20], [0.58, 0.60], [0.40, 0.60]]   # 18 % of the stage wide
    err = B.embed_quad_error("poster", {"quad": narrow}, WHERE)
    assert err and "18% of the stage wide" in err and "25% floor" in err, err
    assert B.EMBED_MIN_W == 0.25
    just = [[0.40, 0.20], [0.66, 0.20], [0.66, 0.60], [0.40, 0.60]]     # 26 %: through
    assert B.embed_quad_error("poster", {"quad": just}, WHERE) is None


def test_darken_is_a_word_or_a_second_and_anything_else_is_refused():
    for ok in ("the wall", 7.0, 0):
        assert B.embed_quad_error("poster", {"quad": POSTER, "darken": ok}, WHERE) is None, ok
    for bad in ("", "  ", -1, True, {"word": "x"}):
        err = B.embed_quad_error("poster", {"quad": POSTER, "darken": bad}, WHERE)
        assert err and "darken" in err, (bad, err)


# ---- which docks may land on a surface, and on which worlds ---------------------------------------------

def test_an_unknown_surface_is_refused_and_the_message_names_what_the_plate_declares(tmp_path):
    embeds = B.plate_embeds(_plate_with_embeds(tmp_path, {"poster": {"quad": POSTER}, "paper": {"quad": PAPER}}))
    assert B.embed_error(PLATE_WORLD, embeds, "poster", WHERE) is None
    err = B.embed_error(PLATE_WORLD, embeds, "tv", WHERE)
    assert err and "embed='tv' is not a surface of 'plate-study'" in err and "it declares paper, poster" in err, err
    assert "layers.json" in err, "the message says where to declare it"
    assert "none" in B.embed_error(PLATE_WORLD, {}, "tv", WHERE)


def test_a_ledger_page_and_a_chart_card_never_embed(tmp_path):
    embeds = B.plate_embeds(_plate_with_embeds(tmp_path, {"poster": {"quad": POSTER}}))
    page = B.embed_error({"kind": B.SPECIES_LEDGER, "page": {}}, embeds, "poster", WHERE)
    assert page and "a chart page never embeds" in page and "B1" in page, page
    for world in ({"kind": B.VECMAP_KIND}, {"kind": B.SPECIES_CLIP, "asset_id": "clip"}, {}):
        drawn = B.embed_error(world, embeds, "poster", WHERE)
        assert drawn and "no painted surface to land on" in drawn, world
    card = B.embed_error(PLATE_WORLD, embeds, "poster", WHERE, species="chart")
    assert card and "the argument's own charts never embed" in card, card
    assert B.embed_error(PLATE_WORLD, embeds, "poster", WHERE, species="press") is None
    assert B.embed_error(PLATE_WORLD, embeds, "poster", WHERE, species="deck") is None


def test_a_named_surface_whose_quad_is_broken_fails_at_the_dock_that_names_it(tmp_path):
    embeds = B.plate_embeds(_plate_with_embeds(tmp_path, {"poster": {"quad": [[0.3, 0.2], [0.8, 0.2], [0.8, 0.6]]}}))
    err = B.embed_error(PLATE_WORLD, embeds, "poster", WHERE)
    assert err and "four [x, y] corners" in err, err


# ---- what the dock carries onto the timeline -------------------------------------------------------------

def test_the_entry_carries_the_surface_its_quad_the_dimming_second_and_the_pictures_aspect():
    e = B.embed_entry("poster", {"quad": POSTER, "darken": 7.0}, card_aspect=160 / 528)
    assert e["name"] == "poster" and e["quad"] == [[round(v, 5) for v in p] for p in POSTER]
    assert e["darken"] == 7.0 and e["img"] == round(160 / 528, 5)
    plain = B.embed_entry("paper", {"quad": PAPER})
    assert "darken" not in plain and "img" not in plain, "only what the plate declared"


def test_the_dimming_word_is_dated_against_the_builds_own_words():
    words = [{"w": "the", "start": 1.0, "end": 1.2}, {"w": "wall", "start": 1.2, "end": 1.6},
             {"w": "behind", "start": 1.6, "end": 2.0}, {"w": "him", "start": 2.0, "end": 2.4}]
    e = B.embed_entry("poster", {"quad": POSTER, "darken": "the wall"}, words=words)
    assert e["darken"] == 1.0, "the second the take says the word"
    with pytest.raises(ValueError) as no_words:
        B.embed_entry("poster", {"quad": POSTER, "darken": "the wall"})
    assert "no words to date it by" in str(no_words.value)
    with pytest.raises(ValueError) as missing:
        B.embed_entry("poster", {"quad": POSTER, "darken": "the ceiling"}, words=words)
    assert "the ceiling" in str(missing.value)


def test_a_dock_entry_carries_embed_only_when_the_row_asks():
    e = B.embed_entry("poster", {"quad": POSTER, "darken": 7.0}, card_aspect=0.3)
    d = B.dock_entry("ev-quote", 0, 5.0, 20.0, 0, B.DOCK_KIND_IMAGE, None, "throw", "paper", False, embed=e)
    assert d["embed"] == e and d["arrive"] == "throw"
    plain = B.dock_entry("ev-quote", 0, 5.0, 20.0, 0)
    assert "embed" not in plain, "a build that never embeds is byte-for-byte what it was"


def test_the_picture_aspect_is_read_off_the_file_because_the_player_cannot_wait_for_a_decode(tmp_path):
    png = tmp_path / "card.png"
    sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
    from build_golden_sources import png_solid  # noqa: E402
    png.write_bytes(png_solid(640, 400, (23, 105, 194)))
    assert B.image_aspect(png) == 0.625
    assert B.image_aspect(tmp_path / "nothing.png") is None
    mp4 = tmp_path / "clip.mp4"; mp4.write_bytes(b"\x00\x00\x00\x18ftypmp42")
    assert B.image_aspect(mp4) is None, "a video dock has no still to measure"


# ---- the camera may take a surface as its target (E59 reason 4) -------------------------------------------

def test_the_camera_takes_a_declared_surface_as_a_target_and_the_compiler_resolves_its_quad():
    assert B.EMBED_TARGET in B.SPECIES_TARGETS["punch"]
    assert B.EMBED_TARGET in B.SPECIES_TARGETS["focus_zoom"]
    assert B.EMBED_TARGET not in B.SPECIES_TARGETS["callout"], "a callout points at a phrase, not at a wall"
    punch = {"kind": "punch", "at": 12.0, "dur": 1.6, "target": {"kind": "embed", "name": "poster"}}
    assert B.validate_species([punch], (0, 0, 0), "plate-study") == []
    B.resolve_embed_targets([punch], {"poster": {"quad": POSTER}}, "shot row 3")
    assert punch["target"]["quad"] == [[round(v, 5) for v in p] for p in POSTER], "the player resolves a region, never a manifest"
    bad = {"kind": "punch", "at": 1.0, "dur": 1.0, "target": {"kind": "embed"}}
    errs = B.validate_species([bad], (0, 0, 0), "plate-study")
    assert errs and "target embed must NAME" in errs[0], errs
    with pytest.raises(ValueError) as unknown:
        B.resolve_embed_targets([{"kind": "punch", "target": {"kind": "embed", "name": "tv"}}],
                                {"poster": {"quad": POSTER}}, "shot row 3")
    assert "is not a surface of this plate" in str(unknown.value) and "poster" in str(unknown.value)


# ---- the golden surface, as committed ---------------------------------------------------------------------

# Until the compiler carries a surface's `kind`, the ENGINE decides the treatment by the surface's NAME:
# scene-evidence-engine.mjs' EMBED_SCREEN. A screen DISPLAYS its card (the plate's own light composited back
# over it, the bezel's inner falloff, the paper lifted toward the light); a paper simply carries it.
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
SCREENS = ("tv", "laptop")


def engine_screen_names() -> set:
    m = re.search(r"const EMBED_SCREEN = /\^\(([a-z|]+)\)", ENGINE.read_text(encoding="utf-8"))
    assert m, "the engine no longer names its screen surfaces where this test reads them"
    return set(m.group(1).split("|"))


def test_the_golden_displays_a_press_card_on_the_tv_and_lays_a_record_on_the_desk_paper():
    """`art-embed`, the committed source: two NAMED surfaces on one plate, a press card on the SCREEN and a
    record on the desk paper, the room dimming on the screen's word, and the punch aimed at it by name. The two
    surfaces are the two TREATMENTS, in one frame (P50 T7 second watch, 2026-09-12) - and the card fills each
    of them corner to corner, which is what the golden frame itself is judged on."""
    tl = json.loads((GOLDEN / "art-embed.timeline.json").read_text(encoding="utf-8"))
    assert tl["aspect"] == "9:16", "a card on a wall has to read on a phone"
    quote, record = tl["scenes"][0]["docks"]
    assert quote["kind"] == B.DOCK_KIND_PRESS and quote["embed"]["name"] == "tv"
    assert quote["embed"]["quad"] == MEASURED["art-embed-study-tv-laptop"]["tv"], \
        "the golden's screen is the quad MEASURED on the approved plate, not a shape drawn for the test"
    assert quote["embed"]["darken"] == 7.0 and quote["embed"]["img"] == round(160 / 528, 5)
    assert quote["arrive"] == "throw", "a throw lands ONTO the surface with its impact"
    assert "place" not in quote and "stack_index" not in quote, "the surface is the park: no place, no pile"
    assert record["embed"]["name"] == "paper" and "darken" not in record["embed"]
    assert record["badge_at"] and record["embed"]["img"] == 0.625, "the badges ride the projection"
    names = engine_screen_names()
    assert quote["embed"]["name"] in names and record["embed"]["name"] not in names, \
        "the golden carries one surface of each treatment: a screen and a paper"
    under, punch = tl["scenes"][0]["species"]
    assert under["form"] == "underline" and under["target"] == {"kind": "phrase", "dock": quote["slide"]}
    assert punch["target"]["kind"] == "embed" and punch["target"]["name"] == "tv"
    assert punch["target"]["quad"] == quote["embed"]["quad"], "the eye and the card read the same surface"
    for surface in (quote["embed"], record["embed"]):
        assert B.embed_quad_error(surface["name"], surface, "the golden") is None


def test_every_surface_the_approved_plates_declare_falls_on_the_right_side_of_the_engines_name_line():
    """The naming default is only safe while it is TRUE of the plates in hand: the two TVs and the laptop are
    screens, the poster and the washi paper are not. A plate that declared a screen under another name would
    be carried as a paper - which is why `embed_entry` should pass `kind` and `sheen` through (two lines), and
    why this test fails the day a new surface name arrives without them."""
    names = engine_screen_names()
    assert {"tv", "laptop"} <= names and not names & {"poster", "paper", "washi", "desk"}
    for stem, want in sorted(MEASURED.items()):
        for name in sorted(want):
            assert (name in names) == (name in SCREENS), f"{stem} {name}: the engine would treat it as the other kind"


# ---- the APPROVED plates, measured (P50 T7, operator 2026-09-12: "The frames are fine") --------------------
# Three Flow stills the operator approved as ART-embed study plates, each with its surfaces MEASURED on the
# rendered stage by channel-assets/money-physics/plates/measure_embed_quads.py and written to the plate's own
# `<plate>.layers.json`. The quads below are those files, copied here so a re-measurement that MOVES a surface
# has to move a test too - a plate's geometry is a committed number, not a number the tool happens to print.
#
# STAGE fractions, not still fractions: the player paints the world plate on `.world`, which is `inset: -5%`
# with `background-size: cover`, so a 768 x 1376 still lands on the 1080 x 1920 stage at
# `stage_px = still_px * 1.546875 + (-54, -104.25)`. A quad read off the raw still would sit 5 % inside the
# surface it was measured on. The engine reads these as `p[0] * STAGE_W, p[1] * STAGE_H` (embedQuadPx).
PLATES = ROOT / "content/video_engine/channel-assets/money-physics/plates"
sys.path.insert(0, str(PLATES))
import measure_embed_quads as MQ  # noqa: E402

MEASURED = {
    "art-embed-study-poster": {
        "poster": [[0.35462, 0.16036], [0.86549, 0.11772], [0.86436, 0.6389], [0.35462, 0.62276]],
    },
    "art-embed-study-tv-laptop": {
        "laptop": [[0.61254, 0.6422], [0.95951, 0.64818], [0.94647, 0.78303], [0.59626, 0.76932]],
        "tv": [[0.23287, 0.20871], [0.9683, 0.20913], [0.96744, 0.50337], [0.2329, 0.49721]],
    },
    "art-embed-washi-tv": {
        "paper": [[0.0, 0.46697], [1.0, 0.46697], [1.0, 1.0], [0.0, 1.0]],
        "tv": [[0.11402, 0.1411], [0.88743, 0.141], [0.88743, 0.39427], [0.11399, 0.38744]],
    },
}


def test_each_approved_plate_declares_its_measured_surfaces_through_the_compilers_own_reader():
    """The file the measurement wrote is the file the COMPILER reads: `<plate>.layers.json` beside the plate,
    the `embed` key, a named set of quads - `plate_embeds`' rule and nothing else. And the stage fractions in
    it are the ones the player will use, so the placement the tool measured against is asserted here too."""
    place = MQ.cover_placement(768, 1376, "9:16")
    assert (round(place["scale"], 6), round(place["ox"], 2), round(place["oy"], 2)) == (1.546875, -54.0, -104.25), \
        "the world plate is painted over 110 % of the stage by cover - measure anywhere else and the card misses"
    for stem, want in sorted(MEASURED.items()):
        side = PLATES / f"{stem}{B.FG_LAYERS_SUFFIX}"
        assert side.exists(), f"{side.name} is the measurement - without it the plate declares no surface"
        got = B.plate_embeds(PLATES / f"{stem}.png")
        assert sorted(got) == sorted(want), f"{stem} declares {sorted(got)}, measured {sorted(want)}"
        assert sorted(got) == sorted(MQ.SURFACES[stem]), \
            f"{stem}: the tool and the file name different surfaces - a re-roll would be measured differently"
        for name, quad in sorted(want.items()):
            assert got[name]["quad"] == quad, f"{stem} {name} has moved"
            assert got[name]["darken"] is None, \
                f"{stem} {name}: the plate declares the surface, the BUILD dates the dimming on its own word"
            assert all(0.0 <= v <= 1.0 for p in got[name]["quad"] for v in p), "a stage fraction, corner to corner"


def test_every_measured_quad_is_a_lawful_surface_a_card_can_be_read_on():
    """`embed_quad_error`'s whole law on every surface the three plates declare: four corners on the stage,
    convex and in TL TR BR BL order, and at least EMBED_MIN_W of the stage wide. The narrowest of the five is
    the laptop's screen at 35 % - none is under the floor, so none needs recording as a surface that cannot
    carry a card; the floor itself is proved to still bite by shrinking that same screen under it."""
    widths = {}
    for stem, want in sorted(MEASURED.items()):
        embeds = B.plate_embeds(PLATES / f"{stem}.png")
        for name, spec in sorted(embeds.items()):
            where = f"{stem} embed {name}"
            assert B.embed_quad_error(name, spec, where) is None, B.embed_quad_error(name, spec, where)
            q = spec["quad"]
            widths[f"{stem}/{name}"] = ((q[1][0] - q[0][0]) + (q[2][0] - q[3][0])) / 2
            world = {"asset_id": stem, "sha256": "0" * 64}
            assert B.embed_error(world, embeds, name, where, species="press") is None, "a press card may land"
            assert B.embed_error(world, embeds, name, where, species="chart") is not None, "B1 still holds"
    assert min(widths.values()) >= B.EMBED_MIN_W, widths
    narrowest = min(widths, key=widths.get)
    assert narrowest == "art-embed-study-tv-laptop/laptop" and round(widths[narrowest], 3) == 0.349, widths
    assert round(widths["art-embed-washi-tv/paper"], 3) == 1.0, "the washi ground is the stage, edge to edge"
    # the floor is not decoration: the same screen, shrunk about its own centre until it is under a quarter of
    # the stage, is refused by name - so a surface that could not carry a readable card never reaches a dock.
    lap = MEASURED["art-embed-study-tv-laptop"]["laptop"]
    cx = sum(p[0] for p in lap) / 4
    shrunk = [[round(cx + (x - cx) * 0.6, 5), y] for x, y in lap]
    err = B.embed_quad_error("laptop", {"quad": shrunk}, "the floor")
    assert err and "of the stage wide" in err and "25% floor" in err, err


def test_a_surfaces_kind_reaches_the_entry_and_a_screen_is_declared_as_one():
    """E66: the plate declares the surface's treatment - `kind` (screen | paper) and `sheen` pass through embed_entry;
    the TVs and the laptop are screens, the poster and the washi paper are paper."""
    import json
    q = [[0.2, 0.2], [0.9, 0.2], [0.9, 0.5], [0.2, 0.5]]
    e = B.embed_entry("tv", {"quad": q, "kind": "screen", "sheen": 0.3})
    assert e["kind"] == "screen" and e["sheen"] == 0.3
    assert "kind" not in B.embed_entry("p", {"quad": q})
    plates = ROOT / "content/video_engine/channel-assets/money-physics/plates"
    kinds = {}
    for fn in ("art-embed-study-poster", "art-embed-study-tv-laptop", "art-embed-washi-tv"):
        for name, spec in json.loads((plates / f"{fn}.layers.json").read_text(encoding="utf-8"))["embed"].items():
            kinds[(fn, name)] = spec.get("kind")
    assert kinds[("art-embed-study-tv-laptop", "tv")] == "screen" and kinds[("art-embed-study-tv-laptop", "laptop")] == "screen"
    assert kinds[("art-embed-washi-tv", "tv")] == "screen" and kinds[("art-embed-washi-tv", "paper")] == "paper"
    assert kinds[("art-embed-study-poster", "poster")] == "paper"
