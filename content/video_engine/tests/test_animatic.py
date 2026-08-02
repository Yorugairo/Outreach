from __future__ import annotations

import json
import hashlib
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from content.video_engine.src.services.animatic import (
    AnimaticError,
    AnimaticService,
    _resolve_local_segment,
    extract_typed_relationship,
)
from content.video_engine.src.services.editorial_motion import (
    build_default_pacing_recipe,
)
from content.video_engine.src.services.history_contracts import canonical_sha256


def _storyboard() -> dict:
    scene = {
        "scene_id": 1,
        "narration_text": "Control the position before the transition.",
        "visual_type": "bjj_action",
        "visual_function": "wide_setup",
        "parameters": {
            "function": "wide_setup",
            "state_from": "closed_guard_neutral",
            "action": "break_posture",
            "state_to": "closed_guard_posture_broken",
            "camera": {"framing": "wide", "move": "push_in"},
            "reference_refs": ["ref-1"],
        },
        "timing": {"target_s": 3.0},
    }
    return {
        "global_settings": {
            "theme": {
                "background_color": "#0F0F12",
                "primary_text": "#FFFFFF",
                "accent_color": "#3B82F6",
                "secondary_accent": "#10B981",
            }
        },
        "scenes": [scene, {**scene, "scene_id": 2, "visual_function": "contact_closeup"}],
    }


def test_animatic_writes_preview_strip_and_review_packet(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def runner(command, **kwargs):
        del kwargs
        calls.append(list(command))
        Path(command[-1]).write_bytes(b"preview")
        return subprocess.CompletedProcess(command, 0, "", "")

    packet = AnimaticService(runner=runner).build(_storyboard(), tmp_path / "animatic")

    assert packet["schema_version"] == "animatic.v1"
    assert packet["provider_calls"] == 0
    assert packet["approval_granted"] is False
    assert packet["functions"] == ["wide_setup", "contact_closeup"]
    assert (tmp_path / packet["preview_path"]).is_file()
    assert (tmp_path / packet["shot_strip_path"]).is_file()
    assert (tmp_path / "animatic" / "review-packet.json").is_file()
    assert calls[0][0] == "ffmpeg"


def test_animatic_fails_when_ffmpeg_does_not_create_preview(tmp_path: Path) -> None:
    def runner(command, **kwargs):
        del kwargs
        return subprocess.CompletedProcess(command, 0, "", "")

    with pytest.raises(AnimaticError, match="preview"):
        AnimaticService(runner=runner).build(_storyboard(), tmp_path / "animatic")


def test_animatic_rejects_empty_storyboard(tmp_path: Path) -> None:
    with pytest.raises(AnimaticError, match="no scenes"):
        AnimaticService().build({"scenes": []}, tmp_path / "animatic")


def test_review_packet_is_machine_readable(tmp_path: Path) -> None:
    def runner(command, **kwargs):
        del kwargs
        Path(command[-1]).write_bytes(b"preview")
        return subprocess.CompletedProcess(command, 0, "", "")

    AnimaticService(runner=runner).build(_storyboard(), tmp_path / "animatic")
    payload = json.loads(
        (tmp_path / "animatic" / "review-packet.json").read_text(encoding="utf-8")
    )
    assert payload["shots"][0]["action"] == "break_posture"
    assert payload["shots"][0]["framing"] == "wide"


def test_history_animatic_uses_approved_style_board_frame(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def runner(command, **kwargs):
        del kwargs
        calls.append(list(command))
        Path(command[-1]).parent.mkdir(parents=True, exist_ok=True)
        Path(command[-1]).write_bytes(b"preview")
        return subprocess.CompletedProcess(command, 0, "", "")

    style_root = tmp_path / "style_board"
    still_root = style_root / "stills"
    still_root.mkdir(parents=True)
    Image.new("RGB", (640, 360), "#151C24").save(
        still_root / "archive.png"
    )
    (style_root / "style_board.json").write_text(
        json.dumps(
            {
                "stills": [
                    {
                        "role": "archive",
                        "path": "stills/archive.png",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    storyboard = {
        "schema_version": "2.2.0",
        "source": {"kind": "history_episode"},
        "scenes": [
            {
                "scene_id": 1,
                "visual_function": "archival_portrait",
                "narration_text": "The archive establishes context.",
                "citation_refs": ["citation-source-one"],
                "timing": {"target_s": 2},
            }
        ],
    }
    packet = {
        "preview_path": "animatic/preview.mp4",
        "provider_calls": 0,
    }

    result = AnimaticService(runner=runner)._render_documentary_motion(
        storyboard,
        tmp_path,
        packet,
    )

    assert result["renderer"] == "editorial_ffmpeg"
    assert result["preview_path"] == "animatic/motion-preview.mp4"
    assert (
        tmp_path / "animatic" / "editorial-beat-plan.json"
    ).is_file()
    assert result["editorial_beat_count"] == 1
    assert result["cut_count"] == 0
    assert result["composition_order"] == (
        "approved_world_then_deterministic_overlay"
    )
    assert any("zoompan=" in " ".join(command) for command in calls)


@pytest.mark.parametrize(
    "function_name",
    [
        "migration_map_timeline",
        "document_quote_closeup",
        "concept_mechanics_cutaway",
        "chapter_cta",
    ],
)
def test_documentary_overlays_retain_the_approved_world(
    tmp_path: Path,
    function_name: str,
) -> None:
    source = tmp_path / "approved-world.png"
    output = tmp_path / f"{function_name}.png"
    Image.new("RGB", (854, 480), (123, 44, 191)).save(source)
    scene = {
        "scene_id": 1,
        "visual_function": function_name,
        "narration_text": "Japan and Brazil changed the documented setting.",
        "citation_refs": ["citation-source-one"],
    }
    beat = {
        "function": function_name,
        "narration_excerpt": scene["narration_text"],
        "citation_refs": scene["citation_refs"],
    }

    AnimaticService()._documentary_frame(
        source,
        scene,
        output,
        beat=beat,
        beat_index=0,
        beat_count=1,
    )

    with Image.open(output) as rendered:
        red, _green, blue = rendered.convert("RGB").getpixel((840, 200))
    assert blue > red
    assert blue > 40


def test_lineage_without_a_sourced_edge_uses_evidence_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = AnimaticService()
    monkeypatch.setattr(
        service,
        "_lofi_relationship_fallback_frame",
        lambda *_args, **_kwargs: pytest.fail(
            "generic auto-graph fallback must not render"
        ),
    )

    result = service._lineage_context_frame(
        Image.new("RGB", (854, 480), "#F4EBDD"),
        "That wider field remains a research question.",
        0,
    )

    assert result.size == (854, 480)


def test_concept_terms_prefer_evidence_bound_phrases() -> None:
    terms = AnimaticService()._semantic_terms(
        (
            "Institutional histories emphasize education, disciplined "
            "practice, efficient use of energy, and mutual benefit."
        ),
        (
            "education",
            "disciplined practice",
            "efficient use of energy",
            "mutual benefit",
        ),
        limit=4,
    )

    assert terms == [
        "education",
        "disciplined practice",
        "efficient use of energy",
        "mutual benefit",
    ]


def test_cold_open_turns_the_approved_spread_into_contrast_cuts() -> None:
    world = Image.new("RGB", (854, 480), "#A44A32")
    right = Image.new("RGB", (427, 480), "#20D69B")
    world.paste(right, (427, 0))
    service = AnimaticService()

    battlefield = service._cold_open_world_frame(world, 0)
    institution = service._cold_open_world_frame(world, 1)

    assert battlefield.getpixel((427, 240)) != institution.getpixel((427, 240))


@pytest.mark.parametrize(
    "unsafe_path",
    ["../outside.mp4", "C:/outside.mp4"],
)
def test_animatic_rejects_manifest_segment_path_escape(
    tmp_path: Path,
    unsafe_path: str,
) -> None:
    with pytest.raises(AnimaticError, match="relative|escapes"):
        _resolve_local_segment(tmp_path / "job", unsafe_path)


def test_relationship_diagrams_fail_closed_on_keywords() -> None:
    assert (
        extract_typed_relationship(
            "That date does not mean every older practice became one lineage."
        )
        is None
    )


def test_relationship_diagrams_require_named_entities_and_typed_edge() -> None:
    assert extract_typed_relationship(
        "In 1882, Jigoro Kano established the Kodokan."
    ) == {
        "source": "Jigoro Kano",
        "target": "Kodokan",
        "label": "FOUNDED",
    }


def _editorial_revision_fixture(tmp_path: Path) -> dict:
    job = tmp_path / "job"
    assets_root = tmp_path / "approved-assets"
    assets_root.mkdir(parents=True)
    job.mkdir()
    (job / "animatic").mkdir()
    (job / "storyboard.json").write_text('{"immutable":true}', encoding="utf-8")
    (job / "animatic" / "motion-preview.mp4").write_bytes(b"active-gate-a")
    source_image = assets_root / "world.png"
    source_image.write_bytes(b"approved-image")
    audio_path = job / "audio" / "canonical" / "narration.mp3"
    audio_path.parent.mkdir(parents=True)
    audio_path.write_bytes(b"canonical-audio")
    asset_core = {
        "assets": {
            "world-one": {
                "path": "world.png",
                "sha256": hashlib.sha256(b"approved-image").hexdigest(),
                "render_eligible": True,
                "human_promoted": True,
            }
        }
    }
    asset_map = {**asset_core, "artifact_hash": canonical_sha256(asset_core)}
    audio_core = {
        "schema_version": "elevenlabs_canonical_audio.v1",
        "status": "ready",
        "narration_hash": "a" * 64,
        "audio_path": "audio/canonical/narration.mp3",
        "audio_sha256": hashlib.sha256(b"canonical-audio").hexdigest(),
        "duration_s": 2.0,
    }
    audio = {**audio_core, "artifact_hash": canonical_sha256(audio_core)}
    pacing = build_default_pacing_recipe()
    shot = {
        "shot_id": "proof-shot-one",
        "parent_beat_ids": ["proof-beat-one"],
        "parent_scene_bundle_id": "proof-bundle-one",
        "start_s": 0.0,
        "duration_s": 2.0,
        "word_range": {"start_index": 0, "end_index": 0},
        "narration_excerpt": "A useful starting point.",
        "purpose": "establish",
        "shot_scale": "wide",
        "focal_point": {"x": 0.5, "y": 0.5},
        "layers": [{"asset_id": "world-one", "role": "world"}],
        "subject_action": "none",
        "ambient_actions": ["lamp_flicker"],
        "information_reveal": "none",
        "camera": {
            "kind": "locked",
            "amount": 0.0,
            "easing": "smoothstep",
            "direction": "toward_focal_point",
            "hold_in_s": 2.0,
            "move_s": 0.0,
            "hold_out_s": 0.0,
        },
        "transition_in": {"kind": "hard_cut", "reason": "opening"},
        "transition_out": {"kind": "hard_cut", "reason": "proof end"},
        "audio_bridge": "continuous_narration",
        "provider_motion": {"requirement": "none", "fallback": "local_layer_motion"},
        "overlay_ids": [],
        "uniqueness_signature": "wide-world-locked-lamp",
    }
    plan_core = {
        "schema_version": "editorial_motion_plan.v1",
        "source_storyboard_hash": "1" * 64,
        "source_beat_plan_hash": "2" * 64,
        "scene_bundle_hashes": ["3" * 64],
        "scene_flow_graph_hash": "4" * 64,
        "asset_map_hash": asset_map["artifact_hash"],
        "audio_manifest_hash": audio["artifact_hash"],
        "pacing_recipe_hash": pacing["artifact_hash"],
        "duration_s": 2.0,
        "source_start_s": 0.0,
        "shots": [shot],
        "provider_calls": 0,
        "revision_only": True,
    }
    plan = {**plan_core, "artifact_hash": canonical_sha256(plan_core)}
    return {
        "job": job,
        "asset_root": assets_root,
        "asset_map": asset_map,
        "audio": audio,
        "pacing": pacing,
        "plan": plan,
        "output": job / "animatic" / "revisions" / "editorial-motion-v1",
    }


def test_editorial_revision_renders_normal_and_diagnostic_without_mutating_gate_a(
    tmp_path: Path,
) -> None:
    values = _editorial_revision_fixture(tmp_path)
    active = values["job"] / "animatic" / "motion-preview.mp4"
    before = active.read_bytes()
    calls: list[list[str]] = []

    def runner(command, **kwargs):
        assert kwargs.get("cwd")
        calls.append(list(command))
        Path(command[-1]).parent.mkdir(parents=True, exist_ok=True)
        Path(command[-1]).write_bytes(b"rendered")
        return subprocess.CompletedProcess(command, 0, "", "")

    packet = AnimaticService(runner=runner).render_editorial_motion_revision(
        values["plan"],
        asset_map=values["asset_map"],
        pacing_recipe=values["pacing"],
        audio_manifest=values["audio"],
        asset_root=values["asset_root"],
        job_dir=values["job"],
        output_dir=values["output"],
    )

    assert len(calls) == 2
    assert all("EditorialMotion" in call for call in calls)
    assert packet["provider_calls"] == 0
    assert packet["gate_a_unchanged"] is True
    assert active.read_bytes() == before
    assert (values["output"] / "revised-preview.mp4").is_file()
    assert (values["output"] / "diagnostic-preview.mp4").is_file()
    props = json.loads((values["output"] / "remotion-props.json").read_text(encoding="utf-8"))
    assert props["caption_policy"] == "platform"
    assert props["citation_policy"] == "credits_only"


def test_editorial_revision_rejects_output_outside_revision_tree(tmp_path: Path) -> None:
    values = _editorial_revision_fixture(tmp_path)
    with pytest.raises(AnimaticError, match="animatic/revisions"):
        AnimaticService().render_editorial_motion_revision(
            values["plan"],
            asset_map=values["asset_map"],
            pacing_recipe=values["pacing"],
            audio_manifest=values["audio"],
            asset_root=values["asset_root"],
            job_dir=values["job"],
            output_dir=values["job"] / "elsewhere",
        )
