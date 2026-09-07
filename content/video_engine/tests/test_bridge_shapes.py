"""P46 T8 - the file shapes (docs/runbooks/BRIDGE-SHAPES.md): fetch, measure, watch, intake-triage - each closed by a FILE,
never by a judgement of prose; and bridge_send's flags for them, with the /watch skill named on every watch order."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import bridge_handlers as H  # noqa: E402
import bridge_send as BS  # noqa: E402

GRAMMAR = "POSITION: done\nPATHS WRITTEN:\n{paths}\nDISAGREEMENTS:\n- none\nPREREQUISITES:\n- none\nNOT FOUND WHERE I LOOKED:\n- none\n"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---- fetch -------------------------------------------------------------------------------------


def test_fetch_closes_on_a_manifest_whose_files_exist_and_hash(tmp_path: Path):
    d = tmp_path / "sources"; d.mkdir()
    a = d / "paper.pdf"; a.write_bytes(b"%PDF fake"); b = d / "page.md"; b.write_text("# page", encoding="utf-8")
    man = {"fetched_at": "2026-09-07T10:00:00-07:00", "entries": [
        {"url": "https://x/paper.pdf", "path": str(a), "sha256": _sha(a), "fetched_at": "2026-09-07T10:00:00-07:00"},
        {"url": "https://x/page", "path": str(b), "sha256": _sha(b), "fetched_at": "2026-09-07T10:00:01-07:00"},
        {"url": "https://x/gone", "status": "not-fetched"}]}
    (d / "MANIFEST.json").write_text(json.dumps(man), encoding="utf-8")
    order = {"replyShape": "fetch", "fetch_dir": str(d)}
    ok = H.classify(order, GRAMMAR.format(paths=str(d / "MANIFEST.json")), tmp_path)
    assert ok["pass"], ok
    assert any(c["name"] == "entries" and "2 fetched" in c["detail"] and "1 not-fetched" in c["detail"] for c in ok["checks"])
    b.write_text("# edited after the fetch", encoding="utf-8")
    bad = H.classify(order, GRAMMAR.format(paths=str(d / "MANIFEST.json")), tmp_path)
    assert not bad["pass"] and bad["class"] == "substance" and "sha256" in bad["reason"] or "!=" in bad["reason"]
    man["entries"][0].pop("sha256")
    (d / "MANIFEST.json").write_text(json.dumps(man), encoding="utf-8")
    missing = H.classify(order, "", tmp_path)
    assert not missing["pass"] and "missing sha256" in missing["reason"]
    assert not H.classify({"replyShape": "fetch"}, "", tmp_path)["pass"], "no fetch_dir on the order is a failure that names it"
    assert not H.classify({"replyShape": "fetch", "fetch_dir": str(tmp_path / "nowhere")}, "", tmp_path)["pass"]


# ---- measure -----------------------------------------------------------------------------------


def test_measure_wants_its_outputs_then_runs_the_tool(tmp_path: Path, monkeypatch):
    out = tmp_path / "cuts.csv"; out.write_text("a,b\n1,2\n", encoding="utf-8")
    ran: list = []
    monkeypatch.setattr(H, "run_command", lambda cmd, repo: (ran.append(cmd) or (0, "ok")))
    order = {"replyShape": "measure", "outputs": [str(out)], "verify": "python measure.py --check"}
    ok = H.classify(order, GRAMMAR.format(paths=str(out)), tmp_path)
    assert ok["pass"] and ran == [["python", "measure.py", "--check"]]
    ran.clear()
    gone = H.classify({**order, "outputs": [str(tmp_path / "missing.csv")]}, "", tmp_path)
    assert not gone["pass"] and gone["class"] == "form" and ran == [], "a missing output is form; the tool never runs"
    monkeypatch.setattr(H, "run_command", lambda cmd, repo: (1, "12 rows off"))
    wrong = H.classify(order, "", tmp_path)
    assert not wrong["pass"] and wrong["class"] == "substance" and "12 rows off" in wrong["reason"]
    assert not H.classify({"replyShape": "measure", "outputs": [str(out)]}, "", tmp_path)["pass"], "no verify, no measure"


# ---- watch -------------------------------------------------------------------------------------


def test_watch_closes_on_the_schema_verbatim_and_enough_rows_with_no_blank_required_cell(tmp_path: Path):
    csv = tmp_path / "cuts.csv"
    order = {"replyShape": "watch", "csv": str(csv), "schema": ["boundary", "t_s", "kind", "note"], "required": ["kind"], "min_rows": 3}
    csv.write_text("boundary,t_s,kind,note\n1,2.0,hard cut,\n2,4.5,dip,\n3,7.1,UNVERIFIED,too dark\n", encoding="utf-8")
    ok = H.classify(order, GRAMMAR.format(paths=str(csv)), tmp_path)
    assert ok["pass"], ok
    csv.write_text("boundary,t_s,transition,note\n1,2.0,hard cut,\n2,4.5,dip,\n3,7.1,dip,\n", encoding="utf-8")
    renamed = H.classify(order, "", tmp_path)
    assert not renamed["pass"] and renamed["class"] == "substance" and "schema" in renamed["reason"]
    csv.write_text("boundary,t_s,kind,note\n1,2.0,hard cut,\n", encoding="utf-8")
    short = H.classify(order, "", tmp_path)
    assert not short["pass"] and "1 row(s), min 3" in short["reason"]
    csv.write_text("boundary,t_s,kind,note\n1,2.0,hard cut,\n2,4.5,,\n3,7.1,dip,\n", encoding="utf-8")
    blank = H.classify(order, "", tmp_path)
    assert not blank["pass"] and "empty cell" in blank["reason"] and "UNVERIFIED" in blank["reason"]


# ---- intake-triage -------------------------------------------------------------------------------


SKELETON = """# Intake - a drop (2026-09-07)

## Claims

| # | claim | source | ours | status |
|---|---|---|---|---|
| 1 | holds breathe 1-2 % | proof line | docs/portable/OPERATOR-RULINGS.md:1463 | held |
| 2 | the black-hole cut | none | none: "black hole cut" | unsourced |

## Dedupe

| # | this drop's item | duplicate of | note |
|---|---|---|---|
| 1 | the transitions table | C:/x/docs/research/motion/WEALTH_LOGIC_TRANSITIONS_MEASURED.md | ours is measured |
| 2 | the idle rule | new | |

## Figures

| # | figure | tag | ours |
|---|---|---|---|
| 1 | 1-2 % | proof | idle.mjs BREATH_AMP |

## NOT FOUND WHERE I LOOKED

- docs_find "breathing", "black hole"
"""


def test_intake_triage_wants_the_skeleton_with_its_clerical_columns_filled(tmp_path: Path):
    area = tmp_path / "docs" / "research" / "motion"; area.mkdir(parents=True)
    f = area / "HYPERFRAMES-INTAKE.md"; f.write_text(SKELETON, encoding="utf-8")
    order = {"replyShape": "intake-triage", "area": "motion"}
    ok = H.classify(order, GRAMMAR.format(paths=str(f)), tmp_path)
    assert ok["pass"], ok
    f.write_text(SKELETON.replace("| docs/portable/OPERATOR-RULINGS.md:1463 | held |", "|  | held |"), encoding="utf-8")
    empty = H.classify(order, GRAMMAR.format(paths=str(f)), tmp_path)
    assert not empty["pass"] and empty["class"] == "substance" and "empty `ours`" in empty["reason"]
    f.write_text(SKELETON.replace("| held |", "| maybe |"), encoding="utf-8")
    status = H.classify(order, GRAMMAR.format(paths=str(f)), tmp_path)
    assert not status["pass"] and "status outside" in status["reason"]
    f.write_text(SKELETON.replace("## Dedupe", "## Duplicates"), encoding="utf-8")
    sec = H.classify(order, GRAMMAR.format(paths=str(f)), tmp_path)
    assert not sec["pass"] and sec["class"] == "form" and "Dedupe" in sec["reason"]
    assert not H.classify(order, GRAMMAR.format(paths=str(tmp_path / "notes.md")), tmp_path)["pass"], "only a *-INTAKE.md counts"


# ---- the send tool -------------------------------------------------------------------------------


def test_bridge_send_carries_the_shape_fields_and_names_the_watch_skill_on_every_watch_order(tmp_path: Path):
    parser = BS.build_parser()
    a = parser.parse_args(["--lane", "gemini", "--brief-file", "x.md", "--reply-shape", "watch", "--csv", "C:/w/cuts.csv",
                           "--schema", "boundary, t_s, kind", "--required", "kind", "--min-rows", "99"])
    order = BS.build_order(a, "brief")
    assert order["csv"].endswith("cuts.csv") and order["schema"] == ["boundary", "t_s", "kind"] and order["required"] == ["kind"] and order["min_rows"] == 99
    assert order["skills"] == ["watch"], "a watch order names the /watch skill even when the sender forgot"
    assert BS.with_skills("# Order\n", ["watch"]).startswith("**Skills:** use the `/watch` skill")
    assert BS.with_skills(BS.with_skills("# Order\n", ["watch"]), ["watch"]).count("**Skills:**") == 1
    b = parser.parse_args(["--lane", "gemini", "--brief-file", "x.md", "--reply-shape", "fetch", "--fetch-dir", "C:/f", "--skill", "research"])
    fo = BS.build_order(b, "brief")
    assert fo["fetch_dir"].endswith("f") and fo["skills"] == ["research"]
    c = parser.parse_args(["--lane", "gemini", "--brief-file", "x.md", "--reply-shape", "measure", "--output", "C:/o/a.csv", "--output", "C:/o/b.md", "--verify", "python m.py"])
    mo = BS.build_order(c, "brief")
    assert len(mo["outputs"]) == 2 and mo["verify"] == "python m.py"
    for shape in ("fetch", "measure", "watch", "intake-triage"):
        assert shape in BS.REPLY_SHAPES and shape in H.HANDLERS and shape in H.TEMPLATES
        assert "PATHS WRITTEN:" in H.template(shape)
