"""Shared fixtures for the paste-lane (P14) services."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pytest

PASTE_SCRIPT = (
    "Most traders lose money before they place a single bad trade. "
    "The exhaustion arrives first and the mistakes follow it. "
    "You reach for the phone before you reach for the day. "
    "That habit is not discipline and calling it discipline keeps it alive. "
    "Name the drain and the trade gets easier."
)

_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082"
)


@pytest.fixture()
def paste_script(tmp_path: Path) -> Path:
    path = tmp_path / "script.txt"
    path.write_text(PASTE_SCRIPT, encoding="utf-8")
    return path


@pytest.fixture()
def paste_attestation() -> dict[str, Any]:
    return {
        "asserted_by": "operator",
        "asserted_at": "2026-08-22T12:00:00+00:00",
        "source_kind": "own_research",
        "source_ref": "internal-notes/trading-energy-drains.md",
        "claim_basis": "Author's own trading journal and published broker fee schedules.",
        "references": [{"kind": "slide_deck", "ref": "decks/energy-drains.pdf"}],
    }


@pytest.fixture()
def paste_brief(paste_script: Path, paste_attestation: dict[str, Any], tmp_path: Path):
    from content.video_engine.src.services.script_ingest import ingest_script

    summary = ingest_script(
        script_path=paste_script,
        attestation=paste_attestation,
        output_dir=tmp_path / "job",
        brief_id="energy-drains",
        title="The Hidden Energy Drains",
        lane="stick_explainer",
    )
    import json

    return json.loads(Path(summary["brief_path"]).read_text(encoding="utf-8"))


def build_proposal(brief: dict[str, Any], *, copy_deferred: bool = True) -> dict[str, Any]:
    """Segment the brief's script into beats without rewriting a word."""

    sentences = [
        part.strip() + "." for part in brief["script"]["text"].split(".") if part.strip()
    ]
    acts = ["hook", "develop", "conflict", "comeback", "payoff", "cta"]
    beats = [
        {
            "beat_id": f"b{index + 1}",
            "act": acts[min(index, len(acts) - 1)],
            "narration_text": sentence,
            "visual_intent": f"trader at a desk, moment {index + 1}",
            "semantic_purpose": "explanation",
            "motion_recipe": "detail_punch",
            "on_screen_text": None if copy_deferred else f"BEAT {index + 1}",
            "copy_deferred": copy_deferred,
        }
        for index, sentence in enumerate(sentences)
    ]
    return {
        "schema_version": "director_proposal.v1",
        "brief_hash": brief["artifact_hash"],
        "lane": brief["lane"],
        "editorial_direction": {
            "pacing_note": "Hold each plate about six seconds; cut on the reframe.",
            "palette_note": "Muted paper white with a single warning red.",
            "identity_note": "Yellow t-shirt block and round head carry identity, not the face.",
        },
        "beats": beats,
    }


def build_candidate_batch(
    pack: dict[str, Any],
    *,
    job_root: Path,
    flags: dict[str, list[str]] | None = None,
    confidence: dict[str, float] | None = None,
    variants: int | None = None,
) -> dict[str, Any]:
    """A batch that answers every group in ``pack`` with real files on disk."""

    flags = flags or {}
    confidence = confidence or {}
    per_slot = variants if variants is not None else int(pack["variants_per_slot"])
    assets = job_root / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    items: list[dict[str, Any]] = []
    for group in pack["groups"]:
        slot_id = group["slot_id"]
        for variant in range(per_slot):
            item_id = f"{slot_id}-v{variant}".lower().replace("_", "-")
            body = _PNG_BYTES + f"{item_id}".encode("utf-8")
            path = assets / f"{item_id}.png"
            path.write_bytes(body)
            items.append(
                {
                    "id": item_id,
                    "slot_id": slot_id,
                    "variant_index": variant,
                    "role": "lofi_comedy",
                    "usage": "full_plate",
                    "path": f"assets/{item_id}.png",
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "source_kind": "ai_assisted_illustration",
                    "preview_eligible": True,
                    "render_eligible": False,
                    "evidence_eligible": False,
                    "contains_factual_text": False,
                    "review_status": "pending",
                    "style_board_selected": False,
                    "disclosure_label": "AI-assisted illustration",
                    "qc_flags": flags.get(item_id, []),
                    "confidence": confidence.get(item_id, 0.9),
                }
            )
    return {
        "schema_version": "generated_visual_candidates.v1",
        "provider": "openai-built-in-image-generation",
        "provider_calls": len(items),
        "items": items,
    }
