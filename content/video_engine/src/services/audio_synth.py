"""ElevenLabs narration synthesis and word-timing artifacts.

The audio stage is deliberately small and deterministic around its provider
boundary:

* storyboard text and voice settings form the cache key;
* the provider is called once per scene through ``/with-timestamps``;
* provider character alignment is reduced to the storyboard's whitespace
  tokenisation (rather than trying to infer words from the character array);
* only failed/transient provider requests are retried; and
* the stage writes the immutable artifacts consumed by rendering/captions.

No provider client dependency is required.  ``urllib`` is used for the real
call, while ``AudioSynthService`` accepts an injected request function for
mocked tests and local dry runs.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import logging
import os
import re
import socket
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from content.video_engine.src.models import StageContext, StageOutput, VideoRun


LOGGER = logging.getLogger(__name__)

DEFAULT_ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"
DEFAULT_ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"
DEFAULT_ELEVENLABS_OUTPUT_FORMAT = "mp3_44100_128"
DEFAULT_TIMEOUT_S = 60.0
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_RETRY_BACKOFF_S = 0.5

# The service reports an estimate only; actual billing varies by ElevenLabs
# plan/model.  Keeping the rate in one exported constant makes the estimate
# explicit and straightforward to override in tests or channel config.
ELEVENLABS_RATE_PER_CHARACTER_USD = 0.0002
TTS_COST_PER_CHARACTER_USD = ELEVENLABS_RATE_PER_CHARACTER_USD
COST_PER_CHARACTER = ELEVENLABS_RATE_PER_CHARACTER_USD

_TOKEN = re.compile(r"\S+", re.UNICODE)

# Pause-mark compilation (doc 37 §1).  Scripts carry semantic marks; the
# provider receives SSML break tags.  v3 has no SSML — this table is the
# multilingual-v2 column; a v3 column would map to [pause]-style audio tags.
PAUSE_MARK_BREAKS: dict[str, str] = {
    "[pre-key]": '<break time="0.6s" />',
    "[post-key]": '<break time="1.2s" />',
}
# Official guidance: excessive break tags cause speed-ups and artifacts.
MAX_BREAK_TAGS_PER_SEGMENT = 3

_BREAK_TAG = re.compile(r'<break\s+time="\d+(?:\.\d+)?s"\s*/>')
_PAUSE_MARK = re.compile(r"`?\[(?:pre|post)-key\]`?")
# Editorial flags ([verify], [check-me], ...) are workflow markup. They must
# never be spoken: the provider reads unknown brackets aloud (operator-caught,
# 2026-08-25). Scripts should not contain them at synthesis time at all; this
# strip is the defensive gate, and finding one is warned as a script defect.
_EDITORIAL_FLAG = re.compile(r"`?\[[a-z][a-z-]*\]`?")


def compile_pause_marks(narration: str) -> str:
    """Translate script pause marks into provider break tags.

    Pause marks become break tags; any OTHER bracketed lowercase token is an
    editorial flag that leaked past scripting and is stripped with a warning —
    the provider would read it aloud verbatim.
    """

    compiled = narration
    for mark, tag in PAUSE_MARK_BREAKS.items():
        # Scripts write the mark inside backticks so it reads as a code span
        # in the markdown draft. Replacing only the mark leaves
        # `<break time="1.2s" />` - the provider cannot parse a backticked
        # SSML tag, so it VOCALISES it. That is the 0.29s artifact heard at
        # 0:08 of the first Steel and Paper take. Consume the backticks.
        compiled = re.sub(r"`\s*" + re.escape(mark) + r"\s*`", tag, compiled)
        compiled = compiled.replace(mark, tag)
    leaked = _EDITORIAL_FLAG.findall(compiled)
    if leaked:
        LOGGER.warning(
            "editorial flags %s found in narration at synthesis time; stripped "
            "— verification belongs before scripting, never in the script",
            sorted(set(leaked)),
        )
        compiled = " ".join(_EDITORIAL_FLAG.sub(" ", compiled).split())
    # A break tag with a stray backtick or bracket still touching it is read
    # aloud. Checking that the MARK is gone is not the same as checking the
    # output is speakable.
    dirty = re.findall(r'[`\[\]]\s*<break[^>]*>|<break[^>]*>\s*[`\[\]]', compiled)
    if dirty:
        raise ValueError(
            f"break tag left adjacent to literal {dirty[0]!r}; the provider "
            f"will speak it - fix compilation, do not record")
    tag_count = len(_BREAK_TAG.findall(compiled))
    if tag_count > MAX_BREAK_TAGS_PER_SEGMENT:
        LOGGER.warning(
            "segment compiles to %d break tags (ration is %d); excessive breaks "
            "cause provider speed-ups and artifacts — split the segment or cut marks",
            tag_count,
            MAX_BREAK_TAGS_PER_SEGMENT,
        )
    return compiled


def strip_pause_markup(text: str) -> str:
    """Remove pause marks and break tags, collapsing the leftover whitespace.

    Used for caption-facing text and for comparing narration against cached
    word timings; the marks are delivery directives, never viewer text.
    """

    stripped = _BREAK_TAG.sub(" ", text)
    stripped = _PAUSE_MARK.sub(" ", stripped)
    stripped = _EDITORIAL_FLAG.sub(" ", stripped)
    return " ".join(stripped.split())


def _pause_word_indices(compiled: str) -> set[int]:
    """Token indices in ``compiled`` that belong to break-tag markup."""

    tag_spans = [match.span() for match in _BREAK_TAG.finditer(compiled)]
    if not tag_spans:
        return set()
    indices: set[int] = set()
    for index, token in enumerate(_TOKEN.finditer(compiled)):
        token_start, token_end = token.span()
        if any(start < token_end and token_start < end for start, end in tag_spans):
            indices.add(index)
    return indices


def _optional_int_env(name: str) -> int | None:
    raw = os.environ.get(name)
    if raw in (None, ""):
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


def _locators_env(name: str) -> tuple[Mapping[str, Any], ...]:
    raw = os.environ.get(name)
    if raw in (None, ""):
        return ()
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{name} must be a JSON array of locator objects") from exc
    if not isinstance(loaded, list) or not all(
        isinstance(item, Mapping) for item in loaded
    ):
        raise RuntimeError(f"{name} must be a JSON array of locator objects")
    return tuple(loaded)


class AudioSynthesisError(RuntimeError):
    """A provider or artifact failure that should fail the audio stage."""


class AlignmentError(ValueError):
    """Provider character alignment cannot be reconciled with narration."""


class AudioRequestFn(Protocol):
    """Callable shape accepted by the injectable HTTP boundary.

    Implementations return ``(status_code, payload)`` where payload is either
    the decoded response mapping or the response bytes.  A callable that uses
    a different but common shape (``json=`` instead of ``payload=``) is also
    adapted by :meth:`AudioSynthService._request_once`.
    """

    def __call__(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        payload: Mapping[str, Any],
        timeout: float,
    ) -> tuple[int, Mapping[str, Any] | bytes]: ...


@dataclass(slots=True)
class ElevenLabsConfig:
    """Runtime configuration for the ElevenLabs ``with-timestamps`` API.

    ``api_key`` is intentionally nullable for object construction in tests;
    :meth:`from_env` and :class:`AudioSynthService` validate it immediately
    before a stage starts, never at module import time.
    """

    api_key: str | None = None
    voice_id: str | None = None
    base_url: str = DEFAULT_ELEVENLABS_BASE_URL
    model_id: str = DEFAULT_ELEVENLABS_MODEL_ID
    output_format: str = DEFAULT_ELEVENLABS_OUTPUT_FORMAT
    timeout_s: float = DEFAULT_TIMEOUT_S
    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    retry_backoff_s: float = DEFAULT_RETRY_BACKOFF_S
    rate_per_character_usd: float = ELEVENLABS_RATE_PER_CHARACTER_USD
    request_headers: dict[str, str] = field(default_factory=dict)
    # doc 37: explicit normalization for narration jobs; "auto"/"on"/"off".
    text_normalization: str = "on"
    # doc 37: optional deterministic retakes.
    seed: int | None = None
    # doc 37 §5: locators for dictionaries already synced to ElevenLabs.
    pronunciation_dictionary_locators: tuple[Mapping[str, Any], ...] = ()

    @classmethod
    def from_env(cls) -> "ElevenLabsConfig":
        """Load provider settings from environment variables.

        The API key is mandatory.  Raising here (when ``run_stage`` invokes
        this method) gives operators a fail-fast error without making imports
        depend on local credentials.  A voice id may be supplied by the
        storyboard; ``ELEVENLABS_VOICE_ID`` is a convenient default.
        """

        api_key = (os.environ.get("ELEVENLABS_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError(
                "ELEVENLABS_API_KEY is required to synthesize audio; "
                "configure it before starting the synthesizing_audio stage"
            )

        def _float_env(name: str, default: float) -> float:
            raw = os.environ.get(name)
            if raw in (None, ""):
                return default
            try:
                return float(raw)
            except ValueError as exc:
                raise RuntimeError(f"{name} must be a number") from exc

        def _int_env(name: str, default: int) -> int:
            raw = os.environ.get(name)
            if raw in (None, ""):
                return default
            try:
                value = int(raw)
            except ValueError as exc:
                raise RuntimeError(f"{name} must be an integer") from exc
            if value < 1:
                raise RuntimeError(f"{name} must be at least 1")
            return value

        base_url = (
            os.environ.get("ELEVENLABS_BASE_URL", DEFAULT_ELEVENLABS_BASE_URL)
            or DEFAULT_ELEVENLABS_BASE_URL
        ).rstrip("/")
        return cls(
            api_key=api_key,
            voice_id=(os.environ.get("ELEVENLABS_VOICE_ID") or "").strip() or None,
            base_url=base_url,
            model_id=os.environ.get("ELEVENLABS_MODEL_ID", DEFAULT_ELEVENLABS_MODEL_ID),
            output_format=os.environ.get(
                "ELEVENLABS_OUTPUT_FORMAT", DEFAULT_ELEVENLABS_OUTPUT_FORMAT
            ),
            timeout_s=_float_env("ELEVENLABS_TIMEOUT_S", DEFAULT_TIMEOUT_S),
            max_attempts=_int_env("ELEVENLABS_MAX_ATTEMPTS", DEFAULT_MAX_ATTEMPTS),
            retry_backoff_s=_float_env(
                "ELEVENLABS_RETRY_BACKOFF_S", DEFAULT_RETRY_BACKOFF_S
            ),
            rate_per_character_usd=_float_env(
                "ELEVENLABS_RATE_PER_CHARACTER_USD",
                ELEVENLABS_RATE_PER_CHARACTER_USD,
            ),
            text_normalization=(
                os.environ.get("ELEVENLABS_TEXT_NORMALIZATION") or "on"
            ).strip(),
            seed=_optional_int_env("ELEVENLABS_SEED"),
            pronunciation_dictionary_locators=_locators_env(
                "ELEVENLABS_PRONUNCIATION_DICTIONARIES"
            ),
        )

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "ElevenLabsConfig":
        """Build config from a persisted/config-file mapping.

        This helper is intentionally permissive about extra keys so channel
        config can be passed through without coupling the stage to that file's
        complete schema.
        """

        known = {
            "api_key",
            "voice_id",
            "base_url",
            "model_id",
            "output_format",
            "timeout_s",
            "max_attempts",
            "retry_backoff_s",
            "rate_per_character_usd",
            "request_headers",
            "text_normalization",
            "seed",
            "pronunciation_dictionary_locators",
        }
        payload = {key: value for key, value in values.items() if key in known}
        if "base_url" in payload and payload["base_url"]:
            payload["base_url"] = str(payload["base_url"]).rstrip("/")
        locators = payload.get("pronunciation_dictionary_locators")
        if locators is not None:
            payload["pronunciation_dictionary_locators"] = tuple(locators)
        return cls(**payload)


@dataclass(slots=True, frozen=True)
class SceneAudioResult:
    """Persisted output summary for one synthesized scene."""

    scene_id: int
    audio_path: Path
    words_path: Path
    duration_s: float
    character_count: int
    cache_hit: bool
    cost_usd: float
    request_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["audio_path"] = str(self.audio_path)
        payload["words_path"] = str(self.words_path)
        return payload


def _normalise_text(value: str) -> str:
    """Collapse provider/storyboard whitespace while preserving punctuation."""

    return unicodedata.normalize("NFC", " ".join(str(value).split()))


def _as_float(value: Any, *, field_name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise AlignmentError(f"alignment field {field_name!r} contains a non-number") from exc
    if result < 0:
        raise AlignmentError(f"alignment field {field_name!r} contains a negative time")
    return result


def _extract_alignment(alignment: Mapping[str, Any]) -> tuple[list[str], list[float], list[float]]:
    """Extract ElevenLabs' character arrays, accepting documented aliases."""

    characters = alignment.get("characters")
    starts = alignment.get("character_start_times_seconds")
    ends = alignment.get("character_end_times_seconds")
    # A few provider SDK versions use the shorter names.  Supporting them is
    # harmless and keeps mocked responses representative of both forms.
    if starts is None:
        starts = alignment.get("character_start_times") or alignment.get("start_times")
    if ends is None:
        ends = alignment.get("character_end_times") or alignment.get("end_times")

    if not isinstance(characters, list) or starts is None or ends is None:
        raise AlignmentError(
            "ElevenLabs response is missing characters and character start/end times"
        )
    if not isinstance(starts, list) or not isinstance(ends, list):
        raise AlignmentError("ElevenLabs character timing fields must be arrays")
    if not (len(characters) == len(starts) == len(ends)):
        raise AlignmentError(
            "ElevenLabs character/timing arrays have different lengths "
            f"({len(characters)}, {len(starts)}, {len(ends)})"
        )
    if not characters:
        raise AlignmentError("ElevenLabs returned an empty character alignment")
    return (
        [str(character) for character in characters],
        [_as_float(value, field_name="start") for value in starts],
        [_as_float(value, field_name="end") for value in ends],
    )


def group_word_timings(
    narration: str,
    alignment: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], float]:
    """Convert character alignment into contract ``words`` + duration.

    ``narration.split()`` is the source of word boundaries.  Alignment spaces
    and punctuation are still consumed while walking the provider character
    stream, which handles multi-space input, em-dashes, and punctuation without
    inventing token boundaries.  The normalized reconstructed text assertion is
    intentionally strict: stale/misaligned provider output must fail before an
    animation render can consume bad timings.
    """

    if not isinstance(narration, str) or not narration.strip():
        raise AlignmentError("narration must contain at least one non-whitespace character")
    characters, starts, ends = _extract_alignment(alignment)
    reconstructed = "".join(characters)
    if _normalise_text(reconstructed) != _normalise_text(narration):
        raise AlignmentError(
            "ElevenLabs alignment text does not match narration "
            f"(got {_normalise_text(reconstructed)!r}, expected {_normalise_text(narration)!r})"
        )

    tokens = [match.group(0) for match in _TOKEN.finditer(narration)]
    if not tokens:
        raise AlignmentError("narration produced no word tokens")

    words: list[dict[str, Any]] = []
    character_index = 0
    for token in tokens:
        # Ignore any amount of whitespace between words in the provider
        # alignment.  It remains part of the reconstructed-text check above.
        while character_index < len(characters) and characters[character_index].isspace():
            character_index += 1
        token_starts: list[float] = []
        token_ends: list[float] = []
        token_index = 0
        while token_index < len(token):
            if character_index >= len(characters):
                raise AlignmentError(f"alignment ended while matching word {token!r}")
            character = characters[character_index]
            if character.isspace():
                # Whitespace in the middle of a token can only be reconciled
                # when the provider normalized a storyboard token.  It is
                # rejected rather than silently assigning a wrong timestamp.
                raise AlignmentError(f"alignment whitespace split word {token!r}")
            expected_character = token[token_index]
            if character != expected_character:
                raise AlignmentError(
                    f"alignment character mismatch for word {token!r}: "
                    f"got {character!r}, expected {expected_character!r}"
                )
            token_starts.append(starts[character_index])
            token_ends.append(ends[character_index])
            character_index += 1
            token_index += 1
        start_s = min(token_starts)
        end_s = max(token_ends)
        if end_s < start_s:
            raise AlignmentError(f"word {token!r} has an end before its start")
        words.append({"w": token, "start_s": start_s, "end_s": end_s})

    # Any trailing characters must be whitespace.  A provider response with
    # extra non-whitespace data is not safe to pair with this narration.
    if any(not character.isspace() for character in characters[character_index:]):
        raise AlignmentError("alignment contains non-whitespace characters after narration")

    duration_s = max(ends)
    return words, duration_s


def _cache_key(voice_id: str, narration_text: str, settings: Mapping[str, Any]) -> str:
    material = (
        voice_id
        + "|"
        + narration_text
        + "|"
        + json.dumps(dict(settings), sort_keys=True)
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _request_id_from_headers(headers: Mapping[str, str] | None) -> str | None:
    """Extract the provider request id (case-insensitive) for stitching."""

    if not headers:
        return None
    for key, value in headers.items():
        if str(key).casefold() == "request-id" and str(value).strip():
            return str(value).strip()
    return None


def _decode_provider_payload(payload: Mapping[str, Any] | bytes) -> dict[str, Any]:
    if isinstance(payload, bytes):
        try:
            payload = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AudioSynthesisError("ElevenLabs returned a non-JSON response") from exc
    if not isinstance(payload, Mapping):
        raise AudioSynthesisError("ElevenLabs response must be a JSON object")
    return dict(payload)


def _decode_audio(payload: Mapping[str, Any]) -> bytes:
    encoded = payload.get("audio_base64")
    if encoded is None:
        # ``audio`` is accepted for a couple of mocked/provider wrappers; the
        # official endpoint uses ``audio_base64``.
        encoded = payload.get("audio")
    if not isinstance(encoded, str) or not encoded:
        raise AudioSynthesisError("ElevenLabs response is missing audio_base64")
    try:
        return base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise AudioSynthesisError("ElevenLabs audio_base64 is not valid base64") from exc


class AudioSynthService:
    """Synthesize all storyboard scenes and persist audio/timing artifacts."""

    def __init__(
        self,
        config: ElevenLabsConfig | None = None,
        *,
        request_fn: AudioRequestFn | Callable[..., Any] | None = None,
        http_client: AudioRequestFn | Callable[..., Any] | None = None,
        transport: AudioRequestFn | Callable[..., Any] | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        self.config = config
        # Three names keep the provider boundary easy to inject while making
        # the public ``request_fn`` spelling the canonical one.
        self._request_fn = request_fn or http_client or transport
        self._sleep_fn = sleep_fn or time.sleep

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        """Run the stage function contract used by :class:`VideoPipeline`."""

        config = self.config or ElevenLabsConfig.from_env()
        self._validate_config(config)
        storyboard = self._load_storyboard(job, ctx)
        summary = self.synthesize_storyboard(storyboard, ctx.job_dir, config=config)
        return StageOutput(summary)

    def synthesize_storyboard(
        self,
        storyboard: Mapping[str, Any],
        job_dir: Path,
        *,
        config: ElevenLabsConfig | None = None,
    ) -> dict[str, Any]:
        """Synthesize each scene in storyboard order and return stage summary."""

        config = config or self.config or ElevenLabsConfig.from_env()
        self._validate_config(config)
        if not isinstance(storyboard, Mapping):
            raise AudioSynthesisError("storyboard must be a JSON object")
        voice = storyboard.get("global_settings", {}).get("voice", {})
        if not isinstance(voice, Mapping):
            raise AudioSynthesisError("storyboard global_settings.voice must be an object")
        provider = str(voice.get("provider", "elevenlabs")).casefold()
        if provider != "elevenlabs":
            raise AudioSynthesisError(
                f"audio_synth only supports ElevenLabs voice provider, got {provider!r}"
            )
        voice_id = str(voice.get("voice_id") or config.voice_id or "").strip()
        if not voice_id:
            raise RuntimeError(
                "an ElevenLabs voice_id is required in storyboard.global_settings.voice "
                "or ELEVENLABS_VOICE_ID"
            )
        settings = voice.get("settings", {})
        if settings is None:
            settings = {}
        if not isinstance(settings, Mapping):
            raise AudioSynthesisError("storyboard voice settings must be an object")

        audio_dir = Path(job_dir) / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        cache_dir = audio_dir / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        scenes = storyboard.get("scenes")
        if not isinstance(scenes, list) or not scenes:
            raise AudioSynthesisError("storyboard must contain a non-empty scenes array")

        scene_results: list[SceneAudioResult] = []
        total_chars = 0
        cache_hits = 0
        billable_chars = 0
        # Request-stitching chain (doc 37 §3): carry the last <=3 provider
        # request ids forward so prosody stays continuous across scenes.
        stitch_chain: list[str] = []
        for scene in scenes:
            if not isinstance(scene, Mapping):
                raise AudioSynthesisError("each storyboard scene must be an object")
            try:
                scene_id = int(scene["scene_id"])
                narration = str(scene["narration_text"])
            except (KeyError, TypeError, ValueError) as exc:
                raise AudioSynthesisError(
                    "each scene requires integer scene_id and narration_text"
                ) from exc
            result = self.synthesize_scene(
                scene_id,
                narration,
                voice_id=voice_id,
                settings=settings,
                audio_dir=audio_dir,
                cache_dir=cache_dir,
                config=config,
                previous_request_ids=tuple(stitch_chain[-3:]),
            )
            if result.request_id:
                stitch_chain.append(result.request_id)
            scene_results.append(result)
            total_chars += result.character_count
            if result.cache_hit:
                cache_hits += 1
            else:
                billable_chars += result.character_count

        total_cost = round(billable_chars * config.rate_per_character_usd, 8)
        return {
            "scene_count": len(scene_results),
            "scenes": [result.to_dict() for result in scene_results],
            "total_chars": total_chars,
            "billable_chars": billable_chars,
            "cache_hits": cache_hits,
            "cache_misses": len(scene_results) - cache_hits,
            "cost_usd": total_cost,
            "voice_id": voice_id,
            "provider": "elevenlabs",
        }

    # ``synthesize`` is a compact alias useful to callers outside the pipeline
    # and keeps the service ergonomic in tests.
    synthesize = synthesize_storyboard

    def synthesize_scene(
        self,
        scene_id: int,
        narration: str,
        *,
        voice_id: str,
        settings: Mapping[str, Any],
        audio_dir: Path,
        cache_dir: Path,
        config: ElevenLabsConfig | None = None,
        previous_request_ids: tuple[str, ...] = (),
    ) -> SceneAudioResult:
        config = config or self.config or ElevenLabsConfig.from_env()
        self._validate_config(config)
        if not narration.strip():
            raise AudioSynthesisError(f"scene {scene_id} narration is empty")
        # Pause marks compile to provider break tags (doc 37 §1); the caption
        # text is the mark-free form.  The cache key uses the compiled text so
        # a pause edit re-synthesizes rather than reusing stale prosody.
        compiled = compile_pause_marks(narration)
        caption_text = strip_pause_markup(narration)
        if not caption_text:
            raise AudioSynthesisError(
                f"scene {scene_id} narration contains only pause markup"
            )
        cache_hash = _cache_key(voice_id, compiled, settings)
        cache_path = Path(cache_dir) / f"{cache_hash}.mp3"
        audio_path = Path(audio_dir) / f"scene_{scene_id}.mp3"
        words_path = Path(audio_dir) / f"scene_{scene_id}.words.json"
        cache_sidecar = cache_path.with_suffix(".words.json")

        request_id: str | None = None
        cache_hit = cache_path.exists()
        if cache_hit:
            try:
                audio_bytes = cache_path.read_bytes()
                words, duration_s = self._load_cached_words(
                    words_path,
                    cache_sidecar,
                    caption_text,
                )
            except AudioSynthesisError:
                # a cache entry that cannot validate is a MISS, never a
                # crash: drop it and resynthesize (2026-08-30 - the first
                # legit cache hit detonated a dormant strip bug and cost
                # a recording run)
                LOGGER.warning(
                    "cache entry failed validation - dropping %s", cache_path)
                cache_path.unlink(missing_ok=True)
                cache_sidecar.unlink(missing_ok=True)
                cache_hit = False
        else:
            payload, request_id = self._request_with_retries(
                voice_id=voice_id,
                narration=compiled,
                settings=settings,
                config=config,
                previous_request_ids=previous_request_ids,
            )
            audio_bytes = _decode_audio(payload)
            alignment = payload.get("alignment") or payload.get("normalized_alignment")
            if not isinstance(alignment, Mapping):
                raise AlignmentError("ElevenLabs response is missing alignment")
            words, duration_s = self._words_from_alignment(
                compiled,
                caption_text,
                alignment,
            )
            cache_path.write_bytes(audio_bytes)
            cache_sidecar.write_text(
                json.dumps(
                    {
                        "scene_id": int(scene_id),
                        "duration_s": duration_s,
                        "words": words,
                        "request_id": request_id,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

        # Copy cached/provider bytes into the run-local canonical path.  A
        # previous path from another job is never referenced directly.
        audio_path.write_bytes(audio_bytes)
        words_payload = {
            "scene_id": int(scene_id),
            "duration_s": float(duration_s),
            "words": words,
            "request_id": request_id,
        }
        words_path.write_text(
            json.dumps(words_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        cost = 0.0 if cache_hit else len(compiled) * config.rate_per_character_usd
        return SceneAudioResult(
            scene_id=int(scene_id),
            audio_path=audio_path,
            words_path=words_path,
            duration_s=float(duration_s),
            character_count=len(compiled),
            cache_hit=cache_hit,
            cost_usd=round(cost, 8),
            request_id=request_id,
        )

    @staticmethod
    def _words_from_alignment(
        compiled: str,
        caption_text: str,
        alignment: Mapping[str, Any],
    ) -> tuple[list[dict[str, Any]], float]:
        """Word timings for viewer-facing text, however the provider aligned.

        The provider may echo the break tags in its alignment or strip them
        first; both are reconciled here, and break-tag tokens never reach the
        caption-facing word list.
        """

        try:
            words, duration_s = group_word_timings(compiled, alignment)
        except AlignmentError:
            if compiled == caption_text:
                raise
            return group_word_timings(caption_text, alignment)
        skip = _pause_word_indices(compiled)
        if skip:
            words = [word for index, word in enumerate(words) if index not in skip]
        return words, duration_s

    def _load_cached_words(
        self,
        words_path: Path,
        cache_sidecar: Path,
        narration: str,
    ) -> tuple[list[dict[str, Any]], float]:
        """Load alignment metadata for a cache hit, with a deterministic fallback."""

        for candidate in (words_path, cache_sidecar):
            if not candidate.exists():
                continue
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8"))
                words = payload["words"]
                duration_s = float(payload["duration_s"])
                if not isinstance(words, list) or duration_s < 0:
                    raise ValueError
                cached_text = " ".join(
                    str(word["w"])
                    for word in words
                    if isinstance(word, Mapping) and word.get("w") is not None
                )
                if not cached_text or _normalise_text(cached_text) != _normalise_text(
                    narration
                ):
                    raise ValueError("cached words do not match narration")
                return words, duration_s
            except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
                LOGGER.warning("ignoring invalid cached word timing artifact: %s", candidate)

        raise AudioSynthesisError(
            "cached audio is missing a valid word-timing sidecar; "
            "remove the incomplete cache entry and rerun the stage"
        )

    def _request_with_retries(
        self,
        *,
        voice_id: str,
        narration: str,
        settings: Mapping[str, Any],
        config: ElevenLabsConfig,
        previous_request_ids: tuple[str, ...] = (),
    ) -> tuple[dict[str, Any], str | None]:
        endpoint = (
            config.base_url.rstrip("/")
            + "/text-to-speech/"
            + urllib.parse.quote(voice_id, safe="")
            + "/with-timestamps"
        )
        url = endpoint + "?" + urllib.parse.urlencode(
            {"output_format": config.output_format}
        )
        payload = {
            "text": narration,
            "model_id": config.model_id,
            "voice_settings": dict(settings),
            "apply_text_normalization": config.text_normalization,
        }
        if config.seed is not None:
            payload["seed"] = int(config.seed)
        if config.pronunciation_dictionary_locators:
            payload["pronunciation_dictionary_locators"] = [
                dict(locator) for locator in config.pronunciation_dictionary_locators
            ]
        if previous_request_ids:
            payload["previous_request_ids"] = list(previous_request_ids[-3:])
        last_error: Exception | None = None
        attempts = max(1, int(config.max_attempts))
        for attempt in range(1, attempts + 1):
            try:
                status, response_payload, response_headers = self._request_once(
                    url,
                    payload,
                    config=config,
                )
                if 200 <= status < 300:
                    return (
                        _decode_provider_payload(response_payload),
                        _request_id_from_headers(response_headers),
                    )
                error = AudioSynthesisError(
                    f"ElevenLabs request failed with HTTP {status}"
                )
                if status < 500:
                    raise error
                last_error = error
                if attempt < attempts:
                    self._sleep_fn(max(0.0, config.retry_backoff_s) * (2 ** (attempt - 1)))
                    continue
                break
            except urllib.error.HTTPError as exc:
                status = int(exc.code)
                body = ""
                try:
                    body = exc.read().decode("utf-8", errors="replace")
                except Exception:  # noqa: BLE001 - diagnostics are best effort
                    pass
                error = AudioSynthesisError(
                    f"ElevenLabs request failed with HTTP {status}"
                    + (f": {body[:300]}" if body else "")
                )
                if status < 500:
                    raise error from exc
                last_error = error
                if attempt < attempts:
                    self._sleep_fn(max(0.0, config.retry_backoff_s) * (2 ** (attempt - 1)))
                    continue
                break
            except (TimeoutError, socket.timeout, urllib.error.URLError) as exc:
                # ``URLError`` is only transient when it represents a timeout;
                # other transport failures are still retry-safe and fail closed
                # after the same bounded attempt count.
                last_error = AudioSynthesisError(f"ElevenLabs request timed out: {exc}")
                if attempt < attempts:
                    self._sleep_fn(max(0.0, config.retry_backoff_s) * (2 ** (attempt - 1)))
                    continue
                break
            except AudioSynthesisError:
                raise
            except Exception as exc:  # noqa: BLE001 - provider boundary
                last_error = AudioSynthesisError(f"ElevenLabs request failed: {exc}")
                if attempt < attempts:
                    self._sleep_fn(max(0.0, config.retry_backoff_s) * (2 ** (attempt - 1)))
                    continue
                break
        if last_error is None:
            last_error = AudioSynthesisError("ElevenLabs request failed")
        raise last_error

    def _request_once(
        self,
        url: str,
        payload: Mapping[str, Any],
        *,
        config: ElevenLabsConfig,
    ) -> tuple[int, Mapping[str, Any] | bytes, Mapping[str, str] | None]:
        headers = {
            "xi-api-key": str(config.api_key or ""),
            "Content-Type": "application/json",
            "Accept": "application/json",
            **dict(config.request_headers),
        }
        if self._request_fn is not None:
            # Canonical shape first; the fallback accommodates simple test
            # doubles and requests-like wrappers without any dependency.
            try:
                result = self._request_fn(
                    url,
                    headers=headers,
                    payload=payload,
                    timeout=config.timeout_s,
                )
            except TypeError:
                try:
                    result = self._request_fn(
                        url,
                        headers=headers,
                        json=payload,
                        timeout=config.timeout_s,
                    )
                except TypeError:
                    result = self._request_fn(url, payload, headers, config.timeout_s)
            return self._coerce_response(result)

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=config.timeout_s) as response:
            status_value = getattr(response, "status", None)
            if status_value is None:
                status_value = response.getcode()
            status = int(status_value)
            body = response.read()
            response_headers = dict(response.headers.items())
        return status, body, response_headers

    @staticmethod
    def _coerce_response(
        result: Any,
    ) -> tuple[int, Mapping[str, Any] | bytes, Mapping[str, str] | None]:
        if isinstance(result, tuple) and len(result) == 3:
            status, payload, headers = result
            return int(status), payload, headers
        if isinstance(result, tuple) and len(result) == 2:
            status, payload = result
            return int(status), payload, None
        if isinstance(result, Mapping) or isinstance(result, bytes):
            return 200, result, None
        status = int(getattr(result, "status_code", getattr(result, "status", 200)))
        headers = getattr(result, "headers", None)
        if hasattr(result, "json"):
            payload = result.json()
        elif hasattr(result, "content"):
            payload = result.content
        elif hasattr(result, "read"):
            payload = result.read()
        else:
            payload = result
        return status, payload, headers if isinstance(headers, Mapping) else None

    @staticmethod
    def _validate_config(config: ElevenLabsConfig) -> None:
        if not (config.api_key or "").strip():
            raise RuntimeError(
                "ELEVENLABS_API_KEY is required to synthesize audio; "
                "configure it before starting the synthesizing_audio stage"
            )
        if not str(config.base_url).strip():
            raise RuntimeError("ElevenLabs base_url must not be empty")
        if int(config.max_attempts) < 1:
            raise RuntimeError("ElevenLabs max_attempts must be at least 1")
        if config.text_normalization not in ("auto", "on", "off"):
            raise RuntimeError(
                "ElevenLabs text_normalization must be one of auto/on/off, "
                f"got {config.text_normalization!r}"
            )
        if len(config.pronunciation_dictionary_locators) > 3:
            raise RuntimeError(
                "ElevenLabs accepts at most 3 pronunciation dictionary locators "
                f"per request, got {len(config.pronunciation_dictionary_locators)}"
            )

    @staticmethod
    def _load_storyboard(job: VideoRun, ctx: StageContext) -> dict[str, Any]:
        candidates: list[Path] = [Path(ctx.job_dir) / "storyboard.json"]
        payload = getattr(job, "input_payload", {}) or {}
        for key in ("storyboard_path", "storyboard_file"):
            value = payload.get(key) if isinstance(payload, Mapping) else None
            if value:
                candidates.append(Path(value))
        source_ref = getattr(job, "source_ref", None)
        if source_ref:
            candidates.append(Path(source_ref))
        inline = payload.get("storyboard") if isinstance(payload, Mapping) else None
        if isinstance(inline, Mapping):
            return dict(inline)
        for candidate in candidates:
            try:
                if candidate.is_file():
                    loaded = json.loads(candidate.read_text(encoding="utf-8"))
                    if isinstance(loaded, Mapping):
                        return dict(loaded)
            except (OSError, json.JSONDecodeError) as exc:
                LOGGER.debug("unable to load storyboard candidate %s: %s", candidate, exc)
        raise AudioSynthesisError(
            "storyboard.json is required before synthesizing audio "
            f"(looked under {Path(ctx.job_dir)!s})"
        )


def run_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
    """Pipeline-compatible module-level stage function."""

    return AudioSynthService().run_stage(job, ctx)


__all__ = [
    "AlignmentError",
    "AudioSynthService",
    "AudioSynthesisError",
    "COST_PER_CHARACTER",
    "DEFAULT_ELEVENLABS_BASE_URL",
    "DEFAULT_ELEVENLABS_MODEL_ID",
    "DEFAULT_ELEVENLABS_OUTPUT_FORMAT",
    "ELEVENLABS_RATE_PER_CHARACTER_USD",
    "ElevenLabsConfig",
    "MAX_BREAK_TAGS_PER_SEGMENT",
    "PAUSE_MARK_BREAKS",
    "SceneAudioResult",
    "TTS_COST_PER_CHARACTER_USD",
    "compile_pause_marks",
    "group_word_timings",
    "run_stage",
    "strip_pause_markup",
]
