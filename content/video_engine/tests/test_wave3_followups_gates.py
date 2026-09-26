"""P72 T46e - the wave-3 follow-ups: gates, tools and captions (lane B).

One section per row, each pinned by the behaviour the row asks for:

  R26-359  `audit_script_doctrine.load_timings` reads a take dir holding a NAMED words file (`scene_kokoro.words.json`)
           beside the numbered scenes: each named file is its own take, never a crash and never glued onto the numbered one.
  R26-358  `enumerate_strength_screens` takes the project's take only when it is THIS script's (the opening gate's in-order
           overlap, TAKE_OVERLAP_MIN); a foreign take is refused by name and the screens estimate; a named foreign
           `--timeline` refuses the run, as the opening gate does.
  R26-403  the motion gate credits a bars `extend` (`field: true` / `bar: k`) as new data (`_brings_new_data`).
  R26-392  the ken-versus-camera clash reads a windowed ken's (t0, t1): a camera move outside the window shares no window
           with the lean (the compiler's `validate_species` and the gate's `_camera_clashes`).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import audit_script_doctrine as A  # noqa: E402
import build_scene_timeline_f as B  # noqa: E402
import enumerate_strength_screens as ESS  # noqa: E402
import gate_motion_density as G  # noqa: E402
import gate_opening_structure as GO  # noqa: E402


# ---- R26-359: a named words file is its own take -------------------------------------------------------------------

THIS_TEXT = ("Five percent was normal once. But a yield is a price, and the price moved. "
             "The bond fund lost money on paper. Nobody sold a thing.")
OTHER_TEXT = ("The harbour cranes stopped at noon. Every container waited on a signature. "
              "The ships kept coming anyway. Nobody counted them.")


def _words(text: str, t0: float = 0.0, step: float = 0.3) -> dict:
    words, t = [], t0
    for w in text.split():
        words.append({"w": w, "start_s": round(t, 3), "end_s": round(t + step * 0.9, 3)})
        t += step
    return {"engine": "test", "duration_s": round(t, 3), "words": words}


def _take(dir_: Path, name: str, text: str) -> None:
    dir_.mkdir(parents=True, exist_ok=True)
    (dir_ / name).write_text(json.dumps(_words(text)), encoding="utf-8")


def _script(tmp: Path, text: str = THIS_TEXT, name: str = "SCRIPT-X-VO.txt") -> Path:
    p = tmp / name
    p.write_text(text + "\n", encoding="utf-8")
    return p


def test_a_named_words_file_beside_the_numbered_scenes_does_not_crash_the_loader(tmp_path):
    """The bridge's vo-short/audio holds scene_1 (the aligned take) and scene_kokoro (a second engine's): at the base the
    sort key `int(re.search(r"\\d+", name).group())` raised AttributeError on the name with no digits."""
    src = _script(tmp_path)
    _take(tmp_path / "vo-short" / "audio", "scene_1.words.json", THIS_TEXT)
    _take(tmp_path / "vo-short" / "audio", "scene_kokoro.words.json", THIS_TEXT)
    words = A.load_timings(src)
    assert words, "a take of this text is on disk - the loader must read one"
    assert [w["w"] for w in words] == THIS_TEXT.split(), "one take, not the two takes glued end to end"


def test_the_named_take_is_chosen_when_only_it_speaks_the_script(tmp_path):
    src = _script(tmp_path)
    _take(tmp_path / "vo" , "scene_1.words.json", OTHER_TEXT)
    _take(tmp_path / "vo", "scene_kokoro.words.json", THIS_TEXT)
    words = A.load_timings(src, THIS_TEXT)
    assert words and [w["w"] for w in words] == THIS_TEXT.split()
    assert A.load_timings(src, "Nothing like either take opens this way at all") is None


def test_numbered_scenes_still_join_in_their_numeric_order(tmp_path):
    src = _script(tmp_path)
    halves = THIS_TEXT.split(". ")
    first, rest = halves[0] + ".", ". ".join(halves[1:])
    d = tmp_path / "vo"
    d.mkdir()
    (d / "scene_10.words.json").write_text(json.dumps(_words(rest)), encoding="utf-8")
    (d / "scene_2.words.json").write_text(json.dumps(_words(first)), encoding="utf-8")
    words = A.load_timings(src)
    assert [w["w"] for w in words] == first.split() + rest.split(), "scene_2 before scene_10 (numeric, not lexical)"
    assert words[len(first.split())]["start"] >= words[len(first.split()) - 1]["end"], "the second scene is offset"


# ---- R26-358: the screens take the project's take only when it is this script's ------------------------------------

def test_the_screens_refuse_another_scripts_take_and_estimate(tmp_path):
    src = _script(tmp_path)
    _take(tmp_path / "vo", "scene_1.words.json", OTHER_TEXT)
    timeline, note = ESS.screens_take(src)
    assert timeline is None, "another script's clock mapped onto this text by position is not this script's clock"
    assert note and "refused" in note and "R26-203" in note and f"{GO.TAKE_OVERLAP_MIN:.2f}" in note, note
    dest, _counts = ESS.build_screens(src)
    assert note in dest.read_text(encoding="utf-8"), "the screens file says which take it refused"


def test_the_screens_keep_this_scripts_own_take(tmp_path):
    src = _script(tmp_path)
    _take(tmp_path / "vo", "scene_1.words.json", THIS_TEXT)
    timeline, note = ESS.screens_take(src)
    assert note is None and timeline and [w["w"] for w in timeline] == THIS_TEXT.split()


def test_the_screens_refuse_a_named_foreign_timeline(tmp_path, monkeypatch, capsys):
    src = _script(tmp_path)
    tl = tmp_path / "timeline.json"
    tl.write_text(json.dumps({"words": [{"w": w["w"], "start": w["start_s"], "end": w["end_s"]}
                                        for w in _words(OTHER_TEXT)["words"]]}), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["enumerate_strength_screens.py", str(src), "--timeline", str(tl)])
    assert ESS.main() == 2
    assert "refused" in capsys.readouterr().err
    assert not src.with_name("SCRIPT-X-SCREENS.md").exists(), "a refused run writes nothing"


# ---- R26-403: a bars extend brings new data ------------------------------------------------------------------------

@pytest.mark.parametrize("extend", [{"field": True}, {"bar": 2}, {"bar": 0}])
def test_a_bars_extend_brings_new_data(extend):
    x = {"kind": "chart_to", "to": "extend", "at": 9.0, "dur": 2.0, **extend}
    assert G._brings_new_data({"species": [x]}, x) is True


@pytest.mark.parametrize("extend", [{"field": False}, {"bar": None}, {}])
def test_an_extend_that_names_no_bars_data_brings_none_by_that_key(extend):
    x = {"kind": "chart_to", "to": "extend", "at": 9.0, "dur": 2.0, **extend}
    assert G._brings_new_data({"species": [x]}, x) is False


def test_a_rescale_naming_field_is_still_not_new_data():
    x = {"kind": "chart_to", "to": "rescale", "at": 9.0, "dur": 2.0, "field": True}
    assert G._brings_new_data({"species": [x]}, x) is False


# ---- R26-392: the clash reads the ken's window ---------------------------------------------------------------------

PLATE = "world-spike-desk-v1"
POINT = {"kind": "point", "x": 0.62, "y": 0.41, "semantic": "the iron spike"}


def _punch(at: float, dur: float = 1.2) -> dict:
    return {"kind": "punch", "at": at, "dur": dur, "target": POINT}


def test_a_camera_move_outside_the_kens_window_is_no_clash():
    ken = (0.04, 10, -6, 5.0, 9.0)
    assert B.validate_species([_punch(12.0)], ken, PLATE) == []
    assert B.validate_species([_punch(2.0, 2.5)], ken, PLATE) == [], "ends at 4.5, before the lean starts"


@pytest.mark.parametrize("at, dur", [(6.0, 1.0), (4.0, 1.5), (8.5, 2.0), (3.0, 8.0)])
def test_a_camera_move_inside_or_across_the_kens_window_still_clashes(at, dur):
    errs = B.validate_species([_punch(at, dur)], (0.04, 10, -6, 5.0, 9.0), PLATE)
    assert len(errs) == 1 and "punch over Ken Burns scale 0.04" in errs[0] and "s9.28 C3" in errs[0], errs
    assert "5.00-9.00s" in errs[0], "the refusal names the lean's window it shares"


def test_an_unwindowed_ken_clashes_with_any_move_as_before():
    errs = B.validate_species([_punch(40.0)], (0.04, 10, -6), PLATE)
    assert len(errs) == 1 and "punch over Ken Burns scale 0.04" in errs[0]


def _scene(species=None, ken=None, keys=None) -> dict:
    s = {"scene_id": "s01", "span": [0.0, 20.0], "species": species or [], "docks": [],
         "world": {"kind": "plate", "ken_burns": ken or {"scale": 0, "x": 0, "y": 0}}}
    if keys:
        s["camera"] = {"keys": keys}
    return s


WIN = {"scale": 0.04, "x": 10, "y": -6, "t0": 5.0, "t1": 9.0}


def test_the_gate_reads_the_window_for_a_species_move():
    assert G._camera_clashes([_scene([_punch(12.0)], WIN)]) == []
    assert G._camera_clashes([_scene([_punch(6.0)], WIN)]) == [("s01", "punch over Ken Burns scale 0.04")]
    assert G._camera_clashes([_scene([_punch(12.0)], {"scale": 0.04, "x": 10, "y": -6})]) == \
        [("s01", "punch over Ken Burns scale 0.04")], "an unwindowed ken reads as it always did"


def test_the_gate_reads_the_window_for_camera_keys():
    keys = [{"t": 12.0, "zoom": 1.0}, {"t": 14.0, "zoom": 1.2}]
    assert G._camera_clashes([_scene(None, WIN, keys)]) == []
    keys_in = [{"t": 6.0, "zoom": 1.0}, {"t": 8.0, "zoom": 1.2}]
    assert G._camera_clashes([_scene(None, WIN, keys_in)]) == [("s01", "camera keys over Ken Burns scale 0.04")]


def test_the_gate_and_the_compiler_agree_on_the_same_row():
    for at in (2.0, 4.5, 6.0, 8.9, 9.5, 12.0):
        ken = (0.04, 10, -6, 5.0, 9.0)
        compiler = bool(B.validate_species([_punch(at)], ken, PLATE))
        gate = bool(G._camera_clashes([_scene([_punch(at)], B.ken_burns_windowed(
            {"scale": ken[0], "x": ken[1], "y": ken[2]}, ken))]))
        assert compiler == gate, (at, compiler, gate)


# ---- R26-136 (5): the natural search terms reach their capability through the index's aliases ---------------------

import build_capabilities_index as BCI  # noqa: E402
import docs_find as DF  # noqa: E402

CAP_DOC = ("# CAPABILITIES\n\n## Tools\n\n| Capability | Where | State | Proof |\n|---|---|---|---|\n"
           "| **The viewer (P36)** - a windowed perception test read cold | `viewer_run.py` | LIVE | `t.py` |\n"
           "| **The viewer's screens (E43)** - folds a screen line in | `viewer_windows.py` | WIRED | `u.py` |\n")


def _alias_repo(tmp: Path, aliases: list[dict] | None) -> Path:
    (tmp / BCI.CAP_REL).parent.mkdir(parents=True, exist_ok=True)
    (tmp / BCI.CAP_REL).write_text(CAP_DOC, encoding="utf-8")
    if aliases is not None:
        (tmp / BCI.ALIASES_REL).parent.mkdir(parents=True, exist_ok=True)
        (tmp / BCI.ALIASES_REL).write_text(json.dumps({"schema": "capability-aliases.v1", "aliases": aliases}),
                                           encoding="utf-8")
    return tmp


def test_an_alias_lands_on_the_one_row_its_span_names(tmp_path):
    root = _alias_repo(tmp_path, [{"row": "The viewer (P36)", "terms": ["blind viewer"], "why": "R26-136 (5)"}])
    parsed = BCI.build(root)
    by_name = {r["name"]: r for r in parsed.records}
    assert by_name["The viewer (P36)"]["aliases"] == ["blind viewer"]
    assert "aliases" not in by_name["The viewer's screens (E43)"], "a row no alias names is the record it always was"
    assert not parsed.failures


@pytest.mark.parametrize("span, count", [("viewer", 2), ("no such row", 0)])
def test_an_alias_whose_span_names_no_row_or_two_is_refused_by_name(tmp_path, span, count):
    root = _alias_repo(tmp_path, [{"row": span, "terms": ["blind viewer"]}])
    parsed = BCI.build(root)
    assert any(span in f and f"{count} rows" in f and "R26-136" in f for f in parsed.failures), parsed.failures


def test_a_malformed_alias_entry_is_refused_by_name(tmp_path):
    root = _alias_repo(tmp_path, [{"row": "The viewer (P36)", "terms": "blind viewer"}])
    assert any("terms" in f for f in BCI.build(root).failures)


def test_no_aliases_file_writes_the_index_it_always_wrote(tmp_path):
    parsed = BCI.build(_alias_repo(tmp_path, None))
    assert not parsed.failures and all("aliases" not in r for r in parsed.records)


def test_docs_find_reaches_the_row_through_its_alias(tmp_path):
    root = _alias_repo(tmp_path, [{"row": "The viewer (P36)", "terms": ["blind viewer"]}])
    BCI.write(root, BCI.build(root))
    result = DF.search("blind viewer", ["capabilities"], root, 5)
    assert [h.line for h in result.hits] == [7], [(h.name, h.line) for h in result.hits]
    assert not result.all_words, "the PHRASE finds it (the alias), not the all-words fallback a phrase hit elsewhere skips"


def test_the_real_aliases_file_resolves_and_every_term_finds_its_row():
    """Every alias in the repo's file names exactly one CAPABILITIES row, and each of R26-136 (5)'s terms the file
    carries finds that row in the capabilities layer built from the real doc."""
    doc = json.loads((ROOT / BCI.ALIASES_REL).read_text(encoding="utf-8"))
    parsed = BCI.build(ROOT)
    assert not [f for f in parsed.failures if "alias" in f], parsed.failures
    for entry in doc["aliases"]:
        rows = [r for r in parsed.records if entry["row"].lower() in r["name"].lower()]
        assert len(rows) == 1 and set(entry["terms"]) <= set(rows[0].get("aliases", [])), entry
    assert any("blind viewer" in e["terms"] for e in doc["aliases"]), "the one term with no right hit at the base"


# ---- R26-352: the ingester re-applies the operator's hand scrub from a terms file in the operator's folder ---------

import zipfile  # noqa: E402
from xml.sax.saxutils import escape  # noqa: E402

import ingest_stock_research as ISR  # noqa: E402

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ENTITY = "Northwind Holdings"          # a planted name, never a real one
DOSSIER_STEM = "12_Applied_Digital_and_TeraWulf_Deep_Analysis"


def _docx(path: Path, paras: list[str]) -> None:
    body = "".join(f'<w:p><w:r><w:t xml:space="preserve">{escape(p)}</w:t></w:r></w:p>' for p in paras)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                                        f'<w:document xmlns:w="{W_NS}"><w:body>{body}</w:body></w:document>')


@pytest.fixture()
def research(tmp_path: Path) -> Path:
    src = tmp_path / "Stock research and ideas"
    src.mkdir()
    _docx(src / f"{DOSSIER_STEM}.docx", [
        'title: "Applied Digital and TeraWulf" category: "Single / Multi-Ticker Research" '
        'source_location: "Outside Research Folder (Root)"',
        "# Applied Digital and TeraWulf",
        f"Applied Digital leases compute capacity; the model was shared by {ENTITY} in June.",
        f"A second mention: northwind holdings asked for the lease terms, and {ENTITY}'s memo followed.",
        "Northwind Holdingsworth is another word entirely and stays.",
    ])
    return src


def _ingest(monkeypatch, tmp_path: Path, src: Path):
    out = tmp_path / "out"
    markets, runs = out / "markets" / "sovereign-compute", out / "runs" / "sovereign-compute-2026-09"
    markets.mkdir(parents=True)
    runs.mkdir(parents=True)
    for name, value in (("SOURCE_DIR", src), ("TARGET_MARKETS_DIR", markets), ("RUNS_DIR", runs), ("REPO_ROOT", out)):
        monkeypatch.setattr(ISR, name, value)
    code = ISR.main()
    return code, {p.relative_to(out).as_posix(): p.read_text(encoding="utf-8") for p in out.rglob("*") if p.is_file()}


def test_a_re_run_applies_the_terms_file_before_anything_is_written(monkeypatch, tmp_path, research, capsys):
    (research / ISR.SCRUB_TERMS_FILE).write_text(f"# the operator's hand scrub (R26-352)\n\n{ENTITY}\n", encoding="utf-8")
    code, files = _ingest(monkeypatch, tmp_path, research)
    assert code == 0 and files, files.keys()
    for rel, text in files.items():
        assert "northwind holdings" not in text.lower().replace("northwind holdingsworth", ""), rel
    doc = files[f"markets/sovereign-compute/{DOSSIER_STEM}.md"]
    assert doc.count(ISR.SCRUB_TERM_MARK) == 3 and "Northwind Holdingsworth" in doc, doc
    out = capsys.readouterr().out
    assert ENTITY.lower() not in out.lower(), "the run never prints a scrubbed term"
    assert f"1 scrub term(s) from {ISR.SCRUB_TERMS_FILE}" in out


def test_a_term_can_name_what_the_hand_scrub_left_in_its_place(monkeypatch, tmp_path, research):
    (research / ISR.SCRUB_TERMS_FILE).write_text(f"{ENTITY} => a private holder\n", encoding="utf-8")
    _code, files = _ingest(monkeypatch, tmp_path, research)
    doc = files[f"markets/sovereign-compute/{DOSSIER_STEM}.md"]
    assert "shared by a private holder in June" in doc and ISR.SCRUB_TERM_MARK not in doc, doc


def test_no_terms_file_writes_what_it_always_wrote(monkeypatch, tmp_path, research):
    _code, files = _ingest(monkeypatch, tmp_path, research)
    assert ENTITY in files[f"markets/sovereign-compute/{DOSSIER_STEM}.md"]


@pytest.mark.parametrize("line", [" => a holder", "=> x", "ab"])
def test_a_malformed_terms_line_refuses_the_run_by_its_line_and_writes_nothing(monkeypatch, tmp_path, research, capsys, line):
    (research / ISR.SCRUB_TERMS_FILE).write_text(f"{ENTITY}\n{line}\n", encoding="utf-8")
    code, files = _ingest(monkeypatch, tmp_path, research)
    assert code == 1 and not files, files.keys()
    out = capsys.readouterr().out
    assert f"{ISR.SCRUB_TERMS_FILE}:2" in out and "R26-352" in out, out


# ---- R26-349: M25 names a schematic's phase names and its tag -------------------------------------------------------
# Step (0) at 151636d: M25 already FAILED a card on a phase name or the tag (the probe reads every chart <text> as an
# item), but by the first class word - `chart.lab`, "an axis label". The schematic has no axis there: its phase names
# carry the narrative and its tag says what the page is (E99 s109 (1)). The probe names them by their own classes.

import measure_page_boxes as MPB  # noqa: E402
import probe as PR  # noqa: E402
import render_baseline as RB  # noqa: E402
import served_player as SP  # noqa: E402


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        return False
    return True


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

SCHEMATIC_GEO = """() => { const st = document.getElementById('stage').getBoundingClientRect();
  const r = (el) => { const b = el.getBoundingClientRect(); return [b.x - st.x, b.y - st.y, b.width, b.height]; };
  return { phases: [...document.querySelectorAll('text.lp-phase')].map(r).filter((b) => b[2] >= 1),
           tag: [...document.querySelectorAll('text.lp-schematic')].map(r).filter((b) => b[2] >= 1) }; }"""


def _schematic_dom(tmp: Path, aspect: str) -> tuple[dict, dict]:
    page = MPB.representative(MPB.SCHEMATIC_LINE)
    tl = MPB._timeline(page, aspect)
    html = tmp / "schematic.html"
    html.write_text(RB.instantiate(tl, {"__audio__": MPB._silence(), **B.longform_assets(tl)}), encoding="utf-8")
    w, h = RB.STAGE[aspect]
    with SP.served(html, w, h) as (pg, errs):
        pg.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                    "s.dispatchEvent(new Event('input', {bubbles:true})); }", MPB.MEASURE_T)
        pg.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                    "s.dispatchEvent(new Event('input', {bubbles:true})); }", MPB.MEASURE_T)
        dom, geo = pg.evaluate(PR.READ_DOM), pg.evaluate(SCHEMATIC_GEO)
        assert not errs, errs
    return dom, geo


def _card_over(dom: dict, box: list[float], aspect: str) -> list[str]:
    grown = [box[0] - 20, box[1] - 20, max(260.0, box[2] + 40), box[3] + 200]
    d2 = dict(dom, docks=[{"el": "card", "name": "card", "box": grown, "op": 1, "arriving": False, "paper": True}])
    inst = PR.derive(d2, MPB.MEASURE_T, "R26-349", {}, aspect, {"card": {"enter": 0.0, "exit": 29.0}}, {"card": grown})
    inst["docks"] = [dict(x, state="parked", rest=1) for x in inst["docks"]]
    return G._layout_faults({"aspect": aspect, "instants": [inst]})[0]


@needs_browser
@pytest.mark.parametrize("aspect", MPB.ASPECTS)
def test_m25_names_a_phase_name_and_the_tag_a_card_covers(tmp_path, aspect):
    dom, geo = _schematic_dom(tmp_path, aspect)
    assert geo["phases"] and geo["tag"], "the fixture draws its phase names and its tag"
    kinds = {i["k"] for i in dom["items"]}
    assert {"chart.phase", "chart.schematic"} <= kinds, kinds
    on_phase = _card_over(dom, geo["phases"][0], aspect)
    assert any(f.startswith("a phase name under card") for f in on_phase), on_phase
    on_tag = _card_over(dom, geo["tag"][0], aspect)
    assert any(f.startswith("the schematic's tag under card") for f in on_tag), on_tag
    assert not any("an axis label" in f for f in on_phase + on_tag), "a schematic draws no axis label there"


def test_the_ink_names_read_as_the_schematic_says():
    assert G._ink_name("chart.phase") == "a phase name"
    assert G._ink_name("chart.schematic") == "the schematic's tag"
    assert G._ink_name("chart.lab") == "an axis label", "every other chart label is named as it always was"


# ---- R26-368 (b): the cadence is read on the stage's own width (the node law: tests/kinetics/cadence_picture_width) --

import re  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"


def _outside_kinetics(text: str) -> str:
    """The engine with every inlined module region blanked - what is left is the engine's own code."""
    return re.sub(r"/\* KINETICS:BEGIN \w+ \*/.*?/\* KINETICS:END \*/", "", text, flags=re.S)


def test_every_throw_the_engine_itself_makes_names_its_stage():
    own = _outside_kinetics(ENGINE.read_text(encoding="utf-8"))
    calls = re.findall(r"throwXf\((?:[^()]|\([^()]*\))*\)", own)
    assert len(calls) >= 4, calls
    assert all("stage_w: STAGE_W" in c for c in calls), [c for c in calls if "stage_w" not in c]


def test_the_engine_carries_the_module_law():
    text = ENGINE.read_text(encoding="utf-8")
    assert "ON1_PW_S: 154 / 1080" in text and "STAGE_W_REF: 1080" in text
    assert "const sw = P.stage_w > 0 ? P.stage_w : P.STAGE_W_REF, on1 = P.ON1_PX_S * sw / P.STAGE_W_REF;" in text


def test_m20_reads_the_threshold_on_the_builds_stage(monkeypatch):
    """A throw at ~200 px/s (the flight slowed so the card's chord crosses in 1.9 s) is on 1s under the 1080 rule and on
    2s on a 16:9 build's 1920 stage; M20's row follows the player."""
    monkeypatch.setattr(G, "STOP_FLIGHT_S", 1.9)
    sc = {"scene_id": "s01", "span": [0.0, 10.0], "species": [], "world": {"kind": "plate"},
          "docks": [{"slide": "ev-a", "arrive": "throw", "enter": 1.0, "exit": 8.0, "place": {"w": 100}}]}
    v = ((100 + G.STOP_THROW_DX) ** 2 + G.STOP_THROW_DY ** 2) ** 0.5 / 1.9
    assert 154 < v < 273.8, v
    assert "-> on 1s" in G._cadence_gate([sc]).message
    assert "-> on 1s" in G._cadence_gate([sc], "9:16").message
    assert "-> on 2s" in G._cadence_gate([sc], "16:9").message


# ---- R26-356: the cards cite CAPABILITIES by row title, and the catalogue build resolves every one ------------------

import shutil  # noqa: E402

import build_effects_catalog as BEC  # noqa: E402

CARD_DIR = ROOT / "content/video_engine/effects/cards"
BY_LINE = re.compile(r"CAPABILITIES\.md:\d+")
CAP_REL = "docs/content-video-engine/CAPABILITIES.md"


def _strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)
    elif isinstance(obj, str):
        yield obj


def test_no_card_cites_capabilities_by_line():
    hits = {p.name: [s for s in _strings(json.loads(p.read_text(encoding="utf-8"))) if BY_LINE.search(s)]
            for p in sorted(CARD_DIR.glob("*.json"))}
    assert not {k: v for k, v in hits.items() if v}, hits


def test_every_card_row_cite_resolves_to_the_one_row_its_span_names():
    records = [r for r in BEC.build(ROOT) if r.get("axis") != "recipe"]
    cites = [c for r in records for c in r.get("row_cites", [])]
    assert len(cites) >= 92, len(cites)
    lines = (ROOT / CAP_REL).read_text(encoding="utf-8").splitlines()
    for c in cites:
        assert c["path"] == CAP_REL and c["line"], c
        span = c["ref"][len("CAPABILITIES["):-1]
        assert lines[c["line"] - 1].startswith("| **") and span.lower() in lines[c["line"] - 1].lower(), c


def _cat_tree(tmp: Path, value: str, field: str = "alias") -> Path:
    shutil.copytree(ROOT / "content/video_engine/configs", tmp / "content/video_engine/configs",
                    ignore=shutil.ignore_patterns("*.py"))
    (tmp / CAP_REL).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / CAP_REL, tmp / CAP_REL)
    card = {"id": "species:trace", "axis": "species", "token": "trace", "title": "The trace card",
            "aliases": [{"name": "trace hops", "source": value}] if field == "alias" else [],
            "does": "The trace hops on its beat.", "when": None,
            "author": {"key": "a key", "example": "'trace'", "check": "none"},
            "lives": {"form": "module", "path": "content/video_engine/scripts/kinetics/w.mjs", "symbol": "W"},
            "doctrine": [], "status": "wired", "proof": {"golden": None, "test": None},
            "callable": {"today": True, "why": None}}
    if field == "blend":
        card["blends"] = [{"source": "Bravos", "became": "the whole arc", "record": value, "tie": "recorded"}]
    d = tmp / BEC.CARDS_REL
    d.mkdir(parents=True, exist_ok=True)
    (d / "species.json").write_text(json.dumps({"schema_version": "effect_cards.v1", "axis": "species",
                                                "cards": [card]}, indent=2), encoding="utf-8")
    (tmp / "docs/DOCS-INDEX.jsonl").write_text("", encoding="utf-8")
    return tmp


WHEN_T = {"SPECIES_WHEN": {"trace": "the sentence names places"}, "CHART_TO_WHEN": {}}


@pytest.mark.parametrize("field", ["alias", "blend"])
def test_a_by_line_capabilities_cite_is_refused_by_name(tmp_path, field):
    tree = _cat_tree(tmp_path, "docs/content-video-engine/CAPABILITIES.md:96", field)
    with pytest.raises(BEC.CatalogError, match=r"species:trace.*by line.*R26-356"):
        BEC.build(tree, WHEN_T)


@pytest.mark.parametrize("span, count", [("species", "rows"), ("no row says this", "0 rows")])
def test_a_title_cite_that_names_no_row_or_many_is_refused_by_name(tmp_path, span, count):
    tree = _cat_tree(tmp_path, f"CAPABILITIES[{span}]")
    with pytest.raises(BEC.CatalogError, match=rf"species:trace.*CAPABILITIES\[{span}\].*{count}"):
        BEC.build(tree, WHEN_T)


def test_a_title_cite_follows_its_row_when_a_row_is_inserted_above(tmp_path):
    tree = _cat_tree(tmp_path, "CAPABILITIES[Trace HOPS + stacked stamps + the UNDER species layer]", "blend")
    before = BEC.build(tree, WHEN_T)[0]["row_cites"][0]["line"]
    lines = (tree / CAP_REL).read_text(encoding="utf-8").split("\n")
    lines.insert(before - 1, "| **A DECOY ROW INSERTED BY THE TEST** - Trace HOPS said in the prose only | x | WIRED | y |")
    (tree / CAP_REL).write_text("\n".join(lines), encoding="utf-8")
    after = BEC.build(tree, WHEN_T)[0]["row_cites"][0]
    assert after["line"] == before + 1 and after["field"] == "blends[0].record", after


def test_the_catalogue_page_prints_each_row_cite_resolved(tmp_path):
    tree = _cat_tree(tmp_path, "CAPABILITIES[Trace HOPS + stacked stamps + the UNDER species layer]")
    text = BEC.render_md(BEC.build(tree, WHEN_T))
    assert "- **row cites** aliases[0].source CAPABILITIES[Trace HOPS + stacked stamps + the UNDER species layer] -> " \
           f"{CAP_REL}:" in text, text[-600:]
