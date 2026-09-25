"""P71 T12 (was P69 T42; A59's BUY folded in from P69 T60): the chip's STATES - `lit` (a held halo; `pulse` blinks it),
`tick_at` (a two-stroke check, the cross's sibling) and `tab` / `tab_at` (a SELL / BUY tab on the card's top edge).

At 7789afa `_validate_chip` refused `state: "lit"` ("chip: state must be one of on|crossed"), and `tab`, `tab_at`,
`tick_at` and `pulse` - and `glyph` (P71 T18's key, not this slice's) - were ACCEPTED AND IGNORED (review finding 7): no
error named them, on the glyph chip or on the stamp form. These tests pin the new states' grammar, every by-name refusal
the slice introduces (rule h, s106: "a silent drop is neither advice nor refusal"), the gate's credit (a held halo 0 events
- s91; a blink, a tick and a tab each an event on its word - s99), the compiler's and the gate's clocks against the
module's, the inks against the template's, and the golden."""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "scripts"))
import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import ledger_page as LPG  # noqa: E402

CHIP_MJS = "./content/video_engine/scripts/species/chip.mjs"
TEMPLATE = ROOT / "docs" / "content-video-engine" / "samples" / "scene-evidence-player.template.html"
CARDS = ROOT / "content" / "video_engine" / "effects" / "cards" / "species.json"
GOLDEN = "chip-states-sell"


def chip(**extra) -> dict:
    """A glyph chip on the NVIDIA / hynix board (H row 7's NVIDIA_CHIP, the Lucide `cpu` glyph)."""
    entry = {"kind": "chip", "at": 5.0, "dur": 8.0, "icon": "cpu", "label": "NVIDIA", "idle": "breath",
             "target": {"kind": "point", "x": 0.4, "y": 0.62}}
    entry.update(extra)
    return entry


def stamp(**extra) -> dict:
    entry = {"kind": "chip", "form": "stamp", "arrive": "stamp", "at": 10.0, "dur": 6.0,
             "icon": "prop-icon-gpu-ai-accelerator-v1", "label": "NVIDIA", "ink": "charcoal",
             "target": {"kind": "point", "x": 0.5, "y": 0.36}}
    entry.update(extra)
    return entry


def errors(entry: dict) -> list[str]:
    return B.validate_species([entry], (0, 0, 0), "plate-plain")


def node_json(js: str):
    r = subprocess.run(["node", "--input-type=module", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def module_chip() -> dict:
    return node_json(f"import {{ CHIP }} from '{CHIP_MJS}'; console.log(JSON.stringify(CHIP));")


# ---------------------------------------------------------------- the grammar
@pytest.mark.parametrize("extra", [
    {"state": "lit"},
    {"state": "lit", "pulse": True},
    {"tick_at": 8.0},
    {"tab": "sell"},
    {"tab": "sell", "tab_at": 7.0},
    {"tab": "buy", "tab_at": 12.9},
    {"state": "lit", "tab": "buy", "tab_at": 6.0},
    {"state": "lit", "tick_at": 9.0},
    {"state": "lit", "cross_at": 9.0},
    {"tab": "sell", "readability": "landscape-phone"},
])
def test_the_states_validate_and_the_entry_is_not_mutated(extra):
    entry = chip(**extra)
    before = copy.deepcopy(entry)
    assert errors(entry) == [], extra
    assert entry == before


def test_every_chip_that_validated_before_still_does():
    for entry in (chip(), chip(state="on"), chip(state="crossed"), chip(cross_at=9.0), stamp()):
        assert errors(entry) == [], entry
    assert B.CHIP_STATES[:2] == ("on", "crossed"), "the existing states keep their order"


REFUSED = [
    ("pulse on a chip that is not lit", {"pulse": True}, "pulse blinks a LIT chip's halo"),
    ("pulse on a crossed chip", {"state": "crossed", "pulse": True}, "pulse blinks a LIT chip's halo"),
    ("pulse not true", {"state": "lit", "pulse": 2}, "pulse must be true"),
    ("pulse as a string", {"state": "lit", "pulse": "yes"}, "pulse must be true"),
    ("pulse with no room for its blinks", {"state": "lit", "pulse": True, "dur": 1.5}, "pulse needs 2.05 s"),
    ("tick_at not a number", {"tick_at": "soon"}, "'tick_at' must be a number"),
    ("tick_at a bool", {"tick_at": True}, "'tick_at' must be a number"),
    ("tick_at before at", {"tick_at": 4.0}, "tick_at 4.0 is not after at 5.0"),
    ("tick_at on at", {"tick_at": 5.0}, "tick_at 5.0 is not after at 5.0"),
    ("tick_at after the chip left", {"tick_at": 13.0}, "tick_at 13.0 is not inside the chip's window"),
    ("tick_at with cross_at", {"tick_at": 8.0, "cross_at": 9.0}, "a thing held or failed, not both"),
    ("tick_at on a crossed chip", {"tick_at": 8.0, "state": "crossed"}, "a thing held or failed, not both"),
    ("tick_at and a tab on one chip", {"tick_at": 8.0, "tab": "sell"}, "the check badge and the tab share the card's top edge"),
    ("a number as a tab", {"tab": 120}, "tab 120 is a number"),
    ("a price as a tab", {"tab": "$120"}, "tab '$120' is a number"),
    ("a share count as a tab", {"tab": "1,000"}, "tab '1,000' is a number"),
    ("a percent as a tab", {"tab": "5%"}, "tab '5%' is a number"),
    ("an unknown tab", {"tab": "hold"}, "tab must be one of sell | buy"),
    ("an upper-case tab", {"tab": "SELL"}, "tab must be one of sell | buy"),
    ("tab_at without a tab", {"tab_at": 7.0}, "tab_at times a tab, and the chip names none"),
    ("tab_at not a number", {"tab": "sell", "tab_at": "on sell"}, "'tab_at' must be a number"),
    ("tab_at before at", {"tab": "sell", "tab_at": 4.0}, "tab_at 4.0 is not after at 5.0"),
    ("tab_at after the chip left", {"tab": "sell", "tab_at": 14.0}, "tab_at 14.0 is not inside the chip's window"),
]


@pytest.mark.parametrize("name,extra,needle", REFUSED, ids=[r[0] for r in REFUSED])
def test_a_malformed_or_misplaced_state_is_refused_by_name(name, extra, needle):
    errs = errors(chip(**extra))
    assert any(needle in e for e in errs), (name, errs)


@pytest.mark.parametrize("key,value", [("pulse", True), ("tick_at", 12.0), ("tab", "sell"), ("tab_at", 12.0)])
def test_the_stamp_form_refuses_every_state_by_name_a_seal_says_its_verdict_in_its_ring_text(key, value):
    errs = errors(stamp(**{key: value}))
    assert any(f"chip stamp: {key} is not supported" in e and "E99 s121" in e for e in errs), errs


def test_the_stamp_form_still_refuses_state_and_cross_at_as_it_did():
    for extra in ({"state": "lit"}, {"state": "crossed"}, {"cross_at": 12.0}):
        assert "chip stamp: state/cross_at are not supported - the prop leaves with its authored dur" in errors(stamp(**extra))


def test_the_tab_number_rule_never_catches_the_two_moves():
    for word in B.CHIP_TABS:
        assert not B.CHIP_TAB_NUMBER.match(word)
    for n in ("120", "$120", "1,000", "5%", "-3.5", "10x", "(12)", "€5", "2.5M"):
        assert B.CHIP_TAB_NUMBER.match(n), n


# ---------------------------------------------------------------- the gate
def scene(*species) -> list[dict]:
    return [{"scene_id": "s-chip", "span": [0.0, 40.0], "species": list(species)}]


def test_the_gate_a_held_halo_is_zero_events_and_a_plain_chip_counts_as_it_did():
    assert G._species_events(scene(chip())) == [5.0]
    assert G._species_events(scene(chip(cross_at=9.0))) == [5.0, 9.0]
    assert G._species_events(scene(chip(state="lit"))) == [5.0], "a light that sits is an annotation (s91)"


def test_the_gate_a_pulse_is_one_event_per_blink_onset():
    ons = [round(5.0 + 0.55 + k * 0.5, 2) for k in range(3)]
    assert G._species_events(scene(chip(state="lit", pulse=True))) == [5.0] + ons
    assert G._species_events(scene(chip(pulse=True))) == [5.0], "a pulse on a chip that is not lit blinks nothing"
    assert G._species_events(scene(chip(state="lit", pulse=True, dur=1.0))) == [5.0, 5.55], "no blink after the chip left"


def test_the_gate_the_tick_and_the_tab_each_land_on_their_word():
    assert G._species_events(scene(chip(tick_at=8.0))) == [5.0, 8.0]
    assert G._species_events(scene(chip(tab="sell", tab_at=7.0))) == [5.0, 7.0]
    assert G._species_events(scene(chip(tab="sell"))) == [5.0], "a tab with no tab_at lands with the chip: one landing"


# ---------------------------------------------------------------- the clocks and the inks, against the module
def test_the_compiler_and_the_gate_mirror_the_modules_clocks():
    m = module_chip()
    assert (B.CHIP_LAND_S, B.CHIP_CROSS_S, B.CHIP_PULSE_N, B.CHIP_PULSE_S) == (m["LAND_S"], m["CROSS_S"], m["PULSE_N"], m["PULSE_S"])
    assert G.CHIP_PULSE == {"land_s": m["LAND_S"], "n": m["PULSE_N"], "s": m["PULSE_S"]}
    onsets = node_json(f"import {{ chipPulseOnsets }} from '{CHIP_MJS}';"
                       "console.log(JSON.stringify(chipPulseOnsets({at: 5, state: 'lit', pulse: true})));")
    assert [round(v, 6) for v in onsets] == [round(5.0 + m["LAND_S"] + k * m["PULSE_S"], 6) for k in range(m["PULSE_N"])]


def _css_var(name: str) -> str:
    m = re.search(r"--" + re.escape(name) + r":\s*(#[0-9A-Fa-f]{6})", TEMPLATE.read_text(encoding="utf-8"))
    assert m, name
    return m.group(1).upper()


def test_the_inks_are_the_templates_sign_inks_and_focus_yellow():
    m = module_chip()
    assert m["TAB_INK"] == {"sell": _css_var("lp-neg"), "buy": _css_var("lp-pos")}, "E28's sign inks"
    assert m["TICK_INK"] == _css_var("lp-pos")
    sq = re.search(r"#species \.sq, #species-under \.sq \{[^}]*stroke: (#[0-9A-Fa-f]{6})", TEMPLATE.read_text(encoding="utf-8"))
    assert sq and m["LIT_INK"] == sq.group(1).upper(), "the halo is the focus yellow, the .sq hand's"
    assert m["LIT_INK"] != "#E8B86D", "never the seal's gold"


def test_the_tab_word_is_at_the_s90_floor():
    assert module_chip()["TAB_TYPE"] >= round(LPG.CARD_TYPE_PX, 2)


# ---------------------------------------------------------------- the card and the golden
def test_the_card_names_the_states_as_options():
    card = next(c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"] if c["id"] == "species:chip")
    tokens = {o["token"] for o in card["options"]}
    assert {"state", "pulse", "tick_at", "tab", "tab_at"} <= tokens
    assert "P71 T12" in card["doctrine"]
    assert any("A59" in b["source"] for b in card["blends"]) and any("A36" in b["source"] for b in card["blends"])


def test_the_sell_golden_is_registered_and_judged_after_the_tab_settles():
    sys.path.insert(0, str(ROOT / "content" / "video_engine" / "tests" / "golden"))
    import build_golden_sources as S
    tl, uris = S.SURFACES[GOLDEN]()
    chips = [sp for s in tl["scenes"] for sp in s["species"] if sp["kind"] == "chip"]
    tabbed = [sp for sp in chips if "tab" in sp]
    assert len(chips) == 2 and len(tabbed) == 1 and tabbed[0]["tab"] == "sell"
    sp, t = tabbed[0], S.FRAME_T[GOLDEN]
    assert sp["tab_at"] + B.CHIP_LAND_S <= t < sp["at"] + sp["dur"], "judged on the settled tab, the chip still standing"
    for c in chips:
        assert errors(c) == []
    for suffix, payload in (("timeline", tl), ("uris", uris)):
        assert b"\r" not in committed_source_bytes(f"{GOLDEN}.{suffix}.json", payload)


def committed_source_bytes(name: str, payload: dict) -> bytes:
    """The golden source AS COMMITTED (LF): the index copy via `git show :<path>`, else the generator's serialisation."""
    rel = f"content/video_engine/tests/golden/sources/{name}"
    try:
        r = subprocess.run(["git", "show", f":{rel}"], cwd=ROOT, capture_output=True, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        r = None
    if r is not None and r.returncode == 0:
        return r.stdout
    return (json.dumps(payload, indent=1, sort_keys=True) + "\n").encode("utf-8")
