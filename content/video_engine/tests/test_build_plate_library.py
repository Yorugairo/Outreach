"""THE PLATE INDEXER NEVER LOSES A RECORD SILENTLY (R26-130; P72 T28).

P58 T2 found `plate-p-viewers-desk` - operator-approved, render-eligible, in the SHIPPED `PLATE-LIBRARY.json` - reproduced by
no scanner, so every rebuild dropped it and nothing said so. The pins: a rebuild that would drop a record the shipped index
carries is REFUSED by the plate's id and writes nothing; the drop is taken only when named (`--drop <id>`), and a `--drop`
naming no lost record is refused by name; the sweep lists every operator-approved plate with no library record (each by id
and path), and says 0 when there is none. Every tree here is a tmp_path fixture: no real scanner root is read.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_plate_library as L  # noqa: E402

PROJECT = "content/video_engine/projects/chan/ep"


def png(path: Path) -> Path:
    from PIL import Image
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 8), (200, 190, 170)).save(path)
    return path


def fixture_repo(tmp_path: Path) -> Path:
    """One project registering one plate of its own (`assets/plates/plates.json`)."""
    repo = tmp_path / "repo"
    plates = repo / PROJECT / "assets/plates"
    png(plates / "plate-kept.png")
    (plates / "plates.json").write_text(json.dumps({"plates": {"plate-kept": {
        "semantic": "a kept plate", "state": "approved", "render_eligible": True}}}), encoding="utf-8")
    return repo


def shipped(out: Path, ids: list[str]) -> bytes:
    body = json.dumps({"schema_version": "plate_library.v2", "plates": [
        {"id": i, "path": f"C:/x/{i}.png", "source": "hand-appended", "state": "approved"} for i in ids]}).encode()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body)
    return body


def rebuild(repo: Path, out: Path, drops: tuple[str, ...] = ()) -> int:
    return L.rebuild(repo, out, codex=repo / "no-codex", drops=drops)


def test_a_rebuild_that_keeps_every_shipped_record_writes(tmp_path, capsys):
    repo = fixture_repo(tmp_path)
    out = repo / "lib/PLATE-LIBRARY.json"
    shipped(out, ["plate-kept"])
    assert rebuild(repo, out) == 0
    assert [p["id"] for p in json.loads(out.read_text(encoding="utf-8"))["plates"]] == ["plate-kept"]


def test_a_rebuild_that_would_drop_a_shipped_record_is_refused_by_the_plates_id_and_writes_nothing(tmp_path, capsys):
    repo = fixture_repo(tmp_path)
    out = repo / "lib/PLATE-LIBRARY.json"
    before = shipped(out, ["plate-kept", "plate-p-viewers-desk"])
    assert rebuild(repo, out) == 1
    text = capsys.readouterr().out
    assert "REFUSED" in text and "plate-p-viewers-desk" in text and "--drop plate-p-viewers-desk" in text
    assert out.read_bytes() == before                         # nothing written


def test_a_named_drop_is_taken_and_said(tmp_path, capsys):
    repo = fixture_repo(tmp_path)
    out = repo / "lib/PLATE-LIBRARY.json"
    shipped(out, ["plate-kept", "plate-gone"])
    assert rebuild(repo, out, drops=("plate-gone",)) == 0
    assert "dropped by name: plate-gone" in capsys.readouterr().out
    assert [p["id"] for p in json.loads(out.read_text(encoding="utf-8"))["plates"]] == ["plate-kept"]


def test_a_drop_that_names_no_lost_record_is_refused_by_name(tmp_path, capsys):
    repo = fixture_repo(tmp_path)
    out = repo / "lib/PLATE-LIBRARY.json"
    before = shipped(out, ["plate-kept"])
    assert rebuild(repo, out, drops=("plate-typo",)) == 1
    assert "--drop plate-typo" in capsys.readouterr().out
    assert out.read_bytes() == before


def test_the_first_build_has_nothing_to_lose(tmp_path):
    repo = fixture_repo(tmp_path)
    out = repo / "lib/PLATE-LIBRARY.json"
    assert rebuild(repo, out) == 0 and out.is_file()


def approvals(repo: Path, stills: list[tuple[str, str, bool]]) -> None:
    """A stills approval file (`stills_approval.v1`) with (shot, approved_path, approved) rows."""
    for _shot, rel, _ok in stills:
        png(repo / PROJECT / rel)
    (repo / PROJECT / "omni-video/stills").mkdir(parents=True, exist_ok=True)
    (repo / PROJECT / "omni-video/stills/APPROVALS.json").write_text(json.dumps({
        "schema_version": "stills_approval.v1",
        "stills": [{"shot": s, "approved_path": rel.replace("/", "\\"), "approved": ok, "approved_by": "operator"}
                   for s, rel, ok in stills]}), encoding="utf-8")


def test_the_sweep_names_every_approved_plate_with_no_library_record(tmp_path):
    repo = fixture_repo(tmp_path)
    approvals(repo, [("desk", "omni-video/stills/approved/still-desk.png", True),
                     ("tab", "omni-video/stills/approved/still-tab.png", True),
                     ("draft", "omni-video/stills/still-draft.png", False)])
    library = {"plates": [{"id": "plate-desk", "path": str(repo / PROJECT / "omni-video/stills/approved/still-desk.png")}]}
    found = L.sweep(repo, library)
    assert [(f["id"], f["path"]) for f in found] == [("tab", f"{PROJECT}/omni-video/stills/approved/still-tab.png")]
    assert "APPROVALS.json" in found[0]["where"]


def test_the_sweep_reads_a_record_by_its_path_from_any_checkout(tmp_path):
    repo = fixture_repo(tmp_path)
    approvals(repo, [("desk", "omni-video/stills/approved/still-desk.png", True)])
    other = "C:/Users/someone/Other Checkout/" + PROJECT + "/omni-video/stills/approved/still-desk.png"
    assert L.sweep(repo, {"plates": [{"id": "plate-desk", "path": other}]}) == []


def test_the_sweep_cli_says_zero_or_names_each(tmp_path, capsys, monkeypatch):
    repo = fixture_repo(tmp_path)
    out = repo / "lib/PLATE-LIBRARY.json"
    shipped(out, ["plate-kept"])
    assert L.main(["--sweep"], repo=repo, out=out) == 0
    assert "0 approved plate(s) with no library record" in capsys.readouterr().out
    approvals(repo, [("tab", "omni-video/stills/approved/still-tab.png", True)])
    assert L.main(["--sweep"], repo=repo, out=out) == 1
    text = capsys.readouterr().out
    assert "1 approved plate(s) with no library record" in text and "UNCOVERED tab" in text


def test_a_plate_wave_under_a_projects_review_claims_is_matched_by_its_path(tmp_path):
    """The claims root sits under a project (`.../review/claims/`): the key must start at `content/video_engine/`, never
    at the inner `review/` - a record from any checkout and the file in this one are the same plate."""
    repo = fixture_repo(tmp_path)
    wave = repo / "content/video_engine/projects/chan/review/claims/chan-plates-wave-1"
    png(wave / "objects/world-a-v1.png")
    (wave / "chan-plates-wave-1.manifest.json").write_text(json.dumps({"operator_approved": ["world-a-v1"]}),
                                                           encoding="utf-8")
    rec = r"C:\Other\content\video_engine\projects\chan\review\claims\chan-plates-wave-1\objects\world-a-v1.png"
    assert L.sweep(repo, {"plates": [{"id": "world-a-v1", "path": rec}]}) == []
    found = L.sweep(repo, {"plates": []})
    assert [f["id"] for f in found] == ["world-a-v1"] and found[0]["where"].endswith("manifest.json")


def test_a_control_character_in_an_approved_path_is_shown_and_the_same_id_record_named(tmp_path):
    """The live APPROVALS.json carries `stills<BEL>pproved` (a backslash-a written unescaped): the sweep says so."""
    repo = fixture_repo(tmp_path)
    (repo / PROJECT / "omni-video/stills").mkdir(parents=True)
    (repo / PROJECT / "omni-video/stills/APPROVALS.json").write_text(json.dumps({
        "schema_version": "stills_approval.v1",
        "stills": [{"shot": "plate-desk", "approved_path": "omni-video/stills\u0007pproved/still-desk.png",
                    "approved": True}]}), encoding="utf-8")
    lib = {"plates": [{"id": "plate-desk", "path": "C:/x/content/video_engine/p/still-desk.png"}]}
    [found] = L.sweep(repo, lib)
    assert found["path"] == "omni-video/stills\\x07pproved/still-desk.png"
    assert "control character" in found["where"] and "a record plate-desk exists" in found["where"]
