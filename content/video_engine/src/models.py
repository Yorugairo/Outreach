from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Protocol
from uuid import uuid4


STORYBOARD_CONTRACT_VERSION = "storyboard.v2.1"
VIDEO_PIPELINE_CONTRACT_VERSION = 3
HISTORY_STORYBOARD_CONTRACT_VERSION = "storyboard.v2.2"
HISTORY_VIDEO_PIPELINE_CONTRACT_VERSION = 4
LIVING_HISTORY_STORYBOARD_CONTRACT_VERSION = "storyboard.v2.3"
LIVING_HISTORY_VIDEO_PIPELINE_CONTRACT_VERSION = "4.1"

SCENE_CLASS_REGISTRY: dict[str, dict[str, Any]] = {
    "BJJActionScene": {
        "visual_types": ["bjj_action"],
        "actions": ["bjj_action", "flash_label"],
        "continuous_with": ["BJJActionScene", "CombatScienceScene"],
    },
    "CombatScienceScene": {
        "visual_types": ["bjj_action", "joint_leverage_diagram", "comparison", "title_card"],
        "actions": ["bjj_action", "flash_label", "reveal_geometry"],
        "continuous_with": ["BJJActionScene", "CombatScienceScene"],
    },
    "StickFigureScene": {
        "visual_types": ["stick_figure_action"],
        "actions": ["pose"],
        "continuous_with": ["StickFigureScene"],
    },
    "TitleConceptCard": {
        "visual_types": ["title_card"],
        "actions": ["flash_label"],
        "continuous_with": ["TitleConceptCard"],
    },
    "JointLeverageScene": {
        "visual_types": ["joint_leverage_diagram"],
        "actions": ["flash_label"],
        "continuous_with": ["JointLeverageScene"],
    },
    "MapNetworkScene": {
        "visual_types": ["map_data_overlay", "timeline"],
        "actions": ["map", "flash_label"],
        "continuous_with": ["MapNetworkScene"],
    },
}

HISTORY_SCENE_CLASS_REGISTRY: dict[str, dict[str, Any]] = {
    "DocumentaryScene": {
        "visual_types": [
            "artifact_cold_open",
            "archival_portrait",
            "illustrated_reconstruction",
            "document_quote_closeup",
            "migration_map_timeline",
            "lineage_graph",
            "concept_mechanics_cutaway",
            "chapter_cta",
        ],
        "actions": [
            "reveal_artifact",
            "parallax",
            "reveal_document",
            "draw_map",
            "draw_timeline",
            "draw_lineage",
            "reveal_concept",
            "flash_label",
        ],
        "continuous_with": ["DocumentaryScene", "MapNetworkScene"],
    },
}
ALL_SCENE_CLASS_REGISTRY = {
    **SCENE_CLASS_REGISTRY,
    **HISTORY_SCENE_CLASS_REGISTRY,
}


def utc_now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid4())


class GateStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"


@dataclass(slots=True)
class VideoRun:
    source_ref: str
    id: str = field(default_factory=new_id)
    status: str = "queued"
    current_stage: str = "queued"
    input_payload: dict[str, Any] = field(default_factory=dict)
    config_snapshot: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    research_gate_status: str = GateStatus.PENDING.value
    asset_gate_status: str = GateStatus.PENDING.value
    visual_gate_status: str = GateStatus.PENDING.value
    gate_a_status: str = GateStatus.PENDING.value
    gate_b_status: str = GateStatus.PENDING.value
    error_text: str | None = None
    queued_at: str = field(default_factory=utc_now_iso)
    started_at: str | None = None
    completed_at: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class VideoStageEvent:
    video_run_id: str
    stage_name: str
    status: str
    id: str = field(default_factory=new_id)
    started_at: str | None = None
    completed_at: str | None = None
    output_summary: dict[str, Any] = field(default_factory=dict)
    error_text: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class StageOutput:
    summary: dict[str, Any] = field(default_factory=dict)


class RepositoryLike(Protocol):
    def update_run(self, run: VideoRun) -> VideoRun: ...


@dataclass(slots=True, frozen=True)
class StageContext:
    repository: RepositoryLike
    configs: dict[str, Any]
    job_dir: Path


StageFn = Callable[[VideoRun, StageContext], StageOutput]
