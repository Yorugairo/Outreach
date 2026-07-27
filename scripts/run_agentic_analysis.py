from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config import load_config
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.agentic_job_service import AgenticJobService


def _repository(artifact_root: str) -> FileBackedInsightRepository:
    return FileBackedInsightRepository(Path(artifact_root))


def _select_pack(repo: FileBackedInsightRepository, run_id: str | None, pack_id: str | None, attempt_id: str | None):
    if pack_id:
        pack = repo.get_site_evidence_pack(pack_id)
        if pack is None:
            raise RuntimeError(f"evidence pack not found: {pack_id}")
        if run_id and pack.run_id != run_id:
            raise RuntimeError("requested pack is out of scoped run")
        if attempt_id and pack.attempt_id != attempt_id:
            raise RuntimeError("requested pack is out of scoped attempt")
        return pack

    if not run_id:
        raise RuntimeError("either --pack-id or --run-id is required")

    packs = repo.list_site_evidence_packs(run_id=run_id)
    if attempt_id:
        for pack in packs:
            if pack.attempt_id == attempt_id:
                return pack
        raise RuntimeError(f"no pack found for run={run_id} and attempt={attempt_id}")

    if not packs:
        raise RuntimeError(f"no evidence pack found for run={run_id}")
    return packs[0]


def _preflight_payload(job_service: AgenticJobService, pack, analysis_mode: str) -> dict:
    preflight = job_service.preflight(pack, analysis_mode=analysis_mode)
    preflight["analysis_mode"] = analysis_mode
    return preflight


def _resolve_pack_argument(
    repo: FileBackedInsightRepository,
    run_id: str | None,
    pack_id: str | None,
    attempt_id: str | None,
) -> dict:
    pack = _select_pack(repo, run_id=run_id, pack_id=pack_id, attempt_id=attempt_id)
    return pack.to_dict()


def _resolve_pack_for_service(repo: FileBackedInsightRepository, run_id, pack_id, attempt_id):
    pack = _select_pack(repo, run_id=run_id, pack_id=pack_id, attempt_id=attempt_id)
    return pack


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Agentic analysis runner preflight and controlled execution scaffold. "
            "Default behavior is preflight-only; provider execution is gated."
        )
    )
    parser.add_argument("--artifact-root", default=str(ROOT_DIR / "artifacts" / "seo_insight_runs"))
    parser.add_argument("--dotenv", default=None)
    parser.add_argument("--run-id", help="Scoped insight run id")
    parser.add_argument("--pack-id", help="Scoped evidence pack id")
    parser.add_argument("--attempt-id", help="Scoped evidence attempt id")
    parser.add_argument("--analysis-mode", default="standard")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Create/run job if operator gate is enabled (no provider calls in this shim)",
    )
    args = parser.parse_args()

    repo = _repository(args.artifact_root)
    service = AgenticJobService(repo, settings=load_config(args.dotenv).agentic)

    pack = _resolve_pack_for_service(
        repo,
        run_id=args.run_id,
        pack_id=args.pack_id,
        attempt_id=args.attempt_id,
    )
    result = {"evidence_pack": _resolve_pack_argument(repo, args.run_id, args.pack_id, args.attempt_id)}
    result["preflight"] = _preflight_payload(service, pack, args.analysis_mode)
    result["command"] = "preflight"

    if not args.execute:
        result["execution"] = "suppressed_by_default"
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if not result["preflight"]["available"]:
        print(json.dumps({"error": "agentic analysis gate is not enabled", **result["preflight"]}, indent=2))
        return 3

    job = service.create_job(pack, analysis_mode=args.analysis_mode)
    result["command"] = "execute"
    result["execution"] = "queued"
    result["job"] = job.to_dict()
    result["note"] = "provider invocation remains controlled by service runtime and is not performed in this script"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
