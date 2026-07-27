"""Run the durable agentic worker outside the API process.

Provider execution is intentionally available only from this worker boundary.
The default is a single bounded pass; use ``--poll`` for a long-lived worker.
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config import APP_RUNTIME_DOTENV, load_config
from src.repositories.file_repository import FileBackedInsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository
from src.services.agentic_worker_service import AgenticWorkerService
from src.services.hermes_runtime import HermesOpenRouterRuntime
from src.services.vertical_agentic_work_executor import VerticalAgenticWorkExecutor


def _repository(args: argparse.Namespace):
    if args.database_path:
        return SQLiteInsightRepository(args.database_path, args.artifact_root)
    return FileBackedInsightRepository(args.artifact_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run queued P10/P12 agentic work outside the API request path.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="process one bounded pass (default)")
    mode.add_argument("--poll", action="store_true", help="poll until interrupted")
    parser.add_argument("--artifact-root", default=str(ROOT_DIR / "artifacts" / "seo_insight_runs"))
    parser.add_argument("--database-path", default=None, help="use SQLite instead of the file repository")
    parser.add_argument(
        "--dotenv",
        default=str(APP_RUNTIME_DOTENV),
        help="operator-owned runtime configuration (defaults to docs/local.env)",
    )
    parser.add_argument("--worker-id", default="agentic-worker")
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--max-jobs", type=int, default=10)
    parser.add_argument("--max-work-items", type=int, default=10)
    parser.add_argument("--max-iterations", type=int, default=None, help="bounded poll iterations for health checks")
    args = parser.parse_args(argv)

    if args.max_jobs < 0 or args.max_work_items < 0:
        parser.error("queue limits cannot be negative")
    if args.poll_interval < 0:
        parser.error("poll interval cannot be negative")
    config = load_config(args.dotenv)
    repo = _repository(args)
    # The worker may construct the runtime, but the Hermes adapter is only
    # called when the persisted operator/promotion gates are available.
    runtime = None
    if config.agentic.available and config.agentic.runtime == "hermes-openrouter":
        runtime = HermesOpenRouterRuntime(
            executable=config.agentic.hermes_executable,
            expected_version=config.agentic.hermes_version,
            working_root=ROOT_DIR,
        )
    p12_executor = (
        VerticalAgenticWorkExecutor(
            repo,
            runtime=runtime,
            artifact_root=args.artifact_root,
            profile=config.agentic.profile,
            action_policy_root=ROOT_DIR / "config" / "agentic" / "action-host-policies",
        )
        if runtime is not None
        else None
    )
    service = AgenticWorkerService(
        repo,
        artifact_root=args.artifact_root,
        settings=config.agentic,
        runtime=runtime,
        work_item_executor=p12_executor,
        worker_id=args.worker_id,
    )

    def _shutdown(*_: object) -> None:
        service.request_shutdown()

    signal.signal(signal.SIGINT, _shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _shutdown)

    if args.poll:
        payload: object = service.poll(
            interval_seconds=args.poll_interval,
            max_jobs=args.max_jobs,
            max_work_items=args.max_work_items,
            max_iterations=args.max_iterations,
        )
    else:
        payload = service.run_once(max_jobs=args.max_jobs, max_work_items=args.max_work_items)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
