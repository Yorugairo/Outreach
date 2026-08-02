from __future__ import annotations

import json

from content.video_engine.src.models import GateStatus, StageContext, StageOutput, VideoRun


class ManualPublishService:
    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        metadata_path = ctx.job_dir / "package" / "metadata.json"
        embed_path = ctx.job_dir / "package" / "embed_payload.json"
        if not metadata_path.exists() or not embed_path.exists():
            raise FileNotFoundError("package metadata and embed payload are required")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not metadata.get("upload_checklist"):
            raise ValueError("manual publish package is missing its upload checklist")
        job.status = "packaged"
        ctx.repository.update_run(job)
        return StageOutput(
            {
                "mode": "manual",
                "status": "packaged",
                "upload_checklist": list(metadata["upload_checklist"]),
                "cost_usd": 0.0,
            }
        )

    def approve_publish(self, job: VideoRun, ctx: StageContext) -> VideoRun:
        if job.gate_b_status != GateStatus.APPROVED.value:
            raise ValueError("Gate B approval is required before marking a run published")
        qc_path = ctx.job_dir / "qc" / "report.json"
        if not qc_path.exists():
            raise FileNotFoundError("qc/report.json is required before publish approval")
        qc_report = json.loads(qc_path.read_text(encoding="utf-8"))
        if qc_report.get("overall") != "pass":
            raise ValueError("QC must pass before publish approval")
        job.status = "published"
        ctx.repository.update_run(job)
        return job
