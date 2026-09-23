"""Focused current-take checks for the bounded Fed pilot schematics."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
EP = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
MODULE = importlib.util.spec_from_file_location("fed_pilot_schematics_current", EP / "pilot_schematics.py")
S = importlib.util.module_from_spec(MODULE)
assert MODULE.loader is not None
MODULE.loader.exec_module(S)


@pytest.fixture(scope="module")
def current_words():
    record = json.loads((EP / "vo-pilot-20260919-r4/scratch-kokoro.words.json").read_text(encoding="utf-8"))
    words = record.get("words", record)
    assert words and not S.W.is_estimated(words)
    return words


def test_kokoro_apostrophe_artifact_keeps_original_word_index(current_words):
    at = S._at(current_words, "Banks’ balances at the Fed rose by just seventy-two billion dollars.")
    index = next(i for i, word in enumerate(current_words) if round(word["start_s"], 3) == at)
    assert current_words[index]["w"] == "Banks"
    assert current_words[index + 1]["w"] in {"’", "�"}


def test_paired_100bn_is_three_input_formula_through_complete_conclusion(current_words):
    item = S.paired_100bn(current_words)
    flow = item["species"][0]
    next_start = S._at(current_words, "The Fed’s own figures show how large those offsetting movements became.")
    assert item["span"][0] == pytest.approx(S._at(current_words, "The Fed’s assets fall by a hundred billion dollars."))
    assert item["span"][1] == pytest.approx(next_start)
    assert len(flow["nodes"]) == 3
    assert [node["id"] for node in flow["nodes"]] == ["assets", "tga", "overnight"]
    assert flow["operators"] == ["-", "-"]
    assert flow["tag"] == "ILLUSTRATION · BANK ACCOUNTS: Δ $0 · OTHER BALANCES FIXED"
    assert flow["result"] == {"account": "bank Fed accounts", "delta_usd_billions": 0,
                               "label": "BANK ACCOUNTS: Δ $0"}
    assert flow["source_custody"]["binding"]["claim_id"] == "C7"
    assert item["binding"]["claim_id"] == "C7"
    assert item["amounts_are_illustrative"] is True


def test_first_on_rrp_flag_targets_retained_current_endpoint(current_words):
    item = S.opening_rrp_flags(current_words)
    flag = item["species"][0]
    points = json.loads((EP / "evidence/objects/fed-on-rrp-history.series.json").read_text(encoding="utf-8"))["series"][0]["pts"]
    assert item["span"] == [pytest.approx(9.15), pytest.approx(11.85)]
    assert flag["at"] == pytest.approx(9.675)
    assert flag["target"]["index"] == len(points) - 1
    assert item["endpoint_index"] == len(points) - 1


def test_superseded_history_recast_is_explicitly_disabled(current_words):
    with pytest.raises(ValueError, match="disabled.*fed-runoff-offsets"):
        S.historical_comparison(current_words)
