from __future__ import annotations

import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable

from content.video_engine.src.models import (
    HISTORY_STORYBOARD_CONTRACT_VERSION,
    HISTORY_VIDEO_PIPELINE_CONTRACT_VERSION,
    LIVING_HISTORY_STORYBOARD_CONTRACT_VERSION,
    LIVING_HISTORY_VIDEO_PIPELINE_CONTRACT_VERSION,
    STORYBOARD_CONTRACT_VERSION,
    VIDEO_PIPELINE_CONTRACT_VERSION,
    GateStatus,
    StageContext,
    StageFn,
    StageOutput,
    VideoRun,
    VideoStageEvent,
)
from content.video_engine.src.repositories.base import VideoJobRepository


LEGACY_STAGES = [
    "ingesting_source",
    "transforming_script",
    "building_storyboard",
    "awaiting_storyboard_approval",
    "synthesizing_audio",
    "rendering_scenes",
    "compositing",
    "generating_captions",
    "packaging",
    "running_qc",
    "awaiting_publish_approval",
    "publishing",
]

V2_STAGES = [
    "ingesting_source",
    "building_technique_manifest",
    "transforming_script",
    "planning_shots",
    "building_storyboard",
    "rendering_animatic",
    "awaiting_storyboard_approval",
    "synthesizing_audio",
    "generating_captions",
    "rendering_scenes",
    "editing_picture",
    "designing_sound",
    "compositing",
    "packaging",
    "running_qc",
    "awaiting_publish_approval",
    "publishing",
]
V3_STAGES = [
    "ingesting_source",
    "building_technique_manifest",
    "transforming_script",
    "resolving_art_direction",
    "planning_shots",
    "compiling_visual_treatments",
    "building_storyboard",
    "rendering_style_board",
    "awaiting_visual_direction_approval",
    "rendering_animatic",
    "awaiting_storyboard_approval",
    "synthesizing_audio",
    "generating_captions",
    "rendering_scenes",
    "editing_picture",
    "designing_sound",
    "compositing",
    "packaging",
    "running_qc",
    "awaiting_publish_approval",
    "publishing",
]
V4_STAGES = [
    "ingesting_source",
    "validating_research",
    "resolving_assets",
    "preparing_research_review",
    "awaiting_research_approval",
    "transforming_script",
    "resolving_art_direction",
    "planning_shots",
    "compiling_visual_treatments",
    "building_storyboard",
    "rendering_style_board",
    "awaiting_visual_direction_approval",
    "rendering_animatic",
    "awaiting_storyboard_approval",
    "synthesizing_audio",
    "generating_captions",
    "rendering_scenes",
    "editing_picture",
    "designing_sound",
    "compositing",
    "packaging",
    "running_documentary_qc",
    "awaiting_publish_approval",
    "publishing",
]
V4_1_STAGES = [
    "ingesting_source",
    "validating_research",
    "resolving_assets",
    "preparing_research_review",
    "awaiting_research_approval",
    "transforming_script",
    "resolving_art_direction",
    "planning_shots",
    "compiling_editorial_coverage",
    "discovering_stock_candidates",
    "preparing_asset_selection_review",
    "awaiting_asset_selection_approval",
    "promoting_selected_assets",
    "compiling_visual_treatments",
    "building_storyboard",
    "rendering_style_board",
    "awaiting_visual_direction_approval",
    "rendering_animatic",
    "awaiting_storyboard_approval",
    "synthesizing_audio",
    "generating_captions",
    "rendering_scenes",
    "editing_picture",
    "designing_sound",
    "compositing",
    "packaging",
    "running_documentary_qc",
    "awaiting_publish_approval",
    "publishing",
]
# Existing callers use DEFAULT_STAGES as the frozen Visual V2 contract.
DEFAULT_STAGES = V2_STAGES
STAGE_ORDER = {stage: index + 1 for index, stage in enumerate(V4_STAGES)}
GATE_STAGES = {
    "awaiting_research_approval": (
        "research",
        "research_gate_status",
        "awaiting_research_gate",
    ),
    "awaiting_asset_selection_approval": (
        "assets",
        "asset_gate_status",
        "awaiting_asset_gate",
    ),
    "awaiting_visual_direction_approval": (
        "visual",
        "visual_gate_status",
        "awaiting_visual_gate",
    ),
    "awaiting_storyboard_approval": ("a", "gate_a_status", "awaiting_gate_a"),
    "awaiting_publish_approval": ("b", "gate_b_status", "awaiting_gate_b"),
}


def _contract_version(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(1)


def _version_at_least(value: Any, target: Any) -> bool:
    return _contract_version(value) >= _contract_version(target)


class VideoPipelineGateApprovalError(ValueError):
    """Raised when an operator approval request fails validation."""

    def __init__(self, gate: str, run_id: str, violations: list[str]):
        self.gate = gate
        self.run_id = run_id
        self.violations = violations
        message = f"run {run_id} failed Gate {gate.upper()} validation: " + "; ".join(
            violations
        )
        super().__init__(message)


class VideoPipeline:
    def __init__(
        self,
        repository: VideoJobRepository,
        *,
        configs: dict[str, Any] | None = None,
        stage_fns: dict[str, StageFn] | None = None,
        storyboard_validator: Callable[[Path], tuple[bool, list[str]]] | None = None,
        now_fn: Callable[[], str] | None = None,
        perf_counter_fn: Callable[[], float] | None = None,
    ):
        from content.video_engine.src.models import utc_now_iso
        from content.video_engine.src.guards.storyboard_guard import guard

        self.repository = repository
        self.configs = dict(configs or {})
        self.stage_fns = dict(stage_fns or {})
        self._storyboard_validator = storyboard_validator or guard
        self._now_fn = now_fn or utc_now_iso
        self._perf_counter_fn = perf_counter_fn or time.perf_counter

    def start(
        self,
        source_ref: str,
        *,
        channel: str = "combat-science",
        targets: list[str] | None = None,
    ) -> VideoRun:
        selected_targets = targets or ["landscape", "vertical"]
        selected_profiles = [
            {
                "landscape": "landscape_final",
                "vertical": "vertical_final",
            }.get(str(target), str(target))
            for target in selected_targets
        ]
        configured_profiles = self.configs.get("render_profiles") or {}
        profile_snapshot = {
            profile: dict(configured_profiles[profile])
            for profile in selected_profiles
            if profile in configured_profiles
        }
        source_slug = Path(source_ref).stem
        configured_channels = self.configs.get("channel_configs") or {}
        channel_config = (
            configured_channels.get(channel, {})
            if isinstance(configured_channels, dict)
            else {}
        )
        v3_pilots = {
            str(value)
            for value in (
                channel_config.get("visual_v3_pilot_slugs")
                or self.configs.get("visual_v3_pilot_slugs", [])
            )
            if str(value)
        }
        source_contract = self._source_contract(source_ref)
        history_lane_config = (
            (channel_config.get("series_lanes") or {}).get(
                "history-of-bjj", {}
            )
            if isinstance(channel_config, dict)
            else {}
        )
        pipeline_version = (
            (
                history_lane_config.get("pipeline_contract_version")
                if isinstance(history_lane_config, dict)
                else None
            )
            or LIVING_HISTORY_VIDEO_PIPELINE_CONTRACT_VERSION
            if source_contract == "history_episode.v1"
            else 3
            if source_slug in v3_pilots
            else 2
        )
        stage_order = (
            V4_1_STAGES
            if _version_at_least(
                pipeline_version, LIVING_HISTORY_VIDEO_PIPELINE_CONTRACT_VERSION
            )
            else V4_STAGES
            if _version_at_least(pipeline_version, 4)
            else V3_STAGES
            if _version_at_least(pipeline_version, 3)
            else V2_STAGES
        )
        series_lane = (
            "history-of-bjj"
            if _version_at_least(pipeline_version, 4)
            else str(channel_config.get("series") or "physics-of-grappling")
        )
        series_config = (
            (channel_config.get("series_lanes") or {}).get(series_lane, {})
            if isinstance(channel_config, dict)
            else {}
        )
        episode_character_pack = (
            (series_config.get("character_packs") or {}).get(source_slug, {})
            if isinstance(series_config, dict)
            else {}
        )
        run = VideoRun(
            source_ref=source_ref,
            input_payload={
                "source_ref": source_ref,
                "channel": channel,
                "series": series_lane,
                "targets": selected_targets,
            },
            config_snapshot={
                "pipeline_contract_version": pipeline_version,
                "storyboard_contract_version": (
                    LIVING_HISTORY_STORYBOARD_CONTRACT_VERSION
                    if _version_at_least(
                        pipeline_version,
                        LIVING_HISTORY_VIDEO_PIPELINE_CONTRACT_VERSION,
                    )
                    else HISTORY_STORYBOARD_CONTRACT_VERSION
                    if _version_at_least(pipeline_version, 4)
                    else STORYBOARD_CONTRACT_VERSION
                ),
                "channel": channel,
                "art_bible_id": (
                    series_config.get("art_bible_id")
                    or channel_config.get("art_bible_id")
                    or self.configs.get("art_bible_id")
                ),
                "character_pack_id": (
                    episode_character_pack.get("id")
                    if isinstance(episode_character_pack, dict)
                    else ""
                ),
                "character_pack_path": (
                    episode_character_pack.get("path")
                    if isinstance(episode_character_pack, dict)
                    else ""
                ),
                "source_contract": source_contract,
                "series": series_lane,
                "targets": selected_targets,
                "selected_render_profiles": selected_profiles,
                "render_profile_configs": profile_snapshot,
                "stage_order": list(stage_order),
            },
        )
        self.repository.create_run(run)
        now = self._now_fn()
        run.status = "running"
        run.started_at = now
        run.updated_at = now
        self.repository.update_run(run)
        return self._execute(run)

    def resume(self, run_id: str) -> VideoRun:
        run = self._require_run(run_id)
        if run.status in {"packaged", "published"}:
            return run
        if (
            run.status == "awaiting_research_gate"
            and run.research_gate_status != GateStatus.APPROVED.value
        ):
            return run
        if (
            run.status == "awaiting_asset_gate"
            and run.asset_gate_status != GateStatus.APPROVED.value
        ):
            return run
        if (
            run.status == "awaiting_visual_gate"
            and run.visual_gate_status != GateStatus.APPROVED.value
        ):
            return run
        if run.status == "awaiting_gate_a" and run.gate_a_status != GateStatus.APPROVED.value:
            return run
        if run.status == "awaiting_gate_b" and run.gate_b_status != GateStatus.APPROVED.value:
            return run
        run.status = "running"
        run.error_text = None
        run.completed_at = None
        run.updated_at = self._now_fn()
        self.repository.update_run(run)
        return self._execute(run)

    def approve(
        self,
        run_id: str,
        gate: str,
        *,
        rubric_path: str | Path | None = None,
    ) -> VideoRun:
        gate = gate.casefold()
        if gate not in {"research", "assets", "visual", "a", "b"}:
            raise ValueError(
                "gate must be 'research', 'assets', 'visual', 'a', or 'b'"
            )
        run = self._require_run(run_id)
        expected_status = (
            "awaiting_research_gate"
            if gate == "research"
            else "awaiting_asset_gate"
            if gate == "assets"
            else "awaiting_visual_gate"
            if gate == "visual"
            else f"awaiting_gate_{gate}"
        )
        if run.status != expected_status:
            raise ValueError(
                f"run {run_id} is {run.status}, not {expected_status}"
            )
        if gate == "research":
            if rubric_path is None:
                raise VideoPipelineGateApprovalError(
                    gate,
                    run_id,
                    ["Research approval requires --rubric"],
                )
            try:
                violations = self._research_approval_violations(
                    self.repository.job_dir(run.id),
                    Path(rubric_path),
                    str(run.config_snapshot.get("research_hash") or ""),
                )
            except Exception as exc:
                raise VideoPipelineGateApprovalError(
                    gate,
                    run_id,
                    [str(exc)],
                ) from exc
            if violations:
                raise VideoPipelineGateApprovalError(gate, run_id, violations)
        elif gate == "assets":
            if rubric_path is None:
                raise VideoPipelineGateApprovalError(
                    gate,
                    run_id,
                    ["Asset Selection approval requires --rubric"],
                )
            try:
                from content.video_engine.src.services.stock_assets import (
                    AssetSelectionGateGuard,
                )

                job_dir = self.repository.job_dir(run.id)
                violations = AssetSelectionGateGuard().validate(
                    job_dir,
                    Path(rubric_path),
                    str(run.config_snapshot.get("coverage_hash") or ""),
                )
            except Exception as exc:
                raise VideoPipelineGateApprovalError(
                    gate,
                    run_id,
                    [str(exc)],
                ) from exc
            if violations:
                raise VideoPipelineGateApprovalError(gate, run_id, violations)
            import json

            review = json.loads(Path(rubric_path).read_text(encoding="utf-8"))
            approved_path = job_dir / "asset_selection" / "approved-review.json"
            approved_path.write_text(
                json.dumps(review, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            run.config_snapshot["asset_selection_hash"] = self._canonical_hash(review)
            run.config_snapshot["candidate_batch_hash"] = str(
                review.get("candidate_batch_hash") or ""
            )
        elif gate == "visual":
            if rubric_path is None:
                raise VideoPipelineGateApprovalError(
                    gate,
                    run_id,
                    ["Visual Direction approval requires --rubric"],
                )
            try:
                violations = self._visual_direction_violations(
                    self.repository.job_dir(run.id),
                    Path(rubric_path),
                    str(run.config_snapshot.get("art_bible_hash") or ""),
                )
            except Exception as exc:
                raise VideoPipelineGateApprovalError(
                    gate,
                    run_id,
                    [str(exc)],
                ) from exc
            if violations:
                raise VideoPipelineGateApprovalError(gate, run_id, violations)
            style_board_hash = self._documentary_style_board_hash(
                self.repository.job_dir(run.id)
            )
            if style_board_hash is not None:
                run.config_snapshot["style_board_hash"] = style_board_hash
        elif gate == "a":
            storyboard_path = self.repository.job_dir(run.id) / "storyboard.json"
            try:
                ok, violations = self._storyboard_validator(storyboard_path)
                expected_storyboard_hash = str(
                    run.config_snapshot.get("storyboard_hash") or ""
                )
                if _version_at_least(
                    run.config_snapshot.get("pipeline_contract_version", 1),
                    HISTORY_VIDEO_PIPELINE_CONTRACT_VERSION,
                ):
                    if not expected_storyboard_hash:
                        violations.append(
                            "Gate A requires a snapshotted storyboard_hash"
                        )
                    else:
                        import json

                        from content.video_engine.src.services.history_contracts import (
                            canonical_sha256,
                        )

                        current_storyboard = json.loads(
                            storyboard_path.read_text(encoding="utf-8")
                        )
                        current_storyboard_hash = canonical_sha256(
                            current_storyboard
                        )
                        if current_storyboard_hash != expected_storyboard_hash:
                            violations.append(
                                "storyboard hash does not match the artifact "
                                "snapshotted before Gate A"
                            )
                    violations.extend(
                        self._documentary_style_board_integrity_violations(
                            self.repository.job_dir(run.id),
                            str(
                                run.config_snapshot.get(
                                    "style_board_hash"
                                )
                                or ""
                            ),
                        )
                    )
                if self._requires_animatic(run):
                    violations = [
                        *violations,
                        *self._animatic_violations(self.repository.job_dir(run.id)),
                        *self._visual_plan_violations(
                            storyboard_path,
                            self.repository.job_dir(run.id),
                        ),
                    ]
                    ok = ok and not violations
            except Exception as exc:  # pragma: no cover - guard exception passthrough
                raise VideoPipelineGateApprovalError(
                    gate,
                    run_id,
                    [str(exc)],
                ) from exc
            if not ok:
                raise VideoPipelineGateApprovalError("a", run_id, violations)
        gate_field = (
            "research_gate_status"
            if gate == "research"
            else "asset_gate_status"
            if gate == "assets"
            else "visual_gate_status"
            if gate == "visual"
            else f"gate_{gate}_status"
        )
        setattr(run, gate_field, GateStatus.APPROVED.value)
        run.status = "running"
        run.updated_at = self._now_fn()
        self.repository.update_run(run)
        return self._execute(run)

    def _execute(self, run: VideoRun) -> VideoRun:
        completed = {
            event.stage_name
            for event in self.repository.list_stage_events(run.id)
            if event.status == "completed"
        }
        ctx = StageContext(
            repository=self.repository,
            configs=self.configs,
            job_dir=self.repository.job_dir(run.id),
        )
        for stage_name in self._stage_order(run):
            if stage_name in completed:
                continue
            run.current_stage = stage_name
            run.updated_at = self._now_fn()
            self.repository.update_run(run)

            gate = GATE_STAGES.get(stage_name)
            if gate is not None:
                _gate_name, gate_field, awaiting_status = gate
                if getattr(run, gate_field) != GateStatus.APPROVED.value:
                    run.status = awaiting_status
                    run.updated_at = self._now_fn()
                    self.repository.append_stage_event(
                        VideoStageEvent(
                            video_run_id=run.id,
                            stage_name=stage_name,
                            status="awaiting_approval",
                            started_at=run.updated_at,
                            output_summary={"cost_usd": 0.0, "wall_time_s": 0.0},
                        )
                    )
                    self.repository.update_run(run)
                    return run
                now = self._now_fn()
                self.repository.append_stage_event(
                    VideoStageEvent(
                        video_run_id=run.id,
                        stage_name=stage_name,
                        status="completed",
                        started_at=now,
                        completed_at=now,
                        output_summary={"cost_usd": 0.0, "wall_time_s": 0.0},
                    )
                )
                continue

            started_at = self._now_fn()
            started = self._perf_counter_fn()
            self.repository.append_stage_event(
                VideoStageEvent(
                    video_run_id=run.id,
                    stage_name=stage_name,
                    status="running",
                    started_at=started_at,
                )
            )
            try:
                stage_fn = self.stage_fns.get(stage_name, self._stub_stage)
                output = stage_fn(run, ctx)
                if not isinstance(output, StageOutput):
                    raise TypeError(f"{stage_name} must return StageOutput")
                wall_time_s = max(0.0, self._perf_counter_fn() - started)
                summary = dict(output.summary)
                summary.setdefault("cost_usd", 0.0)
                summary["wall_time_s"] = round(wall_time_s, 6)
                if (
                    stage_name == "resolving_art_direction"
                    and summary.get("art_bible_hash")
                ):
                    run.config_snapshot["art_bible_hash"] = str(
                        summary["art_bible_hash"]
                    )
                if summary.get("research_hash"):
                    run.config_snapshot["research_hash"] = str(
                        summary["research_hash"]
                    )
                for field in (
                    "coverage_hash",
                    "candidate_batch_hash",
                    "asset_selection_hash",
                ):
                    if summary.get(field):
                        run.config_snapshot[field] = str(summary[field])
                if summary.get("asset_manifest_hash"):
                    run.config_snapshot["asset_manifest_hash"] = str(
                        summary["asset_manifest_hash"]
                    )
                if summary.get("storyboard_hash"):
                    run.config_snapshot["storyboard_hash"] = str(
                        summary["storyboard_hash"]
                    )
                completed_at = self._now_fn()
                self.repository.append_stage_event(
                    VideoStageEvent(
                        video_run_id=run.id,
                        stage_name=stage_name,
                        status="completed",
                        started_at=started_at,
                        completed_at=completed_at,
                        output_summary=summary,
                    )
                )
                run.summary.setdefault("stages", {})[stage_name] = summary
            except Exception as exc:
                completed_at = self._now_fn()
                self.repository.append_stage_event(
                    VideoStageEvent(
                        video_run_id=run.id,
                        stage_name=stage_name,
                        status="failed",
                        started_at=started_at,
                        completed_at=completed_at,
                        output_summary={
                            "cost_usd": 0.0,
                            "wall_time_s": round(
                                max(0.0, self._perf_counter_fn() - started),
                                6,
                            ),
                        },
                        error_text=str(exc),
                    )
                )
                run.status = "failed"
                run.error_text = str(exc)
                run.updated_at = completed_at
                self.repository.update_run(run)
                return run
            run.updated_at = self._now_fn()
            self.repository.update_run(run)

        run.status = "packaged"
        run.current_stage = "completed"
        run.completed_at = run.updated_at = self._now_fn()
        self.repository.update_run(run)
        return run

    def _require_run(self, run_id: str) -> VideoRun:
        run = self.repository.load_run(run_id)
        if run is None:
            raise KeyError(f"video run not found: {run_id}")
        return run

    @staticmethod
    def _stub_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
        del job, ctx
        return StageOutput({"stub": True})

    @staticmethod
    def _requires_animatic(run: VideoRun) -> bool:
        return _version_at_least(
            run.config_snapshot.get("pipeline_contract_version", 1), 2
        )

    @staticmethod
    def _stage_order(run: VideoRun) -> list[str]:
        snapshotted = run.config_snapshot.get("stage_order")
        if isinstance(snapshotted, list) and snapshotted:
            values = [str(value) for value in snapshotted]
            if len(values) == len(set(values)):
                return values
        version = run.config_snapshot.get("pipeline_contract_version", 1)
        if _version_at_least(version, LIVING_HISTORY_VIDEO_PIPELINE_CONTRACT_VERSION):
            return list(V4_1_STAGES)
        if _version_at_least(version, 4):
            return list(V4_STAGES)
        if _version_at_least(version, 3):
            return list(V3_STAGES)
        return list(V2_STAGES if _version_at_least(version, 2) else LEGACY_STAGES)

    @staticmethod
    def _canonical_hash(payload: dict[str, Any]) -> str:
        from content.video_engine.src.services.history_contracts import (
            canonical_sha256,
        )

        return canonical_sha256(payload)

    @staticmethod
    def _visual_direction_violations(
        job_dir: Path,
        rubric_path: Path,
        expected_art_bible_hash: str,
    ) -> list[str]:
        documentary_board = job_dir / "style_board" / "style_board.json"
        if documentary_board.is_file():
            try:
                import json

                payload = json.loads(documentary_board.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, ValueError):
                payload = {}
            if (
                payload.get("source_kind") == "documentary"
                or payload.get("documentary_version")
            ):
                from content.video_engine.src.guards.documentary_visual_direction import (
                    validate_documentary_visual_approval,
                )

                return validate_documentary_visual_approval(
                    documentary_board,
                    rubric_path,
                    expected_art_bible_hash=expected_art_bible_hash,
                )
        from content.video_engine.src.guards.visual_direction import (
            validate_visual_approval,
        )

        return validate_visual_approval(
            job_dir,
            rubric_path,
            expected_art_bible_hash=expected_art_bible_hash,
        )

    @staticmethod
    def _documentary_style_board_hash(job_dir: Path) -> str | None:
        board_path = job_dir / "style_board" / "style_board.json"
        if not board_path.is_file():
            return None
        import json

        from content.video_engine.src.services.history_contracts import (
            canonical_sha256,
        )

        payload = json.loads(board_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("documentary style board must contain an object")
        if (
            payload.get("source_kind") != "documentary"
            and not payload.get("documentary_version")
        ):
            return None
        current_hash = canonical_sha256(payload)
        if payload.get("artifact_hash") != current_hash:
            raise ValueError(
                "documentary style board artifact_hash does not match "
                "canonical content"
            )
        return current_hash

    @classmethod
    def _documentary_style_board_integrity_violations(
        cls,
        job_dir: Path,
        expected_hash: str,
    ) -> list[str]:
        try:
            current_hash = cls._documentary_style_board_hash(job_dir)
        except (OSError, UnicodeError, ValueError) as exc:
            return [f"documentary style board integrity failed: {exc}"]
        if current_hash is None:
            return ["Gate A requires the approved documentary style board"]
        if not expected_hash:
            return [
                "Gate A requires a style_board_hash snapshotted at "
                "Visual Direction approval"
            ]
        if current_hash != expected_hash:
            return [
                "style board hash does not match the artifact snapshotted "
                "at Visual Direction approval"
            ]
        return []

    @staticmethod
    def _research_approval_violations(
        job_dir: Path,
        rubric_path: Path,
        expected_research_hash: str,
    ) -> list[str]:
        from content.video_engine.src.guards.research_gate import (
            validate_research_approval,
        )

        return validate_research_approval(
            job_dir,
            rubric_path,
            expected_research_hash=expected_research_hash,
        )

    def _source_contract(self, source_ref: str) -> str | None:
        """Read only the source discriminator; ingestion performs full validation."""

        project_root = Path(self.configs.get("project_root", Path.cwd())).resolve()
        source_path = Path(source_ref)
        if not source_path.is_absolute():
            source_path = project_root / source_path
        try:
            source_path = source_path.resolve()
            source_path.relative_to(project_root)
        except (OSError, ValueError):
            return None
        if source_path.suffix.casefold() != ".json" or not source_path.is_file():
            return None
        try:
            import json

            payload = json.loads(source_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            return None
        if not isinstance(payload, dict):
            return None
        return str(payload.get("schema_version") or payload.get("contract_version") or "") or None

    @staticmethod
    def _animatic_violations(job_dir: Path) -> list[str]:
        packet_path = job_dir / "animatic" / "review-packet.json"
        if not packet_path.is_file():
            return ["animatic review packet is required before Gate A approval"]
        try:
            import json

            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            return ["animatic review packet is malformed"]
        if not isinstance(packet, dict):
            return ["animatic review packet must contain an object"]
        violations: list[str] = []
        path_fields = ["preview_path", "shot_strip_path"]
        if packet.get("renderer") == "editorial_ffmpeg":
            path_fields.extend(
                [
                    "editorial_beat_plan_path",
                    "motion_contact_sheet_path",
                ]
            )
        resolved_paths: dict[str, Path] = {}
        for field in path_fields:
            raw = packet.get(field)
            if not isinstance(raw, str) or not raw:
                violations.append(f"animatic review packet is missing {field}")
                continue
            candidate = (job_dir / raw).resolve()
            try:
                candidate.relative_to(job_dir.resolve())
            except ValueError:
                violations.append(f"animatic {field} escapes the job directory")
                continue
            if not candidate.is_file():
                violations.append(f"animatic {field} does not exist: {raw}")
                continue
            resolved_paths[field] = candidate
        beat_plan_path = resolved_paths.get("editorial_beat_plan_path")
        if beat_plan_path is not None:
            try:
                from content.video_engine.src.services.history_contracts import (
                    canonical_sha256,
                )

                beat_plan = json.loads(
                    beat_plan_path.read_text(encoding="utf-8")
                )
                storyboard = json.loads(
                    (job_dir / "storyboard.json").read_text(encoding="utf-8")
                )
            except (OSError, UnicodeError, ValueError):
                violations.append("editorial beat plan is malformed")
                return violations
            if not isinstance(beat_plan, dict):
                violations.append("editorial beat plan must contain an object")
                return violations
            if beat_plan.get("artifact_hash") != canonical_sha256(beat_plan):
                violations.append(
                    "editorial beat plan artifact_hash does not match content"
                )
            if beat_plan.get("source_storyboard_hash") != canonical_sha256(
                storyboard
            ):
                violations.append(
                    "editorial beat plan does not match the Gate A storyboard"
                )
            beats = beat_plan.get("beats")
            if not isinstance(beats, list) or not beats:
                violations.append("editorial beat plan contains no beats")
            else:
                if packet.get("editorial_beat_count") != len(beats):
                    violations.append(
                        "animatic editorial beat count does not match its plan"
                    )
                long_beats = [
                    str(beat.get("beat_id") or index + 1)
                    for index, beat in enumerate(beats)
                    if isinstance(beat, dict)
                    and float(beat.get("duration_s") or 0) > 12.0 + 1e-6
                ]
                if long_beats:
                    violations.append(
                        "editorial beats exceed the 12-second visual hold cap: "
                        + ", ".join(long_beats)
                    )
        return violations

    @staticmethod
    def _visual_plan_violations(
        storyboard_path: Path,
        job_dir: Path,
    ) -> list[str]:
        # Isolated orchestration tests may inject a validator without creating
        # a storyboard. Production uses the default guard, which already fails
        # a missing file. Do not make those tests fabricate an unrelated
        # visual contract.
        if not storyboard_path.is_file():
            return []
        import json

        storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
        source = storyboard.get("source") or {}
        if (
            storyboard.get("schema_version") in {"2.2.0", "2.3.0"}
            and isinstance(source, dict)
            and source.get("kind") == "history_episode"
        ):
            from content.video_engine.src.guards.documentary_visual_qc import (
                run_documentary_visual_qc,
            )

            treatment_path = job_dir / "visual_treatment.v2.json"
            if not treatment_path.is_file():
                return [
                    "documentary visual QC: visual_treatment.v2.json is "
                    "required before Gate A"
                ]
            report = run_documentary_visual_qc(
                treatment_path,
                job_dir,
                require_final_manifest=False,
            )
            return [
                f"documentary visual QC: {check['detail']}"
                for check in report["checks"]
                if check["status"] == "fail"
            ]

        from content.video_engine.src.guards.visual_qc import run_visual_qc

        report = run_visual_qc(
            storyboard,
            job_dir,
            require_final_manifest=False,
        )
        return [
            f"visual QC: {check['detail']}"
            for check in report["checks"]
            if check["status"] == "fail"
        ]


def build_default_stage_fns() -> dict[str, StageFn]:
    """Build the production stage registry without import-time provider work."""

    from content.video_engine.src.guards.qc_checks import run_qc_checks
    from content.video_engine.src.guards.storyboard_guard import guard
    from content.video_engine.src.services.audio_synth import run_stage as synth_audio
    from content.video_engine.src.services.animatic import run_stage as render_animatic
    from content.video_engine.src.services.art_direction import (
        ArtDirectionService,
        VisualTreatmentService,
    )
    from content.video_engine.src.services.asset_resolver import AssetResolverService
    from content.video_engine.src.services.captions import CaptionService
    from content.video_engine.src.services.compositor import CompositorService
    from content.video_engine.src.services.editorial import EditorialService
    from content.video_engine.src.services.ingest import IngestService
    from content.video_engine.src.services.history_pipeline import (
        DocumentaryScriptService,
        DocumentaryShotPlanService,
        DocumentaryStoryboardService,
        HistoryArtDirectionService,
        HistoryEvidenceService,
    )
    from content.video_engine.src.services.manim_render import run_stage as render_scenes
    from content.video_engine.src.services.packaging import PackagingService
    from content.video_engine.src.services.publish import ManualPublishService
    from content.video_engine.src.services.shot_plan import ShotPlanService
    from content.video_engine.src.services.sound_design import run_stage as design_sound
    from content.video_engine.src.services.script_transform import (
        ScriptTransformService,
    )
    from content.video_engine.src.services.storyboard_build import (
        StoryboardBuildService,
    )
    from content.video_engine.src.services.style_board import StyleBoardService
    from content.video_engine.src.services.documentary_style_board import (
        DocumentaryStyleBoardService,
    )
    from content.video_engine.src.services.documentary_treatment import (
        DocumentaryTreatmentService,
    )
    from content.video_engine.src.services.technique_manifest import (
        TechniqueManifestService,
    )
    from content.video_engine.src.services.stock_assets import (
        AssetPromotionStage,
        AssetSelectionReviewStage,
        EditorialCoverageStage,
        StockCandidateStage,
    )
    from content.video_engine.src.services.living_history_pipeline import (
        LivingDocumentaryStoryboardService,
        LivingDocumentaryTreatmentService,
    )

    ingest = IngestService()
    transform = ScriptTransformService()
    storyboard_builder = StoryboardBuildService()
    compositor = CompositorService()
    captions = CaptionService()
    editorial = EditorialService()
    packaging = PackagingService()
    publisher = ManualPublishService()
    technique_manifest = TechniqueManifestService()
    shot_planner = ShotPlanService()
    art_direction = ArtDirectionService()
    visual_treatments = VisualTreatmentService()
    style_board = StyleBoardService()
    history_evidence = HistoryEvidenceService()
    asset_resolver = AssetResolverService()
    documentary_transform = DocumentaryScriptService()
    history_art_direction = HistoryArtDirectionService()
    documentary_shot_planner = DocumentaryShotPlanService()
    documentary_treatments = DocumentaryTreatmentService()
    documentary_storyboard = DocumentaryStoryboardService()
    documentary_style_board = DocumentaryStyleBoardService()
    editorial_coverage = EditorialCoverageStage()
    stock_candidates = StockCandidateStage()
    asset_selection_review = AssetSelectionReviewStage()
    asset_promotion = AssetPromotionStage()
    living_treatments = LivingDocumentaryTreatmentService()
    living_storyboard = LivingDocumentaryStoryboardService()

    def is_history_v4(job: VideoRun) -> bool:
        return _version_at_least(
            job.config_snapshot.get("pipeline_contract_version", 1), 4
        )

    def is_history_v4_1(job: VideoRun) -> bool:
        return _version_at_least(
            job.config_snapshot.get("pipeline_contract_version", 1),
            LIVING_HISTORY_VIDEO_PIPELINE_CONTRACT_VERSION,
        )

    def transform_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
        return (
            documentary_transform.run_stage(job, ctx)
            if is_history_v4(job)
            else transform.run_stage(job, ctx)
        )

    def art_direction_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
        return (
            history_art_direction.run_stage(job, ctx)
            if is_history_v4(job)
            else art_direction.run_stage(job, ctx)
        )

    def shot_plan_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
        return (
            documentary_shot_planner.run_stage(job, ctx)
            if is_history_v4(job)
            else shot_planner.run_stage(job, ctx)
        )

    def treatment_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
        return (
            living_treatments.run_stage(job, ctx)
            if is_history_v4_1(job)
            else
            documentary_treatments.run_stage(job, ctx)
            if is_history_v4(job)
            else visual_treatments.run_stage(job, ctx)
        )

    def build_guarded_storyboard(job: VideoRun, ctx: StageContext) -> StageOutput:
        output = (
            living_storyboard.run_stage(job, ctx)
            if is_history_v4_1(job)
            else
            documentary_storyboard.run_stage(job, ctx)
            if is_history_v4(job)
            else storyboard_builder.run_stage(job, ctx)
        )
        ok, violations = guard(ctx.job_dir / "storyboard.json")
        if not ok:
            raise ValueError("storyboard guard failed: " + "; ".join(violations))
        return StageOutput({**output.summary, "guard": "pass"})

    def style_board_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
        return (
            documentary_style_board.run_stage(job, ctx)
            if is_history_v4(job)
            else style_board.run_stage(job, ctx)
        )

    def run_qc(job: VideoRun, ctx: StageContext) -> StageOutput:
        compositor_summary = (
            job.summary.get("stages", {}).get("compositing") or {}
        )
        report = run_qc_checks(
            ctx.job_dir / "storyboard.json",
            ctx.job_dir,
            compositor_summary,
        )
        if report["overall"] != "pass":
            failures = [
                check["detail"]
                for check in report["checks"]
                if check["status"] == "fail"
            ]
            raise ValueError("QC failed: " + "; ".join(failures))
        return StageOutput(
            {
                "report_path": "qc/report.json",
                "overall": "pass",
                "check_count": len(report["checks"]),
                "cost_usd": 0.0,
            }
        )

    def run_documentary_qc(job: VideoRun, ctx: StageContext) -> StageOutput:
        from content.video_engine.src.guards.documentary_visual_qc import (
            run_documentary_visual_qc,
        )

        treatment_path = ctx.job_dir / "visual_treatment.v2.json"
        report = run_documentary_visual_qc(
            treatment_path,
            ctx.job_dir,
            require_final_manifest=True,
        )
        report_path = ctx.job_dir / "qc" / "documentary-report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        import json

        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        if report["overall"] != "pass":
            failures = [
                check["detail"]
                for check in report["checks"]
                if check["status"] == "fail"
            ]
            raise ValueError("documentary QC failed: " + "; ".join(failures))
        return StageOutput(
            {
                "report_path": "qc/documentary-report.json",
                "overall": "pass",
                "check_count": len(report["checks"]),
                "cost_usd": 0.0,
            }
        )

    return {
        "ingesting_source": ingest.run_stage,
        "validating_research": history_evidence.validate_research_stage,
        "resolving_assets": asset_resolver.run_stage,
        "preparing_research_review": history_evidence.prepare_review_stage,
        "building_technique_manifest": technique_manifest.run_stage,
        "transforming_script": transform_stage,
        "resolving_art_direction": art_direction_stage,
        "planning_shots": shot_plan_stage,
        "compiling_editorial_coverage": editorial_coverage.run_stage,
        "discovering_stock_candidates": stock_candidates.run_stage,
        "preparing_asset_selection_review": asset_selection_review.run_stage,
        "promoting_selected_assets": asset_promotion.run_stage,
        "compiling_visual_treatments": treatment_stage,
        "building_storyboard": build_guarded_storyboard,
        "rendering_style_board": style_board_stage,
        "rendering_animatic": render_animatic,
        "synthesizing_audio": synth_audio,
        "generating_captions": captions.run_stage,
        "rendering_scenes": render_scenes,
        "editing_picture": editorial.run_stage,
        "designing_sound": design_sound,
        "compositing": compositor.run_stage,
        "packaging": packaging.run_stage,
        "running_qc": run_qc,
        "running_documentary_qc": run_documentary_qc,
        "publishing": publisher.run_stage,
    }
