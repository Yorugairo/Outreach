"""The stock-research ingester keeps its own scrub (R26-254 (1), the operator 2026-09-22).

The 2026-09-22 baseline scrubbed the Drive ids out of `docs/research/markets/sovereign-compute/` and removed the
fund's term sheet ("you can scrub drive id's and term-sheet references"); a re-run of the old ingester wrote the ids
back and ingested a term sheet like any document. Six dockets whose body is a Drive SEARCH LISTING (third-party
records, not research) were written as research. Every test here runs the ingester over a folder of planted `.docx`
files in `tmp_path` - the operator's folder is never read by a test - and writes into `tmp_path` only.
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import ingest_stock_research as ISR  # noqa: E402

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# planted ids and links - shaped like Drive's (a 33-char file id, a 19-char shared-drive id), never real ones
FILE_ID = "1QzXwVuTsRqPoNmLkJiHgFeDcBa987654"
SUPERSEDED_ID = "1ZyXwVuT5RqPoNmLkJiHgFeDcBa123456"
LISTED_ID = "1MnBvCxZ8LkJhGfDsAqWeRtYuIoP24680"
OUTSIDE_ID = "1PoIuYtR3EwQaSdFgHjKlZxCvBnM13579"
TERM_SHEET_ID = "1TeRmShEeT9aBcDeFgHiJkLmNoPqRsTuV"
STRAY_ID = "1StRaYiD7aBcDeFgHiJkLmNoPqRsTuVwX"
FOLDER_ID = "0AXyZq_7abCDEFg3HIJ"
DOC_URL = f"https://docs.google.com/document/d/{FILE_ID}/edit?usp=drive_link"
FOLDER_URL = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
PLANTED = (FILE_ID, SUPERSEDED_ID, LISTED_ID, OUTSIDE_ID, TERM_SHEET_ID, STRAY_ID, FOLDER_ID)

INVENTORY = "01_Master_Ledger_V3_Finalized"
DOSSIER = "12_Applied_Digital_and_TeraWulf_Deep_Analysis"
LISTING = "11_Deep_Tech_Space_Economy_ASTS_RCAT_FLY_PL"
OFFERING = {
    "31_Sovereign_Fund_Term_Sheet": "term sheet",
    "33_SCML_Fund_PPM": "PPM",
    "34_Subscription_Agreement_Class_A": "subscription",
}
OFFERING_BY_TITLE = "35_Investor_Pack"


def write_docx(path: Path, paras: list[str]) -> Path:
    body = "".join(f'<w:p><w:r><w:t xml:space="preserve">{escape(p)}</w:t></w:r></w:p>' for p in paras)
    xml = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           f'<w:document xmlns:w="{W_NS}"><w:body>{body}</w:body></w:document>')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", xml)
    return path


def front(title: str, category: str = "Single / Multi-Ticker Research") -> str:
    return (f'title: "{title}" category: "{category}" source_id: "{FILE_ID}" '
            f'source_location: "Outside Research Folder (Root)" supersedes: "{SUPERSEDED_ID}"')


def search_hit(n: int, title: str) -> str:
    return (f"[{n}] ID: 1HiT{n:02d}aBcDeFgHiJkLmNoPqRsTuVwXyZ01 | Title: {title} Parent: {FOLDER_ID} | "
            f"Created: 2026-06-05T08:00:00.000Z | Mod: 2026-06-05T08:32:27.451Z Snippet: a third party's record {n}")


@pytest.fixture()
def folder(tmp_path: Path) -> Path:
    src = tmp_path / "Stock research and ideas"
    src.mkdir()
    write_docx(src / f"{INVENTORY}.docx", [
        front("Master Ingestion and Valuation Ledger", "Master Ledgers & Frameworks"),
        f"ID: {LISTED_ID} | Title: Research Deep Dive C1 | Mime: application/vnd.google-apps.document | "
        "Mod: 2026-06-08T04:48:30.711Z",
        f"ID: {OUTSIDE_ID} | Title: Structural Bottlenecks | Parent: {FOLDER_ID} | "
        "Mime: application/vnd.google-apps.document | Mod: 2026-06-05T08:32:27.451Z",
        f"ID: {TERM_SHEET_ID} | Title: Confidential Term Sheet & Offering | Parent: {FOLDER_ID} | "
        "Mime: application/vnd.google-apps.document | Mod: 2026-05-28T16:20:46.714Z",
    ])
    write_docx(src / f"{DOSSIER}.docx", [
        front("Applied Digital and TeraWulf: An Exhaustive Analysis"),
        "# Applied Digital and TeraWulf: An Exhaustive Analysis",
        "Applied Digital converts stranded power into leased compute capacity for hyperscale tenants.",
        f"The model sits at {DOC_URL} and the folder at {FOLDER_URL} for the working files.",
        f"One cited working file: ID: {STRAY_ID} | Title: The APLD lease model",
    ])
    write_docx(src / f"{LISTING}.docx", [
        front("Deep Tech Infrastructure and the Space Economy"),
        *[search_hit(n, f"Some search result {n}") for n in range(1, 6)],
    ])
    for stem in OFFERING:
        write_docx(src / f"{stem}.docx", [front("Confidential material"), "Offering terms, for discussion only."])
    write_docx(src / f"{OFFERING_BY_TITLE}.docx", [
        front("Confidential Term Sheet & Offering Summary"), "Offering terms, for discussion only."])
    return src


def run_ingest(monkeypatch, tmp_path: Path, src: Path) -> tuple[int | None, Path, Path]:
    markets = tmp_path / "out" / "markets" / "sovereign-compute"
    runs = tmp_path / "out" / "runs" / "sovereign-compute-2026-09"
    markets.mkdir(parents=True)
    runs.mkdir(parents=True)
    monkeypatch.setattr(ISR, "SOURCE_DIR", src)
    monkeypatch.setattr(ISR, "TARGET_MARKETS_DIR", markets)
    monkeypatch.setattr(ISR, "RUNS_DIR", runs)
    monkeypatch.setattr(ISR, "REPO_ROOT", tmp_path / "out")
    return ISR.main(), markets, runs


def written(tmp_path: Path) -> dict[str, str]:
    out = tmp_path / "out"
    return {p.relative_to(out).as_posix(): p.read_text(encoding="utf-8") for p in out.rglob("*") if p.is_file()}


# --- the search listing FAILS (the Expected RED) ------------------------------------------------


def test_a_docket_whose_body_is_a_search_listing_fails_and_is_never_written(monkeypatch, tmp_path, folder, capsys):
    rc, markets, runs = run_ingest(monkeypatch, tmp_path, folder)
    out = capsys.readouterr().out
    assert not (markets / f"{LISTING}.md").exists()
    assert not (runs / f"raw_{LISTING}.md").exists()
    assert f"FAIL {LISTING}.docx" in out and "search listing" in out
    assert rc == 1


def test_a_docket_with_one_cited_record_is_research_not_a_listing(monkeypatch, tmp_path, folder):
    _, markets, _ = run_ingest(monkeypatch, tmp_path, folder)
    assert (markets / f"{DOSSIER}.md").is_file()
    assert (markets / f"{INVENTORY}.md").is_file()


def test_a_clean_folder_exits_zero(monkeypatch, tmp_path, folder):
    (folder / f"{LISTING}.docx").unlink()
    rc, _, _ = run_ingest(monkeypatch, tmp_path, folder)
    assert rc == 0


# --- no Drive id, no Drive URL, anywhere it writes ----------------------------------------------


def test_a_re_run_writes_no_drive_id_and_no_drive_url(monkeypatch, tmp_path, folder):
    run_ingest(monkeypatch, tmp_path, folder)
    files = written(tmp_path)
    assert files, "the ingester wrote nothing"
    for rel, text in files.items():
        for planted in PLANTED:
            assert planted not in text, f"{rel} carries the planted Drive id {planted}"
        assert "docs.google.com" not in text and "drive.google.com" not in text, f"{rel} carries a Drive URL"


def test_the_drive_inventory_json_is_not_written(monkeypatch, tmp_path, folder):
    _, _, runs = run_ingest(monkeypatch, tmp_path, folder)
    assert not (runs / "google_drive_docket_301.json").exists()


def test_the_frontmatter_carries_no_source_id_or_supersedes(monkeypatch, tmp_path, folder):
    _, markets, _ = run_ingest(monkeypatch, tmp_path, folder)
    head = (markets / f"{DOSSIER}.md").read_text(encoding="utf-8").split("---", 2)[1]
    assert "source_id" not in head and "supersedes" not in head
    assert 'source_location: "Outside Research Folder (Root)"' in head


def test_a_supersedes_that_names_no_drive_id_is_kept_as_the_scrub_kept_it(monkeypatch, tmp_path, folder):
    write_docx(folder / "02_Accretive_Investment_Thesis_Framework.docx", [
        'title: "The Accretive Investment Thesis" category: "Master Ledgers & Frameworks" '
        'source_location: "Inside Research Folder" supersedes: "None (Original unique document)"'])
    _, markets, _ = run_ingest(monkeypatch, tmp_path, folder)
    text = (markets / "02_Accretive_Investment_Thesis_Framework.md").read_text(encoding="utf-8")
    assert 'supersedes: "None (Original unique document)"' in text
    assert "- **Supersedes:** `None (Original unique document)`" in text


def test_the_inventory_table_keeps_titles_and_drops_every_id_column(monkeypatch, tmp_path, folder):
    _, markets, _ = run_ingest(monkeypatch, tmp_path, folder)
    text = (markets / f"{INVENTORY}.md").read_text(encoding="utf-8")
    assert "| Research Deep Dive C1 | `application/vnd.google-apps.document` | 2026-06-08T04:48:30.711Z |" in text
    assert "Google Drive ID" not in text and "Parent Folder" not in text


def test_the_dossier_keeps_its_prose_with_the_links_removed(monkeypatch, tmp_path, folder):
    _, markets, _ = run_ingest(monkeypatch, tmp_path, folder)
    text = (markets / f"{DOSSIER}.md").read_text(encoding="utf-8")
    assert "Applied Digital converts stranded power into leased compute capacity" in text
    assert "The APLD lease model" in text


# --- offering documents are refused BY NAME ------------------------------------------------------


@pytest.mark.parametrize("stem,kind", sorted(OFFERING.items()))
def test_an_offering_document_is_refused_by_its_file_name(monkeypatch, tmp_path, folder, capsys, stem, kind):
    _, markets, runs = run_ingest(monkeypatch, tmp_path, folder)
    out = capsys.readouterr().out
    assert not (markets / f"{stem}.md").exists() and not (runs / f"raw_{stem}.md").exists()
    line = next((l for l in out.splitlines() if l.startswith(f"REFUSED {stem}.docx")), "")
    assert "offering document" in line and kind in line, out


def test_an_offering_document_is_refused_by_its_title_too(monkeypatch, tmp_path, folder, capsys):
    _, markets, _ = run_ingest(monkeypatch, tmp_path, folder)
    out = capsys.readouterr().out
    assert not (markets / f"{OFFERING_BY_TITLE}.md").exists()
    assert any(l.startswith(f"REFUSED {OFFERING_BY_TITLE}.docx") and "term sheet" in l for l in out.splitlines())


def test_an_inventory_row_naming_a_term_sheet_is_dropped(monkeypatch, tmp_path, folder):
    run_ingest(monkeypatch, tmp_path, folder)
    for rel, text in written(tmp_path).items():
        assert "term sheet" not in text.lower(), f"{rel} still names the term sheet"


def test_the_catalog_lists_and_links_only_what_was_written(monkeypatch, tmp_path, folder):
    _, markets, _ = run_ingest(monkeypatch, tmp_path, folder)
    catalog = (markets / "00_SOVEREIGN_COMPUTE_MASTER_CATALOG.md").read_text(encoding="utf-8")
    for link in re.findall(r"\]\(\./([^)]+\.md)\)", catalog):
        assert (markets / link).is_file(), f"the catalog links {link}, which was not written"
    assert "2 Master Research Documents" in catalog


@pytest.mark.parametrize("name", [
    "Q3 Subscription Revenue Models", "Sheet Metal Termination Costs", "Opportunity Map 2026",
    "Rare Earth Purity at 5 PPM", "HALEU Enrichment to 20ppm",
])
def test_a_research_title_that_merely_shares_a_word_is_not_refused(name):
    assert ISR.offering_refusal(name, "") is None


# --- the detector, on the real tree -------------------------------------------------------------


@pytest.mark.parametrize("token", [
    "14_Optical_Connectivity_Fabrinet_and_Marvell_Trillion_Trajectory",
    "23_Sovereign_Bottlenecks_and_Geometric_Growth_2026_2028",
    "RESEARCH-2026-09-20-SOVEREIGN-COMPUTE-DATA",
    "application/vnd.google-apps.spreadsheet",
])
def test_a_file_stem_or_a_mime_type_is_not_a_drive_id(token):
    assert ISR.drive_refs(token) == []


def test_the_scrub_marks_what_it_removed_and_keeps_the_prose():
    stem = "14_Optical_Connectivity_Fabrinet_and_Marvell_Trillion_Trajectory"
    text = f"See {DOC_URL} and ID: {STRAY_ID} beside `{stem}`."

    scrubbed = ISR.scrub_drive_refs(text)

    assert scrubbed == f"See {ISR.DRIVE_URL_MARK} and ID: {ISR.DRIVE_ID_MARK} beside `{stem}`."
    assert ISR.drive_refs(scrubbed) == []
    assert ISR.drive_refs(text) == [DOC_URL, STRAY_ID]


def test_the_committed_dockets_carry_no_drive_ref():
    """The gate over this checkout's scrubbed baseline: the detector finds nothing the 2026-09-22 scrub left. The six
    search-listing dockets kept on disk (gitignored) are exactly what the ingester now FAILS, so they are skipped."""
    markets = ROOT / "docs" / "research" / "markets" / "sovereign-compute"
    files = sorted(markets.glob("*.md"))
    assert files
    checked = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        if ISR.search_listing(text):
            continue
        assert ISR.drive_refs(text) == [], path.name
        checked += 1
    assert checked >= 25
