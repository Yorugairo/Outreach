"""The publish package (R26-8, P52 T16): `<build>/publish/` written from the build's OWN artifacts - no hand text in
the tool, byte-identical on a second run, the master left to the existing render path, and a checklist that says what
a human still does. Tokyo's hand-written `SCRIPT-90S-DESCRIPTION.md` is the fixture this is measured against and is
never touched."""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import publish_package as PP  # noqa: E402

TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
T0 = TOKYO / "build-short-t0"                      # read ONLY, with --out; a frozen review build is never written
HAND = TOKYO / "SCRIPT-90S-DESCRIPTION.md"         # the hand-written description: the fixture, not an output

needs_tokyo = pytest.mark.skipif(not (T0 / "timeline.json").is_file(),
                                 reason="the Tokyo build-short-t0 artifacts are not on disk")

SENTS = [
    {"text": "Tokyo took a tea break.", "start": 0.0, "end": 1.4},
    {"text": "And left America with an unfunded bar tab.", "start": 1.7, "end": 4.7},
    {"text": "The Fed has not moved, but your borrowing costs climbed anyway.", "start": 5.1, "end": 8.5},
    {"text": "Japan has sold a hundred and twenty-two billion dollars of it.", "start": 9.0, "end": 13.8},
    {"text": "Tokyo pledged 10 trillion yen to chips.", "start": 14.0, "end": 18.0},
    {"text": "The tab stayed here.", "start": 19.0, "end": 21.0},
]

DOSSIER = """# Demo - evidence dossier

**Fetched 2026-09-03. Every row re-verified against the live source on that date.**

## Spoken figures

| the script says | actual | source | verdict |
|---|---|---|---|
| "a hundred and twenty-two billion" | -$122.6 B | TIC Table 5 | **PASS** |

## Sources

| id | what | cadence |
|---|---|---|
| `ticdata.treasury.gov/x/slt_table5.txt` | TIC Table 5, Major Foreign Holders of Treasury Securities | monthly |
| FRED `DGS10` | US 10-year Treasury constant maturity | daily |

**Derived, not quoted:** the hedge cost.

## Charts built

| sidecar | proves | form |
|---|---|---|
| `ev-a` | the selling | line |
"""

TITLED_SOURCE = """SOURCE ON DISK - fetched 2026-09-10 via tavily_extract (text), for the demo.

URL: https://example.org/the-article
Title: The article's own headline - Example Wire
Byline: A REPORTER
"""

UNTITLED_SOURCE = """SOURCE ON DISK - fetched 2026-09-10 via tavily_extract from example.com product pages, for the demo
chart (the operator: "show the thing"), which wraps across lines and ends on a period.

URL: https://example.com/products/1
Example Product ETF - Average Annual Total Returns
| | 1y | 3y |
| Total Return (%) | 1.0 | 2.0 |
"""

TIMELINE = {
    "schema_version": "scene_evidence_timeline.v1", "runtime_s": 21.0, "title": "Demo Short",
    "subtitle": "Demo Channel · short", "episode_id": "demo", "aspect": "9:16",
    "evidence": {"dock-a": {"source": "Nikkei Asia · 12 Nov 2024"},
                 "dock-b": {"source": "@StickMike · Demo Channel"}},
    "scenes": [{"world": {"kind": "ledger", "page": {"source": "US Treasury TIC Table 5 · 2026-09"},
                          "page_states": [{"source": "US Treasury TIC Table 5 · 2026-09"}]}}],
}


def _fixture(tmp_path: Path, *, dossier: str | None = DOSSIER, sources: bool = True) -> tuple[Path, Path]:
    project = tmp_path / "demo-episode"
    build = project / "build-short-x"
    build.mkdir(parents=True)
    (build / "timeline.json").write_text(json.dumps(
        {"episode": "demo", "script": "SCRIPT-VO.txt", "take": "vo-short", "runtime_s": 21.0, "sentences": SENTS}),
        encoding="utf-8")
    (build / "demo.timeline.json").write_text(json.dumps(TIMELINE), encoding="utf-8")
    if dossier is not None:
        (project / "EVIDENCE-DOSSIER.md").write_text(dossier, encoding="utf-8")
    if sources:
        src = project / "evidence" / "sources"
        src.mkdir(parents=True)
        (src / "a-titled.txt").write_text(TITLED_SOURCE, encoding="utf-8")
        (src / "b-untitled.txt").write_text(UNTITLED_SOURCE, encoding="utf-8")
    (build / "self-watch").mkdir()
    (build / "self-watch" / "O1-0000.0.png").write_bytes(b"\x89PNG\r\n\x1a\n-not-a-real-png-but-bytes")
    return project, build


def _tree(folder: Path) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in sorted(folder.iterdir()) if p.is_file()}


# ---------------------------------------------------------------- the spoken text, read off the take
def test_the_hook_is_what_begins_in_the_first_seconds():
    assert PP.hook(SENTS) == ["Tokyo took a tea break.", "And left America with an unfunded bar tab."]
    late = [{"text": "One long opening sentence.", "start": 6.0, "end": 12.0}]
    assert PP.hook(late) == ["One long opening sentence."]          # never empty: the first sentence is the grab
    assert PP.hook([]) == []


def test_the_figure_sentences_include_spoken_numbers_and_skip_the_hook():
    f = PP.figures(SENTS, skip=PP.hook(SENTS))
    assert f == ["Japan has sold a hundred and twenty-two billion dollars of it.",
                 "Tokyo pledged 10 trillion yen to chips."]         # words AND digits; the Fed line carries no figure
    assert PP.close(SENTS, skip=PP.hook(SENTS) + f) == ["The tab stayed here."]   # the ring, minus what was said


def test_onscreen_sources_are_citations_not_our_own_credit():
    assert PP.onscreen_sources(TIMELINE, "Demo Channel") == ["Nikkei Asia · 12 Nov 2024",
                                                             "US Treasury TIC Table 5 · 2026-09"]
    assert "@StickMike · Demo Channel" in PP.onscreen_sources(TIMELINE)   # no channel given: nothing dropped


# ---------------------------------------------------------------- the dossier and the fetched sources
def test_the_dossier_sources_table_is_the_citation_block():
    rows = PP.dossier_rows(DOSSIER)
    assert rows == [{"id": "ticdata.treasury.gov/x/slt_table5.txt",
                     "what": "TIC Table 5, Major Foreign Holders of Treasury Securities", "cadence": "monthly"},
                    {"id": "FRED DGS10", "what": "US 10-year Treasury constant maturity", "cadence": "daily"}]
    assert PP.dossier_fetched(DOSSIER) == "2026-09-03"
    assert PP.dossier_rows("# no sources heading\n| a | b | c |\n") == [] and PP.dossier_fetched("") is None


def test_the_links_come_from_the_sources_own_headers(tmp_path):
    project, _ = _fixture(tmp_path)
    assert PP.fetched_links(project) == [
        {"label": "The article's own headline - Example Wire", "url": "https://example.org/the-article"},
        {"label": "Example Product ETF - Average Annual Total Returns", "url": "https://example.com/products/1"}]
    assert PP.fetched_links(tmp_path / "nothing-here") == []


# ---------------------------------------------------------------- the folder
def test_the_package_carries_every_file_a_posting_pass_needs(tmp_path):
    _, build = _fixture(tmp_path)
    out = PP.write_package(build)
    assert out == build / "publish"
    assert sorted(p.name for p in out.iterdir()) == sorted([*PP.FILES, "first-frame.png"])
    yt = (out / "DESCRIPTION-YOUTUBE.md").read_text(encoding="utf-8")
    assert "## Title (paste into the title field)" in yt and "Demo Short" in yt
    assert yt.index("Tokyo took a tea break.") < yt.index("Japan has sold a hundred")     # the grab leads


def test_the_description_carries_the_dossiers_sources_and_the_links(tmp_path):
    _, build = _fixture(tmp_path)
    out = PP.write_package(build)
    yt = (out / "DESCRIPTION-YOUTUBE.md").read_text(encoding="utf-8")
    assert "Sources (fetched 2026-09-03):" in yt
    for row in ("TIC Table 5, Major Foreign Holders of Treasury Securities (monthly)",
                "US 10-year Treasury constant maturity (daily)", "FRED DGS10"):
        assert row in yt, row
    assert "https://example.org/the-article" in yt                                   # the URL the source itself carries
    assert "On screen: Nikkei Asia · 12 Nov 2024; US Treasury TIC Table 5 · 2026-09" in yt
    assert (out / "SOURCES.md").read_text(encoding="utf-8").count("TIC Table 5") >= 1


def test_the_facebook_caption_moves_the_link_to_the_first_comment(tmp_path):
    _, build = _fixture(tmp_path)
    out = PP.write_package(build)
    fb = (out / "DESCRIPTION-FACEBOOK.md").read_text(encoding="utf-8")
    body = fb.split("## First comment")[0]
    assert "Links in the first comment." in body and "https://" not in body
    assert "https://example.org/the-article" in fb.split("## First comment")[1]
    assert "#Reels" in fb and "#Shorts" not in fb
    assert "#Shorts" in (out / "DESCRIPTION-YOUTUBE.md").read_text(encoding="utf-8")


def test_the_pinned_comment_is_the_source_note(tmp_path):
    _, build = _fixture(tmp_path)
    out = PP.write_package(build)
    pin = (out / "PINNED-COMMENT.md").read_text(encoding="utf-8")
    assert "Every figure in this video, with its source (fetched 2026-09-03):" in pin
    assert "TIC Table 5, Major Foreign Holders of Treasury Securities (monthly)" in pin


def test_the_checklist_is_one_page_of_what_a_human_still_does(tmp_path):
    _, build = _fixture(tmp_path)
    md = (PP.write_package(build) / "CHECKLIST.md").read_text(encoding="utf-8")
    assert len(md.splitlines()) <= 40                                       # one page
    for step in ("Upload the master", "thumbnail", "keywords", "schedule", "pin it", "FIRST COMMENT"):
        assert step in md, step
    assert "never schedules and never posts" in md and "R26-8" in md
    assert "render_episode.py" in md and "no second size" in md             # the master stays the existing path
    assert "the 1440p master (render/)" in md                              # this fixture has none, and it says so


def test_no_second_render_lives_in_this_tool():
    """The master stays the existing render path: the package NAMES the file, it never makes one."""
    src = (ROOT / "content/video_engine/scripts/publish_package.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    code = src.replace(ast.get_docstring(tree) or "", "")
    imported = {n.names[0].name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import)}
    imported |= {(n.module or "").split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    assert not imported & {"subprocess", "playwright", "PIL", "render_episode"}, imported
    for forbidden in ("ffmpeg", "Popen", "device_scale_factor"):
        assert forbidden not in code, forbidden
    assert "render_episode.py" in code                                      # it names the one render path instead


def test_the_package_regenerates_byte_identically(tmp_path):
    _, build = _fixture(tmp_path)
    first = _tree(PP.write_package(build))
    second = _tree(PP.write_package(build))
    assert first == second
    other = PP.write_package(build, out=tmp_path / "elsewhere")             # the folder is a function of the build only
    assert _tree(other) == first


def test_a_build_without_a_dossier_or_a_channel_file_still_writes_a_package(tmp_path):
    _, build = _fixture(tmp_path, dossier=None, sources=False)
    out = PP.write_package(build)
    md = (out / "CHECKLIST.md").read_text(encoding="utf-8")
    assert "the evidence dossier (EVIDENCE-DOSSIER.md)" in md and "CHANNEL-DESCRIPTION.md)" in md
    manifest = json.loads((out / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["channel_line"] is None and manifest["counts"]["dossier_sources"] == 0
    assert "On screen:" in (out / "DESCRIPTION-YOUTUBE.md").read_text(encoding="utf-8")   # the cut's own lines remain


def test_a_stale_thumbnail_copy_is_removed_not_left(tmp_path):
    _, build = _fixture(tmp_path)
    out = PP.write_package(build)
    (out / "thumbnail.png").write_bytes(b"stale")
    assert "thumbnail.png" not in _tree(PP.write_package(build))


# ---------------------------------------------------------------- Tokyo, read only, through --out
@needs_tokyo
def test_tokyos_own_build_writes_the_package_without_touching_the_build_or_the_hand_written_description(tmp_path):
    before = hashlib.sha256(HAND.read_bytes()).hexdigest()
    out_a = PP.write_package(T0, out=tmp_path / "a")
    out_b = PP.write_package(T0, out=tmp_path / "b")
    assert _tree(out_a) == _tree(out_b)                                     # byte-identical on the real build too
    assert not (T0 / "publish").exists()                                   # the frozen build is untouched
    assert hashlib.sha256(HAND.read_bytes()).hexdigest() == before          # the fixture is never overwritten
    yt = (out_a / "DESCRIPTION-YOUTUBE.md").read_text(encoding="utf-8")
    assert "Tokyo Tea Break" in yt and "Tokyo took a tea break." in yt
    assert "TIC Table 5, Major Foreign Holders of Treasury Securities (monthly)" in yt   # the dossier's row
    assert "https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.txt" in yt
    assert "The market isn't magic. It's mechanics." in yt                  # the channel's own line, not the tool's
    assert "#MoneyPhysics" in yt and "#Shorts" in yt
    assert (out_a / "first-frame.png").read_bytes() == (T0 / "self-watch" / "O1-0000.0.png").read_bytes()
    m = json.loads((out_a / "MANIFEST.json").read_text(encoding="utf-8"))
    assert m["episode"] == "tokyo-tea-break" and m["aspect"] == "9:16" and m["fetched"] == "2026-09-03"
    assert m["counts"]["dossier_sources"] == 5 and m["channel_slug"] == "money-physics"
    assert str(tmp_path) not in json.dumps(m) and str(ROOT) not in json.dumps(m)   # no absolute path in the manifest


@needs_tokyo
def test_the_cli_writes_the_folder_and_lists_it(tmp_path, capsys):
    assert PP.main([str(T0), "--out", str(tmp_path / "cli")]) == 0
    printed = capsys.readouterr().out
    assert "CHECKLIST.md" in printed and "DESCRIPTION-YOUTUBE.md" in printed
