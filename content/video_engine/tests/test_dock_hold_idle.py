"""P70 T13 - the drift-hold: a held chart card or evidence dock breathes, turns a fraction and catches a light, one
whole cycle per hold (the operator, 2026-09-24: "npx hyperframes add drift-hold i think this becomes an interesting
reference to hold charts/evidence docks with"; HyperFrames drift-hold; E99 s124 as amended).

The dock option `idle: "hold" | "hold:whisper" | "hold:standard"` is an OPT-IN per dock (never a default change): a
dock that names none compiles to the entry it always did, byte for byte. An unqualified `hold` takes its grade from
the payload - `whisper` for a card carrying a chart (it must stay readable), `standard` for a picture. A prop lives
in the world and a stamp is drawn over it (E99 s128); a cutout is a person with no card: none of them is a held
CARD, so each is refused the hold by name. `hold` is not a plate's or a species' idle: `;idle=hold` stays refused.
The pose itself is `kinetics/idle.mjs` (`idle.test.mjs`); this file is the compiler's half, the engine's copy and the
dock painter's handover (the held span on the LIFE clock, the light), whose frame is the `drift-hold-tripwire` golden.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402

IDLE_MJS = ROOT / "content/video_engine/scripts/kinetics/idle.mjs"
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
COMPILER = ROOT / "content/video_engine/scripts/build_scene_timeline_f.py"
CHART_EV = {"species": "chart", "title": "t", "source": "s", "badges": []}
DECK_EV = {"species": "deck", "title": "t", "source": "s", "badges": []}


def test_idle_is_a_dock_option_and_the_hold_is_its_value():
    assert "idle" in B.DOCK_OPTS
    for v in ("hold", "hold:whisper", "hold:standard"):
        assert B.dock_opts({"idle": v}) == {"idle": v}
    assert B.DOCK_IDLES == ("hold", "hold:whisper", "hold:standard")


@pytest.mark.parametrize("bad", ["breath", "live", "hold:loud", "hold:", "HOLD", "", 1, True, None, {"hold": 1}])
def test_a_dock_idle_that_is_not_the_hold_is_refused_by_name(bad):
    with pytest.raises(ValueError) as e:
        B.dock_opts({"idle": bad})
    assert "hold|hold:whisper|hold:standard" in str(e.value), str(e.value)


@pytest.mark.parametrize("other, word", [
    ({"prop": True}, "prop"),
    ({"prop": True, "arrive": "stamp"}, "prop"),
    ({"arrive": "stamp"}, "stamp"),
    ({"cutout": True}, "cutout"),
])
def test_the_hold_is_a_cards_idle_a_prop_a_stamp_and_a_cutout_are_refused_it_by_name(other, word):
    with pytest.raises(ValueError) as e:
        B.dock_opts({"idle": "hold", **other})
    msg = str(e.value)
    assert f"idle=hold and {word}" in msg, msg
    if word in ("prop", "stamp"):
        assert "E99 s128" in msg, msg


def test_an_unqualified_hold_takes_its_grade_from_the_payload():
    assert B.dock_idle({"idle": "hold"}, CHART_EV) == "hold:whisper"      # a card carrying a chart stays readable
    assert B.dock_idle({"idle": "hold"}, DECK_EV) == "hold:standard"     # a picture
    assert B.dock_idle({"idle": "hold"}, {**DECK_EV, "chart": {"series": []}}) == "hold:whisper"   # a live chart payload
    assert B.dock_idle({"idle": "hold"}, {**DECK_EV, "card": {"profile": "card"}}) == "hold:whisper"   # a chart card
    assert B.dock_idle({"idle": "hold:standard"}, CHART_EV) == "hold:standard", "an authored grade is the author's"
    assert B.dock_idle({"idle": "hold:whisper"}, DECK_EV) == "hold:whisper"
    assert B.dock_idle({}, CHART_EV) is None
    assert B.dock_idle(None, DECK_EV) is None


def test_a_dock_that_names_no_idle_is_the_entry_it_always_was():
    args = ("ev-card", 0, 2.0, 12.0, 1)
    plain = B.dock_entry(*args)
    assert "idle" not in plain
    assert B.dock_entry(*args, idle=None) == plain
    held = B.dock_entry(*args, idle="hold:whisper")
    assert held["idle"] == "hold:whisper"
    assert {k: v for k, v in held.items() if k != "idle"} == plain, "the hold adds one key and moves nothing else"


def test_the_main_loop_hands_the_resolved_idle_to_the_entry():
    src = COMPILER.read_text(encoding="utf-8")
    assert re.search(r"docks\.append\(dock_entry\([^;]*?idle=dock_idle\(dopt, evidence\[aid\]\)", src, re.S), \
        "the dock loop resolves the row's idle against the evidence it just registered"


def test_hold_is_not_a_plate_or_a_species_idle():
    assert "hold" not in B.IDLE_KINDS, "opt-in per dock / card: a plate's and a species' kinds are unchanged"
    with pytest.raises(ValueError):
        B.split_plate_opts("plate-07;idle=hold")


def test_the_grades_are_the_modules():
    src = IDLE_MJS.read_text(encoding="utf-8")
    m = re.search(r"export const IDLE_HOLD_GRADES = Object\.freeze\(\[(.*?)\]\);", src)
    assert m, "idle.mjs names its grades"
    assert tuple(re.findall(r'"(\w+)"', m.group(1))) == B.DOCK_HOLD_GRADES
    kinds = re.search(r"export const IDLE_KINDS = Object\.freeze\(\[(.*?)\]\);", src).group(1)
    assert '"hold"' not in kinds, "the plate / species kinds are unchanged in the module too"
    cards = re.search(r"export const IDLE_CARD_KINDS = Object\.freeze\(\[(.*?)\]\);", src).group(1)
    assert tuple(re.findall(r'"([\w:]+)"', cards)) == B.DOCK_IDLES, "the dock's values are the module's card kinds"


def test_the_engine_carries_the_hold_inside_its_idle_region_and_is_in_sync():
    text = ENGINE.read_text(encoding="utf-8")
    a, b = text.index("/* KINETICS:BEGIN idle */"), text.index("/* KINETICS:BEGIN stopaction */")
    region = text[a:b]
    for name in ("const IDLE_HOLD = Object.freeze", "const IDLE_CARD_KINDS = ", "const holdPose = ", "const holdPhase = ",
                 "const holdLightCss = "):
        assert name in region, name
    r = subprocess.run([sys.executable, str(ROOT / "content/video_engine/scripts/sync_kinetics.py"), "--check"],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr


def test_the_dock_painter_hands_every_dock_its_held_span_on_the_life_clock():
    text = ENGINE.read_text(encoding="utf-8")
    assert "const holdSpanOf = (span) => (span ? { HOLD_SPAN: [lifeT(+span[0]), lifeT(+span[1])] } : {});" in text,         "a freeze beat holds every idle: the span is converted to the life clock the idle's own t is on"
    assert re.search(r"const idleCssFor = \(cls, override, t, seed, salt, span\) => .*holdSpanOf\(span\)", text)
    dock_call = r'idleCssFor\("dock", d\.idle, t, Math\.round\(d\.enter \* 100\) \+ (?:\(d\.slot \| 0\)|s), 3'
    assert len(re.findall(dock_call + r", \[d\.enter, d\.exit\]\)", text)) == 4, "the four dock paths hand over the span"
    assert len(re.findall(dock_call + r"\)", text)) == 0, "no dock path is left without it"
    assert len(re.findall(r'idleCssFor\("(?:page|pill|caption)"', text)) >= 4, "every other class's call is untouched"
    assert not re.search(r'idleCssFor\("(?:page|pill|caption)"[^;]*\[d\.enter', text)


def test_the_light_is_painted_once_per_dock_and_only_for_a_card_that_holds():
    text = ENGINE.read_text(encoding="utf-8")
    assert text.count("paintHoldLight(el, d, t);") == 1
    body = text[text.index("const paintHoldLight = "):]
    body = body[:body.index("};") + 2]
    assert "if (!holdGradeOf(k)) { if (lt) lt.style.display = \"none\"; return; }" in body,         "a dock that does not hold mounts nothing (and hides a light a previous card left)"
    assert "holdLightCss(x, el.clientWidth, el.clientHeight)" in body and "holdSpanOf([d.enter, d.exit])" in body
