from __future__ import annotations

import json
from pathlib import Path

from content.video_engine.scripts import build_finance_stealth_wealth_proof as builder


def test_report_and_audio_inputs_are_hash_bound() -> None:
    hashes = builder.verify_inputs()
    assert hashes["deep_research_report"] == builder.REPORT_SHA256
    assert hashes["canonical_audio"] == builder.EXPECTED_AUDIO_SHA256
    assert len(builder.read_words()) >= 277


def test_claim_packet_contains_report_backed_metrics() -> None:
    ids = {claim["claim_id"] for claim in builder.CLAIMS}
    assert {"sp500-cape", "memory-forward-pe", "top-ten-weight", "top-ten-earnings", "passive-flow", "thirty-rivals", "memory-triopoly"} <= ids
    for claim in builder.CLAIMS:
        assert claim["source_locator"].startswith("Memory Deep Research.txt:")
        assert claim["citation"].startswith("[cite:")


def test_builder_stages_source_bound_proof_contract(tmp_path: Path) -> None:
    result = builder.build_artifacts(proof_root=tmp_path / "proof")
    proof_root = Path(result["proof_root"])
    props = json.loads((proof_root / "proof-props.v1.json").read_text(encoding="utf-8"))
    binding = json.loads((proof_root / "source-binding.v1.json").read_text(encoding="utf-8"))
    assert props["duration_s"] == 105.0
    assert props["render_profile"]["width"] == 1280
    assert props["render_profile"]["height"] == 720
    assert len(props["beats"]) == 5
    assert props["report_source"]["sha256"] == builder.REPORT_SHA256
    assert binding["status"] == "source_bound"
    assert (proof_root / "source/Memory Deep Research.txt").is_file()
    assert (proof_root / "source/canonical.words.json").is_file()
    assert (proof_root / "public/audio/canonical.mp3").is_file()
