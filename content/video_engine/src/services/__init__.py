"""Video-engine service implementations.

The service modules intentionally have no import-time provider side effects.  A
stage validates its provider configuration when it is executed, which keeps
the package importable in local/test environments without credentials.
"""

from .audio_synth import (
    AudioSynthService,
    AudioSynthesisError,
    AlignmentError,
    ElevenLabsConfig,
    SceneAudioResult,
    group_word_timings,
    run_stage,
)
from .higgsfield_explainer import (
    ELEVENLABS_BLOCK_AUDIO_MANIFEST_VERSION,
    HIGGSFIELD_BLOCK_PLAN_VERSION,
    HIGGSFIELD_JOB_MANIFEST_VERSION,
    HIGGSFIELD_LOCAL_ASSEMBLY_MANIFEST_VERSION,
    HiggsfieldCli,
    HiggsfieldExplainerError,
    bind_canonical_audio_to_higgsfield_blocks,
    compile_audio_aligned_higgsfield_blocks,
    compile_higgsfield_blocks,
    compile_higgsfield_job_manifest,
    compile_higgsfield_local_assembly,
    preflight_higgsfield_models,
    record_higgsfield_output,
    record_higgsfield_task,
    resolve_elevenlabs_audio,
    validate_elevenlabs_block_audio_manifest,
    validate_higgsfield_blocks,
    validate_higgsfield_job_manifest,
)
from .history_narration import (
    CANONICAL_AUDIO_VERSION,
    HISTORY_NARRATION_VERSION,
    HistoryNarrationError,
    compile_history_narration,
    resolve_canonical_elevenlabs_audio,
    validate_canonical_audio,
    validate_history_narration,
)

__all__ = [
    "AlignmentError",
    "AudioSynthService",
    "AudioSynthesisError",
    "ElevenLabsConfig",
    "SceneAudioResult",
    "group_word_timings",
    "run_stage",
    "ELEVENLABS_BLOCK_AUDIO_MANIFEST_VERSION",
    "HIGGSFIELD_BLOCK_PLAN_VERSION",
    "HIGGSFIELD_JOB_MANIFEST_VERSION",
    "HIGGSFIELD_LOCAL_ASSEMBLY_MANIFEST_VERSION",
    "HiggsfieldCli",
    "HiggsfieldExplainerError",
    "bind_canonical_audio_to_higgsfield_blocks",
    "compile_audio_aligned_higgsfield_blocks",
    "compile_higgsfield_blocks",
    "compile_higgsfield_job_manifest",
    "compile_higgsfield_local_assembly",
    "preflight_higgsfield_models",
    "record_higgsfield_output",
    "record_higgsfield_task",
    "resolve_elevenlabs_audio",
    "validate_elevenlabs_block_audio_manifest",
    "validate_higgsfield_blocks",
    "validate_higgsfield_job_manifest",
    "CANONICAL_AUDIO_VERSION",
    "HISTORY_NARRATION_VERSION",
    "HistoryNarrationError",
    "compile_history_narration",
    "resolve_canonical_elevenlabs_audio",
    "validate_canonical_audio",
    "validate_history_narration",
]
