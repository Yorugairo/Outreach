"""Synthetic, read-only preflight tests for the Fed liquidity episode."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
BUILDER_PATH = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure/build_fed_liquidity.py"
SPEC = importlib.util.spec_from_file_location("fed_liquidity_builder", BUILDER_PATH)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)

GATES_PATH = ROOT / "content/video_engine/scripts/run_script_gates.py"
GATES_SPEC = importlib.util.spec_from_file_location("fed_run_script_gates", GATES_PATH)
assert GATES_SPEC and GATES_SPEC.loader
GATES = importlib.util.module_from_spec(GATES_SPEC)
sys.modules[GATES_SPEC.name] = GATES
GATES_SPEC.loader.exec_module(GATES)


def _write(path: Path, value: str | bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, bytes):
        path.write_bytes(value)
    else:
        path.write_text(value, encoding="utf-8")
    return path


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claims(root: Path) -> None:
    rrp = _write(root / "evidence/sources/rrp.csv", "date,value\n2026-09-18,0\n")
    rrp_meta = _write(root / "evidence/sources/rrp.html", "metadata\n")
    mpr = _write(root / "evidence/sources/mpr.html", "table\n")
    derived = _write(root / "evidence/derived/metadata.json", "{}\n")
    extractor = _write(root / "evidence/extract_sources.py", "# extractor\n")
    rates = _write(root / "evidence/derived/rates.csv", "date,rate\n")
    repo = _write(root / "evidence/derived/repo.csv", "date,accepted\n")

    def ref(path: Path) -> dict[str, str]:
        return {"path": path.relative_to(root).as_posix(), "sha256": _digest(path)}

    claims = {
        "schema": "mp-fed-liquidity.claims.v1",
        "claims": [
            {
                "id": "C1-C2",
                "source": {**ref(rrp), "metadata_path": rrp_meta.relative_to(root).as_posix(), "metadata_sha256": _digest(rrp_meta)},
                "units": "USD billions",
                "cutoff": "2026-09-18",
            },
            {
                "id": "C3",
                "source": ref(mpr),
                "units": "USD billions",
                "window": {"start": "2022-06-01", "end": "2025-06-11"},
            },
            {
                "id": "C5-funding-data",
                "source": ref(derived),
                "extractor": ref(extractor),
                "rates": {**ref(rates), "window": {"start": "2025-09-02", "end": "2026-09-17"}},
                "repo_take_up": {**ref(repo), "window": {"start": "2026-09-01", "end": "2026-09-18"}, "units": "USD"},
            },
        ],
        "qualitative_claims": [],
    }
    _write(root / "claims.v1.json", json.dumps(claims, indent=2))


ANCHOR_ROWS = [
    ("P01", "The Fed shrank its balance sheet by trillions.", "Before you see the hiring freeze or the cancelled expansion, someone has to decide what the next loan will cost."),
    ("P02", "One shortcut for watching this system is called net liquidity.", "We'll test the distinction against the Fed's June twenty twenty-five record."),
    ("P03", "Start with the Fed's balance sheet.", "So total Fed assets should tell you which way the banks' cushion moves."),
    ("P04", "Take a tax payment.", "Next, follow the cash that money funds parked at the Fed."),
    ("P05", "Then there is overnight reverse repo.", "Its balance tells you where that cash is sitting today."),
    ("P06", "At the end of twenty twenty-two, that balance briefly reached about two and a half trillion dollars.", "It was being moved into other investments, with consequences for the rest of the system."),
]


def _script(root: Path) -> tuple[Path, list[str]]:
    paragraphs = [f"{opening} {closing}" for _, opening, closing in ANCHOR_ROWS]
    paragraphs.append(" ".join(f"filler{i}" for i in range(47)))
    path = _write(root / "SCRIPT-VO.txt", "\n\n".join(paragraphs) + "\n")
    tokens = BUILDER._normalised_tokens(BUILDER._canonical_spoken(path.read_text(encoding="utf-8")))
    assert len(tokens) == 180
    return path, tokens


def _reports(root: Path, script: Path) -> None:
    digest = BUILDER.script_hash(script.read_text(encoding="utf-8"))
    _write(root / "SCRIPT-GATES.md", f"script_hash: {digest}\nRESULT: 0 FAIL / 0 WARN / 1 PASS\nVERDICT: PASS\n")
    _write(root / "SCRIPT-VIEWER.md", f"script_hash: {digest}\nRESULT: 0 FAIL / 0 WARN / 1 PASS / 0 INFO\n")
    _write(root / "SCRIPT-VIEWER-WINDOWS.json", json.dumps({"schema_version": "viewer_windows.v1", "script": "SCRIPT-VO.txt", "windows": [{"i": 0, "span": "0:00-1:00", "text": BUILDER.viewer_windows.spoken(script.read_text(encoding="utf-8"))}]}))
    _write(root / "SCRIPT-VIEWER-REPORTS.json", json.dumps({"schema_version": "viewer_reports.v1", "script": "SCRIPT-VO.txt", "windows_file": "SCRIPT-VIEWER-WINDOWS.json", "windows_run": 1, "reports": [{"i": 0, "span": "0:00-1:00"}]}))


def _anchors(root: Path) -> None:
    rows = [
        "| Group | Original beats | Opening anchor | Closing anchor | Authored states / handoff |",
        "|---|---|---|---|---|",
    ]
    rows.extend(f"| {group} | S | {opening} | {closing} | state |" for group, opening, closing in ANCHOR_ROWS)
    _write(root / "PILOT-SCENES.md", "\n".join(rows) + "\n")


def _assets(root: Path) -> None:
    ids = [
        "w2-owner-workshop-world-v1", "w4-finance-evidence-hall-v1",
        "p2-owner-loan-folio-v1",
    ]
    _write(root / "ASSET-CLAIM-SPEC.json", json.dumps({"slots": [{"asset_id": asset_id} for asset_id in ids]}))
    entries = []
    for index, asset_id in enumerate(ids):
        asset = _write(root / f"selected/asset-{index}.png", f"asset-{index}".encode())
        approval_payload = {
            "schema_version": "mp-fed-liquidity.asset-approval.v1",
            "episode_id": "fed-liquidity-pressure",
            "asset_id": asset_id,
            "asset_path": asset.relative_to(root).as_posix(),
            "asset_sha256": _digest(asset),
            "operator_decision": "approved_for_composition",
            "approved_at": "2026-09-19T00:00:00Z",
            "approval_basis": "synthetic operator HG2 fixture",
            "render_eligible": True,
        }
        approval_payload["artifact_hash"] = hashlib.sha256(
            json.dumps(approval_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        approval = _write(root / f"selected/approval-{index}.json", json.dumps(approval_payload, indent=2))
        entries.append({
            "asset_id": asset_id,
            "path": asset.relative_to(root).as_posix(),
            "sha256": _digest(asset),
            "approval_path": approval.relative_to(root).as_posix(),
            "approval_sha256": _digest(approval),
        })
    _write(root / "SELECTED-ASSETS.json", json.dumps({"schema": "mp-fed-liquidity.selected-assets.v1", "assets": entries}, indent=2))


def test_current_asset_contract_excludes_superseded_layers() -> None:
    current = json.loads((BUILDER.EPISODE_ROOT / BUILDER.ASSET_SPEC_NAME).read_text(encoding="utf-8"))
    assert {slot["asset_id"] for slot in current["slots"]} == set(BUILDER.APPROVED_ASSET_IDS)
    assert not BUILDER.SUPERSEDED_LAYER_ASSET_IDS.intersection(BUILDER.APPROVED_ASSET_IDS)


def test_layered_asset_contract_is_archived_but_not_current() -> None:
    archived = BUILDER.EPISODE_ROOT / "review/asset-contract-layered-v1/ASSET-CLAIM-SPEC.json"
    if not archived.is_file():
        pytest.skip("quarantined review archive is not part of a clean checkout")
    archived_ids = {
        slot["asset_id"]
        for slot in json.loads(archived.read_text(encoding="utf-8"))["slots"]
    }
    assert BUILDER.SUPERSEDED_LAYER_ASSET_IDS <= archived_ids


def test_superseded_layer_spec_fails_clearly(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    spec_path = root / "ASSET-CLAIM-SPEC.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["slots"] = [{"asset_id": asset_id} for asset_id in sorted(BUILDER.SUPERSEDED_LAYER_ASSET_IDS)]
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("superseded seven-layer contract is not accepted" in blocker for blocker in result.blockers)


def test_superseded_layer_manifest_has_no_coexistence_loophole(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    document, assets = _selected(root)
    assets[0]["asset_id"] = "w2-owner-workshop-background-v1"
    assets[1]["asset_id"] = "w2-owner-workshop-mid-v1"
    _rewrite_selected(root, document)
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("superseded seven-layer IDs are not accepted" in blocker for blocker in result.blockers)


def _take(root: Path, tokens: list[str]) -> Path:
    take = root / "take"
    _write(take / "scratch-kokoro.mp3", b"synthetic audio")
    words = [{"w": token, "start_s": round(index / 3, 6), "end_s": round((index + 1) / 3, 6)} for index, token in enumerate(tokens)]
    _write(take / "scratch-kokoro.words.json", json.dumps({
        "engine": "synthetic", "voice": "test", "duration_s": 60.0,
        "script_hash": BUILDER.script_hash((root / "SCRIPT-VO.txt").read_text(encoding="utf-8")),
        "words": words,
    }))
    return take


def _fixture(tmp_path: Path, *, selected: bool = True) -> Path:
    root = tmp_path / "episode"
    _claims(root)
    script, tokens = _script(root)
    _reports(root, script)
    _anchors(root)
    _assets(root)
    if not selected:
        (root / "SELECTED-ASSETS.json").unlink()
    _take(root, tokens)
    return root


@pytest.fixture
def fake_ffprobe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(BUILDER, "ffprobe_duration", lambda _path: 60.0)


def test_missing_inputs_fail_closed(tmp_path: Path) -> None:
    result = BUILDER.check_inputs(project_root=tmp_path, take_dir=tmp_path / "take", segment="pilot")
    assert not result.ok
    assert "selected asset manifest missing; HG2 pending" in result.blockers
    assert any("claims manifest" in blocker for blocker in result.blockers)
    assert any("script viewer" in blocker for blocker in result.blockers)


def test_script_hash_matches_run_script_gates_contract() -> None:
    text = "[payoff] The measured take is ready. [post-key]\n"
    assert BUILDER.script_hash(text) == GATES.script_hash(text)


def test_source_hash_mismatch_is_blocking(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    source = root / "evidence/sources/rrp.csv"
    source.write_text(source.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert not result.ok
    assert any("claims.claims[0].source.path: sha256 mismatch" in blocker for blocker in result.blockers)


@pytest.mark.parametrize("mutation", ["unhashed", "duplicate", "slot"])
def test_claim_and_slot_identity_cannot_drift(tmp_path: Path, fake_ffprobe: None, mutation: str) -> None:
    root = _fixture(tmp_path, selected=False)
    path = root / ("ASSET-CLAIM-SPEC.json" if mutation == "slot" else "claims.v1.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if mutation == "unhashed":
        del data["claims"][2]["extractor"]["sha256"]
    elif mutation == "duplicate":
        data["claims"].append(data["claims"][0])
    else:
        data["slots"][0]["asset_id"] = "unapproved-replacement"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any(x != "selected asset manifest missing; HG2 pending" for x in result.blockers)


@pytest.mark.parametrize("mutation", ["schema", "count", "index", "error", "span", "text", "filename"])
def test_stale_or_incomplete_viewer_is_rejected(tmp_path: Path, fake_ffprobe: None, mutation: str) -> None:
    root = _fixture(tmp_path, selected=False)
    filename = "SCRIPT-VIEWER-WINDOWS.json" if mutation == "text" else "SCRIPT-VIEWER-REPORTS.json"
    path = root / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    if mutation == "schema":
        data["schema_version"] = "wrong"
    elif mutation == "count":
        data["windows_run"] = 2
    elif mutation == "index":
        data["reports"][0]["i"] = 1
    elif mutation == "error":
        data["reports"][0]["error"] = "failed"
    elif mutation == "span":
        data["reports"][0]["span"] = "different"
    elif mutation == "filename":
        data["windows_file"] = "another.json"
    else:
        data["windows"][0]["text"] += " Stale added text."
    path.write_text(json.dumps(data), encoding="utf-8")
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any(x.startswith("viewer:") for x in result.blockers)


def test_units_and_date_window_contracts_are_checked(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    path = root / "claims.v1.json"
    claims = json.loads(path.read_text(encoding="utf-8"))
    claims["claims"][1]["units"] = "USD"
    claims["claims"][1]["window"]["end"] = "2025-06-12"
    path.write_text(json.dumps(claims), encoding="utf-8")
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("C3: units" in blocker for blocker in result.blockers)
    assert any("C3: window" in blocker for blocker in result.blockers)


def test_selected_manifest_missing_is_explicit_even_with_valid_take(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path, selected=False)
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert not result.ok
    assert result.blockers == ["selected asset manifest missing; HG2 pending"]


def test_word_clock_rejects_nonmonotone_timing_and_bad_hash(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    path = root / "take/scratch-kokoro.words.json"
    words = json.loads(path.read_text(encoding="utf-8"))
    words["script_hash"] = "0" * 64
    words["words"][12]["start_s"] = words["words"][11]["start_s"] - 1
    path.write_text(json.dumps(words), encoding="utf-8")
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("take word clock: word 12 is not monotone" in blocker for blocker in result.blockers)
    assert any("take: stale script_hash" in blocker for blocker in result.blockers)


def test_operator_bound_approval_passes(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert result.ok, result.blockers


def _selected(root: Path) -> tuple[dict, list[dict]]:
    path = root / "SELECTED-ASSETS.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    return document, document["assets"]


def _rewrite_selected(root: Path, document: dict) -> None:
    _write(root / "SELECTED-ASSETS.json", json.dumps(document, indent=2))


def _rewrite_approval(root: Path, entry: dict, payload: dict, *, refresh_manifest_hash: bool = True) -> None:
    approval_path = root / entry["approval_path"]
    _write(approval_path, json.dumps(payload, indent=2))
    if refresh_manifest_hash:
        entry["approval_sha256"] = _digest(approval_path)


def test_selected_approval_rejects_worker_only_completion_flag(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    document, assets = _selected(root)
    _rewrite_approval(root, assets[0], {"approved": True})
    _rewrite_selected(root, document)
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("selected approval w2-owner-workshop-world-v1: explicit operator_decision is required" in blocker for blocker in result.blockers)


def test_selected_approval_rejects_duplicate_operator_decision_key(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    document, assets = _selected(root)
    approval_path = root / assets[0]["approval_path"]
    original = approval_path.read_text(encoding="utf-8")
    marker = '  "operator_decision": "approved_for_composition",\n'
    assert marker in original
    approval_path.write_text(
        original.replace(marker, marker + '  "operator_decision": "worker",\n', 1),
        encoding="utf-8",
    )
    assets[0]["approval_sha256"] = _digest(approval_path)
    _rewrite_selected(root, document)
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any(
        "selected approval w2-owner-workshop-world-v1 artifact: duplicate JSON key 'operator_decision'" in blocker
        for blocker in result.blockers
    )


def test_selected_manifest_rejects_duplicate_key(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    path = root / "SELECTED-ASSETS.json"
    original = path.read_text(encoding="utf-8")
    marker = '  "schema": "mp-fed-liquidity.selected-assets.v1",\n'
    assert marker in original
    path.write_text(
        original.replace(marker, marker + '  "schema": "wrong",\n', 1),
        encoding="utf-8",
    )
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("selected asset manifest: duplicate JSON key 'schema'" in blocker for blocker in result.blockers)


def test_json_parser_rejects_nonfinite_constants(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    path = root / "SELECTED-ASSETS.json"
    original = path.read_text(encoding="utf-8")
    marker = '  "assets": ['
    assert marker in original
    path.write_text(original.replace(marker, '  "assets": [NaN,', 1), encoding="utf-8")
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("selected asset manifest: non-finite JSON constant 'NaN'" in blocker for blocker in result.blockers)


def test_selected_approval_rejects_changed_asset_bytes(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    _, assets = _selected(root)
    asset_path = root / assets[0]["path"]
    asset_path.write_bytes(asset_path.read_bytes() + b"tampered")
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("selected asset w2-owner-workshop-world-v1: sha256 mismatch" in blocker for blocker in result.blockers)
    assert any("selected approval w2-owner-workshop-world-v1: asset_sha256 does not match current asset bytes" in blocker for blocker in result.blockers)


def test_selected_approval_rejects_wrong_or_duplicate_identity(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    document, assets = _selected(root)
    assets[0]["asset_id"] = assets[1]["asset_id"]
    _rewrite_selected(root, document)
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("duplicate asset_id" in blocker for blocker in result.blockers)

    root = _fixture(tmp_path / "wrong")
    document, assets = _selected(root)
    approval_payload = json.loads((root / assets[0]["approval_path"]).read_text(encoding="utf-8"))
    approval_payload["asset_id"] = "w2-owner-workshop-mid-v1"
    _rewrite_approval(root, assets[0], approval_payload)
    _rewrite_selected(root, document)
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("asset_id binding is invalid" in blocker for blocker in result.blockers)


def test_selected_approval_rejects_escaping_path_and_stale_artifact_hash(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    document, assets = _selected(root)
    assets[0]["approval_path"] = "../outside-approval.json"
    _rewrite_selected(root, document)
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("selected approval w2-owner-workshop-world-v1: path escapes episode root" in blocker for blocker in result.blockers)

    root = _fixture(tmp_path / "stale")
    document, assets = _selected(root)
    approval_payload = json.loads((root / assets[0]["approval_path"]).read_text(encoding="utf-8"))
    approval_payload["approval_basis"] = "changed without re-signing"
    _rewrite_approval(root, assets[0], approval_payload)
    _rewrite_selected(root, document)
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert any("artifact_hash mismatch" in blocker for blocker in result.blockers)


@pytest.mark.parametrize("verdict", ["", "VERDICT: FAIL", "VERDICT: PASS\nVERDICT: FAIL"])
def test_gate_requires_explicit_unambiguous_pass(tmp_path: Path, fake_ffprobe: None, verdict: str) -> None:
    root = _fixture(tmp_path, selected=False)
    path = root / "SCRIPT-GATES.md"
    path.write_text(path.read_text(encoding="utf-8").replace("VERDICT: PASS", verdict), encoding="utf-8")
    result = BUILDER.check_inputs(project_root=root, take_dir=root / "take", segment="pilot")
    assert "script gates: exactly one explicit PASS verdict is required" in result.blockers


def test_cli_check_is_read_only_and_assembly_refuses_before_prerequisites(tmp_path: Path, fake_ffprobe: None, capsys: pytest.CaptureFixture[str]) -> None:
    root = _fixture(tmp_path, selected=False)
    tracked = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())
    before = {relative: (root / relative).read_bytes() for relative in tracked}
    assert BUILDER.main(["--segment", "pilot", "--check-inputs", "--project-root", str(root), "--take-dir", str(root / "take")]) == 1
    output = capsys.readouterr().out
    assert "selected asset manifest missing; HG2 pending" in output
    assert BUILDER.main(["--segment", "pilot", "--project-root", str(root)]) == 1
    refusal = capsys.readouterr().out
    assert "assembly: --take-dir is required; historical scratch fallback is disabled" in refusal
    assert "selected asset manifest missing; HG2 pending" in refusal
    assert not (root / "build-pilot").exists()
    after = {relative: (root / relative).read_bytes() for relative in tracked}
    assert before == after


def test_read_only_check_requires_an_explicit_take_without_historical_fallback(
    tmp_path: Path, fake_ffprobe: None,
) -> None:
    root = _fixture(tmp_path, selected=False)
    result = BUILDER.check_inputs(project_root=root, take_dir=None, segment="pilot")
    assert "take: --take-dir is required; historical scratch fallback is disabled" in result.blockers
    assert not any("r1337" in blocker for blocker in result.blockers)


@pytest.mark.parametrize("estimated,incoming", [(False, None), (False, "dip"), (True, None), (True, "dip")])
def test_pilot_rows_share_the_same_word_derived_boundary(monkeypatch, estimated, incoming):
    table = BUILDER.SHOT_TABLE_PILOT
    specs = (
        table.ShotSpec("P01", "Alpha.", table.WORKSHOP_WORLD, table.NO_KEN),
        table.ShotSpec("P01", "Beta.", table.WORKSHOP_WORLD, table.NO_KEN, incoming),
    )
    monkeypatch.setattr(table, "specs_for", lambda _segment: specs)
    words = [
        {"w": "Alpha.", "start_s": 0.0, "end_s": 0.6, "estimated": estimated},
        {"w": "Beta.", "start_s": 2.0, "end_s": 2.6, "estimated": estimated},
    ]
    rows = table.build_rows(words, 3.0, "bed")
    boundary = table.W.cut_before(words, "Beta.", exit=incoming or "cut")
    assert rows[0][0] == 0.0 and rows[-1][1] == 3.0
    assert rows[0][1] == rows[1][0] == boundary
    assert words[1]["start_s"] == 2.0  # The take is never moved to fit the cut.


def test_assembly_synthetic_fixture_writes_only_after_preflight(tmp_path: Path, fake_ffprobe: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """Exercise the authoring hand-off without touching real media or compiler state."""
    root = _fixture(tmp_path)
    # The base preflight fixture is intentionally dense.  Give the synthetic
    # P01 closing sentence a measured 0.50s gap so the real-tail guard is
    # exercised without pretending the fixture is production audio.
    clock_path = root / "take/scratch-kokoro.words.json"
    clock = json.loads(clock_path.read_text(encoding="utf-8"))
    for word in clock["words"][28:]:
        word["start_s"] = round(float(word["start_s"]) + 0.5, 6)
        word["end_s"] = round(float(word["end_s"]) + 0.5, 6)
    clock["duration_s"] = 60.5
    clock_path.write_text(json.dumps(clock), encoding="utf-8")
    monkeypatch.setattr(BUILDER, "ffprobe_duration", lambda _path: 60.5)
    for object_id in BUILDER.SOURCE_OBJECT_IDS:
        _write(root / "evidence/objects" / f"{object_id}.series.json", "{}\n")

    monkeypatch.setattr(
        BUILDER.SHOT_TABLE_PILOT,
        "group_end_phrase",
        lambda _group: ANCHOR_ROWS[0][2],
    )
    monkeypatch.setattr(
        BUILDER.SHOT_TABLE_PILOT,
        "build_rows",
        lambda _words, runtime, _segment: [(0.0, runtime, "w2-owner-workshop-world-v1;idle=none", (0.04, 12, -5), [], None, [])],
    )
    monkeypatch.setattr(
        BUILDER,
        "_trim_take_audio",
        lambda _take, build, _runtime: _write(build / "audio/episode.mp3", b"synthetic-trimmed-audio"),
    )
    monkeypatch.setattr(
        BUILDER.T,
        "caption_pages",
        lambda build, char_budget, max_words: _write(build / "caption-pages.json", json.dumps({"char_budget": char_budget, "max_words": max_words})),
    )
    monkeypatch.setattr(BUILDER.T, "compile_timeline", lambda *_args, **_kwargs: 0)

    assert BUILDER.assemble(project_root=root, take_dir=root / "take", segment="bed") == 0
    build = root / "build-bed"
    assert (build / "audio/episode.mp3").is_file()
    assert (build / "timeline.json").is_file()
    assert (build / "caption-pages.json").is_file()
    assert (build / "SHOT-TABLE-PILOT.py").is_file()
    assert (build / "BUILD-RECEIPT.md").is_file()
    receipt = (build / "BUILD-RECEIPT.md").read_text(encoding="utf-8")
    assert "one-direction Ken Burns" in receipt
    assert BUILDER.SHOT_TABLE_PILOT.AUTHORING_STATUS in receipt
    assert "spoken end:" in receipt
    assert "following word onset:" in receipt


def test_assembly_refuses_legacy_take_without_creating_build(tmp_path: Path, fake_ffprobe: None) -> None:
    root = _fixture(tmp_path)
    legacy = root / "vo-scratch-r1337"
    legacy.mkdir()
    before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
    assert BUILDER.assemble(project_root=root, take_dir=legacy, segment="pilot") == 1
    assert not (root / "build-pilot").exists()
    after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
    assert after == before


def test_segment_runtime_requires_real_tail_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(BUILDER.SHOT_TABLE_PILOT, "group_end_phrase", lambda _group: "Done.")
    words = [
        {"w": "Done.", "start_s": 0.0, "end_s": 1.0},
        {"w": "Next", "start_s": 2.0, "end_s": 2.5},
    ]
    boundary = BUILDER._segment_runtime(words, "bed", audio_duration_s=3.0)
    assert boundary.end_s == 1.45
    assert boundary.end_word_index == 0
    assert boundary.closing_phrase == "Done."
    assert boundary.spoken_end_s == 1.0
    assert boundary.next_word_start_s == 2.0
    bound = BUILDER._segment_runtime(
        words,
        "bed",
        audio_duration_s=3.0,
        anchors={"P01": {"closing_phrase": "Done.", "closing_index": 0}},
    )
    assert bound.end_word_index == 0
    with pytest.raises(ValueError, match="no longer matches"):
        BUILDER._segment_runtime(
            words,
            "bed",
            audio_duration_s=3.0,
            anchors={"P01": {"closing_phrase": "Done.", "closing_index": 1}},
        )

    crossing = [dict(words[0]), {"w": "Next", "start_s": 1.2, "end_s": 1.7}]
    with pytest.raises(ValueError, match="silence tail reaches"):
        BUILDER._segment_runtime(crossing, "bed", audio_duration_s=3.0)

    with pytest.raises(ValueError, match="no following word onset"):
        BUILDER._segment_runtime(words[:1], "bed", audio_duration_s=None)
    boundary = BUILDER._segment_runtime(words[:1], "bed", audio_duration_s=2.0)
    assert boundary.end_s == 1.45
    assert boundary.next_word_start_s is None


@pytest.mark.parametrize(
    ("bad_words", "message"),
    [
        ([{"w": "Done.", "start_s": 0.0, "end_s": True}], "non-finite"),
        ([{"w": "Done.", "start_s": 0.0, "end_s": math.nan}], "non-finite"),
        ([
            {"w": "Done.", "start_s": 1.0, "end_s": 1.5},
            {"w": "Next", "start_s": 0.5, "end_s": 2.0},
        ], "out of order"),
    ],
)
def test_segment_runtime_rejects_malformed_word_clock(
    monkeypatch: pytest.MonkeyPatch,
    bad_words: list[dict[str, object]],
    message: str,
) -> None:
    monkeypatch.setattr(BUILDER.SHOT_TABLE_PILOT, "group_end_phrase", lambda _group: "Done.")
    with pytest.raises(ValueError, match=message):
        BUILDER._segment_runtime(bad_words, "bed", audio_duration_s=3.0)


PILOT_REVIEW_PATH = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure/pilot_review.py"
PILOT_REVIEW_SPEC = importlib.util.spec_from_file_location("fed_liquidity_pilot_review_test", PILOT_REVIEW_PATH)
assert PILOT_REVIEW_SPEC and PILOT_REVIEW_SPEC.loader
PILOT_REVIEW = importlib.util.module_from_spec(PILOT_REVIEW_SPEC)
sys.modules[PILOT_REVIEW_SPEC.name] = PILOT_REVIEW
PILOT_REVIEW_SPEC.loader.exec_module(PILOT_REVIEW)


def _receipt_fixture(root: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """Create only synthetic pre-existing artifacts for the finalizer contract."""
    clock_path = root / "take/scratch-kokoro.words.json"
    clock = json.loads(clock_path.read_text(encoding="utf-8"))
    tokens = [str(item["w"]) for item in clock["words"]]
    _, closing_end = BUILDER._find_anchor(tokens, ANCHOR_ROWS[-1][2])[0]
    for word in clock["words"][closing_end:]:
        word["start_s"] = round(float(word["start_s"]) + 0.5, 6)
        word["end_s"] = round(float(word["end_s"]) + 0.5, 6)
    clock["duration_s"] = 60.5
    clock_path.write_text(json.dumps(clock), encoding="utf-8")
    monkeypatch.setattr(BUILDER, "ffprobe_duration", lambda _path: 60.5)

    scenes_path = root / "PILOT-SCENES.md"
    scenes = scenes_path.read_text(encoding="utf-8")
    scenes_path.write_text(scenes.replace("| P06 | S |", "| P06 | S09 |"), encoding="utf-8")
    _write(
        root / "PILOT-CHECK-SCOPE.md",
        "\n".join(
            [
                "schema: fed-liquidity.prefix-scope.v1",
                "timeline: fed-liquidity-pilot.timeline.json",
                "M01-M34 M36 M41 apply",
                "M35 M37 M38 M39 deferred",
                "M40 JUDGE",
                "M42 INFO",
                "",
            ]
        ),
    )
    for object_id in BUILDER.SOURCE_OBJECT_IDS:
        _write(root / "evidence/objects" / f"{object_id}.series.json", "{\"synthetic\":true}\n")

    build = root / "build-pilot"
    build.mkdir(parents=True)
    timeline_path = _write(
        build / "fed-liquidity-pilot.timeline.json",
        json.dumps({"schema_version": "scene_evidence_timeline.v1", "runtime_s": 60.5}),
    )
    player_path = _write(build / "player.html", "<!doctype html><title>synthetic pilot</title>\n")
    timeline_digest = _digest(timeline_path)
    player_digest = _digest(player_path)
    _write(
        build / "GATES-MOTION.md",
        "\n".join(
            [
                "=== MOTION DENSITY GATE: build-pilot ===",
                f"TIMELINE: fed-liquidity-pilot.timeline.json sha256:{timeline_digest}",
                "[PASS] M01 synthetic preflight",
                "[PASS] M35 deferred outside prefix",
                "[JUDGE] M40 parent review",
                "[INFO] M42 preserved note",
                "RESULT: 0 FAIL / 0 WARN / 1 PASS",
                "",
            ]
        ),
    )
    _write(
        build / "SELF-WATCH.md",
        "\n".join(
            [
                "# SELF-WATCH - synthetic - build-pilot - 2026-09-19 - prefix",
                f"player.html sha256 {player_digest} - timeline fed-liquidity-pilot.timeline.json - runtime 1:01",
                "[PASS] M01 synthetic frame check",
                "",
            ]
        ),
    )
    _write(
        build / "layout-probe.json",
        json.dumps({"schema": "synthetic.layout.v1", "timeline": "fed-liquidity-pilot.timeline.json", "player_sha256": player_digest}),
    )
    _write(
        build / "seam-frames.json",
        json.dumps({"schema": "synthetic.seams.v1", "build": "build-pilot", "runtime_s": 60.5, "boundaries": []}),
    )

    script_digest = _digest(root / "SCRIPT-VO.txt")
    audio_digest = _digest(root / "take/scratch-kokoro.mp3")
    parent_reads: dict[str, dict[str, object]] = {}
    for kind in ("visual", "audio"):
        evidence_path = _write(
            root / "review" / f"parent-{kind}-read.json",
            json.dumps(
                {
                    "schema": "fed-liquidity.parent-read.v1",
                    "kind": kind,
                    "observations": [f"synthetic {kind} read fixture"],
                    "timeline_sha256": timeline_digest,
                    "script_sha256": script_digest,
                    "audio_sha256": audio_digest,
                }
            ),
        )
        parent_reads[kind] = {
            "status": "READ",
            "evidence": {"path": evidence_path.relative_to(root).as_posix(), "sha256": _digest(evidence_path)},
            "read_at": "2026-09-19T00:00:00Z",
        }
    parent_reads_path = _write(root / "review/parent-reads.json", json.dumps(parent_reads, indent=2))
    return build, parent_reads_path.relative_to(root)


def test_finalize_receipt_is_consumable_by_pilot_review(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture(tmp_path)
    build, parent_reads_path = _receipt_fixture(root, monkeypatch)

    assert BUILDER.main(
        [
            "--finalize-review-receipt",
            "--segment",
            "pilot",
            "--project-root",
            str(root),
            "--take",
            "take",
            "--parent-reads",
            parent_reads_path.as_posix(),
        ]
    ) == 0
    receipt_path = build / BUILDER.RECEIPT_NAME
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["schema"] == "fed-liquidity.build-receipt.v1"
    assert receipt["prefix"]["measured_from"] == "take-word-clock"
    review = PILOT_REVIEW.inspect_build(build, mode="prefix")
    assert review.ok, review.blockers
    assert review.status == "PREFIX READY_FOR_PARENT_READ"


def test_finalize_refusal_does_not_overwrite_existing_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _fixture(tmp_path)
    build, parent_reads_path = _receipt_fixture(root, monkeypatch)
    assert BUILDER.finalize_review_receipt(
        project_root=root,
        take_dir=root / "take",
        parent_reads_path=parent_reads_path,
        segment="pilot",
    ) == 0
    receipt_path = build / BUILDER.RECEIPT_NAME
    before = receipt_path.read_bytes()

    parent_reads_file = root / parent_reads_path
    parent_reads = json.loads(parent_reads_file.read_text(encoding="utf-8"))
    parent_reads["visual"]["status"] = "PENDING"
    parent_reads_file.write_text(json.dumps(parent_reads), encoding="utf-8")
    assert BUILDER.finalize_review_receipt(
        project_root=root,
        take_dir=root / "take",
        parent_reads_path=parent_reads_path,
        segment="pilot",
    ) == 1
    assert receipt_path.read_bytes() == before


def test_finalize_missing_build_fails_closed_without_receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _fixture(tmp_path)
    parent_reads_path = _write(root / "review/parent-reads.json", "{}\n").relative_to(root)
    assert BUILDER.finalize_review_receipt(
        project_root=root,
        take_dir=root / "take",
        parent_reads_path=parent_reads_path,
        segment="pilot",
    ) == 1
    assert not (root / "build-pilot").exists()


def test_phrase_end_preserves_original_records_across_split_punctuation():
    words = [
        {"w": "Banks", "start_s": 0.0, "end_s": .3},
        {"w": "’", "start_s": .3, "end_s": .31},
        {"w": "balances", "start_s": .31, "end_s": .6},
        {"w": "held—without", "start_s": .6, "end_s": .9},
        {"w": "growing.", "start_s": .9, "end_s": 1.2},
    ]
    assert BUILDER._phrase_end_index(words, "Banks’ balances held—without growing.") == 4


def test_phrase_end_rejects_duplicate_sentence():
    words = [{"w": "Again.", "start_s": t, "end_s": t + .5} for t in (0., 1.)]
    with pytest.raises(ValueError, match="occur once"):
        BUILDER._phrase_end_index(words, "Again.")


def test_surface_arrival_uses_continuous_word_onset_not_a_hard_cut(monkeypatch):
    table = BUILDER.SHOT_TABLE_PILOT
    specs = (
        table.ShotSpec("P01", "Alpha.", table.FINANCE_EVIDENCE_HALL, table.NO_KEN),
        table.ShotSpec("P01", "Beta.", "ledger:fed-on-rrp-history:line::right:surface=center-paper,1.2:cut", table.NO_KEN),
    )
    monkeypatch.setattr(table, "specs_for", lambda _segment: specs)
    words = [{"w": "Alpha.", "start_s": 0., "end_s": 2.},
             {"w": "Beta.", "start_s": 2., "end_s": 3.}]
    rows = table.build_rows(words, 3.5, "bed")
    assert rows[0][1] == rows[1][0] == 2.
