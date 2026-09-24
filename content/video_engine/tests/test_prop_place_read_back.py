"""R26-298 - A READ-BACK PLAN KEEPS A PROP'S AUTHORED PLACE, REST AND MOVES.

P69 T26d gave a prop dock an AUTHORED `place` {x, y, w} (stage fractions), a resting `rot` and `moves` (fractions,
`at` in seconds or a phrase). The compiler writes a DERIVED pixel box `place` {x, y, w, h} and DERIVED pixel-box
`moves` onto the compiled dock, which the deriver must never copy back (fixes5b: the compiler refuses them). So the
compiled dock also records what the author wrote - `authored_place` / `authored_moves` - and the deriver copies THOSE
back as the option `place` / `moves`. `rot` is carried onto the compiled dock as authored (rounded to 3 dp).

The round trip below: a plan with a placed, moved prop -> the compiler accepts it -> the dock compiled by the
functions the row loop calls -> `derive_beat_moves.derive` reads the cut back -> the read-back plan carries the same
place / rot / moves, and the compiler accepts it again.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import derive_beat_moves as D  # noqa: E402
import render_baseline as RB  # noqa: E402
from authoring import shapes as SH  # noqa: E402

SURFACE = "prop-stamp"
ASSET = "dock-a-fed-stamp"
PLACE = {"x": 0.62, "y": 0.62, "w": 0.12}
ROT = -4
MOVES = [{"at": 14.0, "x": 0.4, "y": 0.66, "w": 0.16, "dur": 1.0, "ease": "minjerk"},
         {"at": 16.0, "rot": 6, "dur": 0.6}]
OPTIONS = {"prop": True, "arrive": "stamp", "mass": "ink", "ink": "own", "place": PLACE, "rot": ROT, "moves": MOVES}
SENTENCE = "The Fed stamps its mark on the page and moves it."
PAGE = "ledger:ev-a-v1:line:3:right:axes:cut"   # the shapes compiler opens on a page (E99 s66: it never invents one)


def _record(options: dict) -> dict:
    """One beat in M41's schema, on a chart page, whose sentence STAMPS the placed, moved prop on its first words."""
    return {"beat": 1, "t0": G.PROP_STAMP_ENTER, "t1": G.PROP_STAMP_EXIT, "sentence": SENTENCE,
            "act": "none of the 11 - it states the claim", "comparator": {"compared_to": "this against that"},
            "capabilities": [], "recipe": None, "why_none": "no proven recipe names this combination",
            "plate": PAGE, "source": "a fixture",
            "moves": [{"kind": SH.MOVE_DOCK, "at_word": "The Fed", "asset": ASSET, "options": copy.deepcopy(options)}]}


def _take() -> list[dict]:
    """The sentence laid word by word across the beat, the way `authoring/words.py` reads a real take."""
    toks = SENTENCE.split()
    t0, t1 = G.PROP_STAMP_ENTER, G.PROP_STAMP_EXIT
    step = (t1 - t0) / len(toks)
    return [{"w": w, "start": round(t0 + i * step, 2), "end": round(t0 + i * step + min(step, 0.35), 2)}
            for i, w in enumerate(toks)]


def _compiled_dock() -> dict:
    """The prop dock as the row loop compiles it: dock_opts -> the stamp fit -> prop_moves -> dock_entry."""
    if not G.PROP_CUTOUT.is_file():
        pytest.skip(f"the gitignored prop cutout is not in this checkout: {G.PROP_CUTOUT.name}")
    tl, _uris, _t, _a = RB.load_surface(SURFACE)
    world = copy.deepcopy(tl["scenes"][0]["world"])
    dopt = B.dock_opts(copy.deepcopy(OPTIONS))
    fed = B.painted_box(G.PROP_CUTOUT)
    fit = B.stamp_dock_place(world, "16:9", dopt, fed, None, None, "t")
    moves, _w = B.prop_moves(dopt, fed, fit, "16:9", G.PROP_STAMP_ENTER, G.PROP_STAMP_EXIT, None, "t", world)
    return B.dock_entry(ASSET, 0, G.PROP_STAMP_ENTER, G.PROP_STAMP_EXIT, 0, B.DOCK_KIND_PROP,
                        {k: fit[k] for k in ("x", "y", "w", "h", "room")}, "stamp", "ink", True, prop=True,
                        ink="own", ring_to=fit["ring_to"], from_to=fit["from_to"], paint=fit["paint"],
                        rot=dopt.get("rot"), moves=moves,
                        authored_place=dopt.get("place"), authored_moves=dopt.get("moves"))


def _build(tmp_path: Path, dock: dict) -> Path:
    """A build dir the deriver reads: the plan, the take, and ONE compiled timeline carrying the dock."""
    build = tmp_path / "project" / "build-x"
    build.mkdir(parents=True)
    (build / D.PLAN_NAME).write_text(json.dumps(_record(OPTIONS)) + "\n", encoding="utf-8")
    (build / D.WORDS_NAME).write_text(json.dumps({"words": _take()}), encoding="utf-8")
    scene = {"scene_id": "s1", "span": [G.PROP_STAMP_ENTER, G.PROP_STAMP_EXIT], "species": [], "docks": [dock]}
    (build / "x.timeline.json").write_text(json.dumps({"scenes": [scene]}), encoding="utf-8")
    return build


def _dock_options(plan: list[dict]) -> dict:
    [move] = [m for r in plan for m in r.get("moves") or [] if m.get("kind") == SH.MOVE_DOCK]
    return move["options"]


def test_the_compiler_accepts_the_plan_with_a_placed_moved_prop():
    plan = [_record(OPTIONS)]
    rows, _ = SH.compile(plan, _take(), SH.DEFAULTS, "16:9")
    assert [d[0] for d in rows[0][4]] == [ASSET], rows[0][4]


def test_the_compiled_dock_records_the_authored_place_and_moves_beside_the_derived_boxes():
    dock = _compiled_dock()
    assert dock["authored_place"] == PLACE and dock["authored_moves"] == MOVES
    assert set(dock["place"]) == {"x", "y", "w", "h"} and dock["place"] != PLACE      # the derived pixel box
    assert dock["moves"] != MOVES and dock["rot"] == ROT                              # derived boxes; the rest as authored


def test_a_dock_that_authors_no_place_or_moves_writes_no_authored_key():
    d = B.dock_entry("a", 0, 1, 5, 0, B.DOCK_KIND_PROP, {"x": 1, "y": 2, "w": 3, "h": 4}, "stamp", "ink", True,
                     prop=True, ring_to=1.5, from_to=2.0, paint=[0, 0, 1, 1])
    assert "authored_place" not in d and "authored_moves" not in d


def test_the_read_back_plan_carries_the_same_place_rot_and_moves(tmp_path: Path):
    build = _build(tmp_path, _compiled_dock())
    moves, skipped = D.derive(build)
    assert skipped == [], skipped
    _was, now = D.render(build, moves)
    read_back = [json.loads(line) for line in now.decode("utf-8").splitlines() if line.strip()]
    options = _dock_options(read_back)
    assert options["prop"] is True and options["ink"] == "own" and options["arrive"] == "stamp", options
    assert options["place"] == PLACE and options["rot"] == ROT and options["moves"] == MOVES, options
    assert "authored_place" not in options and "authored_moves" not in options
    assert "centre" not in options, "a placed prop's `centre` is the row loop's, and dock_opts refuses it beside `place`"
    B.dock_opts({k: v for k, v in options.items() if k != SH.MOVE_SLOT})     # the compiler admits the read-back
    rows, _ = SH.compile(read_back, _take(), SH.DEFAULTS, "16:9")
    assert [d[0] for d in rows[0][4]] == [ASSET], rows[0][4]


def test_the_deriver_never_copies_the_derived_pixel_moves_back():
    """The compiled `moves` are whole canvas boxes in stage px - a plan carrying them is refused (off the stage)."""
    assert "moves" in SH.dock_option_keys() and "moves" not in D.dock_option_fields()
    compiled = {"slide": "dock-x", "slot": 0, "enter": 1.0, "exit": 3.0, "prop": True, "rot": 2.0,
                "place": {"x": 346, "y": 309, "w": 518, "h": 315},
                "moves": [{"at": 1.5, "dur": 0.6, "ease": "minjerk", "x": 800.0, "y": 500.0, "w": 200.0, "rot": 2.0}]}
    move = D.dock_move(compiled, "A sentence", D.dock_option_fields())
    assert move["options"] == {"prop": True, "rot": 2.0, SH.MOVE_SLOT: 0}, move


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
