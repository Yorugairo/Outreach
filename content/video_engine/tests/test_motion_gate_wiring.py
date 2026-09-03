"""Motion gate wired into the build and the render (P34 T4, ruling E21 / doc 29
s9.25): `write_report` writes GATES-MOTION.md beside the timeline (red on
Steel and Paper as shipped, green on a dense synthetic build) and
`render_episode.py` refuses a FULL render on FAIL, honours --force, and
never blocks a slice."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_motion_density as G  # noqa: E402
import render_episode as RE  # noqa: E402

BUILD = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f"
needs_ep1 = pytest.mark.skipif(not (BUILD / "steel-and-paper.timeline.json").exists(), reason="episode one build not on disk")


# ---- write_report -----------------------------------------------------------

@needs_ep1
def test_ep1_report_is_the_four_fail_baseline():
    path, n_fail = G.write_report(BUILD, "steel-and-paper.timeline.json")
    assert path == BUILD / "GATES-MOTION.md" and path.exists()
    assert n_fail in (4, 5)   # 4 before caption modes were declared; 5 once M08 enforces on the rebuilt ep1
    text = path.read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# MOTION GATE — build-f"
    assert "[FAIL ] M01" in text and "> 12s" in text
    # 4 FAIL before caption modes were declared; 5 once the rebuilt ep1 declares them and M08 enforces
    assert ("RESULT: 4 FAIL / 1 WARN / 2 PASS / 2 JUDGE / 1 INFO" in text
            or "RESULT: 5 FAIL / 1 WARN / 2 PASS / 1 JUDGE / 0 INFO" in text), text[-400:]
    assert text.rstrip().splitlines()[-1] in ("VERDICT: FAIL (4 FAIL)", "VERDICT: FAIL (5 FAIL)")


def _dense_build(runtime=180.0, scene_len=6.0, dock_every=20.0, stage=False):
    scenes = []
    t = 0.0
    i = 0
    while t < runtime:
        scenes.append({"scene_id": f"s{i:02d}", "world": {"asset_id": f"world-{i}"}, "span": [t, min(t + scene_len, runtime)]})
        t += scene_len; i += 1
    docks = [{"asset": f"ev-{k}", "at": a, "end": min(a + 8.0, runtime)} for k, a in enumerate([x * dock_every + 3.0 for x in range(int(runtime // dock_every))])]
    pages = []
    t = 0.0
    while t < runtime:
        pages.append({"s": t, "e": t + 1.5, "t": [{"w": "x"}] * 5}); t += 1.5
    rows = [{"t": s["span"][0], "cap_mode": "stage"} for s in scenes] if stage else []
    tl = {"runtime_s": runtime, "scenes": scenes, "caption_pages": pages, "rows": rows}
    mp = {"cues": [{"kind": "evidence", "in": d["at"] + 1.0, "out": d["at"] + 1.5} for d in docks]}
    return tl, docks, mp


def _write_build(build: Path, tl: dict, docks: list, mp: dict) -> None:
    # the three files `_load` reads, under the names it reads them by
    (build / "timeline.json").write_text(json.dumps(tl), encoding="utf-8")
    (build / "evidence-dock.json").write_text(json.dumps(docks), encoding="utf-8")
    (build / "motion-plan.json").write_text(json.dumps(mp), encoding="utf-8")


def test_dense_synthetic_build_reports_pass(tmp_path: Path):
    _write_build(tmp_path, *_dense_build())
    path, n_fail = G.write_report(tmp_path, "timeline.json")
    assert n_fail == 0
    text = path.read_text(encoding="utf-8")
    assert text.rstrip().splitlines()[-1] == "VERDICT: PASS (0 FAIL)"
    assert "RESULT: 0 FAIL" in text


def test_report_text_is_what_main_prints(tmp_path: Path, capsys):
    tl, docks, mp = _dense_build()
    _write_build(tmp_path, tl, docks, mp)
    gates, stats = G.run(tl, docks, mp)
    report, _ = G.write_report(tmp_path, "timeline.json")
    sys.argv = ["gate_motion_density.py", str(tmp_path), "--timeline", "timeline.json"]
    assert G.main() == 0
    printed = capsys.readouterr().out
    assert printed == G.report_text(gates, stats, tmp_path) + "\n"
    assert printed.strip() in report.read_text(encoding="utf-8")   # verbatim inside the fenced block


# ---- render refusal ---------------------------------------------------------

@pytest.fixture()
def render_sandbox(tmp_path: Path, monkeypatch):
    """render_episode pointed at tmp_path; anything that would actually
    render or shell out raises unless a test swaps it for a recorder."""
    monkeypatch.setattr(RE, "BUILD", tmp_path)
    monkeypatch.setattr(RE, "OUT", tmp_path / "render")
    (tmp_path / "timeline.json").write_text(json.dumps({"runtime_s": 2.0}), encoding="utf-8")

    def boom(*a, **k):
        raise AssertionError(f"render side effect reached: {a[:1]}")

    monkeypatch.setattr(RE.subprocess, "run", boom)
    monkeypatch.setattr(RE.subprocess, "Popen", boom)
    monkeypatch.setattr(RE, "capture", boom)
    monkeypatch.setattr(RE, "parallel_render", boom)
    monkeypatch.setattr(RE, "mix_audio", boom)
    return tmp_path


def _fail_report(build: Path) -> Path:
    p = build / "GATES-MOTION.md"
    p.write_text("# MOTION GATE — x\n\n```text\nRESULT: 1 FAIL\n```\n\nVERDICT: FAIL (1 FAIL)\n", encoding="utf-8")
    return p


def _arm_capture(monkeypatch) -> list:
    """Swap the capture chain for recorders so a permitted render is provable."""
    calls: list = []
    monkeypatch.setattr(RE, "capture", lambda t0, t1, out: calls.append(("capture", t0, t1)))
    monkeypatch.setattr(RE, "mix_audio", lambda dur: calls.append(("mix", dur)) or Path("mix.m4a"))
    monkeypatch.setattr(RE.subprocess, "run", lambda *a, **k: calls.append(("ffmpeg", a[0][0])))
    return calls


def test_full_render_refuses_on_fail(render_sandbox: Path, monkeypatch, capsys):
    report = _fail_report(render_sandbox)
    monkeypatch.setattr(sys, "argv", ["render_episode.py"])
    assert RE.main() == 2
    out = capsys.readouterr().out
    assert str(report) in out
    assert "refusing full render (E21); re-run with --force to override" in out


def test_full_render_refuses_without_report(render_sandbox: Path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["render_episode.py"])
    assert RE.main() == 2
    assert "MOTION GATE: no report - run build_scene_timeline_f.py first" in capsys.readouterr().out


def test_slice_render_skips_the_gate(render_sandbox: Path, monkeypatch, capsys):
    _fail_report(render_sandbox)
    calls = _arm_capture(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["render_episode.py", "--t0", "0", "--t1", "1", "--workers", "1"])
    assert RE.main() == 0
    assert ("capture", 0.0, 1.0) in calls
    assert "MOTION GATE" not in capsys.readouterr().out


def test_force_overrides_fail_and_renders(render_sandbox: Path, monkeypatch, capsys):
    _fail_report(render_sandbox)
    calls = _arm_capture(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["render_episode.py", "--force", "--workers", "1"])
    assert RE.main() == 0
    assert "[FORCED] motion gate FAIL overridden" in capsys.readouterr().out
    assert ("capture", 0.0, 2.0) in calls


def test_pass_report_lets_full_render_through(render_sandbox: Path, monkeypatch, capsys):
    (render_sandbox / "GATES-MOTION.md").write_text("# MOTION GATE — x\n\nVERDICT: PASS (0 FAIL)\n", encoding="utf-8")
    calls = _arm_capture(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["render_episode.py", "--workers", "1"])
    assert RE.main() == 0
    assert ("capture", 0.0, 2.0) in calls
    assert "FORCED" not in capsys.readouterr().out
