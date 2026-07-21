from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import ROOT_DIR
from src.orchestrator import InsightRunOrchestrator
from src.repositories.file_repository import FileBackedInsightRepository

COMMANDS = {"run", "status", "inspect", "validate", "resume", "rerun", "diff"}
GLOBAL_OPTIONS_WITH_VALUES = {"--artifact-root"}


def _repo(artifact_root: str) -> FileBackedInsightRepository:
    return FileBackedInsightRepository(Path(artifact_root))


def _normalize_legacy_args(argv: list[str]) -> list[str]:
    """Preserve the documented shorthand: script.py URL --mode quick.

    The explicit control-plane form is `script.py run URL ...`, but AGENTS.md and
    older operator habits use the URL as the first positional. If the first
    positional token is not a known command, inject `run` before it.
    """
    skip_next = False
    for index, arg in enumerate(argv):
        if skip_next:
            skip_next = False
            continue
        if arg in {"-h", "--help"}:
            return argv
        if arg in GLOBAL_OPTIONS_WITH_VALUES:
            skip_next = True
            continue
        if any(arg.startswith(f"{option}=") for option in GLOBAL_OPTIONS_WITH_VALUES):
            continue
        if arg.startswith("-"):
            continue
        if arg in COMMANDS:
            return argv
        return [*argv[:index], "run", *argv[index:]]
    return argv


def main() -> int:
    parser = argparse.ArgumentParser(description="SEO Insight Run control plane")
    parser.add_argument("--artifact-root", default=str(ROOT_DIR / "artifacts" / "seo_insight_runs"))
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="start a new insight run")
    p_run.add_argument("url")
    p_run.add_argument("--mode", default="standard", choices=["quick", "standard", "full"])
    p_run.add_argument("--max-pages", type=int, default=5)

    p_status = sub.add_parser("status", help="show run status")
    p_status.add_argument("run_id")

    p_inspect = sub.add_parser("inspect", help="show run + report summary")
    p_inspect.add_argument("run_id")

    p_validate = sub.add_parser("validate", help="validate artifact-backed completion")
    p_validate.add_argument("run_id")

    p_resume = sub.add_parser("resume", help="resume a failed or incomplete run")
    p_resume.add_argument("run_id")
    p_resume.add_argument("--max-pages", type=int, default=5)

    p_rerun = sub.add_parser("rerun", help="rerun a stage and all downstream stages")
    p_rerun.add_argument("run_id")
    p_rerun.add_argument("stage")
    p_rerun.add_argument("--max-pages", type=int, default=5)

    p_diff = sub.add_parser("diff", help="compare two completed insight runs")
    p_diff.add_argument("base_run_id")
    p_diff.add_argument("comparison_run_id")

    args = parser.parse_args(_normalize_legacy_args(sys.argv[1:]))
    repo = _repo(args.artifact_root)
    orch = InsightRunOrchestrator(repo, artifact_root=args.artifact_root)

    if args.command == "run":
        run = orch.start(args.url, mode=args.mode, max_pages=args.max_pages)
        print(json.dumps({"run_id": run.id, "status": run.status, "validation": orch.validate(run.id)}, indent=2))
    elif args.command == "status":
        print(json.dumps(orch.status(args.run_id), indent=2))
    elif args.command == "inspect":
        print(json.dumps(orch.status(args.run_id), indent=2))
    elif args.command == "validate":
        validation = orch.validate(args.run_id)
        print(json.dumps(validation, indent=2))
        return 0 if validation.get("valid") else 1
    elif args.command == "resume":
        run = orch.resume(args.run_id, max_pages=args.max_pages)
        print(json.dumps({"run_id": run.id, "status": run.status, "validation": orch.validate(run.id)}, indent=2))
    elif args.command == "rerun":
        run = orch.rerun_stage(args.run_id, args.stage, max_pages=args.max_pages)
        print(json.dumps({"run_id": run.id, "status": run.status, "validation": orch.validate(run.id)}, indent=2))
    elif args.command == "diff":
        print(json.dumps(orch.diff_runs(args.base_run_id, args.comparison_run_id), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
