"""T19 compiler-only surface handoff contract; no renderer or approval claim."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402

FED_EP = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
FED_PAGE = "ledger:fed-on-rrp-history:line::right:surface=center-paper,1.20:cut"
FED_FLAT = "ledger:fed-on-rrp-history:line"
QUAD = [[0.25, 0.20], [0.75, 0.20], [0.75, 0.50], [0.25, 0.50]]


@pytest.fixture(autouse=True)
def _landscape_surface_contract(monkeypatch):
    """Surface grammar tests model the default landscape compiler input.

    Other compiler tests intentionally exercise a short and leave the module
    global at ``9:16``.  Keep that process history from changing the default
    contract tests; the final test below explicitly covers the portrait guard.
    """
    monkeypatch.setattr(B, "ASPECT", None)


def _fixture(tmp_path: Path, *, render_eligible: bool = True, status: str = "approved",
             kind: str = "paper", quad=None) -> tuple[Path, Path]:
    plate = tmp_path / "hall.png"
    plate.write_bytes(b"synthetic-approved-hall")
    sidecar = plate.with_suffix(".layers.json")
    sidecar.write_text(json.dumps({
        "status": status,
        "render_eligible": render_eligible,
        "embed": {"center-paper": {"kind": kind, "quad": quad or QUAD}},
    }), encoding="utf-8")
    return plate, sidecar


def _episode(tmp_path: Path) -> tuple[Path, Path]:
    series_path = tmp_path / "evidence" / "objects" / "fed-on-rrp-history.series.json"
    series_path.parent.mkdir(parents=True, exist_ok=True)
    series_path.write_text("synthetic series source", encoding="utf-8")
    return tmp_path, series_path


def _scenes(tmp_path: Path, monkeypatch, *, previous_world=None, current_span=(4.0, 8.0),
            current_camera=None, lead=1.2, source_ref=None):
    plate, _ = _fixture(tmp_path)
    episode, series_path = _episode(tmp_path)
    monkeypatch.setattr(B.R, "find_asset", lambda _asset_id: plate)
    ref = source_ref or {"series_id": "fed-on-rrp-history", "variant": "line", "sha256": B.sha(series_path)}
    page = {
        "builder": "dense-line", "variant": "line", "enter": "surface",
        "surface_from": {"surface": "center-paper", "lead_s": lead, "source_ref": ref},
        "_surface_source_ref": dict(ref),
    }
    previous = {
        "scene_id": "s03", "span": [0.0, 4.0], "world": previous_world or {
            "asset_id": "hall", "sha256": B.sha(plate), "ken_burns": {"scale": 0, "x": 0, "y": 0},
        }, "camera": B.camera_identity(),
    }
    current = {
        "scene_id": "s04", "span": list(current_span),
        "world": {"kind": B.SPECIES_LEDGER, "page": page,
                   "ken_burns": {"scale": 0, "x": 0, "y": 0}},
        "camera": current_camera or B.camera_identity(),
    }
    return [previous, current], episode, page


def test_surface_grammar_binds_dense_line_source_ref_and_flat_pages_stay_plain():
    world = B.world_for_plate(FED_PAGE, (0, 0, 0), FED_EP)
    source = FED_EP / "evidence/objects/fed-on-rrp-history.series.json"
    assert world["page"]["builder"] == "dense-line"
    assert world["page"]["enter"] == "surface"
    assert world["page"]["surface_from"]["source_ref"] == {
        "series_id": "fed-on-rrp-history", "variant": "line", "sha256": B.sha(source)
    }
    flat = B.world_for_plate(FED_FLAT, (0, 0, 0), FED_EP)
    assert "surface_from" not in flat["page"]
    assert "enter" not in flat["page"]


@pytest.mark.parametrize("lead", ["", "nan", "inf", "0", "-1", "1,2"])
def test_surface_lead_must_be_finite_positive_and_unambiguous(lead):
    plate_id = f"ledger:fed-on-rrp-history:line::right:surface=center-paper,{lead}:cut"
    with pytest.raises(ValueError, match="surface.*lead"):
        B.world_for_plate(plate_id, (0, 0, 0), FED_EP)


@pytest.mark.parametrize("option", ["depth=1", "plane=tilt:5", "form=tilted_line:5", "arrive=throw"])
def test_surface_cannot_compete_with_page_plane_form_or_arrival(option):
    with pytest.raises(ValueError, match="surface=.*cannot combine"):
        B.world_for_plate(f"{FED_PAGE};{option}", (0, 0, 0), FED_EP)


def test_surface_plot_geometry_is_native_wide_from_full_quad():
    geom = B.surface_plot_geometry(QUAD, (1920, 1080), view_h=560)
    assert geom["kind"] == "wide-dense-line"
    assert geom["view_h"] == 560.0
    assert geom["view_w"] == pytest.approx(560 * (0.5 * 1920) / (0.3 * 1080))


def test_synthetic_approved_surface_binds_two_linked_records(monkeypatch, tmp_path):
    scenes, episode, page = _scenes(tmp_path, monkeypatch)
    notes = B.bind_surface_page_arrivals(scenes, episode)
    previous, current = scenes
    establish = previous["surface_page"]
    incoming = current["world"]["page"]["surface_from"]
    assert notes and establish["to_scene"] == "s04"
    assert establish["presentation"] == "establish"
    assert establish["span"] == [2.8, 4.0]
    assert establish["quad"] == incoming["quad"] == QUAD
    assert establish["surface_layout"] == incoming["surface_layout"]
    assert establish["source_ref"] == incoming["source_ref"]
    assert incoming["scene"] == "s03"
    assert incoming["lead_s"] == 1.2 and incoming["grow_s"] == 0.45


def test_compiled_world_and_binder_wire_one_real_series_into_synthetic_fixture(monkeypatch, tmp_path):
    source = FED_EP / "evidence/objects/fed-on-rrp-history.series.json"
    target_source = tmp_path / "evidence" / "objects" / source.name
    target_source.parent.mkdir(parents=True, exist_ok=True)
    target_source.write_bytes(source.read_bytes())
    plate, _ = _fixture(tmp_path)
    monkeypatch.setattr(B.R, "find_asset", lambda _asset_id: plate)
    page_world = B.world_for_plate(FED_PAGE, (0, 0, 0), tmp_path)
    scenes = [
        {"scene_id": "s03", "span": [0.0, 4.0],
         "world": {"asset_id": "hall", "sha256": B.sha(plate),
                   "ken_burns": {"scale": 0, "x": 0, "y": 0}},
         "camera": B.camera_identity()},
        {"scene_id": "s04", "span": [4.0, 8.0], "world": page_world,
         "camera": B.camera_identity()},
    ]
    B.bind_surface_page_arrivals(scenes, tmp_path)
    assert scenes[0]["surface_page"]["source_ref"] == scenes[1]["world"]["page"]["surface_from"]["source_ref"]
    assert "_surface_source_ref" not in scenes[1]["world"]["page"]


def test_quarantined_synthetic_hall_remains_blocked(monkeypatch, tmp_path):
    scenes, episode, _page = _scenes(tmp_path, monkeypatch)
    plate = B.R.find_asset("hall")
    sidecar = plate.with_suffix(".layers.json")
    quarantined = json.loads(sidecar.read_text(encoding="utf-8"))
    quarantined["status"] = "quarantined_geometry_only"
    quarantined["render_eligible"] = False
    sidecar.write_text(json.dumps(quarantined), encoding="utf-8")
    with pytest.raises(ValueError, match="quarantined|render-eligible"):
        B.bind_surface_page_arrivals(scenes, episode)


def test_quarantined_copy_of_real_hall_sidecar_remains_blocked(monkeypatch, tmp_path):
    source_plate = FED_EP / "review/imagegen-complete-worlds-v1/finance-evidence-hall-hosted-v3-cream.png"
    source_sidecar = source_plate.with_suffix(".layers.json")
    if not source_plate.is_file() or not source_sidecar.is_file():
        pytest.skip("quarantined review plate and sidecar are not part of a clean checkout")
    plate = tmp_path / "quarantined-finance-hall.png"
    shutil.copyfile(source_plate, plate)
    quarantined = json.loads(source_sidecar.read_text(encoding="utf-8"))
    quarantined["status"] = "quarantined_geometry_only"
    quarantined["render_eligible"] = False
    plate.with_suffix(".layers.json").write_text(json.dumps(quarantined), encoding="utf-8")
    scenes, _episode_dir, page = _scenes(tmp_path, monkeypatch)
    monkeypatch.setattr(B.R, "find_asset", lambda _asset_id: plate)
    scenes[0]["world"]["sha256"] = B.sha(plate)
    real_series = FED_EP / "evidence/objects/fed-on-rrp-history.series.json"
    page["surface_from"]["source_ref"] = {
        "series_id": "fed-on-rrp-history", "variant": "line", "sha256": B.sha(real_series)
    }
    page["_surface_source_ref"] = dict(page["surface_from"]["source_ref"])
    with pytest.raises(ValueError, match="quarantined|render-eligible"):
        B.bind_surface_page_arrivals(scenes, FED_EP)


def test_surface_rejects_missing_or_unknown_registered_name(monkeypatch, tmp_path):
    scenes, episode, _page = _scenes(tmp_path, monkeypatch)
    plate = B.R.find_asset("hall")
    plate.with_suffix(".layers.json").unlink()
    with pytest.raises(ValueError, match="sidecar.*missing|invalid"):
        B.bind_surface_page_arrivals(scenes, episode)

    plate, _ = _fixture(tmp_path)
    data = json.loads(plate.with_suffix(".layers.json").read_text(encoding="utf-8"))
    data["embed"] = {"other-paper": data["embed"]["center-paper"]}
    plate.with_suffix(".layers.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="not registered"):
        B.bind_surface_page_arrivals(scenes, episode)


def test_surface_requires_paper_kind_and_registered_full_quad(monkeypatch, tmp_path):
    scenes, episode, _page = _scenes(tmp_path, monkeypatch)
    plate = B.R.find_asset("hall")
    plate.with_suffix(".layers.json").write_text(json.dumps({
        "status": "approved", "render_eligible": True,
        "embed": {"center-paper": {"kind": "chart", "quad": QUAD}},
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="paper"):
        B.bind_surface_page_arrivals(scenes, episode)

    plate.with_suffix(".layers.json").write_text(json.dumps({
        "status": "approved", "render_eligible": True,
        "embed": {"center-paper": {"kind": "paper", "quad": [[0.45, 0.2], [0.55, 0.2], [0.55, 0.5], [0.45, 0.5]]}},
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="under|floor"):
        B.bind_surface_page_arrivals(scenes, episode)


def test_surface_rejects_nonstatic_predecessor_camera_idle_and_grow_drift(monkeypatch, tmp_path):
    scenes, episode, _page = _scenes(tmp_path, monkeypatch,
                                     previous_world={"kind": B.SPECIES_LEDGER, "asset_id": "hall",
                                                     "sha256": "unused", "ken_burns": {"scale": 0, "x": 0, "y": 0}})
    with pytest.raises(ValueError, match="static image plate"):
        B.bind_surface_page_arrivals(scenes, episode)

    scenes, episode, _page = _scenes(tmp_path, monkeypatch,
                                     previous_world={"asset_id": "hall",
                                                     "ken_burns": {"scale": 0.1, "x": 0, "y": 0}})
    with pytest.raises(ValueError, match="zero Ken Burns"):
        B.bind_surface_page_arrivals(scenes, episode)

    camera = {"keys": [{"t": 4.1, "zoom": 1.1}], "attention": "locked"}
    scenes, episode, _page = _scenes(tmp_path, monkeypatch, current_camera=camera)
    with pytest.raises(ValueError, match="camera.*surface grow"):
        B.bind_surface_page_arrivals(scenes, episode)


def test_surface_rejects_lead_or_grow_span_shortfall(monkeypatch, tmp_path):
    scenes, episode, _page = _scenes(tmp_path, monkeypatch, current_span=(4.0, 4.2), lead=1.2)
    with pytest.raises(ValueError, match="insufficient incoming span"):
        B.bind_surface_page_arrivals(scenes, episode)

    scenes, episode, _page = _scenes(tmp_path, monkeypatch, lead=4.1)
    with pytest.raises(ValueError, match="insufficient incoming span"):
        B.bind_surface_page_arrivals(scenes, episode)


def test_surface_rejects_source_digest_drift(monkeypatch, tmp_path):
    bad_ref = {"series_id": "fed-on-rrp-history", "variant": "line", "sha256": "0" * 64}
    scenes, episode, _page = _scenes(tmp_path, monkeypatch, source_ref=bad_ref)
    with pytest.raises(ValueError, match="source_ref"):
        B.bind_surface_page_arrivals(scenes, episode)


@pytest.mark.parametrize("field,value", [("series_id", "other-series"), ("variant", "bars")])
def test_surface_rejects_public_source_identity_tamper(monkeypatch, tmp_path, field, value):
    scenes, episode, page = _scenes(tmp_path, monkeypatch)
    page["surface_from"]["source_ref"][field] = value
    with pytest.raises(ValueError, match="source_ref.*changed"):
        B.bind_surface_page_arrivals(scenes, episode)


def test_surface_is_explicitly_16_by_9_only(monkeypatch):
    monkeypatch.setattr(B, "ASPECT", "9:16")
    with pytest.raises(ValueError, match="16:9-only"):
        B.world_for_plate(FED_PAGE, (0, 0, 0), FED_EP)


def test_surface_validation_keeps_lead_and_option_errors_ahead_of_portrait_guard(monkeypatch):
    monkeypatch.setattr(B, "ASPECT", "9:16")
    invalid_lead = "ledger:fed-on-rrp-history:line::right:surface=center-paper,0:cut"
    with pytest.raises(ValueError, match="surface.*lead"):
        B.world_for_plate(invalid_lead, (0, 0, 0), FED_EP)
    with pytest.raises(ValueError, match="surface=.*cannot combine"):
        B.world_for_plate(f"{FED_PAGE};depth=1", (0, 0, 0), FED_EP)
