"""Script-gate runner + recording refusal (PRP P34 T1).

doc 40 MEDIA-TDD: red on the known-real case, green on a conforming one.
Red is Steel and Paper as written - the opening gate carries 26 FAIL, so the
gates report says VERDICT: FAIL and the recorders refuse it. Green is the
conforming opening from the opening-gate test plus a doc-35 tell. The
recorders refuse a script whose report is missing / stale / FAIL and honour
`--force "<reason>"` (Human Gate 3: hard refuse).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
TESTS = ROOT / "content/video_engine/tests"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TESTS))

import run_script_gates as RG          # noqa: E402
import record_chained_take as RC       # noqa: E402
import record_master_take as RM        # noqa: E402
from test_gate_opening_structure import _conforming_opening   # noqa: E402

EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
SCRIPT = EP / "SCRIPT-G-VO.txt"
TIMELINE = EP / "build-f/timeline.json"
needs_ep1 = pytest.mark.skipif(not SCRIPT.exists(), reason="episode one script not on disk")

# Script G's P4 pivot line (SCRIPT-G-PRODUCTION.md "[P4 · PIVOT]"; ledger: 50.6%)
PIVOT = ("And that's the part everyone repeating this chart missed — including, "
         "just this once, the people who drew it.")
# doc 35 rule 2: the audit FAILs a script with no falsifiable tell; the
# opening-gate fixture stops at P2, so the tell is added past the opening.
TELL = ("The threshold is the first month memory gets cheaper while the buildout "
        "still stands; if that prints and I hold, I am wrong. ")
GATE_ARGS = ["--ring", "spike", "--counterparty", "Bravos"]


def _conforming_script(tmp_path: Path) -> Path:
    script = tmp_path / "CONFORM-VO.txt"
    script.write_text(_conforming_opening() + TELL, encoding="utf-8")
    return script


# ---- RED: episode one -------------------------------------------------------

@needs_ep1
def test_red_episode_one_report_fails(tmp_path):
    copy = tmp_path / SCRIPT.name
    shutil.copy(SCRIPT, copy)
    argv = [str(copy), "--pivot", PIVOT, *GATE_ARGS]
    if TIMELINE.exists():
        argv += ["--timeline", str(TIMELINE)]

    assert RG.main(argv) == 1

    report = (tmp_path / "SCRIPT-G-GATES.md").read_text(encoding="utf-8")
    assert "VERDICT: FAIL" in report
    assert "\nTOOLS      lint: exit " in report
    assert "opening gate: exit 1, " in report
    assert (tmp_path / "SCRIPT-G-SCREENS.md").exists()
    assert RG.check_report(copy)[0] == "fail"


# ---- the hash and the report states ----------------------------------------

def test_script_hash_keys_the_spoken_text_only():
    spoken = "The safest thing you own looks like this. An iron spike."
    tagged = "The safest  thing you own looks like this. `[post-key]` [promise] An iron spike. "
    assert RG.script_hash(tagged) == RG.script_hash(spoken)
    assert RG.script_hash(tagged) != RG.script_hash(spoken + " Really.")


def test_check_report_missing_then_ok_or_fail_then_stale(tmp_path):
    script = _conforming_script(tmp_path)
    assert RG.check_report(script)[0] == "missing"

    code = RG.main([str(script), *GATE_ARGS])
    state, path = RG.check_report(script)
    assert Path(path) == tmp_path / "CONFORM-GATES.md"
    assert state == ("ok" if code == 0 else "fail")

    script.write_text(script.read_text(encoding="utf-8").replace("iron spike", "iron nail", 1),
                      encoding="utf-8")
    assert RG.check_report(script)[0] == "stale"


# ---- GREEN: a conforming script ---------------------------------------------

def test_green_conforming_script_passes(tmp_path):
    script = _conforming_script(tmp_path)
    code = RG.main([str(script), *GATE_ARGS])
    report = (tmp_path / "CONFORM-GATES.md").read_text(encoding="utf-8")
    assert code == 0, report
    assert "VERDICT: PASS" in report
    assert "script_hash: " + RG.script_hash(script.read_text(encoding="utf-8")) in report
    for name in ("lint_script_pattern.py", "audit_script_doctrine.py",
                 "gate_opening_structure.py", "enumerate_strength_screens.py"):
        assert f"## {name}" in report
    assert RG.check_report(script)[0] == "ok"


# ---- the recorders refuse ----------------------------------------------------

def _isolate(monkeypatch, module, tmp_path: Path, argv: list[str]) -> Path:
    """No env, no key, no network, no writes into the episode dir."""
    script = tmp_path / "X-VO.txt"
    script.write_text("The safest thing you own looks like this. `[post-key]` An iron spike.",
                      encoding="utf-8")
    env = tmp_path / "local.env"
    env.write_text("", encoding="utf-8")
    monkeypatch.setattr(module, "VO_TEXT", script)
    monkeypatch.setattr(module, "ENV_FILE", env)
    monkeypatch.setattr(module, "OUT", tmp_path / "vo")
    monkeypatch.setattr(module, "AUDIO_DIR", tmp_path / "vo/audio")
    monkeypatch.setattr(module, "CACHE_DIR", tmp_path / "vo/cache")
    monkeypatch.setattr(module, "credits_remaining", lambda key: None)
    monkeypatch.setattr(sys, "argv", ["record.py", *argv])
    for k in ("ELEVENLABS_API_KEY", "ELEVENLABS_VOICE_ID"):
        monkeypatch.delenv(k, raising=False)
    return script


@pytest.mark.parametrize("module", [RM, RC], ids=["master", "chained"])
def test_recorder_refuses_when_report_missing(monkeypatch, capsys, tmp_path, module):
    _isolate(monkeypatch, module, tmp_path, [])
    assert module.main() == 1
    out = capsys.readouterr().out
    assert "[FAIL] gates report missing" in out
    assert "run_script_gates.py" in out
    assert "[FORCED]" not in out


@pytest.mark.parametrize("module", [RM, RC], ids=["master", "chained"])
def test_recorder_force_with_reason_continues(monkeypatch, capsys, tmp_path, module):
    _isolate(monkeypatch, module, tmp_path, ["--force", "test reason"])
    module.main()                       # still fails later on env/key - not asserted
    out = capsys.readouterr().out
    assert "[FORCED] gates report missing - reason: test reason" in out
    assert "[FAIL] gates report" not in out


@pytest.mark.parametrize("module", [RM, RC], ids=["master", "chained"])
def test_recorder_force_without_reason_is_a_fail(monkeypatch, capsys, tmp_path, module):
    _isolate(monkeypatch, module, tmp_path, ["--force", "--go"])
    assert module.main() == 1
    out = capsys.readouterr().out
    assert "--force needs a reason" in out
    assert "[FORCED]" not in out


def test_force_reason_takes_the_next_argv_item():
    assert RG.force_reason(["--go"]) == (False, "")
    assert RG.force_reason(["--force", "the take is a probe"]) == (True, "the take is a probe")
    assert RG.force_reason(["--force"]) == (True, "")
    assert RG.force_reason(["--force", "--go"]) == (True, "")


# ---- E24: --title / --thumb / --thumb-file reach the opening gate -------------------------

def test_title_and_thumb_pass_through_to_the_opening_gate(tmp_path):
    script = _conforming_script(tmp_path)
    code = RG.main([str(script), *GATE_ARGS, "--title", "The Safest Thing You Own Is an Iron Spike",
                    "--thumb", "STEEL or PAPER?", "--thumb-file", "packaging/thumb.png"])
    report = (tmp_path / "CONFORM-GATES.md").read_text(encoding="utf-8")
    assert code == 0, report
    assert "[PASS ] G45 title-word proxy" in report and "[JUDGE] J12 open packaging/thumb.png" in report
    assert "\nTOOLS      lint: exit " in report        # the s5 TOOLS block keeps its shape
