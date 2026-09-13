"""The pipe check catches a gated step whose exit code tail/head swallows, and leaves honest pipes alone."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import check_gated_pipes as C  # noqa: E402


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_pytest_into_tail_before_a_push_fails(tmp_path):
    _write(tmp_path, "ship.sh", "#!/bin/bash\npytest -q | tail -3 && git push\n")
    assert C.check(tmp_path) == ["ship.sh:2: pytest -q | tail -3 && git push"]
    assert C.main(["--root", str(tmp_path)]) == 1


def test_a_gate_into_tail_under_pipefail_passes(tmp_path, capsys):
    _write(tmp_path, "join.sh", "#!/bin/bash\nset -euo pipefail\npython gate_drift.py | tail -5\nnext_step\n")
    assert C.check(tmp_path) == []
    assert C.main(["--root", str(tmp_path)]) == 0
    assert capsys.readouterr().out.strip().endswith("check_gated_pipes: PASS")


def test_a_markdown_bash_fence_chaining_after_the_pipe_fails(tmp_path):
    _write(tmp_path, "docs/runbook.md", "# Run\n\n```bash\npython -m pytest -q | tail -3 && git commit -m x\n```\n")
    assert C.check(tmp_path) == ["docs/runbook.md:4: python -m pytest -q | tail -3 && git commit -m x"]


def test_a_one_off_example_pipe_with_nothing_after_it_passes(tmp_path):
    _write(tmp_path, "docs/example.md", "```bash\npytest -q | tail -3\n```\n")
    assert C.check(tmp_path) == []


def test_an_ungated_head_pipe_passes(tmp_path):
    _write(tmp_path, "list.sh", "ls | head -5 && echo done\n")
    assert C.check(tmp_path) == []


def test_a_python_subprocess_string_piping_pytest_into_tail_fails(tmp_path):
    _write(tmp_path, "tools/run.py", 'import subprocess\nsubprocess.run("pytest -q | tail -3", shell=True)\n')
    assert C.check(tmp_path) == ["tools/run.py:2: pytest -q | tail -3"]


def test_powershell_select_last_before_and_fails_and_pipestatus_exempts(tmp_path):
    _write(tmp_path, "docs/ps.md", "```powershell\nnpm test | Select-Object -Last 5 && git push\n```\n")
    _write(tmp_path, "ok.sh", 'pytest | tail -3\n[ "${PIPESTATUS[0]}" -eq 0 ] || exit 1\n')
    assert C.check(tmp_path) == ["docs/ps.md:2: npm test | Select-Object -Last 5 && git push"]
