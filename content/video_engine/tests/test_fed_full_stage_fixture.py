"""R26-235: full-stage measurement is a 16:9 geometry variant, not new ink.

The fixture is keyed by the flat geometry names ``16:9`` and
``16:9|full_stage``; malformed entries and stale player markers remain covered
without reviving the old nested variant shape.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
import sys

sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402
import measure_page_boxes as M  # noqa: E402

FULL = "16:9|full_stage"


def _page(*, full_stage: bool = False) -> dict:
    """A deterministic shape-only page; none of its copy is a claim about finance."""
    page = {
        "schema_version": "ledger_page.v1",
        "surface": "page",
        "builder": "story",
        "variant": "bars",
        "title": "Synthetic geometry page",
        "sub": "Synthetic layout only",
        "source": "Synthetic source; not a figure about the world",
        "quiet_zone": "right",
        "badges": [],
    }
    if full_stage:
        page["full_stage"] = True
    return page


def _timeline(path: Path, *, aspect: str, pages: list[dict]) -> Path:
    path.write_text(json.dumps({
        "aspect": aspect,
        "scenes": [{"world": {"page": page}} for page in pages],
    }), encoding="utf-8")
    return path


def _fake_entry(calls: list, builder: str, aspect: str, page: dict | None = None,
                *, full_stage: bool | None = None) -> dict:
    rendered = dict(page or _page())
    if full_stage is True:
        rendered["full_stage"] = True
    elif full_stage is False:
        rendered.pop("full_stage", None)
    calls.append((builder, aspect, full_stage, LPG.full_stage(rendered, aspect)))
    out = {
        "ink": LPG.page_ink_key(rendered),
        "title": rendered.get("title"),
        "boxes": {"plot": {"x": 10, "y": 20, "w": 30, "h": 40}},
        "bands": {"below": {"y": 60}},
        "axis": {"x": None, "y": None},
        "data_mask": ["0" * 16 for _ in range(16)],
    }
    if LPG.full_stage(rendered, aspect):
        out["full_stage"] = True
    return out


def test_timeline_reader_keeps_mixed_landscape_geometry_under_one_ink(tmp_path: Path):
    legacy = _page()
    stamped = _page(full_stage=True)
    aspect, pages = M.timeline_pages(_timeline(tmp_path / "mixed.timeline.json", aspect="16:9",
                                                pages=[legacy, stamped]))

    ink = LPG.page_ink_key(legacy)
    assert aspect == "16:9"
    assert sorted(pages) == [ink]
    assert LPG.page_ink_key(pages[ink]) == ink
    assert "full_stage" not in pages[ink]
    assert list(M.variant_pages(pages[ink], "16:9")) == ["16:9", "16:9|full_stage"]

    rendered = M._timeline(legacy, "16:9", True)
    assert rendered["aspect"] == "16:9"
    assert rendered["scenes"][0]["world"]["page"]["full_stage"] is True


def test_portrait_full_stage_stamp_keeps_the_old_ink_identity(tmp_path: Path):
    stamped = _page(full_stage=True)
    aspect, pages = M.timeline_pages(_timeline(tmp_path / "portrait.timeline.json", aspect="9:16",
                                                pages=[stamped]))
    ink = LPG.page_ink_key(stamped)

    assert aspect == "9:16"
    assert set(pages) == {ink}
    assert LPG.page_ink_key(pages[ink]) == ink
    assert pages[ink]["full_stage"] is True

    rendered = M._timeline(stamped, "9:16")
    assert rendered["aspect"] == "9:16"
    assert rendered["scenes"][0]["world"]["page"]["full_stage"] is True


def test_build_pages_routes_legacy_and_full_stage_entries_separately(tmp_path: Path, monkeypatch):
    page = _page(full_stage=True)
    tl = _timeline(tmp_path / "fed.timeline.json", aspect="16:9", pages=[page])
    calls: list = []
    monkeypatch.setattr(M, "entry", lambda *args, **kwargs: _fake_entry(calls, *args, **kwargs))

    pages, read = M.build_pages([str(tl)])

    ink = LPG.page_ink_key(page)
    bucket = pages[ink]
    assert read == [M._rel(tl)]
    assert bucket["16:9|full_stage"]["ink"] == ink
    assert bucket["16:9|full_stage"]["full_stage"] is True
    assert [call[1] for call in calls] == ["16:9"]
    assert [call[3] for call in calls] == [True]


def test_build_pages_keeps_a_portrait_stamp_and_legacy_landscape_page(tmp_path: Path, monkeypatch):
    portrait = _timeline(tmp_path / "portrait.timeline.json", aspect="9:16",
                          pages=[_page(full_stage=True)])
    landscape = _timeline(tmp_path / "legacy.timeline.json", aspect="16:9", pages=[_page()])
    calls: list = []
    monkeypatch.setattr(M, "entry", lambda *args, **kwargs: _fake_entry(calls, *args, **kwargs))

    pages, _read = M.build_pages([str(portrait), str(landscape)])

    ink = LPG.page_ink_key(_page())
    assert pages[ink]["9:16"]["ink"] == ink
    assert "full_stage" not in pages[ink]["9:16"]
    assert pages[ink]["16:9"]["ink"] == ink
    assert "full_stage" not in pages[ink]["16:9"]
    assert [(call[1], call[3]) for call in calls] == [
        ("16:9", False), ("16:9", True), ("9:16", False)]


def test_build_pages_merges_same_ink_across_timeline_files_in_either_order(tmp_path: Path, monkeypatch):
    ink = LPG.page_ink_key(_page())
    for case, full_first in enumerate((True, False)):
        folder = tmp_path / f"case-{case}"
        folder.mkdir()
        full_name, legacy_name = (("a-full.timeline.json", "b-legacy.timeline.json")
                                  if full_first else ("b-full.timeline.json", "a-legacy.timeline.json"))
        full = _timeline(folder / full_name, aspect="16:9", pages=[_page(full_stage=True)])
        legacy = _timeline(folder / legacy_name, aspect="16:9", pages=[_page()])
        calls: list = []
        monkeypatch.setattr(M, "entry", lambda *args, **kwargs: _fake_entry(calls, *args, **kwargs))

        pages, _read = M.build_pages([str(legacy), str(full)])
        bucket = pages[ink]
        assert bucket[FULL]["ink"] == ink
        assert True in [call[3] for call in calls]
        assert False in [call[3] for call in calls]


def test_default_build_preserves_legacy_buckets_and_adds_landscape_variant(monkeypatch):
    calls: list = []
    monkeypatch.setattr(M, "representative", lambda _builder: _page())
    monkeypatch.setattr(M, "entry", lambda *args, **kwargs: _fake_entry(calls, *args, **kwargs))

    doc = M.build(["story"])
    by_aspect = doc["builders"]["story"]
    ink = LPG.page_ink_key(_page())

    assert set(by_aspect) == {"16:9", "16:9|full_stage", "9:16"}
    assert by_aspect["16:9"]["ink"] == ink
    assert by_aspect["16:9|full_stage"]["ink"] == ink
    assert by_aspect["16:9|full_stage"]["full_stage"] is True
    assert "full_stage" not in by_aspect["9:16"]
    assert [(call[1], call[3]) for call in calls] == [("16:9", False), ("16:9", True), ("9:16", False)]


_MISSING = object()


def _measured_entry(page: dict, *, shift: int = 0, full_stage: bool = False,
                    ink: str | None = None) -> dict:
    """Shape-only fixture entry with deliberately distinguishable boxes."""
    base = 100 + shift
    boxes = {name: {"x": base + i, "y": base + i * 2, "w": 200 + i, "h": 40 + i}
             for i, name in enumerate(LPG.BOX_KEYS)}
    entry = {
        "ink": ink or LPG.page_ink_key(page),
        "title": page["title"],
        "boxes": boxes,
        "bands": {"below": {"x": base, "y": base + 20, "w": 100, "h": 30}},
        "axis": {"x": None, "y": None},
        "data_mask": ["0" * 16 for _ in range(16)],
    }
    if full_stage:
        entry["full_stage"] = True
    return entry


def _fixture(path: Path, *, builders: dict, pages: dict, player_sha=_MISSING) -> Path:
    document = {"schema": LPG.PAGE_BOXES_SCHEMA, "builders": builders, "pages": pages}
    if player_sha is not _MISSING:
        document["player_sha256"] = player_sha
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _use_fixture(monkeypatch, path: Path) -> None:
    monkeypatch.setattr(LPG, "PAGE_BOXES_FIXTURE", path)
    LPG._doc.cache_clear()


def test_full_stage_exact_page_variant_drives_page_and_card_boxes(tmp_path: Path, monkeypatch):
    page = _page(full_stage=True)
    ink = LPG.page_ink_key(page)
    exact = _measured_entry(page, shift=7, full_stage=True)
    legacy = _measured_entry(page, shift=70)
    builder = _measured_entry(page, shift=700, full_stage=True)
    fixture = _fixture(
        tmp_path / "exact.json",
        builders={"story": {"16:9": legacy, FULL: builder}},
        pages={ink: {"16:9": legacy, FULL: exact}},
        player_sha=M.template_sha(),
    )
    _use_fixture(monkeypatch, fixture)

    assert LPG.measured_entry(page, "16:9") == exact
    boxes = LPG.page_boxes(page, "16:9")
    assert boxes["measured"] is True
    assert {key: boxes[key] for key in LPG.BOX_KEYS} == exact["boxes"]

    seen = []
    original = B.free_bands

    def capture(card_boxes, reserve=None):
        seen.append(card_boxes)
        return original(card_boxes, reserve)

    monkeypatch.setattr(B, "free_bands", capture)
    B.page_place(page, "16:9")
    assert seen and seen[0]["plot"] == exact["boxes"]["plot"]


def test_full_stage_uses_same_ink_builder_entry_when_exact_page_is_invalid(tmp_path: Path, monkeypatch):
    page = _page(full_stage=True)
    ink = LPG.page_ink_key(page)
    invalid_exact = _measured_entry(page, shift=2)
    builder = _measured_entry(page, shift=31, full_stage=True)
    fixture = _fixture(
        tmp_path / "builder-fallback.json",
        builders={"story": {"16:9": _measured_entry(page), FULL: builder}},
        pages={ink: {FULL: invalid_exact}},
        player_sha=M.template_sha(),
    )
    _use_fixture(monkeypatch, fixture)

    assert LPG.measured_entry(page, "16:9") == builder
    assert LPG.page_boxes(page, "16:9")["plot"] == builder["boxes"]["plot"]


def test_full_stage_rejects_malformed_or_wrong_markers_before_legacy_fallback(tmp_path: Path, monkeypatch):
    page = _page(full_stage=True)
    ink = LPG.page_ink_key(page)
    marker_only = {"ink": ink, "full_stage": True}
    scalar_box = _measured_entry(page, full_stage=True)
    scalar_box["boxes"]["plot"] = "not-a-box"
    nonnumeric_box = _measured_entry(page, full_stage=True)
    nonnumeric_box["boxes"]["title"]["x"] = "bad"
    nonfinite_box = _measured_entry(page, full_stage=True)
    nonfinite_box["boxes"]["chart"]["w"] = float("nan")
    negative_extent = _measured_entry(page, full_stage=True)
    negative_extent["boxes"]["source"]["h"] = -1
    invalid = [
        None,
        marker_only,
        scalar_box,
        nonnumeric_box,
        nonfinite_box,
        negative_extent,
        _measured_entry(page, ink="not-this-ink", full_stage=True),
        _measured_entry(page),
        _measured_entry(page, full_stage=True, ink=ink),
    ]
    invalid[-1]["full_stage"] = False
    for index, candidate in enumerate(invalid):
        fixture = _fixture(
            tmp_path / f"invalid-{index}.json",
            builders={"story": {"16:9": {"ink": ink, "boxes": {}}}},
            pages={ink: {FULL: candidate}},
            player_sha=M.template_sha(),
        )
        _use_fixture(monkeypatch, fixture)
        assert LPG.measured_entry(page, "16:9") is None
        assert LPG.page_boxes(page, "16:9")["measured"] is False


def test_full_stage_malformed_flat_entries_fail_closed(tmp_path: Path, monkeypatch):
    page = _page(full_stage=True)
    ink = LPG.page_ink_key(page)
    malformed = [
        ({ink: ["x"]}, {"story": ["x"]}),
        ({ink: {"16:9": []}}, {"story": {"16:9": "not-a-family"}}),
        ({ink: {FULL: []}},
         {"story": {FULL: "not-an-entry"}}),
    ]
    for index, (pages, builders) in enumerate(malformed):
        fixture = _fixture(tmp_path / f"families-{index}.json", builders=builders, pages=pages,
                           player_sha=M.template_sha())
        _use_fixture(monkeypatch, fixture)
        assert LPG.measured_entry(page, "16:9") is None


@pytest.mark.parametrize("player_sha", [_MISSING, "stale-player-digest"])
def test_full_stage_stale_or_missing_player_marker_keeps_measured_geometry(
        tmp_path: Path, monkeypatch, player_sha):
    page = _page(full_stage=True)
    ink = LPG.page_ink_key(page)
    entry = _measured_entry(page, full_stage=True)
    fixture = _fixture(
        tmp_path / ("missing-hash.json" if player_sha is _MISSING else "stale-hash.json"),
        builders={"story": {FULL: entry}},
        pages={ink: {FULL: entry}},
        player_sha=player_sha,
    )
    _use_fixture(monkeypatch, fixture)

    assert LPG._full_stage_fixture_is_fresh() is False
    assert LPG.measured_entry(page, "16:9") == entry
    boxes = LPG.page_boxes(page, "16:9")
    assert boxes["measured"] is True
    assert boxes["plot"] == entry["boxes"]["plot"]


def test_player_hashes_ignore_crlf_vs_lf_line_endings(tmp_path: Path, monkeypatch):
    template = tmp_path / "player.html"
    engine = tmp_path / "engine.mjs"
    lf_template = b"<main>same player\n</main>\n"
    lf_engine = b"const player = true;\n"

    monkeypatch.setattr(M.RB, "TEMPLATE", template)
    monkeypatch.setattr(M.RB, "ENGINE", engine)
    monkeypatch.setattr(LPG, "_PLAYER_TEMPLATE", template)
    monkeypatch.setattr(LPG, "_PLAYER_ENGINE", engine)
    monkeypatch.setattr(LPG, "_PLAYER_SHA_CACHE", None)

    template.write_bytes(lf_template)
    engine.write_bytes(lf_engine)
    lf_template_sha = M.template_sha()
    LPG._PLAYER_SHA_CACHE = None
    lf_player_sha = LPG._player_sha256()

    template.write_bytes(lf_template.replace(b"\n", b"\r\n"))
    engine.write_bytes(lf_engine.replace(b"\n", b"\r\n"))
    crlf_template_sha = M.template_sha()
    LPG._PLAYER_SHA_CACHE = None
    crlf_player_sha = LPG._player_sha256()

    assert lf_template_sha == crlf_template_sha
    assert lf_player_sha == crlf_player_sha
    assert lf_template_sha == lf_player_sha


def test_portrait_stamp_and_legacy_landscape_keep_their_existing_entries(tmp_path: Path, monkeypatch):
    portrait = _page(full_stage=True)
    legacy = _page()
    portrait_entry = _measured_entry(portrait, shift=9)
    legacy_entry = _measured_entry(legacy, shift=19)
    fixture = _fixture(
        tmp_path / "legacy-and-portrait.json",
        builders={"story": {"9:16": portrait_entry, "16:9": legacy_entry}},
        pages={},
    )
    _use_fixture(monkeypatch, fixture)

    assert LPG.measured_entry(portrait, "9:16") == portrait_entry
    assert LPG.page_boxes(portrait, "9:16")["measured"] is True
    assert LPG.measured_entry(legacy, "16:9") == legacy_entry
    assert LPG.page_boxes(legacy, "16:9")["measured"] is True
