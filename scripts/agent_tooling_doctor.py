from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def run(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    executable = shutil.which(command[0]) or command[0]
    return subprocess.run(
        [executable, *command[1:]],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )


def main() -> int:
    checks: list[dict[str, object]] = []

    def record(name: str, ok: bool, detail: object) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    for name, command in {
        "sigmap": ["sigmap", "--version"],
        "sqz": ["sqz", "--version"],
        "ast-grep": ["ast-grep", "--version"],
        "ast-grep-outline": ["ast-grep", "outline", "--help"],
    }.items():
        executable = shutil.which(command[0])
        if executable is None:
            record(f"tool:{name}", False, "not on PATH")
            continue
        result = run([executable, *command[1:]], timeout=30)
        detail = (result.stdout or result.stderr).strip().splitlines()
        record(f"tool:{name}", result.returncode == 0, detail[0] if detail else result.returncode)

    build = run([sys.executable, "scripts/sigmap_context.py", "build"], timeout=180)
    record("sigmap:regenerate", build.returncode == 0, "index regenerated" if build.returncode == 0 else build.stderr)

    report_result = run(["sigmap", "--report", "--json"], timeout=60)
    try:
        report = json.loads(report_result.stdout)
    except json.JSONDecodeError:
        report = {}
    coverage = report.get("coverage", {})
    record("sigmap:coverage", coverage.get("score", 0) >= 95, f"{coverage.get('score', 0)}%")
    record("sigmap:grade", coverage.get("grade") == "A", coverage.get("grade"))
    record("sigmap:confidence", coverage.get("confidence") == "HIGH", coverage.get("confidence"))
    record("sigmap:budget-drops", report.get("droppedCount") == 0, report.get("droppedCount"))

    for ignored in [
        ".context/doctor-probe.md",
        ".sigmap-cache.json",
        ".github/copilot-instructions.md",
    ]:
        result = run(["git", "check-ignore", "--no-index", "--quiet", ignored], timeout=30)
        record(f"ignored:{ignored}", result.returncode == 0, "ignored" if result.returncode == 0 else "not ignored")

    expected_agents = {
        "speedster": ("gpt-5.3-codex-spark", "low", "workspace-write"),
        "junior_developer": (
            "gpt-5.3-codex-spark",
            "xhigh",
            "workspace-write",
        ),
        "implementation_luna": ("gpt-5.6-luna", "max", "workspace-write"),
        "architect_sol": ("gpt-5.6-sol", "high", "workspace-write"),
        "release_steward": (
            "gpt-5.3-codex-spark",
            "high",
            "workspace-write",
        ),
        "explorer": ("gpt-5.3-codex-spark", "xhigh", "read-only"),
        "docs_researcher": ("gpt-5.3-codex-spark", "xhigh", "read-only"),
        "reviewer": ("gpt-5.3-codex-spark", "xhigh", "read-only"),
    }
    for agent, expected in expected_agents.items():
        path = REPO_ROOT / ".codex" / "agents" / f"{agent}.toml"
        if not path.exists():
            record(f"agent:{agent}", False, "missing")
            continue
        try:
            profile = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            record(f"agent:{agent}", False, f"invalid TOML: {exc}")
            continue
        actual = (
            profile.get("model"),
            profile.get("model_reasoning_effort"),
            profile.get("sandbox_mode"),
        )
        record(
            f"agent:{agent}",
            actual == expected,
            {
                "model": actual[0],
                "reasoning_effort": actual[1],
                "sandbox_mode": actual[2],
                "expected": expected,
            },
        )

    allowlist = run(
        [sys.executable, "scripts/configure_codex_skill_allowlist.py", "--check"],
        timeout=60,
    )
    record(
        "skill-allowlist:current",
        allowlist.returncode == 0,
        "current" if allowlist.returncode == 0 else "run with --write",
    )

    failures = [check for check in checks if not check["ok"]]
    print(json.dumps({"ok": not failures, "checks": checks, "failures": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
