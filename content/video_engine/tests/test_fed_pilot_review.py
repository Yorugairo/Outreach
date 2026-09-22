"""Focused contract tests for the Fed episode PREFIX review adapter."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
sys.path.insert(0, str(EPISODE))

import pilot_review as review  # noqa: E402


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode() if isinstance(data, str) else data)


def _scope() -> str:
    return """# scope
scope schema: `fed-liquidity.prefix-scope.v1`
timeline: fed-liquidity-pilot.timeline.json
M01-M34 M36 M41 apply; M35 M37 M38 M39 deferred; M40 JUDGE; M42 INFO.
"""


def _fixture(tmp_path: Path, *, fail: str = "pass") -> tuple[Path, Path]:
    episode = tmp_path / "episode"
    build = episode / "build-pilot"
    build.mkdir(parents=True)
    _write(episode / "PILOT-CHECK-SCOPE.md", _scope())
    _write(episode / "SCRIPT-VO.txt", "A bounded synthetic script next.")
    _write(
        episode / review.PILOT_SCENES_NAME,
        """# synthetic pilot scene bindings

| Group | Original beats | Opening anchor | Closing anchor | Authored states / handoff |
|---|---|---|---|---|
| P06 | S09 | A bounded | synthetic script | synthetic |
""",
    )
    _write(episode / "sources.json", "{\"source\": true}\n")
    _write(episode / "asset.png", b"asset")
    _write(build / "player.html", "<html></html>\n")
    timeline = {
        "duration_s": 120.0,
        "words": [
            {"w": "A", "start_s": 0.0, "end_s": 10.0},
            {"w": "bounded", "start_s": 10.0, "end_s": 20.0},
            {"w": "synthetic", "start_s": 50.0, "end_s": 60.0},
            {"w": "script", "start_s": 90.0, "end_s": 100.0},
            {"w": "next", "start_s": 110.0, "end_s": 115.0},
        ],
    }
    timeline_bytes = json.dumps(timeline, sort_keys=True) + "\n"
    _write(build / review.TIMELINE_NAME, timeline_bytes)
    gate = {
        "pass": "  [PASS ] M01 one measured row\n  [JUDGE] M40 parity\n  [INFO ] M42 reported\n  [PASS ] M35 whole-cut floor\n",
        "within": "  [FAIL ] M01 failure at 10s\n  [JUDGE] M40 parity\n  [INFO ] M42 reported\n  [PASS ] M35 whole-cut floor\n",
        "unknown": "  [FAIL ] M01 failure location not stated\n  [JUDGE] M40 parity\n  [INFO ] M42 reported\n  [PASS ] M35 whole-cut floor\n",
        "outside": "  [FAIL ] M01 failure at 110s\n  [JUDGE] M40 parity\n  [INFO ] M42 reported\n  [PASS ] M35 whole-cut floor\n",
    }[fail]
    timeline_sha = _sha(build / review.TIMELINE_NAME)
    gate_text = (
        f"=== MOTION DENSITY GATE: {build} ===\n"
        + gate
        + "\nRESULT: 0 FAIL / 0 WARN / 1 PASS / 1 JUDGE / 1 INFO\n"
        + f"TIMELINE: {review.TIMELINE_NAME} sha256:{timeline_sha}\n"
    )
    _write(build / "GATES-MOTION.md", gate_text)
    player_sha = _sha(build / "player.html")
    _write(
        build / "SELF-WATCH.md",
        f"# SELF-WATCH - episode - {build.name} - 2026-09-18 - long (3 min opening)\n"
        f"player.html sha256 {player_sha[:12]} - timeline {review.TIMELINE_NAME} - runtime 2:00 - aspect 16:9 - script SCRIPT-VO\n\n"
        "## 1. The gates\n\n"
        "| one-shot floor (M35) | PASS | whole-cut floor |\n",
    )
    _write(
        build / "layout-probe.json",
        json.dumps({"instants": [], "player_sha256": player_sha, "timeline": review.TIMELINE_NAME}, sort_keys=True) + "\n",
    )
    _write(
        build / "seam-frames.json",
        json.dumps({"boundaries": [], "build": build.name, "runtime_s": 120.0}, sort_keys=True) + "\n",
    )
    _write(build / "take.wav", b"wav")
    _write(build / "take.words.json", timeline_bytes)
    _write(build / "assets.json", "{\"assets\": []}\n")
    script_sha = _sha(episode / "SCRIPT-VO.txt")
    audio_sha = _sha(build / "take.wav")
    evidence_paths = {}
    for kind in ("visual", "audio"):
        evidence_path = episode / "review" / f"parent-read-{kind}.json"
        _write(
            evidence_path,
            json.dumps(
                {
                    "schema": "fed-liquidity.parent-read.v1",
                    "kind": kind,
                    "timeline_sha256": timeline_sha,
                    "script_sha256": script_sha,
                    "audio_sha256": audio_sha,
                    "observations": [{"at_s": 0.0, "note": f"synthetic {kind} observation"}],
                },
                sort_keys=True,
            )
            + "\n",
        )
        evidence_paths[kind] = evidence_path
    refs = {
        "script": {"path": "SCRIPT-VO.txt", "sha256": script_sha},
        "take": {
            "id": "synthetic-take",
            "audio": {"path": "build-pilot/take.wav", "sha256": audio_sha},
            "words": {"path": "build-pilot/take.words.json", "sha256": _sha(build / "take.words.json")},
        },
        "timeline": {"path": f"build-pilot/{review.TIMELINE_NAME}", "sha256": timeline_sha},
        "player": {"path": "build-pilot/player.html", "sha256": _sha(build / "player.html")},
        "assets": {"manifest": {"path": "build-pilot/assets.json", "sha256": _sha(build / "assets.json")}},
        "source_custody": [{"path": "sources.json", "sha256": _sha(episode / "sources.json")}],
        "asset_custody": [{"path": "asset.png", "sha256": _sha(episode / "asset.png")}],
        "reports": [
            {"path": f"build-pilot/{name}", "sha256": _sha(build / name)} for name in review.REPORT_NAMES
        ],
        "prefix": {
            "sections": [f"S{i:02d}" for i in range(1, 10)],
            "start_s": 0,
            "end_s": 105.0,
            "spoken_end_s": 100.0,
            "end_word_index": 3,
            "measured_from": "take-word-clock",
        },
        "parent_reads": {
            "visual": {
                "status": "READ",
                "evidence": {"path": "review/parent-read-visual.json", "sha256": _sha(evidence_paths["visual"])},
                "read_at": "2026-09-18T10:00:00Z",
            },
            "audio": {
                "status": "READ",
                "evidence": {"path": "review/parent-read-audio.json", "sha256": _sha(evidence_paths["audio"])},
                "read_at": "2026-09-18T10:00:00Z",
            },
        },
        "schema": "fed-liquidity.build-receipt.v1",
    }
    _write(build / review.RECEIPT_NAME, json.dumps(refs, indent=2, sort_keys=True) + "\n")
    return build, episode / "PILOT-CHECK-SCOPE.md"


def _load_receipt(build: Path) -> dict:
    return json.loads((build / review.RECEIPT_NAME).read_text(encoding="utf-8"))


def _save_receipt(build: Path, receipt: dict) -> None:
    _write(build / review.RECEIPT_NAME, json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def _mutate_parent_read(build: Path, read_kind: str, **changes: object) -> None:
    receipt = _load_receipt(build)
    evidence_ref = receipt["parent_reads"][read_kind]["evidence"]
    evidence_path = build.parent / evidence_ref["path"]
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence.update(changes)
    _write(evidence_path, json.dumps(evidence, sort_keys=True) + "\n")
    evidence_ref["sha256"] = _sha(evidence_path)
    _save_receipt(build, receipt)


def _refresh_report_ref(build: Path, name: str) -> None:
    receipt = _load_receipt(build)
    entry = next(item for item in receipt["reports"] if Path(item["path"]).name == name)
    entry["sha256"] = _sha(build / name)
    _save_receipt(build, receipt)


def test_missing_report_blocks_without_writing(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    (build / "SELF-WATCH.md").unlink()
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("SELF-WATCH.md" in item for item in result.blockers)
    assert not (build / review.REVIEW_NAME).exists()


def test_script_hash_mismatch_blocks(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    (build.parent / "SCRIPT-VO.txt").write_text("changed\n", encoding="utf-8")
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("script: sha256 mismatch" in item for item in result.blockers)


def test_take_hash_mismatch_blocks(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    (build / "take.wav").write_bytes(b"changed take")
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("take.audio: sha256 mismatch" in item for item in result.blockers)


def test_within_prefix_failure_cannot_be_reclassified(tmp_path: Path):
    build, scope = _fixture(tmp_path, fail="within")
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    row = next(item for item in result.rows if item["id"] == "M01")
    assert row["classification"] == "WITHIN_PREFIX_FAIL"
    assert any("inside measured prefix" in item for item in result.blockers)


def test_unknown_failure_location_blocks(tmp_path: Path):
    build, scope = _fixture(tmp_path, fail="unknown")
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    row = next(item for item in result.rows if item["id"] == "M01")
    assert row["classification"] == "UNKNOWN_LOCATION"


def test_full_mode_rejects_prefix_deferrals(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    result = review.inspect_build(build, mode="full", scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("full mode" in item for item in result.blockers)


def test_whole_cut_floor_is_deferred_not_passed(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX READY_FOR_PARENT_READ"
    floor_rows = [item for item in result.rows if item["id"] == "M35"]
    assert floor_rows and all(item["classification"] == "FULL_EPISODE_DEFERRED" for item in floor_rows)


def test_multiple_named_timelines_block(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    _write(build / "other.timeline.json", "{}\n")
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("exactly one" in item for item in result.blockers)


def test_out_of_prefix_failure_is_explicitly_annotated(tmp_path: Path):
    build, scope = _fixture(tmp_path, fail="outside")
    result = review.inspect_build(build, scope_path=scope)
    assert not result.blockers
    row = next(item for item in result.rows if item["id"] == "M01")
    assert row["classification"] == "OUTSIDE_PREFIX"


def test_parent_read_evidence_missing_file_blocks(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    evidence_path = build.parent / "review" / "parent-read-visual.json"
    evidence_path.unlink()
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("parent read: visual.evidence: file missing" in item for item in result.blockers)


def test_parent_read_evidence_bad_hash_blocks(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    receipt = _load_receipt(build)
    receipt["parent_reads"]["visual"]["evidence"]["sha256"] = "0" * 64
    _save_receipt(build, receipt)
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("parent read: visual.evidence: sha256 mismatch" in item for item in result.blockers)


def test_parent_read_evidence_outside_episode_blocks(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    receipt = _load_receipt(build)
    receipt["parent_reads"]["visual"]["evidence"]["path"] = "../outside-parent-read.json"
    _save_receipt(build, receipt)
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("parent read: visual.evidence.path: path escapes episode root" in item for item in result.blockers)


def test_parent_read_evidence_wrong_timeline_blocks(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    _mutate_parent_read(build, "visual", timeline_sha256="0" * 64)
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("parent read: visual.evidence.timeline_sha256: must match receipt timeline sha256" in item for item in result.blockers)


def test_parent_read_evidence_wrong_kind_blocks(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    _mutate_parent_read(build, "visual", kind="audio")
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("parent read: visual.evidence.kind: must be visual" in item for item in result.blockers)


def test_parent_read_evidence_empty_observations_blocks(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    _mutate_parent_read(build, "audio", observations=[])
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("parent read: audio.evidence.observations: must be a non-empty array" in item for item in result.blockers)


def test_empty_raw_gate_report_blocks_even_with_fresh_receipt_hash(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    (build / "GATES-MOTION.md").write_text("\n", encoding="utf-8")
    _refresh_report_ref(build, "GATES-MOTION.md")
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("GATES-MOTION.md: report is empty" in item for item in result.blockers)


def test_unparseable_raw_gate_report_blocks_even_with_fresh_receipt_hash(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    (build / "GATES-MOTION.md").write_text("not a gate report\n", encoding="utf-8")
    _refresh_report_ref(build, "GATES-MOTION.md")
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("GATES-MOTION.md: no parseable gate rows" in item for item in result.blockers)


def test_raw_gate_timeline_binding_rejects_stale_same_name_report(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    text = (build / "GATES-MOTION.md").read_text(encoding="utf-8")
    text = text.replace(_load_receipt(build)["timeline"]["sha256"], "0" * 64)
    (build / "GATES-MOTION.md").write_text(text, encoding="utf-8")
    _refresh_report_ref(build, "GATES-MOTION.md")
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("GATES-MOTION.md: timeline sha256 does not match receipt" in item for item in result.blockers)


def test_raw_layout_binding_rejects_wrong_build_player(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    data = json.loads((build / "layout-probe.json").read_text(encoding="utf-8"))
    data["player_sha256"] = "0" * 64
    _write(build / "layout-probe.json", json.dumps(data, sort_keys=True) + "\n")
    _refresh_report_ref(build, "layout-probe.json")
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("layout-probe.json: player sha256 does not match receipt" in item for item in result.blockers)


def test_prefix_end_must_match_bound_p06_word_clock(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    receipt = _load_receipt(build)
    receipt["prefix"]["end_s"] = 99.0
    _save_receipt(build, receipt)
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert result.prefix["end_s"] == 99.0
    assert any("precedes measured spoken end" in item for item in result.blockers)


def test_prefix_end_rejects_wrong_bound_word_clock_even_when_receipt_is_rehashed(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    words = json.loads((build / "take.words.json").read_text(encoding="utf-8"))
    words["words"][3]["end_s"] = 105.0
    words["duration_s"] = 120.0
    payload = json.dumps(words, sort_keys=True) + "\n"
    _write(build / "take.words.json", payload)
    _write(build / review.TIMELINE_NAME, payload)
    receipt = _load_receipt(build)
    receipt["take"]["words"]["sha256"] = _sha(build / "take.words.json")
    receipt["timeline"]["sha256"] = _sha(build / review.TIMELINE_NAME)
    for kind in ("visual", "audio"):
        evidence_path = build.parent / receipt["parent_reads"][kind]["evidence"]["path"]
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["timeline_sha256"] = receipt["timeline"]["sha256"]
        _write(evidence_path, json.dumps(evidence, sort_keys=True) + "\n")
        receipt["parent_reads"][kind]["evidence"]["sha256"] = _sha(evidence_path)
    receipt["prefix"]["end_s"] = 105.0
    _save_receipt(build, receipt)
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert result.prefix["end_s"] == 105.0
    assert any("spoken_end_s does not match" in item for item in result.blockers)


def test_wrong_build_word_clock_is_not_prefix_ready(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    words = json.loads((build / "take.words.json").read_text(encoding="utf-8"))
    words["words"][-1]["w"] = "other"
    payload = json.dumps(words, sort_keys=True) + "\n"
    _write(build / "take.words.json", payload)
    _write(build / review.TIMELINE_NAME, payload)
    receipt = _load_receipt(build)
    receipt["take"]["words"]["sha256"] = _sha(build / "take.words.json")
    receipt["timeline"]["sha256"] = _sha(build / review.TIMELINE_NAME)
    for kind in ("visual", "audio"):
        evidence_path = build.parent / receipt["parent_reads"][kind]["evidence"]["path"]
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["timeline_sha256"] = receipt["timeline"]["sha256"]
        _write(evidence_path, json.dumps(evidence, sort_keys=True) + "\n")
        receipt["parent_reads"][kind]["evidence"]["sha256"] = _sha(evidence_path)
    _save_receipt(build, receipt)
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("spoken tokens do not match bound script" in item for item in result.blockers)


def test_prefix_end_can_land_in_measured_silence_before_next_word(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX READY_FOR_PARENT_READ"
    assert result.prefix["end_s"] == 105.0
    assert result.prefix["derived_spoken_end_s"] == 100.0
    assert result.prefix["derived_next_word_start_s"] == 110.0


def test_prefix_end_cannot_cross_next_spoken_word(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    receipt = _load_receipt(build)
    receipt["prefix"]["end_s"] = 111.0
    _save_receipt(build, receipt)
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("crosses the next spoken word" in item for item in result.blockers)


def test_prefix_spoken_end_and_word_index_are_explicitly_bound(tmp_path: Path):
    build, scope = _fixture(tmp_path)
    receipt = _load_receipt(build)
    receipt["prefix"]["spoken_end_s"] = 99.0
    receipt["prefix"]["end_word_index"] = 2
    _save_receipt(build, receipt)
    result = review.inspect_build(build, scope_path=scope)
    assert result.status == "PREFIX BLOCKED"
    assert any("spoken_end_s does not match" in item for item in result.blockers)
    assert any("end_word_index does not match" in item for item in result.blockers)
