"""Gate-A checks for storyboard contracts.

The storyboard is an input contract, not an open-ended prompt.  This module
keeps the checks deterministic and side-effect free so it can run before any
provider call (and again after a Gate-A edit).  ``guard`` intentionally returns
the same two-item shape as the article engine's guard, while collecting every
violation instead of stopping at the first one.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator, FormatChecker

from content.video_engine.src.models import SCENE_CLASS_REGISTRY


GuardResult = tuple[bool, list[str]]

_NUMBER = re.compile(r"\b\d{2,}(?:\.\d+)?\b")
_YEAR = re.compile(r"\b(?:1[89]\d\d|20\d\d)\b")
_SCORE_HINT = re.compile(
    r"\b(score[d]?\s*(of|is|at)?\s*\d)|(?:\b\d{2,3}\s*\+)|"
    r"(?:registry score[:\s]+\d)",
    re.IGNORECASE,
)
_MEDICAL = re.compile(
    r"\b(?:medical|health(?:care)?|injur(?:y|ies)|pain(?:ful)?|"
    r"joint|bone|muscle|therap(?:y|ist)|"
    r"diagnos(?:e|is)|treat(?:s|ment|ed)?|rehab(?:ilitation)?|"
    r"fracture|dangerous|safely|safety|risk)\b",
    re.IGNORECASE,
)
_FINANCIAL = re.compile(
    r"\b(?:financial|finance|money|cost|price|invest(?:s|ment)?|"
    r"profit|loss|revenue|return|market|fund|stock|loan|interest|"
    r"income|guarantee(?:d)?)\b",
    re.IGNORECASE,
)
_SUPERLATIVE = re.compile(
    r"\b(?:best|worst|greatest|most|least|first|only|never|always|"
    r"ultimate|perfect|strongest|weakest|fastest|slowest|easiest|"
    r"hardest|guaranteed|unbeatable|number\s+one)\b|#1",
    re.IGNORECASE,
)
_CREDENTIAL_FRAMING = re.compile(
    r"\b(?:doctor|surgeon|physician|therapist|economist)\b"
    r".*\b(?:explains|breaks\s+down|reveals)\b",
    re.IGNORECASE,
)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_ACTION_PREFIXES = {"pose", "map", "flash_label", "bjj_action"}

# The pose library is owned by the scene/render work package.  Keeping this
# small fallback lets the guard run in isolation before that package lands;
# once files exist, the directory listing is authoritative.
_KNOWN_POSES = {
    "closed_guard",
    "armbar_extension",
    "arm_yank_fail",
    "tap_frantic",
    "posture_broken",
    "gym_enforcer",
    "bowler_hat_maeda",
    "kano_throw",
}


@dataclass(frozen=True, slots=True)
class GuardDiagnostics:
    """Full Gate-A result, including non-blocking ledger warnings."""

    ok: bool
    violations: list[str]
    warnings: list[str]

    def as_tuple(self) -> GuardResult:
        return self.ok, self.violations


def _default_schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "configs" / "storyboard.schema.json"


def _load_json(value: Mapping[str, Any] | str | Path) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return json.loads(Path(value).read_text(encoding="utf-8"))


def _format_path(path: Sequence[Any]) -> str:
    if not path:
        return "$"
    rendered = "$"
    for part in path:
        rendered += f"[{part!r}]" if isinstance(part, int) else f".{part}"
    return rendered


def _schema_violations(
    storyboard: Mapping[str, Any], schema_path: str | Path | None
) -> list[str]:
    path = Path(schema_path) if schema_path is not None else _default_schema_path()
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"schema: unable to load {path}: {exc}"]

    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(storyboard),
        key=lambda error: (tuple(str(item) for item in error.path), error.message),
    )
    return [f"schema {_format_path(error.path)}: {error.message}" for error in errors]


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_SPLIT.split(text.strip()) if part.strip()]


def _requires_claim(sentence: str) -> tuple[bool, str | None]:
    # Years are explicitly allowlisted (the same 18xx/19xx/20xx rule used by
    # content/bjj-registry/src/llm_guard.py).  Any other two-or-more-digit value
    # remains a claim-bearing assertion.
    number_match = next(
        (match for match in _NUMBER.finditer(sentence) if not _YEAR.fullmatch(match.group(0))),
        None,
    )
    if number_match is not None:
        return True, f"number {number_match.group(0)!r}"
    if _SCORE_HINT.search(sentence):
        return True, "score/percent language"
    if _MEDICAL.search(sentence):
        return True, "medical language"
    if _FINANCIAL.search(sentence):
        return True, "financial language"
    if _SUPERLATIVE.search(sentence):
        return True, "superlative language"
    return False, None


def _available_poses(assets_root: str | Path | None) -> set[str]:
    if assets_root is None:
        root = Path(__file__).resolve().parents[1] / "assets" / "poses"
    else:
        root = Path(assets_root)
    try:
        names = {path.stem for path in root.glob("*.svg") if path.is_file()}
    except OSError:
        names = set()
    return names or set(_KNOWN_POSES)


def _check_claims(
    storyboard: Mapping[str, Any], violations: list[str], warnings: list[str]
) -> None:
    claims = {
        str(claim.get("id")): claim
        for claim in storyboard.get("claims", [])
        if isinstance(claim, Mapping) and claim.get("id") is not None
    }
    referenced: set[str] = set()
    for scene in storyboard.get("scenes", []):
        if not isinstance(scene, Mapping):
            continue
        scene_id = scene.get("scene_id", "?")
        refs = [str(ref) for ref in scene.get("claim_refs", [])]
        referenced.update(refs)
        valid_refs: list[str] = []
        for ref in refs:
            claim = claims.get(ref)
            if claim is None:
                violations.append(f"scene {scene_id} references missing claim {ref!r}")
            elif not bool(claim.get("verified")):
                violations.append(f"scene {scene_id} references unverified claim {ref!r}")
            else:
                valid_refs.append(ref)

        narration = str(scene.get("narration_text", ""))
        for sentence in _sentences(narration):
            required, reason = _requires_claim(sentence)
            if required and not valid_refs:
                violations.append(
                    f"scene {scene_id} has unledgered {reason}: {sentence!r}"
                )

    for claim_id in sorted(set(claims) - referenced):
        warnings.append(f"claim {claim_id!r} is unreferenced (warning)")


def _check_arc(storyboard: Mapping[str, Any], violations: list[str]) -> float:
    scenes = [scene for scene in storyboard.get("scenes", []) if isinstance(scene, Mapping)]
    if not scenes:
        return 0.0
    acts = [str(scene.get("act", "")) for scene in scenes]
    if len(set(scene.get("scene_id") for scene in scenes)) != len(scenes):
        violations.append("scene_ids must be unique")
    if acts.count("hook") != 1:
        violations.append(f"arc requires exactly one hook scene (found {acts.count('hook')})")
        if not acts or acts[0] != "hook":
            violations.append("hook scene must be first")
    elif acts[0] != "hook":
        violations.append("hook scene must be first")
    if acts.count("cta") != 1:
        violations.append(f"arc requires exactly one cta scene (found {acts.count('cta')})")
        if not acts or acts[-1] != "cta":
            violations.append("cta scene must be last")
    elif acts[-1] != "cta":
        violations.append("cta scene must be last")
    if "develop" not in acts:
        violations.append("arc requires at least one develop scene")
    if "payoff" not in acts:
        violations.append("arc requires at least one payoff scene")

    durations: list[float] = []
    for scene in scenes:
        timing = scene.get("timing", {})
        try:
            durations.append(float(timing.get("target_s", 0)))
        except (TypeError, ValueError):
            durations.append(0.0)
    total = sum(durations)
    starts: list[float] = []
    cursor = 0.0
    for duration in durations:
        starts.append(cursor)
        cursor += duration

    if scenes and acts[0] == "hook" and durations[0] > 12:
        violations.append(f"hook scene exceeds 12s budget ({durations[0]:g}s)")

    conflicts = [index for index, act in enumerate(acts) if act == "conflict"]
    comebacks = [index for index, act in enumerate(acts) if act == "comeback"]
    if comebacks and not conflicts:
        violations.append("comeback scene requires a paired conflict scene")
    if total > 90:
        if not any(starts[index] < total / 3 for index in conflicts):
            violations.append("runs over 90s require a conflict in the first third")
        if not comebacks:
            violations.append("runs over 90s require a comeback paired with conflict")
    return total


def _check_assets(
    storyboard: Mapping[str, Any], violations: list[str], assets_root: str | Path | None
) -> None:
    poses = _available_poses(assets_root)
    for scene in storyboard.get("scenes", []):
        if not isinstance(scene, Mapping):
            continue
        scene_id = scene.get("scene_id", "?")
        scene_class = str(scene.get("manim_class", ""))
        registration = SCENE_CLASS_REGISTRY.get(scene_class)
        if registration is None:
            violations.append(f"scene {scene_id} references unknown manim_class {scene_class!r}")
            registration = {"visual_types": [], "actions": []}
        visual_type = scene.get("visual_type")
        if visual_type not in registration.get("visual_types", []):
            violations.append(
                f"scene {scene_id} visual_type {visual_type!r} is incompatible with {scene_class!r}"
            )

        parameters = scene.get("parameters", {})
        if isinstance(parameters, Mapping):
            for pose in parameters.get("poses", []) or []:
                if str(pose) not in poses:
                    violations.append(f"scene {scene_id} references missing pose {pose!r}")

        for beat in scene.get("beats", []) or []:
            if not isinstance(beat, Mapping):
                continue
            action = str(beat.get("action", ""))
            prefix, separator, value = action.partition(":")
            actions = set(registration.get("actions", []))
            if prefix not in actions:
                violations.append(
                    f"scene {scene_id} beat action {action!r} is not exposed by {scene_class!r}"
                )
                continue
            if prefix in _ACTION_PREFIXES and (not separator or not value.strip()):
                violations.append(f"scene {scene_id} beat action {action!r} has no target")
            elif prefix == "pose" and value not in poses:
                violations.append(f"scene {scene_id} beat references missing pose {value!r}")


def _check_pacing(storyboard: Mapping[str, Any], violations: list[str]) -> None:
    settings = storyboard.get("global_settings", {})
    pacing = settings.get("pacing", {}) if isinstance(settings, Mapping) else {}
    try:
        visual_budget = float(pacing.get("visual_change_max_s", 6))
    except (TypeError, ValueError):
        visual_budget = 6.0
    try:
        interrupt_budget = float(pacing.get("pattern_interrupt_max_s", 30))
    except (TypeError, ValueError):
        interrupt_budget = 30.0
    targets = settings.get("targets", []) if isinstance(settings, Mapping) else []
    vertical_target = "vertical" in targets
    try:
        vertical_visual_budget = float(pacing.get("shorts_visual_change_max_s", 3))
    except (TypeError, ValueError):
        vertical_visual_budget = 3.0

    hard_cuts: dict[str, int] = {}
    for scene in storyboard.get("scenes", []):
        if not isinstance(scene, Mapping):
            continue
        scene_id = scene.get("scene_id", "?")
        timing = scene.get("timing", {})
        try:
            target = float(timing.get("target_s", 0))
        except (TypeError, ValueError):
            continue
        try:
            min_s = float(timing.get("min_s", 2))
            max_s = float(timing.get("max_s", 45))
        except (TypeError, ValueError):
            min_s, max_s = 2.0, 45.0
        if target < min_s:
            violations.append(f"scene {scene_id} target {target:g}s is below min_s {min_s:g}s")
        if target > max_s:
            violations.append(f"scene {scene_id} target {target:g}s exceeds max_s {max_s:g}s")

        beats = scene.get("beats", []) or []
        transition = scene.get("transition", {})
        transition_in = transition.get("in", "continuous") if isinstance(transition, Mapping) else "continuous"
        # A boundary/beat is a visual change.  Reject clearly dead stretches while
        # preserving short worked examples whose continuous motion carries through.
        if target > visual_budget and not beats and str(scene.get("act")) != "cta":
            violations.append(
                f"scene {scene_id} exceeds visual-change budget without a beat ({target:g}s > {visual_budget:g}s)"
            )
        if (
            vertical_target
            and target > vertical_visual_budget
            and not beats
            and str(scene.get("act")) != "cta"
        ):
            violations.append(
                f"scene {scene_id} exceeds vertical visual-change budget without a beat "
                f"({target:g}s > {vertical_visual_budget:g}s)"
            )

        act = str(scene.get("act", ""))
        if transition_in == "hard_cut":
            hard_cuts[act] = hard_cuts.get(act, 0) + 1

    for act, count in sorted(hard_cuts.items()):
        if count > 1:
            violations.append(f"act {act!r} has {count} hard cuts (maximum is 1)")

    # A long uninterrupted run with no deliberate transition/beat is an
    # interrupt-budget breach.  The threshold is intentionally measured over
    # adjacent scenes so scene boundaries count as real visual changes.
    scenes = [scene for scene in storyboard.get("scenes", []) if isinstance(scene, Mapping)]
    cursor = 0.0
    quiet_start: float | None = None
    for scene in scenes:
        timing = scene.get("timing", {})
        try:
            target = float(timing.get("target_s", 0))
        except (TypeError, ValueError):
            target = 0.0
        has_interrupt = bool(scene.get("beats")) or (
            isinstance(scene.get("transition"), Mapping)
            and scene["transition"].get("in") in {"crossfade", "match_cut", "hard_cut"}
        )
        if has_interrupt:
            quiet_start = None
        elif quiet_start is None:
            quiet_start = cursor
        cursor += target
        if quiet_start is not None and cursor - quiet_start > interrupt_budget * 1.5:
            violations.append(
                f"pattern-interrupt budget exceeded ({cursor - quiet_start:g}s > {interrupt_budget:g}s)"
            )
            quiet_start = None


def _check_disclosure(storyboard: Mapping[str, Any], violations: list[str]) -> None:
    realistic = any(
        isinstance(scene, Mapping) and bool(scene.get("realistic_recreation"))
        for scene in storyboard.get("scenes", [])
    )
    packaging = storyboard.get("packaging", {})
    disclosure = packaging.get("synthetic_content_disclosure", {}) if isinstance(packaging, Mapping) else {}
    if realistic and not bool(disclosure.get("required")):
        violations.append(
            "realistic_recreation requires packaging.synthetic_content_disclosure.required=true"
        )


def _check_shorts(storyboard: Mapping[str, Any], violations: list[str]) -> None:
    scene_ids = {
        scene.get("scene_id")
        for scene in storyboard.get("scenes", [])
        if isinstance(scene, Mapping)
    }
    for short in storyboard.get("shorts", []) or []:
        if not isinstance(short, Mapping):
            continue
        clip_id = short.get("clip_id", "?")
        missing = [scene_id for scene_id in short.get("scene_ids", []) if scene_id not in scene_ids]
        if missing:
            violations.append(f"short {clip_id!r} references missing scene ids {missing!r}")


def _check_voice(storyboard: Mapping[str, Any], violations: list[str]) -> None:
    settings = storyboard.get("global_settings", {})
    voice = settings.get("voice", {}) if isinstance(settings, Mapping) else {}
    if voice.get("provider") == "elevenlabs" and voice.get("is_custom_voice") is not True:
        violations.append("elevenlabs voice must set is_custom_voice=true")


def _evaluate(
    storyboard: Mapping[str, Any],
    *,
    assets_root: str | Path | None = None,
    schema_path: str | Path | None = None,
) -> GuardDiagnostics:
    violations = _schema_violations(storyboard, schema_path)
    if violations:
        return GuardDiagnostics(False, violations, [])

    warnings: list[str] = []
    _check_claims(storyboard, violations, warnings)
    _check_arc(storyboard, violations)
    _check_assets(storyboard, violations, assets_root)
    _check_pacing(storyboard, violations)
    _check_disclosure(storyboard, violations)
    _check_shorts(storyboard, violations)
    _check_voice(storyboard, violations)
    expert = storyboard.get("expert")
    if not isinstance(expert, Mapping):
        for scene in storyboard.get("scenes", []):
            if isinstance(scene, Mapping) and _CREDENTIAL_FRAMING.search(
                str(scene.get("narration_text", ""))
            ):
                violations.append(
                    f"scene {scene.get('scene_id', '?')} uses credential framing without a named expert"
                )

    return GuardDiagnostics(not violations, violations, warnings)


def guard(
    storyboard: Mapping[str, Any] | str | Path,
    assets_root: str | Path | None = None,
    *,
    schema_path: str | Path | None = None,
) -> GuardResult:
    """Return ``(passed, violations)`` for a storyboard mapping or JSON path."""

    loaded = _load_json(storyboard)
    if str(loaded.get("schema_version") or "") in {"2.2.0", "2.3.0"}:
        from content.video_engine.src.guards.documentary_storyboard import (
            guard as documentary_guard,
        )

        return documentary_guard(loaded)
    return _evaluate(loaded, assets_root=assets_root, schema_path=schema_path).as_tuple()


def guard_with_warnings(
    storyboard: Mapping[str, Any] | str | Path,
    assets_root: str | Path | None = None,
    *,
    schema_path: str | Path | None = None,
) -> GuardDiagnostics:
    """Return the Gate-A result plus non-blocking unreferenced-claim warnings."""

    loaded = _load_json(storyboard)
    if str(loaded.get("schema_version") or "") in {"2.2.0", "2.3.0"}:
        from content.video_engine.src.guards.documentary_storyboard import (
            guard as documentary_guard,
        )

        ok, violations = documentary_guard(loaded)
        return GuardDiagnostics(ok, violations, [])
    return _evaluate(loaded, assets_root=assets_root, schema_path=schema_path)


def guard_from_path(
    path: str | Path,
    assets_root: str | Path | None = None,
    *,
    schema_path: str | Path | None = None,
) -> GuardResult:
    return guard(path, assets_root, schema_path=schema_path)


validate_storyboard = guard


__all__ = [
    "GuardDiagnostics",
    "GuardResult",
    "_NUMBER",
    "_SCORE_HINT",
    "guard",
    "guard_from_path",
    "guard_with_warnings",
    "validate_storyboard",
]
