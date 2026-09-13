"""The docs manifest is the document-level retrieval contract: one line per file, one `rg` call.

`DOCS-INDEX` answers "where is the section about X"; this answers the question that keeps
costing tree walks - "do we have X, and which doc holds it". These pin the record shape on a
synthetic docs tree (kind by path and filename, the purpose fallback chain, `defines` vs
`mentions`, key-term ordering, the JSONL-only heading list, CAPABILITIES / BACKLOG rows folding
into their file), that
`--write` is deterministic and `--check` follows the docs, and that the manifest built over the
REAL tree still carries what an agent looks for: the rulings ledger owns E41, CAPABILITIES owns
the G2 short-mode row, `kubelka` lands on doc 44, a heading phrase reaches its document, and the
Markdown stays small enough to read whole."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_docs_index as BDI  # noqa: E402
import build_docs_manifest as BDM  # noqa: E402

SOURCES_ROOT = "content/video_engine/sources"
CONFIG = BDI.IndexConfig(roots=("docs", SOURCES_ROOT))

RULINGS_REL = "docs/portable/OPERATOR-RULINGS.md"
CAPS_REL = "docs/content-video-engine/CAPABILITIES.md"
BACKLOG_REL = "docs/content-video-engine/BACKLOG.md"
DOCTRINE_REL = "docs/content-video-engine/29-FAKE-MOTION-STANDARDS.md"
TERMS_REL = "docs/content-video-engine/47-FAKE-VOCABULARY.md"
PATTERN_REL = "docs/content-video-engine/patterns/FAKE-MAP.md"
README_REL = "docs/content-video-engine/README.md"
CONTRACT_REL = "docs/fake-platform-contract.md"
HEADINGS_REL = "docs/content-video-engine/48-FAKE-HEADINGS.md"

RULINGS = (
    "# OPERATOR RULINGS — the standing corrections ledger\n"
    "\n"
    "*2026-01-01 — the ledger of standing corrections*\n"
    "\n"
    "Every entry is a correction the operator actually made, with the reason it was made.\n"
    "The reason is the load-bearing part.\n"
    "\n"
    "## A3 — The anchor sits at a tenth of runtime (2026-01-01)\n"
    "\n"
    "Ruled once, applies always.\n"
    "\n"
    "## E41 — The shorts-script ledger (2026-01-02)\n"
    "\n"
    "Move beats, never clip words. Superseded in part by E30 elsewhere.\n"
)

DOCTRINE = (
    "# 29 — Fake Motion Standards\n"
    "\n"
    "Status: accepted working standard, 2026-01-01\n"
    "Proven by: a scrubbable proof\n"
    "\n"
    "The lane is the scene-evidence lane, and this sentence is long enough to be one.\n"
    "A second sentence follows it.\n"
    "\n"
    "## M08 — the caption gate\n"
    "\n"
    "The gate that E41 asks for, checked by G-g and by S12a.\n"
)

TERMS_DOC = (
    "# Fake vocabulary\n"
    "\n"
    "This document explains the thing in one clear sentence. A second sentence follows.\n"
    "\n"
    "## One\n"
    "\n"
    "**Why:** the `zulu-two` and the `alpha-one` pairing.\n"
    "\n"
    "## Two\n"
    "\n"
    "The `alpha-one` again.\n"
    "\n"
    "## Three\n"
    "\n"
    "The `alpha-one` a third time.\n"
)

PATTERN = (                                     # no lead under the H1: the fallback paragraph wins
    "# FAKE MAP — the spine\n"
    "\n"
    "## P9 — the phase\n"
    "\n"
    "The spine fuses the classical architecture with the platform micro-rules.\n"
)

README = (                                      # no paragraph at all: the first H2 is the purpose
    "# Fake readme\n"
    "\n"
    "## Live doctrine, indexed\n"
)

CAPS = (
    "# CAPABILITIES — what is already built\n"
    "\n"
    "Check this file before building anything at all in this repository.\n"
    "\n"
    "| Capability | Where | Notes |\n"
    "|---|---|---|\n"
    "| **G2 short mode (doc 51 s51.2 as gates)** | `run_short` | shipped |\n"
    "| **Caption STAGE mode** | `stage.mjs` | shipped |\n"
)

BACKLOG = (
    "# Backlog — fake engine\n"
    "\n"
    "Hand-maintained. The census is generated elsewhere; this is the work itself.\n"
    "\n"
    "| Backlog id | Item | Decision |\n"
    "|---|---|---|\n"
    "| **B7** | **Plate reveal** | queued |\n"
    "| ~~M11~~ | ~~**Spotlit chart**~~ | shipped |\n"
)

HEADINGS_DOC = (
    "# 48 — Fake headings\n"
    "\n"
    "The document whose headings are the thing an agent greps for, not its body.\n"
    "\n"
    "## 9.31 The page VORTEX — how a page leaves\n"
    "\n"
    "It leaves by a spiral and comes back the same way, which is a long enough lead.\n"
    "\n"
    "### § 2. The retract\n"
    "\n"
    "Every colour on the page becomes a particle, and this lead clears the floor.\n"
    "\n"
    "#### The fourth level is not what the document is about\n"
    "\n"
    "A paragraph under a level-4 heading, long enough to be a lead in its own right.\n"
)

TREE = {
    HEADINGS_REL: HEADINGS_DOC,
    RULINGS_REL: RULINGS,
    DOCTRINE_REL: DOCTRINE,
    TERMS_REL: TERMS_DOC,
    PATTERN_REL: PATTERN,
    README_REL: README,
    CAPS_REL: CAPS,
    BACKLOG_REL: BACKLOG,
    "docs/portable/FAKE-DOCTRINE.md": "# Fake doctrine\n\nPortable and model-agnostic, loaded first.\n",
    "docs/content-video-engine/briefs/FAKE-BRIEF.md": "# Fake brief\n\nA dispatched work order, frozen.\n",
    "docs/content-video-engine/prompts/FAKE-PROMPT.md": "# Fake prompt\n\nThe prompt that built the library.\n",
    "docs/runbooks/FAKE_RUNS.md": "# Fake runbook\n\nHow to run the thing when it breaks.\n",
    "docs/research/2026-01-01-fake-assessment.md": "# Fake assessment\n\nWhat the market already does.\n",
    f"{SOURCES_ROOT}/reference_analyses/FAKE_REPORT.md": "# Fake report\n\nThe reference, shot by shot.\n",
    CONTRACT_REL: "# Fake platform contract\n\nThe evidence contract for the platform.\n",
}


def _tree(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for rel_path, text in TREE.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def _entries(root: Path) -> dict[str, dict]:
    records = BDI.build_index(root, CONFIG)
    return {e["path"]: e for e in BDM.build(records, root)}


def _with_index(tmp_path: Path) -> Path:
    """The tree plus the index the manifest folds - what the CLI expects to find."""
    root = _tree(tmp_path)
    assert BDI.main(["--write", "--repo", str(root), "--root", "docs", "--root", SOURCES_ROOT]) == 0
    return root


# --- kind ------------------------------------------------------------------------------------

def test_kind_is_decided_by_path_prefix_and_filename() -> None:
    cases = {
        RULINGS_REL: "ruling-ledger",
        CAPS_REL: "capabilities",
        BACKLOG_REL: "backlog",
        DOCTRINE_REL: "doctrine",                                   # docs/content-video-engine/<NN>-
        "docs/content-video-engine/21-ART-STYLE-REVIEW.md": "doctrine",   # numbered beats *-REVIEW
        "docs/portable/DOCTRINE-CORE.md": "doctrine",
        "docs/content-video-engine/RULE-the-page-is-the-ground.md": "doctrine",
        "docs/content-video-engine/PIPELINE.md": "doctrine",
        "docs/AGENTS-SEO-PLATFORM.md": "doctrine",
        README_REL: "index",
        "docs/content-video-engine/RESEARCH-INDEX.md": "index",
        "docs/agent-context/SKILL_ROUTER.md": "index",
        "docs/AGENT_START_HERE.md": "index",
        PATTERN_REL: "pattern",
        "docs/content-video-engine/briefs/FAKE-BRIEF.md": "brief",
        "docs/content-video-engine/prompts/FAKE-PROMPT.md": "prompt",
        "docs/runbooks/PRP_EXECUTION.md": "runbook",
        "docs/harness/HARNESS_EVALUATION_CHECKLIST.md": "runbook",
        "docs/content-video-engine/22-AUDIO-FIX-RUNBOOK.md": "doctrine",  # numbered first
        f"{SOURCES_ROOT}/reference_analyses/FAKE_REPORT.md": "source-bundle",
        "docs/research/2026-01-01-fake-assessment.md": "research",
        "docs/content-video-engine/FINDING-gaps-are-the-edit.md": "research",
        "docs/content-video-engine/P13-GATE-A-ARMBAR-REVIEW.md": "research",
        "docs/content-video-engine/REMOTION-UI-HARVEST.md": "research",
        CONTRACT_REL: "spec",
        "docs/seo-insights-platform-architecture.md": "spec",
        "docs/seo-ingestion-pipeline-spec.md": "spec",
        "docs/seo-insights-platform-implementation-plan.md": "spec",
        "docs/ARCHITECTURE_DECISION_SEO_PLATFORM.md": "spec",
        "docs/run-centric-schema-notes.md": "spec",
        "docs/production-api-ui-database.md": "spec",
        "docs/STATE-OF-WORK.md": "spec",
        # the spec rules are last and only catch `docs/`: an earlier rule and another tree win
        "docs/runbooks/PROMOTION-plan.md": "runbook",
        "content/video_engine/seo-notes.md": "other",
        "docs/agent-memory/explorer/MEMORY.md": "other",
    }
    assert {p: BDM.classify(p) for p in cases} == cases
    assert {kind for _, _, kind in BDM.KIND_RULES} <= set(BDM.KINDS)
    assert BDM.FALLBACK_KIND in BDM.KINDS


# --- the record ---------------------------------------------------------------------------------

def test_one_record_per_document_with_the_contract_keys(tmp_path: Path) -> None:
    entries = _entries(_tree(tmp_path))
    assert set(entries) == set(TREE)
    assert list(entries[DOCTRINE_REL]) == ["path", "doc", "title", "kind", "purpose", "sections",
                                           "headings", "labels", "leads", "defines", "mentions",
                                           "key_terms", "byline"]
    doctrine = entries[DOCTRINE_REL]
    assert doctrine["doc"] == "29"
    assert doctrine["title"] == "29 — Fake Motion Standards"
    assert doctrine["sections"] == 2                       # the H1 and the M08 H2
    assert entries[CONTRACT_REL]["doc"] is None


def test_the_purpose_falls_back_lead_then_paragraph_then_first_h2(tmp_path: Path) -> None:
    entries = _entries(_tree(tmp_path))
    # the H1's lead, with the `Status:` / `Proven by:` run taken as the byline
    assert entries[DOCTRINE_REL]["purpose"] == (
        "The lane is the scene-evidence lane, and this sentence is long enough to be one.")
    assert entries[DOCTRINE_REL]["byline"] == (
        "Status: accepted working standard, 2026-01-01 Proven by: a scrubbable proof")
    # an italic byline is a byline, not a purpose
    assert entries[RULINGS_REL]["byline"] == "2026-01-01 — the ledger of standing corrections"
    assert entries[RULINGS_REL]["purpose"].startswith("Every entry is a correction")
    # no lead under the H1: the first non-heading paragraph anywhere
    assert entries[PATTERN_REL]["byline"] is None
    assert entries[PATTERN_REL]["purpose"] == (
        "The spine fuses the classical architecture with the platform micro-rules.")
    # no paragraph at all: the first H2
    assert entries[README_REL]["purpose"] == "Live doctrine, indexed"
    # one sentence, not the whole paragraph
    assert entries[TERMS_REL]["purpose"] == "This document explains the thing in one clear sentence."


def test_defines_is_what_the_file_owns_and_mentions_is_what_it_only_refers_to(tmp_path: Path) -> None:
    entries = _entries(_tree(tmp_path))
    rulings, doctrine = entries[RULINGS_REL], entries[DOCTRINE_REL]
    assert rulings["defines"] == ["A3", "E41"]             # ruling ids from the ledger's own H2s
    assert "E30" in rulings["mentions"] and "E30" not in rulings["defines"]
    # the same ruling id in another file is a mention, never a definition
    assert doctrine["defines"] == ["M08"]                  # a gate id in this file's own heading
    assert "E41" in doctrine["mentions"]
    assert "G-g" in doctrine["mentions"] and "S12a" in doctrine["mentions"]
    assert entries[PATTERN_REL]["defines"] == ["P9"]       # plan ids count as owned
    assert len(entries[RULINGS_REL]["mentions"]) <= BDM.MENTION_LIMIT


def test_capability_and_backlog_rows_fold_into_their_file(tmp_path: Path) -> None:
    entries = _entries(_tree(tmp_path))
    caps, backlog = entries[CAPS_REL], entries[BACKLOG_REL]
    assert caps["kind"] == "capabilities" and backlog["kind"] == "backlog"
    assert caps["defines"] == ["Caption STAGE mode", "G2 short mode (doc 51 s51.2 as gates)"]
    assert caps["sections"] == 1                           # the rows are not sections
    assert backlog["defines"] == ["B7", "M11"]
    assert len(entries) == len(TREE)                       # a row never becomes its own record


def test_key_terms_rank_by_count_then_first_appearance(tmp_path: Path) -> None:
    key_terms = _entries(_tree(tmp_path))[TERMS_REL]["key_terms"]
    assert key_terms[:2] == ["alpha-one", "zulu-two"]      # zulu-two appears first, alpha-one wins
    assert "Why:" not in key_terms                         # a lead-in is not vocabulary
    assert len(key_terms) <= BDM.KEY_TERM_LIMIT


def test_headings_are_levels_one_to_three_with_the_numbering_stripped(tmp_path: Path) -> None:
    headings = _entries(_tree(tmp_path))[HEADINGS_REL]["headings"]
    assert headings == ["Fake headings",                      # "48 — " is a filing coordinate
                        "The page VORTEX — how a page leaves",
                        "The retract"]                        # "§ 2." stripped too
    assert not any("fourth level" in h for h in headings)     # H4 is a paragraph marker


def test_headings_are_bounded_in_length_and_in_count() -> None:
    records = [{"path": "docs/x.md", "level": 2, "heading": f"{n}. heading " + "long " * 40,
                "lead": "", "labels": [], "terms": [], "doc": None} for n in range(60)]
    headings = BDM.headings_of(records)
    assert len(headings) == BDM.HEADING_LIMIT
    assert max(len(h) for h in headings) <= BDM.HEADING_TEXT_MAX
    assert headings[0].startswith("heading long")


def test_labels_are_distinct_and_in_first_appearance_order(tmp_path: Path) -> None:
    entries = _entries(_tree(tmp_path))
    assert entries[CAPS_REL]["labels"][:2] == ["G2 short mode (doc 51 s51.2 as gates)",
                                               "Caption STAGE mode"]
    assert entries[HEADINGS_REL]["labels"] == []           # nothing bold in it: labels miss it


def test_labels_are_bounded_in_length_and_in_count() -> None:
    records = [{"path": "docs/x.md", "level": 2, "heading": "h", "lead": "",
                "labels": [f"label {n} " + "long " * 40, "REPEATED", "repeated"],
                "terms": [], "doc": None} for n in range(80)]
    labels = BDM.labels_of(records)
    assert len(labels) == BDM.LABEL_LIMIT
    assert max(len(v) for v in labels) <= BDM.LABEL_TEXT_MAX
    assert sum(1 for v in labels if v.casefold() == "repeated") == 1   # distinct, case-folded


def test_leads_carry_the_opening_words_of_levels_one_to_three(tmp_path: Path) -> None:
    """The layer under the heading and the label: doc 29 hides `spiral` in a lead, not a heading."""
    leads = _entries(_tree(tmp_path))[HEADINGS_REL]["leads"]
    assert leads == ["The document whose headings are the thing an agent greps for, not",
                     "It leaves by a spiral and comes back the same way, which",
                     "Every colour on the page becomes a particle, and this lead clears"]
    assert all(len(lead.split()) <= BDM.LEAD_WORDS for lead in leads)
    assert not any("level-4" in lead for lead in leads)    # H4 leads are paragraph markers


def test_leads_are_bounded_in_length_and_in_count() -> None:
    records = [{"path": "docs/x.md", "level": 3, "heading": "h", "labels": [], "terms": [],
                "lead": f"lead {n} " + "verylongword" * 20, "doc": None} for n in range(120)]
    leads = BDM.leads_of(records)
    assert len(leads) == BDM.LEAD_LIMIT
    assert max(len(v) for v in leads) <= BDM.LEAD_TEXT_MAX
    assert leads[0].startswith("lead 0")


def test_the_markdown_does_not_carry_the_heading_list(tmp_path: Path) -> None:
    root = _with_index(tmp_path)
    assert BDM.main(["--write", "--repo", str(root)]) == 0
    text = (root / BDM.MD_REL).read_text(encoding="utf-8")
    record = json.loads(next(line for line in (root / BDM.JSONL_REL).read_text(
        encoding="utf-8").splitlines() if HEADINGS_REL in line))
    assert record["headings"] and record["leads"]              # the JSONL has them
    assert "The page VORTEX" not in text                       # the size ladder stays
    assert "It leaves by a spiral" not in text                 # and never carries a lead
    assert "labels:" not in text and "leads:" not in text      # the line keeps its four fields


# --- the artifacts --------------------------------------------------------------------------------

def test_write_is_byte_identical_across_runs_and_lands_lf(tmp_path: Path) -> None:
    root = _with_index(tmp_path)
    assert BDM.main(["--write", "--repo", str(root)]) == 0
    first = {rel: (root / rel).read_bytes() for rel in (BDM.JSONL_REL, BDM.MD_REL)}
    assert BDM.main(["--write", "--repo", str(root)]) == 0
    assert {rel: (root / rel).read_bytes() for rel in (BDM.JSONL_REL, BDM.MD_REL)} == first
    for blob in first.values():
        assert b"\r\n" not in blob
    paths = [json.loads(line)["path"] for line in first[BDM.JSONL_REL].decode("utf-8").splitlines()]
    assert paths == sorted(paths, key=lambda p: (p.lower(), p))


def test_the_markdown_carries_the_recipe_and_one_line_per_document(tmp_path: Path) -> None:
    root = _with_index(tmp_path)
    assert BDM.main(["--write", "--repo", str(root)]) == 0
    text = (root / BDM.MD_REL).read_text(encoding="utf-8")
    assert "rg -i" in text and "DOCS-MANIFEST.md" in text
    lines = [line for line in text.splitlines() if line.startswith("- ")]
    assert len(lines) == len(TREE)
    headings = [line[3:] for line in text.splitlines() if line.startswith("## ")]
    assert headings == [kind for kind in BDM.KINDS if kind in headings]   # grouped, in kind order
    assert set(headings) == {BDM.classify(rel) for rel in TREE}
    caps_line = next(line for line in lines if CAPS_REL in line)
    assert "G2 short mode" in caps_line and "defines:" in caps_line and "terms:" in caps_line
    assert text.count("## doctrine") == 1


def test_check_follows_the_docs_and_reports_a_missing_artifact(tmp_path: Path, capsys) -> None:
    root = _with_index(tmp_path)
    assert BDM.main(["--write", "--repo", str(root)]) == 0
    assert BDM.main(["--check", "--repo", str(root)]) == 0
    assert BDM.main(["--repo", str(root)]) == 0                     # no flag is --check

    doc = root / DOCTRINE_REL
    doc.write_text(doc.read_text(encoding="utf-8").replace("Fake Motion Standards",
                                                           "Fake Motion Standards v2"), encoding="utf-8")
    capsys.readouterr()
    assert BDM.main(["--check", "--repo", str(root)]) == 1
    out = capsys.readouterr().out
    assert "STALE" in out and BDM.MD_REL in out and "run --write" in out

    assert BDM.main(["--write", "--repo", str(root)]) == 0
    (root / BDM.MD_REL).unlink()
    capsys.readouterr()
    assert BDM.main(["--check", "--repo", str(root)]) == 1
    assert "(missing)" in capsys.readouterr().out


def test_a_missing_index_is_refused_and_is_not_reported_as_staleness(tmp_path: Path, capsys) -> None:
    root = _tree(tmp_path)
    capsys.readouterr()
    assert BDM.main(["--check", "--repo", str(root)]) == 2
    out = capsys.readouterr().out
    assert "INDEX ERROR" in out and "STALE" not in out


# --- collapsed families ---------------------------------------------------------------------------

def _entry(path: str, kind: str = "other") -> dict:
    return {"path": path, "title": path.rsplit("/", 1)[-1], "kind": kind, "purpose": "A purpose.",
            "defines": [], "key_terms": ["term"]}


def test_a_collapsed_family_renders_as_one_row_per_folder_and_the_jsonl_keeps_every_file() -> None:
    entries = [
        _entry("docs/agent-memory/operator/MEMORY.md", "index"),
        _entry("docs/agent-memory/operator/recall-system.md"),
        _entry("docs/agent-memory/operator/casebook/README.md", "index"),
        _entry("docs/agent-memory/operator/casebook/the-thin-one-shot/CASE.md"),
        _entry("content/video_engine/sources/reference_analyses/bravos-x/REPORT.claude.md"),
        _entry("content/video_engine/sources/reference_analyses/bravos-x/SHOT_LEDGER.claude.md"),
        _entry("content/video_engine/sources/reference_analyses/MASTER_RESEARCH_INDEX.md", "index"),
        _entry(DOCTRINE_REL, "doctrine"),
    ]
    text = BDM.render_md(entries)
    lines = [line for line in text.splitlines() if line.startswith("- ")]
    rows = [line for line in lines if " documents" in line]
    assert [row.split(" — ")[0] for row in rows] == [
        "- content/video_engine/sources/reference_analyses/bravos-x/",
        "- docs/agent-memory/operator/",
        "- docs/agent-memory/operator/casebook/",            # the narrower family wins its files
    ]
    assert "2 documents, index MEMORY.md" in rows[1] and "2 documents, index README.md" in rows[2]
    assert "recall-system.md" not in text and "CASE.md" not in text.replace("one CASE.md", "")
    assert any(DOCTRINE_REL in line for line in lines)                    # the rest keep a line each
    assert any("MASTER_RESEARCH_INDEX.md" in line for line in lines)      # a loose file is not a family
    assert f"## {BDM.FAMILIES_HEADING}" in text and "## other" not in text   # no empty kind section
    assert f"{len(entries)} documents across" in text
    jsonl = [json.loads(line)["path"] for line in BDM.render_jsonl(entries).splitlines()]
    assert jsonl == [e["path"] for e in entries]


def _folder_rows(text: str) -> list[str]:
    section = text.split(f"\n## {BDM.FAMILIES_HEADING}\n", 1)
    return [line for line in section[1].splitlines() if line.startswith("- ")] if len(section) == 2 else []


def test_an_episode_folder_is_one_row_carrying_its_index_title_and_purpose() -> None:
    lane = "content/video_engine/projects/lane"
    entries = [
        _entry(f"{lane}/episode/README.md", "index"),
        _entry(f"{lane}/episode/SCRIPT-A.md"),
        _entry(f"{lane}/episode/review-v1/NOTES.md"),
        _entry(f"{lane}/pilots/p1/SCRIPT.md"),
        _entry(f"{lane}/SEEDS.md"),
    ]
    text = BDM.render_md(entries)
    assert _folder_rows(text) == [
        f"- {lane}/episode/ — one episode's working folder — 3 documents, index README.md: README.md — A purpose.",
        f"- {lane}/pilots/p1/ — one pilot's working folder — 1 document, index SCRIPT.md: SCRIPT.md — A purpose.",
    ]
    assert any(line.startswith(f"- {lane}/SEEDS.md — ") for line in text.splitlines())   # a lane file stays


MEMORY_REL = "docs/agent-memory/operator/fake-memory.md"
MEMORY_DOC = (
    "---\n"
    "name: fake-memory\n"
    'description: "a recorded take is the record - never edit it in place"\n'
    "metadata:\n"
    "  type: feedback\n"
    "---\n"
    "\n"
    "The VO text of a recorded take is not a draft: the timeline and the caption chain align to it.\n"
)
MEMORY_INDEX_REL = "docs/agent-memory/operator/MEMORY.md"


def test_a_front_matter_document_with_no_heading_yields_one_record_named_by_its_front_matter(
        tmp_path: Path) -> None:
    root = _tree(tmp_path)
    for rel_path, body in ((MEMORY_REL, MEMORY_DOC),
                           (MEMORY_INDEX_REL, "- [Fake memory](fake-memory.md) — the recorded take rule\n")):
        (root / rel_path).parent.mkdir(parents=True, exist_ok=True)
        (root / rel_path).write_text(body, encoding="utf-8")
    records = BDI.build_index(root, CONFIG)
    assert not [r for r in records if r["path"] in (MEMORY_REL, MEMORY_INDEX_REL)]   # no heading to index
    entries = _entries(root)
    memory = entries[MEMORY_REL]
    assert memory["title"] == "fake-memory"
    assert memory["purpose"] == "a recorded take is the record - never edit it in place"
    assert memory["sections"] == 1 and memory["headings"] == ["fake-memory"]
    assert any("recorded take" in lead for lead in memory["leads"])        # the body, not the YAML
    assert "feedback" not in json.dumps(memory)
    assert entries[MEMORY_INDEX_REL]["title"] == "MEMORY.md" and entries[MEMORY_INDEX_REL]["purpose"]
    stale = BDM.build([r for r in records if r["path"] != DOCTRINE_REL], root)
    assert DOCTRINE_REL not in {e["path"] for e in stale}                   # a stale index is not masked


def test_family_of_matches_whole_segments_only() -> None:
    assert BDM.family_of("docs/agent-memory/explorer/MEMORY.md") == (
        "docs/agent-memory/explorer/", "agent memory copies, one file per memory")
    assert BDM.family_of("docs/agent-memory/README.md") is None               # the folder itself
    assert BDM.family_of("docs/agent-memory-other/x/y.md") is None
    assert BDM.family_of(DOCTRINE_REL) is None


# --- the real tree ----------------------------------------------------------------------------------

def _real_entries() -> dict[str, dict]:
    records = BDM.load_index(ROOT / BDM.INDEX_REL)
    return {e["path"]: e for e in BDM.build(records, ROOT)}


def test_real_docs_yield_one_record_per_document_and_a_readable_markdown() -> None:
    entries = _real_entries()
    assert len(entries) > 150
    assert (ROOT / BDM.MD_REL).is_file() and (ROOT / BDM.JSONL_REL).is_file()
    text = BDM.render_md(list(entries.values()))
    assert len(text.encode("utf-8")) <= BDM.MD_MAX_BYTES
    assert (ROOT / BDM.MD_REL).stat().st_size <= BDM.MD_MAX_BYTES
    assert all(entry["purpose"] for entry in entries.values())


def test_real_docs_own_their_ids_and_reach_the_body_vocabulary() -> None:
    entries = _real_entries()
    assert "E41" in entries["docs/portable/OPERATOR-RULINGS.md"]["defines"]
    caps = entries["docs/content-video-engine/CAPABILITIES.md"]["defines"]
    assert any("G2 short mode" in title for title in caps)
    text = BDM.render_md(list(entries.values()))
    hits = [line for line in text.splitlines() if "kubelka" in line.lower()]
    assert any("44-INK-AND-SURFACE.md" in line for line in hits), hits


def test_real_heading_phrases_reach_their_document_through_the_jsonl() -> None:
    """`rg -i "brand line" docs/DOCS-MANIFEST.jsonl` has to land on the ledger that ruled it."""
    entries = _real_entries()
    lines = (ROOT / BDM.JSONL_REL).read_text(encoding="utf-8").splitlines()
    hits = [json.loads(line)["path"] for line in lines if "brand line" in line.lower()]
    assert "docs/portable/OPERATOR-RULINGS.md" in hits, hits
    rulings = entries["docs/portable/OPERATOR-RULINGS.md"]["headings"]
    assert any("brand line" in h.lower() for h in rulings)     # E41's own heading, not its body
    assert all(len(h) <= BDM.HEADING_TEXT_MAX for e in entries.values() for h in e["headings"])


def test_a_word_that_lives_only_in_a_lead_still_reaches_its_document() -> None:
    """`spiral` is doc 29 section 9.31's page vortex, and it is in neither the heading ("The page
    VORTEX") nor the label ("The retract") - `leads` is the layer that carries it."""
    lines = (ROOT / BDM.JSONL_REL).read_text(encoding="utf-8").splitlines()
    hits = [json.loads(line)["path"] for line in lines if "spiral" in line.lower()]
    doc29 = "docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md"
    assert doc29 in hits, hits
    entry = _real_entries()[doc29]
    assert any("spiral" in lead.lower() for lead in entry["leads"])
    assert not any("spiral" in v.lower() for v in [*entry["headings"], *entry["labels"]])
    assert all(len(v) <= BDM.LABEL_TEXT_MAX for e in _real_entries().values() for v in e["labels"])


def test_the_committed_markdown_is_byte_identical_after_the_jsonl_grew() -> None:
    """`labels` and `leads` are JSONL-only: the committed Markdown, generated before they existed,
    has to come back out of the builder at the same size, byte for byte."""
    committed = (ROOT / BDM.MD_REL).read_bytes()
    rebuilt = BDM.rendered(ROOT)[BDM.MD_REL].encode("utf-8")
    assert len(rebuilt) == len(committed) == (ROOT / BDM.MD_REL).stat().st_size
    assert rebuilt == committed


def test_real_families_collapse_and_the_last_rung_still_fits_the_cap() -> None:
    """The ladder is a runaway guard: when even its last rung misses the cap, the next document
    tips the file over. Collapsed folders keep that rung under MD_MAX_BYTES; the JSONL keeps them."""
    entries = list(_real_entries().values())
    last = BDM.render_md(entries, BDM.MD_LADDER[-1])
    assert len(last.encode("utf-8")) <= BDM.MD_MAX_BYTES
    text = BDM.render_md(entries)
    folders = {BDM.family_of(e["path"])[0] for e in entries if BDM.family_of(e["path"])}
    assert "docs/agent-memory/operator/" in folders
    walked = [p.relative_to(ROOT).as_posix() for p in BDI.doc_files(ROOT, BDI.load_config(ROOT))]
    memories = [p for p in walked if p.startswith("docs/agent-memory/")]
    paths = {e["path"] for e in entries}
    assert memories and [p for p in memories if p not in paths] == []     # every memory is findable
    for folder in folders:
        assert sum(1 for line in text.splitlines() if line.startswith(f"- {folder} — ")) == 1
    jsonl = [json.loads(line)["path"] for line in BDM.render_jsonl(entries).splitlines()]
    assert jsonl == [e["path"] for e in entries]
