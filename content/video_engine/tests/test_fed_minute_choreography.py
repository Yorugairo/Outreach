"""The rejected pilot's shortcuts may not return in the minute treatment."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
EP = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))


def treatment():
    spec = importlib.util.spec_from_file_location("minute_treatment_test", EP / "SHOT-TABLE-MINUTE.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    words = json.loads((EP / "vo-pilot-20260919-r4/scratch-kokoro.words.json").read_text())["words"]
    words = [word for word in words if word["start_s"] < 65]
    return mod, mod.build_rows(words, 65.425, "minute")


def test_minute_keeps_one_rrp_world_and_no_generic_icons():
    _, rows = treatment()
    assert sum("ledger:fed-on-rrp-history:" in row[2] for row in rows) == 1
    chips = [s for row in rows for s in row[6] if s["kind"] == "chip"]
    assert chips
    assert all(s["form"] == "stamp" and s["icon"].startswith("prop-") for s in chips)
    assert not any(s["kind"] == "agenda" for row in rows for s in row[6])


def test_minute_draws_unseen_data_and_targets_exact_points():
    _, rows = treatment()
    rrp = next(row for row in rows if "ledger:fed-on-rrp-history:" in row[2])
    caps = [s for s in rrp[6] if s["kind"] == "build_to"]
    assert [s["target"]["index"] for s in caps] == [248, 1175]
    assert all(s["target"]["series"] == 0 for s in caps)
    assert caps[1]["at"] >= rrp[0]
    assert caps[1]["at"] + caps[1]["dur"] < 11.3
    marks = [s for s in rrp[6] if s["kind"] in ("spotlight", "callout")]
    assert all(s["target"]["kind"] == "datum" for s in marks)


def test_minute_is_contiguous_and_keeps_narrative_shots():
    _, rows = treatment()
    assert rows[0][0] == 0 and rows[-1][1] == 65.425
    assert all(a[1] == b[0] for a, b in zip(rows, rows[1:]))
    assert all(r[1] > r[0] for r in rows)
    assert any("w2-owner-workshop" in r[2] and r[0] < 24 < r[1] for r in rows)
    assert any(len(r) == 8 for r in rows), "narrative framing must be authored"
    assert sum(r[1]-r[0] for r in rows if not r[2].startswith("ledger:")) > 30


def test_minute_machine_punch_and_ledger_prop_are_not_small_icon_substitutes():
    _, rows = treatment()
    machine = next(r for r in rows if r[0] < 32 < r[1])
    assert max(k["zoom"] for k in machine[7]["keys"]) >= 2
    assert machine[7]["keys"][-1]["zoom"] == 1, "return to the owner for wages/materials/hire"
    closing = rows[-1]
    assert "build=lines:4.2" in closing[2]
    prop = next(s for s in closing[6] if s.get("icon") == "prop-liquidity-drain-pump-v1")
    assert prop["size"] >= 500
    assert prop["at"] > 60
