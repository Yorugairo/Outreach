from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run_sigmap(arguments: list[str]) -> int:
    executable = shutil.which("sigmap")
    if executable is None:
        print("error: SigMap is not installed or not on PATH", file=sys.stderr)
        return 1

    try:
        completed = subprocess.run(
            [executable, *arguments, "--no-track"],
            cwd=PROJECT_ROOT,
            check=False,
        )
    except OSError as exc:
        print(f"error: could not run SigMap: {exc}", file=sys.stderr)
        return 1
    return completed.returncode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Regenerate and query the local SigMap context index."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("build", help="regenerate the Copilot-only context index")

    ask = subcommands.add_parser("ask", help="ask SigMap for a grounded code answer")
    ask.add_argument("query")

    query = subcommands.add_parser("query", help="rank code paths relevant to a query")
    query.add_argument("query")
    query.add_argument("--json", action="store_true", help="request JSON output")
    query.add_argument("--top", type=int, help="limit ranked paths")

    verify = subcommands.add_parser("verify", help="verify a Markdown answer against the index")
    verify.add_argument("answer")
    verify.add_argument("--json", action="store_true", help="request JSON output")

    evidence = subcommands.add_parser("evidence", help="build a deterministic evidence pack")
    evidence.add_argument("query")
    evidence.add_argument("--markdown", action="store_true", help="render Markdown to stdout")

    return parser


def _action_arguments(args: argparse.Namespace) -> list[str]:
    if args.command == "ask":
        return ["ask", args.query]
    if args.command == "query":
        command = ["--query", args.query]
        if args.top is not None:
            command.extend(["--top", str(args.top)])
        if args.json:
            command.append("--json")
        return command
    if args.command == "verify":
        command = ["verify", args.answer]
        if args.json:
            command.append("--json")
        return command
    if args.command == "evidence":
        command = ["evidence", args.query]
        if args.markdown:
            command.append("--markdown")
        return command
    return []


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if _run_sigmap([]) != 0:
        return 1
    if args.command == "build":
        return 0
    return _run_sigmap(_action_arguments(args))


if __name__ == "__main__":
    raise SystemExit(main())
