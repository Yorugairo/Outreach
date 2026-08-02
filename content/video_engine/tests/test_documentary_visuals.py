from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

from content.video_engine.src.guards.documentary_visual_direction import (
    validate_documentary_visual_approval,
)
from content.video_engine.src.guards.documentary_visual_qc import run_documentary_visual_qc
from content.video_engine.src.scenes.documentary import (
    DOCUMENTARY_FUNCTIONS,
    DocumentaryScene,
    DocumentarySceneError,
    illustrated_reconstruction,
)
from content.video_engine.src.services.documentary_style_board import (
    DOCUMENTARY_RUBRIC_DIMENSIONS,
    DOCUMENTARY_STYLE_BOARD_ROLES,
    DocumentaryStyleBoardService,
)
from content.video_engine.src.services.documentary_treatment import (
    DocumentaryTreatmentError,
    DocumentaryTreatmentService,
)
from content.video_engine.src.services.generated_visuals import (
    GeneratedVisualValidationError,
    motion_candidates_by_role,
    validate_generated_visual_candidates,
)


ART_BIBLE = Path(__file__).parents[1] / "configs" / "art_bibles" / "combat-history-archival-editorial-v1.json"
BRANDED_BIBLE = (
    Path(__file__).parents[1]
    / "configs"
    / "art_bibles"
    / "combat-history-branded-literature-v1.json"
)
PROFILE_FORK_BIBLE = (
    Path(__file__).parents[1]
    / "configs"
    / "art_bibles"
    / "combat-history-longform-cutout-fork-v1.json"
)


def _bible() -> dict:
    return json.loads(ART_BIBLE.read_text(encoding="utf-8"))


def _assets() -> dict:
    return {
        "assets": [
            {
                "asset_id": f"asset-{name}",
                "render_eligible": True,
                "credit_id": f"credit-asset-{name}",
                "attribution": "Local fixture",
                "license": "CC0",
            }
            for name in ("artifact", "portrait", "illustration", "document")
        ]
    }


def _plan() -> dict:
    return {
        "episode_id": "episode-1",
        "shots": [
            {"shot_id": 1, "function": "artifact_cold_open", "duration_s": 2, "asset_ids": ["asset-artifact"], "citations": ["claim-1"]},
            {"shot_id": 2, "function": "archival_portrait", "duration_s": 2, "asset_ids": ["asset-portrait"], "citations": ["claim-1"]},
            {"shot_id": 3, "function": "illustrated_reconstruction", "duration_s": 2, "asset_ids": ["asset-illustration"], "citations": ["claim-1"]},
            {"shot_id": 4, "function": "document_quote_closeup", "duration_s": 2, "asset_ids": ["asset-document"], "citations": ["claim-1"]},
            {"shot_id": 5, "function": "migration_map_timeline", "duration_s": 2, "citations": ["claim-1"]},
            {"shot_id": 6, "function": "lineage_graph", "duration_s": 2, "citations": ["claim-1"]},
            {"shot_id": 7, "function": "chapter_cta", "duration_s": 2},
        ],
    }


def test_documentary_factories_cover_eight_functions_and_label_illustration() -> None:
    assert len(DOCUMENTARY_FUNCTIONS) == 8
    record = illustrated_reconstruction({"asset_ids": [], "citations": ["claim-1"]})
    assert record["scene_class"] == "DocumentaryScene"
    assert "ILLUSTRATION" in record["illustration_label"]
    with pytest.raises(DocumentarySceneError):
        illustrated_reconstruction({"asset_ids": ["asset-a"], "source_url": "https://example.invalid/a.jpg"})
    scene = DocumentaryScene(record)
    scene.construct()
    assert scene.function == "illustrated_reconstruction"


def test_documentary_scene_refreshes_function_between_sequence_sections() -> None:
    scene = DocumentaryScene(
        {
            "scene_id": 1,
            "function": "artifact_cold_open",
            "parameters": {"label": "first"},
        }
    )
    scene._activate_scene(
        {
            "scene_id": 2,
            "function": "migration_map_timeline",
            "parameters": {
                "locations": [
                    {"id": "japan", "label": "Japan"},
                    {"id": "brazil", "label": "Brazil"},
                ]
            },
        },
        audio_duration=1.0,
    )

    assert scene.function == "migration_map_timeline"
    assert scene.record["scene_id"] == 2
    assert scene.parameters["locations"][1]["label"] == "Brazil"


def test_documentary_treatment_compiles_ids_only_and_is_deterministic() -> None:
    kwargs = {"research_packet": {"citations": [{"citation_id": "claim-1", "source_url": "https://evidence.invalid"}]}, "asset_manifest": _assets()}
    service = DocumentaryTreatmentService()
    first = service.compile(_plan(), _bible(), **kwargs)
    second = service.compile(_plan(), _bible(), **kwargs)
    assert first["schema_version"] == "visual_treatment.v2"
    assert first["source_kind"] == "documentary"
    assert first["artifact_hash"] == second["artifact_hash"]
    encoded = json.dumps(first)
    assert "https://evidence.invalid" not in encoded
    assert all(shot["scene_class"] == "DocumentaryScene" for shot in first["shots"])


def test_documentary_treatment_rejects_concept_over_budget() -> None:
    plan = {"shots": [{"shot_id": 1, "function": "concept_mechanics_cutaway", "duration_s": 2, "citations": ["claim-1"]}, {"shot_id": 2, "function": "chapter_cta", "duration_s": 1}]}
    with pytest.raises(DocumentaryTreatmentError, match="15%"):
        DocumentaryTreatmentService().compile(plan, _bible(), research_packet={"citations": [{"citation_id": "claim-1"}]}, asset_manifest={"assets": []})


def test_documentary_style_board_and_visual_gate(tmp_path: Path) -> None:
    board = DocumentaryStyleBoardService(width=160, height=96).build(_bible(), tmp_path / "style_board")
    assert board["required_roles"] == list(DOCUMENTARY_STYLE_BOARD_ROLES)
    assert board["approval_granted"] is False
    assert all((tmp_path / "style_board" / still["path"]).is_file() for still in board["stills"])
    rubric = {"schema_version": "documentary_visual_direction.v1", "art_bible_hash": board["art_bible_hash"], "scores": {key: 4 for key in DOCUMENTARY_RUBRIC_DIMENSIONS}}
    assert validate_documentary_visual_approval(tmp_path / "style_board", rubric, board["art_bible_hash"]) == []


def test_branded_literature_board_contains_all_three_editorial_modes(
    tmp_path: Path,
) -> None:
    bible = json.loads(BRANDED_BIBLE.read_text(encoding="utf-8"))
    board = DocumentaryStyleBoardService(width=320, height=180).build(
        bible,
        tmp_path / "branded-literature",
    )

    assert board["art_bible_id"] == "combat-history-branded-literature-v1"
    assert set(board["literature_modes"]) == {
        "lofi_comedy",
        "historical_comic",
        "archive_evidence",
    }
    assert {still["literature_mode"] for still in board["stills"]} == set(
        board["literature_modes"]
    )
    lineage = next(
        still for still in board["stills"] if still["role"] == "lineage_concept"
    )
    assert lineage["literature_mode"] == "lofi_comedy"


def test_profile_fork_board_preserves_hash_bound_production_grammar(
    tmp_path: Path,
) -> None:
    bible = json.loads(PROFILE_FORK_BIBLE.read_text(encoding="utf-8"))
    board = DocumentaryStyleBoardService(width=320, height=180).build(
        bible,
        tmp_path / "profile-fork",
    )

    assert board["art_bible_id"] == "combat-history-longform-cutout-fork-v1"
    assert board["production_profile"] == {
        "id": "longform-illustrated-history-v1",
        "hash": "6762c8c43e8d80aef7e0b8b39dc2cb5d5f77e46e259135cdc5fed0a4fab3cd35",
        "contract": "production_profile_fork.v1",
    }
    assert all(
        still["production_profile_id"]
        == "longform-illustrated-history-v1"
        for still in board["stills"]
    )


def test_profile_fork_board_integrates_job_local_selected_stock(
    tmp_path: Path,
) -> None:
    bible = json.loads(PROFILE_FORK_BIBLE.read_text(encoding="utf-8"))
    project = tmp_path / "project"
    job = tmp_path / "job"
    archive_path = project / "archive.jpg"
    stock_path = job / "asset_selection" / "assets" / "stock.jpg"
    ship_path = job / "asset_selection" / "assets" / "ship.jpg"
    for path, color in (
        (archive_path, "#777777"),
        (stock_path, "#285A92"),
        (ship_path, "#9B6739"),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (160, 96), color).save(path)
    assets = {
        "assets": [
            {
                "asset_id": "archive-kano",
                "local_path": "archive.jpg",
                "render_eligible": True,
            },
            {
                "asset_id": "magnific-stock-judo",
                "local_path": "asset_selection/assets/stock.jpg",
                "render_eligible": True,
            },
            {
                "asset_id": "magnific-stock-ship",
                "local_path": "asset_selection/assets/ship.jpg",
                "render_eligible": True,
            },
        ]
    }
    treatments = {
        "shots": [
            {
                "treatment_id": "treatment-archive",
                "function": "archival_portrait",
                "asset_ids": ["archive-kano", "magnific-stock-judo"],
            },
            {
                "treatment_id": "treatment-map",
                "function": "migration_map_timeline",
                "asset_ids": ["magnific-stock-ship"],
            },
        ]
    }

    board = DocumentaryStyleBoardService(width=320, height=180).build(
        bible,
        job / "style_board",
        treatments=treatments,
        asset_manifest=assets,
        project_root=project,
        job_root=job,
    )

    archive = next(still for still in board["stills"] if still["role"] == "archive")
    route = next(
        still for still in board["stills"] if still["role"] == "map_timeline"
    )
    assert archive["resolved_asset_count"] == 2
    assert route["resolved_asset_count"] == 1
    assert board["selected_stock_asset_count"] == 2


def _generated_visual_batch(job: Path) -> dict:
    items = []
    fixtures = (
        ("battlefield", "cold_open", "full_plate", "#8B3D2E", True),
        ("institution", "cold_open", "full_plate", "#D8C7A2", True),
        ("voyage", "illustration", "full_plate", "#34566F", True),
        ("joke", "lofi_comedy", "full_plate", "#C99A49", False),
        ("archive-world", "document", "background_only", "#513A29", True),
        ("travel-world", "map_timeline", "background_only", "#294754", True),
    )
    for item_id, role, usage, color, selected in fixtures:
        path = job / "generated_visuals" / "candidates" / f"{item_id}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (160, 96), color).save(path)
        items.append(
            {
                "id": f"generated-{item_id}",
                "role": role,
                "usage": usage,
                "path": path.relative_to(job).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "source_kind": "ai_assisted_illustration",
                "preview_eligible": True,
                "render_eligible": False,
                "evidence_eligible": False,
                "contains_factual_text": False,
                "review_status": "pending",
                "style_board_selected": selected,
                "disclosure_label": "AI-assisted illustration / reconstruction",
                "prompt_summary": "Original editorial print reconstruction.",
            }
        )
    return {
        "schema_version": "generated_visual_candidates.v1",
        "provider": "fixture-provider",
        "provider_calls": 6,
        "cost_usd": 0.0,
        "items": items,
    }


def test_generated_visual_candidates_are_preview_only_and_hash_bound(
    tmp_path: Path,
) -> None:
    payload = _generated_visual_batch(tmp_path)
    validated = validate_generated_visual_candidates(
        payload,
        job_root=tmp_path,
    )

    assert len(validated["items"]) == 6
    assert len(validated["artifact_hash"]) == 64
    assert all(item["render_eligible"] is False for item in validated["items"])

    payload["items"][0]["render_eligible"] = True
    with pytest.raises(
        GeneratedVisualValidationError,
        match="must remain false",
    ):
        validate_generated_visual_candidates(payload, job_root=tmp_path)


def test_generated_visual_candidates_reject_remote_paths(
    tmp_path: Path,
) -> None:
    payload = _generated_visual_batch(tmp_path)
    payload["items"][0]["path"] = "https://example.invalid/battlefield.png"

    with pytest.raises(
        GeneratedVisualValidationError,
        match="job-relative local path",
    ):
        validate_generated_visual_candidates(payload, job_root=tmp_path)


def test_generated_document_and_map_candidates_are_background_only(
    tmp_path: Path,
) -> None:
    payload = _generated_visual_batch(tmp_path)
    document = next(
        item for item in payload["items"] if item["role"] == "document"
    )
    document["usage"] = "full_plate"

    with pytest.raises(
        GeneratedVisualValidationError,
        match="background_only",
    ):
        validate_generated_visual_candidates(payload, job_root=tmp_path)


def test_generated_world_first_roles_support_motion_review_and_lineage_board(
    tmp_path: Path,
) -> None:
    payload = _generated_visual_batch(tmp_path)
    fixtures = (
        ("lineage-scroll", "lineage_concept", "full_plate", True),
        ("concept-cutaway", "concept_mechanics", "background_only", False),
    )
    for name, role, usage, board_selected in fixtures:
        path = tmp_path / "generated_visuals" / "candidates" / f"{name}.png"
        Image.new("RGB", (160, 96), "#D8C7A2").save(path)
        payload["items"].append(
            {
                "id": f"generated-{name}",
                "role": role,
                "usage": usage,
                "path": path.relative_to(tmp_path).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "source_kind": "ai_assisted_illustration",
                "preview_eligible": True,
                "render_eligible": False,
                "evidence_eligible": False,
                "contains_factual_text": False,
                "review_status": "pending",
                "style_board_selected": board_selected,
                "motion_selected": True,
                "disclosure_label": "AI-assisted illustration / reconstruction",
                "prompt_summary": "Original unlabeled woodblock world plate.",
            }
        )
    validated = validate_generated_visual_candidates(payload, job_root=tmp_path)
    assert validated["items"][-1]["motion_selected"] is True
    grouped, _ = motion_candidates_by_role(payload, job_root=tmp_path)
    assert set(grouped) == {"lineage_concept", "concept_mechanics"}

    bible = json.loads(PROFILE_FORK_BIBLE.read_text(encoding="utf-8"))
    board = DocumentaryStyleBoardService(width=320, height=180).build(
        bible,
        tmp_path / "world-first-board",
        generated_visuals=payload,
        project_root=tmp_path,
        job_root=tmp_path,
    )
    lineage = next(
        still for still in board["stills"] if still["role"] == "lineage_concept"
    )
    assert lineage["source"] == "generated_editorial_preview"
    assert lineage["generated_candidate_ids"] == ["generated-lineage-scroll"]


def test_profile_fork_board_uses_generated_visuals_only_as_gate_previews(
    tmp_path: Path,
) -> None:
    bible = json.loads(PROFILE_FORK_BIBLE.read_text(encoding="utf-8"))
    batch = _generated_visual_batch(tmp_path)
    board = DocumentaryStyleBoardService(width=320, height=180).build(
        bible,
        tmp_path / "style_board",
        generated_visuals=batch,
        project_root=tmp_path,
        job_root=tmp_path,
    )

    cold_open = next(
        still for still in board["stills"] if still["role"] == "cold_open"
    )
    illustration = next(
        still for still in board["stills"] if still["role"] == "illustration"
    )
    assert board["source"] == "hybrid_documentary_style_board"
    assert board["provider_calls"] == 6
    assert board["selected_generated_visual_count"] == 5
    assert len(cold_open["generated_candidate_ids"]) == 2
    assert len(illustration["generated_candidate_ids"]) == 1
    document = next(
        still for still in board["stills"] if still["role"] == "document"
    )
    map_timeline = next(
        still for still in board["stills"] if still["role"] == "map_timeline"
    )
    assert len(document["generated_candidate_ids"]) == 1
    assert len(map_timeline["generated_candidate_ids"]) == 1
    assert (
        cold_open["illustration_label"]
        == "AI-ASSISTED ILLUSTRATION / RECONSTRUCTION"
    )


def test_documentary_qc_rejects_stick_figures_missing_citations_and_duplicates() -> None:
    artifact = {"shots": [
        {"shot_id": 1, "function": "archival_portrait", "scene_class": "StickFigureScene", "treatment_id": "treatment-a", "uniqueness_signature": "same", "camera": {"safe_zone": "center"}, "duration_s": 2, "asset_ids": ["asset-a"]},
        {"shot_id": 2, "function": "archival_portrait", "scene_class": "DocumentaryScene", "treatment_id": "treatment-a", "uniqueness_signature": "same", "camera": {"safe_zone": "center"}, "duration_s": 2, "asset_ids": ["asset-a"]},
    ], "credits": {"credit-asset-a": {"display": "fixture"}}}
    result = run_documentary_visual_qc(artifact)
    assert result["overall"] == "fail"
    failed = {item["check_id"] for item in result["checks"] if item["status"] == "fail"}
    assert {"no_stick_figure_scene", "citation_coverage", "treatment_repetition"} <= failed


def test_documentary_qc_excludes_top_level_credit_records_from_renderer_provenance() -> None:
    artifact = {
        "shots": [
            {
                "shot_id": 1,
                "function": "archival_portrait",
                "scene_class": "DocumentaryScene",
                "treatment_id": "treatment-archive",
                "uniqueness_signature": "archive-hold",
                "camera": {"safe_zone": "center"},
                "duration_s": 2,
                "asset_ids": ["world-archive-study-v1"],
                "citations": ["claim-1"],
            }
        ],
        "credits": {
            "credit-world-archive-study-v1": {
                "source_url": "https://credits.example/world",
            }
        },
    }

    result = run_documentary_visual_qc(artifact)

    boundary = next(
        check for check in result["checks"] if check["check_id"] == "renderer_asset_boundary"
    )
    assert boundary["status"] == "pass"


def test_documentary_qc_allows_non_adjacent_signature_reuse() -> None:
    shots = []
    for index, signature in enumerate(("repeat", "middle", "repeat"), start=1):
        shots.append(
            {
                "shot_id": index,
                "function": "chapter_cta",
                "scene_class": "DocumentaryScene",
                "treatment_id": f"treatment-{index}",
                "uniqueness_signature": signature,
                "camera": {"safe_zone": "center"},
                "duration_s": 2,
            }
        )
    result = run_documentary_visual_qc({"shots": shots})
    repetition = next(
        item
        for item in result["checks"]
        if item["check_id"] == "treatment_repetition"
    )
    assert repetition["status"] == "pass"
