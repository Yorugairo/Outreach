---
id: P13-VIDEO-ENGINE-IMPLEMENTATION
title: Video Engine Implementation — Agent Work Packages
status: blocked
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-07-28
updated: 2026-07-28
---

# Plan: Video Engine Implementation — Agent Work Packages (P13 build)

## Summary

Implements P13 (`P13-CONTENT-VIDEO-FLYWHEEL.plan.md`) as **seven self-contained work packages
(WP-A…WP-G)** sized for delegation to developer agents (Opus/GPT class) working in parallel.
Every package carries its own interface contracts, codebase patterns, gotchas, and validation —
an agent should implement its package without searching the repo or asking questions.

## Intent And Acceptance

As the operator, I want the corpus→video pipeline built as parallel, contract-bounded work
packages, so multiple agents can develop it quickly without colliding, and I get the thin slice
(armbar-from-guard end-to-end) then the pilot season.

## Problem → Solution

Docs exist (`docs/content-video-engine/00–08` + `storyboard.schema.json`); no code exists.
→ `content/video_engine/` package implementing the 12-stage gated pipeline, validated by pytest
and one evidence-verified end-to-end run.

## Metadata

- **Complexity**: XL (split into 7 packages: 1 Large foundation, 1 Large render, 5 Medium)
- **Source PRD**: `docs/content-video-engine/01-PRD.md` (P0 phase) + `.claude/PRPs/plans/P13-CONTENT-VIDEO-FLYWHEEL.plan.md` (T1–T8 map onto WP-A…WP-G)
- **Estimated Files**: ~35 source + ~15 test files
- **UX**: N/A — operator-facing CLI + artifacts; no web UX

## Scope

Implement the importable `content/video_engine/` package, its deterministic pipeline,
guarded provider boundaries, render/assembly services, operator CLI, fixtures, and tests
defined by WP-A through WP-G.

## Human Gates

- This implementation request approves local code and test changes in the named worktree.
- Gate A and Gate B remain operator-only per-video approvals.
- Paid ElevenLabs calls, publishing, registry writes, deployment, and other external changes
  require separate explicit approval and are not authorized by this implementation request.

## Execution Path

WP-A lands first because it owns the frozen contracts and shared foundation. WP-B, WP-C, WP-D,
and WP-F then use disjoint write sets. WP-E follows the audio/render contracts, and parent-owned
WP-G integrates, verifies, and records evidence.

---

## ⚠ Path correction (supersedes doc spelling)

Docs say `content/video-engine/`. **Hyphenated directories are not importable Python packages;
pytest + `--cov` need imports.** The implementation root is:

```
content/video_engine/          # underscore — importable; "content-video-engine" stays the product label in docs
```

All docs references map 1:1 onto this root. Do not add a sys.path hack to keep the hyphen
(bjj-registry's flat-script pattern is not test-friendly; we follow the main `src/` package
pattern instead).

---

## Mandatory Reads

| Priority | File | Why |
|---|---|---|
| P0 | `docs/content-video-engine/03-SYSTEM-ARCHITECTURE.md` | The design this implements — stages, gates, continuity rendering |
| P0 | `docs/content-video-engine/storyboard.schema.json` | The v2 contract every package consumes |
| P0 | This file's **Interface Contracts** section | The boundaries between packages |
| P1 | `docs/content-video-engine/04-STORYBOARD-CONTRACT.md` | Worked example = canonical fixture |
| P1 | `docs/content-video-engine/06-SCRIPT-TRANSFORMATION-SPEC.md` | Arc/pacing/flow rules the guard enforces |
| P2 | `AGENTS.md` §5 | Evidence-first definition of done |
| P2 | `docs/content-video-engine/07-PILOT-SEASON.md` | What WP-G produces |

## External Documentation

| Topic | Source | Key takeaway |
|---|---|---|
| Manim CE | docs.manim.community (v0.20.x) | Python API render via `with tempconfig({...}): SceneClass().render()`; quality flags: `-ql`=854×480@15, `-qh`=1080p60; `Scene.next_section()` splits one scene into segment files |
| ElevenLabs | elevenlabs.io/docs — `POST /v1/text-to-speech/{voice_id}/with-timestamps` | Returns `audio_base64` + `alignment{characters[], character_start_times_seconds[], character_end_times_seconds[]}` — **character-level; word grouping is ours** |
| Loudness | ffmpeg `loudnorm` | Two-pass loudnorm to I=-14 LUFS; verify with `loudnorm print_format=json` second pass |
| MoviePy | zulko.github.io/moviepy | v2 API renamed (`with_audio`, `subclipped`); pin and code against the pinned major |

KEY_INSIGHT: audio precedes render — measured per-scene durations drive Manim (`03` §3).
APPLIES_TO: WP-C output contract, WP-D input contract.
GOTCHA: never stretch/trim audio to fit video; renderer asserts video duration = audio ±1%.

---

## Interface Contracts (the parallelization backbone — FROZEN before coding)

Agents build against these, not against each other's code.

1. **`storyboard.json`** — validates against `content/video_engine/configs/storyboard.schema.json`
   (copied verbatim from `docs/content-video-engine/storyboard.schema.json`). Canonical fixture:
   the worked example in `04-STORYBOARD-CONTRACT.md` §4, saved as
   `content/video_engine/tests/fixtures/armbar_storyboard.json`.
2. **Job artifact tree** — exactly as `03-SYSTEM-ARCHITECTURE.md` §4:
   `runtime/jobs/<job_id>/{job.json, events/*.json, storyboard.json, audio/, video/<profile>/, captions/, package/, qc/}`.
3. **`audio/scene_<id>.words.json`** (WP-C → WP-D/WP-E):
   `{"scene_id": int, "duration_s": float, "words": [{"w": str, "start_s": float, "end_s": float}]}`.
4. **Scene clip files** (WP-D → WP-E): `video/<profile>/scene_<id>.mp4` for cut scenes;
   `video/<profile>/seq_<firstid>-<lastid>.mp4` for continuous sequences; plus
   `video/<profile>/manifest.json`: `{"segments": [{"path": str, "scene_ids": [int], "duration_s": float}]}`.
5. **`VideoRun` / `VideoStageEvent`** dataclasses (WP-A, `models.py`) — fields mirror
   `InsightRun`/`RunStageEvent` shape: ids via `new_id()`-style uuid4 hex, ISO-8601 UTC
   timestamps, `status`, `input_payload`, `config_snapshot`, per-stage `output_summary: dict`.
6. **Stage function signature** (WP-A pipeline; all services implement):
   `def run_stage(job: VideoRun, ctx: StageContext) -> StageOutput` where `StageContext` carries
   repository, configs, job dir; `StageOutput.summary: dict` lands in the stage event.
7. **`qc/report.json`** (WP-B ← WP-E/WP-F inputs): `{"overall": "pass"|"fail", "checks": [{"check_id": str, "status": "pass"|"fail"|"skip", "detail": str}]}`.
8. **`package/metadata.json`** (WP-F): keys `titles[]`, `description` (UTM-resolved), `tags[]`,
   `chapters[]` (`{"start_s": float, "title": str}`), `disclosure: {"required": bool, "reason": str|null}`,
   `upload_checklist[]`. **`package/embed_payload.json`**: `{"source_slug": str, "target_page_slugs": [str], "video_object_jsonld": {…}, "youtube_url": null}`.

Change control: any contract change lands in THIS file first, then in affected packages.

---

## Patterns To Mirror

### VERSION_CONSTANTS + REGISTRY (models)
```python
# SOURCE: src/models.py:11,48-56
PROVIDER_CALL_CONTRACT_VERSION = "provider-calls.v1"
PRODUCT_SURFACE_VERSIONS = {
    "technical_seo_health": TECHNICAL_SEO_HEALTH_VERSION, ...
}
```
→ video engine: `STORYBOARD_CONTRACT_VERSION = "storyboard.v2"`, `VIDEO_PIPELINE_CONTRACT_VERSION = 1`,
`SCENE_CLASS_REGISTRY = {"StickFigureScene": {...}, ...}` (guard + renderer share it).

### STAGE LIST + ORDER (pipeline)
```python
# SOURCE: src/pipeline.py:53-60
DEFAULT_STAGES = [*V4_STAGES[:-1], "scoring_conversion_readiness", LEGACY_STAGES[-1]]
PIPELINE_CONTRACT_VERSION = 5
STAGE_ORDER = {stage: index + 1 for index, stage in enumerate(DEFAULT_STAGES)}
```

### RUN CREATION with config_snapshot (pipeline)
```python
# SOURCE: src/pipeline.py:88-118 (abridged)
run = InsightRun(..., input_payload={...}, config_snapshot={"pipeline_contract_version": PIPELINE_CONTRACT_VERSION, ...})
self.repository.create_run(run)
run.status = "running"; run.started_at = run.updated_at = self._now()
self.repository.update_run(run)
```

### REPOSITORY PROTOCOL
```python
# SOURCE: src/repositories/base.py:52-59
class InsightRepository(Protocol):
    def create_run(self, run: InsightRun) -> InsightRun: ...
    def update_run(self, run: InsightRun) -> InsightRun: ...
    def append_stage_event(self, event: RunStageEvent) -> RunStageEvent: ...
```
→ `VideoJobRepository(Protocol)` with `create_run/update_run/append_stage_event/load_run/list_runs`;
file-backed impl writes under `content/video_engine/runtime/jobs/`.

### GUARD RETURNS (ok, reason)
```python
# SOURCE: content/bjj-registry/src/llm_guard.py:24-27,44-48
def guard(bundle: dict, prose: str) -> tuple[bool, Optional[str]]:
    if not prose or not prose.strip():
        return False, "empty prose"
    ...
    return False, f"unsourced numeric value '{num}' in prose"
```
→ `storyboard_guard.guard(storyboard: dict) -> GuardResult` where
`GuardResult = (ok: bool, violations: list[str])` — collect ALL violations (Gate A shows the
full list), unlike llm_guard's first-failure return. Numeric/claims regex approach mirrors
`_NUMBER`/`_SCORE_HINT` (llm_guard.py:17-21) with the claims-ledger allowlist replacing the
bundle allowlist (llm_guard.py:39-48).

### LLM CONFIG FROM ENV
```python
# SOURCE: content/bjj-registry/src/llm_writer.py:31-49 (abridged)
@dataclass
class LLMConfig:
    provider: str = DEFAULT_PROVIDER
    model: str = DEFAULT_MODEL
    @classmethod
    def from_env(cls) -> "LLMConfig":
        provider = os.environ.get("LLM_PROVIDER", DEFAULT_PROVIDER).lower()
        key = os.environ.get("LLM_API_KEY") or os.environ.get(
            "OPENROUTER_API_KEY" if provider == "openrouter" else "OPENAI_API_KEY")
```
→ reuse verbatim shape for script-transform LLM; add `ElevenLabsConfig.from_env()` (key required
→ raise `RuntimeError` at stage start, not import time).

### SYSTEM PROMPT AS NUMBERED HARD RULES
```python
# SOURCE: content/bjj-registry/src/llm_writer.py:60-70
SECTION_SYSTEM = ("You are a black-belt ... Rules you MUST obey:\n"
    "1. Use ONLY the provided facts ... Never invent ...\n"
    "2. Do NOT print any numeric registry scores ...")
```
→ transform prompt embeds `06-SCRIPT-TRANSFORMATION-SPEC` rules as numbered MUSTs.

### CLI SHAPE
```python
# SOURCE: scripts/run_insight_pipeline.py:8-21
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
COMMANDS = {"run", "status", "inspect", "validate", "resume", "rerun", "diff"}
def _repo(artifact_root: str) -> FileBackedInsightRepository: ...
```
→ `content/video_engine/cli.py`, `COMMANDS = {"run", "resume", "status", "approve", "validate"}`
(bootstrap inserts the REPO root so `from content.video_engine.src...` imports work).

### TEST STRUCTURE (builders + determinism assertion)
```python
# SOURCE: tests/test_conversion_readiness.py:12-24,47-53
def _page(evidence: dict, *, page_class: str = "homepage") -> PageRecord: ...
def _evidence(**overrides):
    evidence = {...}; evidence.update(overrides); return evidence
def test_bjj_conversion_checks_are_vertical_aware_and_deterministic():
    first = ConversionReadinessService().build(pages, "national_bjj_registry.v1")
    second = ConversionReadinessService().build(pages, "national_bjj_registry.v1")
    assert first.to_dict() == second.to_dict()
```
→ tests live in `content/video_engine/tests/`, plain functions, `_storyboard(**overrides)`
builders, descriptive behavior names, determinism asserted the same way. Markers:
`@pytest.mark.render_smoke`, `@pytest.mark.assembly`, `@pytest.mark.integration` for slow tests.

### ENV EXAMPLE STYLE
```
# SOURCE: .env.example:1-6 — bare KEY= lines
```
→ append `ELEVENLABS_API_KEY=`, `ELEVENLABS_VOICE_ID=`, `LLM_*` noted as shared.

---

## Not Building

Upload API/OAuth · Gemini QC pre-screener (P1) · MCP server (P1) · recipe extractor (P1) ·
finance/trades content · parallel render farm · registry table writes · Windows-service/daemon
mode — CLI runs are foreground.

---

## Task Slices

> **Dependency graph:** WP-A → {WP-B, WP-C, WP-D, WP-F in parallel} → WP-E (needs C+D contracts,
> stubs fine) → WP-G (integration, needs all). Suggested agent class is advisory — contracts are
> what matter. Each package = one branch/session; merge order follows the graph.

### T1: WP-A — Foundation: configs, models, repository, pipeline, CLI
- Status: completed
- Owner: parent
- Depends on: plan approval
- **Agent**: Opus-class (architecture-shaping) · **Size**: Large · **Blocks**: everyone
- Write set: `content/video_engine/{__init__.py, cli.py, configs/{storyboard.schema.json, channels/combat-science.json, render_profiles.json}, src/{__init__.py, models.py, pipeline.py, repositories/{base.py, file_repository.py}}, tests/{test_configs.py, test_pipeline.py, fixtures/armbar_storyboard.json}, AGENTS.md}` + append `.gitignore` (`content/video_engine/runtime/`)
- **Tasks**:
  1. **ACTION** copy schema from docs; author channel + render-profile configs (values from `03` §6 table). **VALIDATE** `jsonschema` validates the armbar fixture.
  2. **ACTION** `models.py`: `VideoRun`, `VideoStageEvent`, `GateStatus`, version constants, `SCENE_CLASS_REGISTRY`. **MIRROR** VERSION_CONSTANTS + RUN CREATION. **GOTCHA** frozen dataclasses where practical (python rules); timestamps via injected `now_fn` for testability.
  3. **ACTION** `repositories/`: Protocol + file-backed (json files per contract #2, append-only events with zero-padded index prefix). **MIRROR** REPOSITORY PROTOCOL.
  4. **ACTION** `pipeline.py`: `STAGES` list incl. `awaiting_storyboard_approval`/`awaiting_publish_approval`; sequential executor; stages resolved from a `dict[str, StageFn]` so packages plug in; `resume` starts at first non-completed stage; gate stages park with `status="awaiting_gate_a|b"`; per-stage wall-time + `cost_usd` fields in `output_summary`. **MIRROR** STAGE LIST + RUN CREATION.
  5. **ACTION** `cli.py`: `run --source <path> [--channel combat-science] [--targets landscape,vertical]`, `resume <job_id>`, `status [job_id]`, `approve <job_id> --gate a|b`, `validate <storyboard.json>`. **MIRROR** CLI SHAPE.
- Acceptance: `python content/video_engine/cli.py run --source ...fixture...` with stub stages produces job.json + ordered events; resume/approve transitions verified by tests. **VALIDATE** `python -m pytest content/video_engine/tests/test_pipeline.py -q`
- Validate: `python -m pytest content/video_engine/tests/test_pipeline.py -q`
- Evidence: `python -m pytest content/video_engine/tests/test_configs.py content/video_engine/tests/test_pipeline.py -q` → 8 passed; CLI validation → `OK`; Gate-A job `.context/wpa-cli-evidence/86af45cc-15ff-4c6b-82ea-6f42b1151f52/job.json`

### T2: WP-B — Guards: `storyboard_guard.py` + `qc_checks.py`
- Status: completed
- Owner: implementation_luna
- Depends on: T1
- **Agent**: Opus-class (rule-dense, TDD) · **Size**: Medium · **Depends**: WP-A models/fixture
- Write set: `src/guards/{__init__.py, storyboard_guard.py, qc_checks.py}`, `tests/{test_storyboard_guard.py, test_qc_checks.py}`
- **Tasks** (RED first — write the violation table as tests, then implement):
  1. Schema validation (jsonschema, all errors collected).
  2. Claims: every 2+ digit number / medical / financial / superlative sentence in `narration_text` must map via `claim_refs` to a `verified: true` claim; ledger entries unreferenced by any scene → warning not violation. **MIRROR** GUARD RETURNS + `_NUMBER`/`_SCORE_HINT` regexes; years allowlisted as in llm_guard.py:43-46.
  3. Arc shape (hook first, cta last, ≥1 develop/payoff; conflict in first third + comeback pairing for runs >90s — compute from `timing.target_s` sums).
  4. Credential framing ban (regex `\b(doctor|surgeon|physician|therapist|economist)\b.*\b(explains|breaks down|reveals)\b` case-insensitive) without `expert`.
  5. Asset resolution against `SCENE_CLASS_REGISTRY` + `assets/poses/` listing; beats `action` prefixes (`pose:`, `map:`, `flash_label:`) must resolve.
  6. Pacing budgets + hard-cut count (>1 `hard_cut` per act → violation) + `realistic_recreation` ⇒ `disclosure.required`.
  7. `qc_checks.py`: duration drift ≤2% (manifest vs storyboard), words.json coverage, loudness field check (reads compositor's measured LUFS from its summary), caption file presence, metadata completeness (contract #8), silent-gap list from words.json (>500ms between scenes flagged).
- Acceptance: armbar fixture passes; each violation class has a failing fixture. **VALIDATE** `python -m pytest content/video_engine/tests/test_storyboard_guard.py -q`
- Validate: `python -m pytest content/video_engine/tests/test_storyboard_guard.py -q`
- Evidence: delegated diff independently reviewed; `python -m pytest content/video_engine/tests/test_storyboard_guard.py content/video_engine/tests/test_qc_checks.py -q` → 20 passed; parent integration aligned QC duration with audio padding.

### T3: WP-C — Audio: `services/audio_synth.py`
- Status: completed
- Owner: implementation_luna
- Depends on: T1
- **Agent**: GPT-class (API tooling) · **Size**: Medium · **Depends**: WP-A
- Write set: `src/services/{__init__.py, audio_synth.py}`, `tests/test_audio_synth.py`
- **Tasks**:
  1. `ElevenLabsConfig.from_env()` (**MIRROR** LLM CONFIG FROM ENV); fail-fast RuntimeError at stage start if key missing.
  2. Per-scene POST `with-timestamps`; decode base64 mp3 → `audio/scene_<id>.mp3`; char→word grouping: split narration on whitespace, walk `characters[]` accumulating boundaries; emit contract #3. **GOTCHA** alignment includes spaces/punctuation as characters — group on the narration's own tokenization, not the characters array alone; assert reconstructed text == narration (normalized).
  3. Cache: `sha256(voice_id + "|" + narration_text + "|" + json.dumps(settings, sort_keys=True))` → skip synth when `audio/.cache/<hash>.mp3` exists.
  4. Retry ×3 exponential backoff on 5xx/timeout; 4xx → fail stage with reason in event. No fallback voice ever.
  5. Record `cost_usd` estimate (chars × rate constant) in `StageOutput.summary`.
- Acceptance: mocked-API tests green incl. cache hits, retry, grouping edge cases (multi-space, em-dash, unicode). **VALIDATE** `python -m pytest content/video_engine/tests/test_audio_synth.py -q`
- Validate: `python -m pytest content/video_engine/tests/test_audio_synth.py -q`
- Evidence: delegated implementation independently reviewed; official ElevenLabs contract verified (`output_format` query parameter); `python -m pytest content/video_engine/tests/test_audio_synth.py -q` → 9 passed, including fail-closed incomplete-cache behavior.

### T4: WP-D — Scenes + Render: `scenes/*` + `services/manim_render.py`
- Status: completed
- Owner: implementation_luna
- Depends on: T1
- **Agent**: GPT-class (Manim-heavy; largest creative-code surface) · **Size**: Large · **Depends**: WP-A (configs, registry); words.json contract only from WP-C
- Write set: `src/scenes/{__init__.py, base.py, stick_figure.py, title_card.py, joint_leverage.py, map_network.py}`, `src/assets/poses/*.svg` (initial: `closed_guard, armbar_extension, arm_yank_fail, tap_frantic, posture_broken, gym_enforcer, bowler_hat_maeda`), `src/services/manim_render.py`, `tests/{test_scene_contracts.py, test_manim_render.py}`
- **Tasks**:
  1. `ThemedScene(base)`: reads theme + aspect frame config (`config.frame_width/height` via `tempconfig`); enforces **entrance contract** — subclasses implement `entrance()` and `body(audio_duration: float)`; base asserts first animation starts ≤0.5s; helper `pace_to(duration)` scales `self.play` run_times to fill `audio_duration` exactly.
  2. Scene classes take `(scene_spec: dict, layout: str, audio_duration: float, theme: dict)`; poses loaded from SVG via `SVGMobject`; beats schedule mid-scene actions at word-time offsets (from words.json passed in scene_spec at render time).
  3. `manim_render.py`: groups consecutive `transition.in == "continuous"` scenes with compatible classes into one render unit using `self.next_section()` per storyboard scene (segment files = contract #4 `seq_*.mp4`); renders via Python API under `tempconfig` (draft/final ladder from `render_profiles.json`); **never shell strings** (Windows host — pathlib everywhere). **GOTCHA** `-ql`≡854×480@15 draft only; final = 1080p60 landscape / 1080×1920@30 vertical; Manim caches partial movie files — set distinct `media_dir` per job to avoid cross-job cache bleed.
  4. Post-render assertion: ffprobe duration vs audio_duration ±1% per unit; mismatch → stage fail listing scene ids. Emit manifest (contract #4).
  5. Determinism: no `random` without fixed seed from job_id; no wall-clock in scene code.
- Acceptance: `@pytest.mark.render_smoke` renders armbar scenes 1-2 landscape_draft headless; contract tests (fast) verify pacing math, grouping logic, entrance enforcement without rendering. **VALIDATE** `python -m pytest content/video_engine/tests -q -m "not render_smoke"` then `-m render_smoke` locally
- Validate: `python -m pytest content/video_engine/tests/test_scene_contracts.py content/video_engine/tests/test_manim_render.py -q -m "not render_smoke"`
- Evidence: delegated diff independently reviewed; fast scene/render contracts → 11 passed. Manim Community 0.20.1 is installed in the project `.venv`; the real two-scene `landscape_draft` smoke → 2 passed. Installing Manim exposed and led to correction of a `Scene.wait` redispatch bug that truncated the audio clock. Durable render evidence: `.context/p13-review/manim-smoke/video/landscape_draft/seq_1-2.mp4` (854×480, 15fps, 12.066667s; expected 12.0s, within 1%).

### T5: WP-E — Assembly: `services/compositor.py` + `services/captions.py`
- Status: completed
- Owner: parent
- Depends on: T3, T4
- Write set: `content/video_engine/src/services/{compositor.py,captions.py}`, `content/video_engine/tests/test_compositor.py`
- **Agent**: GPT-class (ffmpeg/moviepy) · **Size**: Medium · **Depends**: contracts #3/#4 (stub inputs fine until WP-C/D merge)
- **Tasks**:
  1. Concat manifest segments per profile honoring `transition.in` (`crossfade` 0.3s default, `match_cut`/`hard_cut` straight cut) — continuous scenes are already single files.
  2. Narration track laid at per-scene offsets (cumulative durations + `padding_s`); music bed continuous full-length at −18dB rel voice, ducking optional flag; two-pass ffmpeg `loudnorm` to −14 LUFS; write measured integrated LUFS into `StageOutput.summary` (WP-B qc reads it).
  3. `captions.py`: words.json → grouped caption lines (≤3 words/line vertical, ≤7 landscape, gaps ≥80ms merge-safe); burn on vertical via subtitles filter within safe-zone margins; sidecar `.srt` landscape.
  4. ffprobe final duration vs storyboard sum ≤2%.
- Acceptance: `@pytest.mark.assembly` produces both finals from fixture segments (tiny synthetic mp4s in tests/fixtures) + srt/burned check via ffprobe stream inspection. **VALIDATE** `python -m pytest content/video_engine/tests/test_compositor.py -q -m assembly`
- Validate: `python -m pytest content/video_engine/tests/test_compositor.py -q`
- Evidence: `python -m pytest content/video_engine/tests/test_compositor.py -q` → 5 passed, including local FFmpeg/ffprobe assembly, two-pass loudnorm, duration enforcement, caption grouping, and crossfade timeline preservation.

### T6: WP-F — Packaging + Publish (manual mode): `services/packaging.py` + `services/publish.py`
- Status: completed
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/src/services/{packaging.py,publish.py}`, `content/video_engine/tests/test_packaging.py`
- **Agent**: GPT-class · **Size**: Medium · **Depends**: WP-A
- **Tasks**:
  1. Thumbnails: render TitleConceptCard stills (reuse WP-D class in image mode) per `thumbnail.variant_texts`.
  2. `metadata.json` (contract #8): UTM injection `{ARTICLE_URL}`/`{REGISTRY_URL}` → `utm_source=youtube&utm_medium=longform&utm_campaign=<job_slug>`; chapters from cumulative scene times at act boundaries; disclosure passthrough from storyboard determination.
  3. `embed_payload.json`: `VideoObject` JSON-LD (name from titles[0], description, thumbnailUrl placeholder, uploadDate null until publish, duration ISO-8601 `PT#M#S`); target slugs = technique slug + taught_at city slugs from source corpus record.
  4. `publish.py` v1: emit `upload_checklist` (title variant choice, disclosure toggle **only if** `disclosure.required`, spacing rule reminder ≥48h, playlist/lane badge) and mark run `packaged`; Gate B approval → `published` only via `cli approve`.
- Acceptance: metadata/embed payloads schema-checked in tests; UTM links parse. **VALIDATE** `python -m pytest content/video_engine/tests/test_packaging.py -q`
- Validate: `python -m pytest content/video_engine/tests/test_packaging.py -q`
- Evidence: `python -m pytest content/video_engine/tests/test_packaging.py -q` → 4 passed; metadata, UTM links, JSON-LD embed payload, 1280×720 `TitleConceptCard` thumbnail stills, conditional disclosure checklist, and Gate-B/QC publish guard verified. Visual evidence: `.context/p13-review/thumbnail.png`.

### T7: WP-G — Integration + thin-slice evidence + pilot enablement
- Status: blocked
- Owner: parent
- Depends on: T2, T3, T4, T5, T6
- Write set: `content/video_engine/src/{pipeline.py,services/ingest.py,services/script_transform.py,services/storyboard_build.py}`, `content/video_engine/content_queue/`, `.env.example`, P13 plans, integration tests
- **Agent**: Opus-class (integrator; owns merge order) · **Size**: Medium · **Depends**: all
- **Tasks**:
  1. Register real stage fns into pipeline dict; wire `transforming_script` deterministic corpus path (transcript steps → beats per `06` §3; LLM rewording optional behind `LLM_API_KEY` presence, guarded).
  2. Full run on `content/bjj-registry/corpus/armbar-from-guard.json` through both gates (operator approves via CLI) → verify **every** DoD artifact (`03` §9) on disk; store evidence paths in P13 T-slices.
  3. Cost/wall-time table printed by `cli status <job_id>`; coverage run; `.env.example` additions; update `P13-CONTENT-VIDEO-FLYWHEEL.plan.md` slice statuses + Evidence lines.
  4. Author pilot storyboard for E5 (Open Mat Survival Guide) as the first Gate A candidate.
- Acceptance: evidence-verified end-to-end run; `pytest content/video_engine/tests -q` green; coverage ≥80% on guards/services/pipeline (render/assembly marks excluded). **VALIDATE** `python -m pytest content/video_engine/tests --cov=content/video_engine/src --cov-report=term-missing -m "not render_smoke and not assembly"`
- Validate: `python -m pytest content/video_engine/tests --cov=content/video_engine/src --cov-report=term-missing -m "not render_smoke and not assembly"`
- Evidence: real local CLI job `.context/wpg-cli-evidence/1687b272-eb0f-4bb1-aa3f-ee534ecf7991/job.json` completed ingest/transform/storyboard, Gate A approval, ElevenLabs audio, both Manim profiles, compositing, captions, packaging, and QC; it is now parked at Gate B with `qc/report.json` overall `pass`. ElevenLabs recorded one bounded generation of 846 billable characters at `$0.1692`; no second provider call was made during local compositor retries. Video-engine tests → **86 passed**; full repository suite is **519 passed**. The remaining provider-backed DoD blocker is operator Gate B review/publication approval. E5 is not fabricated because no Open Mat Survival Guide source record exists in the repository.

---

## Testing Strategy

| Layer | Tests | Marker |
|---|---|---|
| Unit (fast, CI-default) | guard violations table, word grouping, pacing math, sequence grouping, UTM/chapters, repository round-trip, resume logic | none |
| Render smoke | 2-scene draft render, entrance/duration assertions | `render_smoke` |
| Assembly | concat + audio mix + captions on synthetic fixtures | `assembly` |
| Integration | full pipeline with mocked TTS + draft renders | `integration` |

Edge cases: empty scenes array (schema rejects) · storyboard >90s missing conflict · claim id referenced but absent · unicode/em-dash narration grouping · scene audio 0.4s (< min_s) · vertical safe-zone overflow · cache-hit after storyboard edit (only edited scene re-synths) · resume mid-render after kill · approve wrong gate.

## Validation Commands (project-wide)

```bash
python -m pytest content/video_engine/tests -q -m "not render_smoke and not assembly"
```
EXPECT: green, <60s, no network.
```bash
python -m pytest content/video_engine/tests --cov=content/video_engine/src --cov-report=term-missing -m "not render_smoke and not assembly"
```
EXPECT: ≥80% on guards/services/pipeline.
```bash
python -m json.tool content/video_engine/configs/storyboard.schema.json > /dev/null
```
EXPECT: parses.
```bash
python content/video_engine/cli.py validate content/video_engine/tests/fixtures/armbar_storyboard.json
```
EXPECT: `OK` + zero violations.

## Acceptance Criteria
- [x] All 7 packages merged in dependency order; unit suite green; coverage ≥80% (fast tests)
- [ ] Evidence-verified armbar end-to-end run (DoD `03` §9 artifacts on disk)
- [ ] E5 pilot storyboard authored and guard-passing, parked at Gate A
- [x] P13 slice statuses + Evidence fields updated

## Verification

Run the focused command recorded on each task slice before the full fast suite and coverage
gate. Slow render and assembly checks remain explicit local gates.

## Evidence And Handoff

Record exact commands, test counts, job IDs, and artifact paths on each task slice and in
`P13-CONTENT-VIDEO-FLYWHEEL.plan.md`. Do not claim provider-backed or publish evidence without
the separately authorized external action.

## Blockers

- Complete Gate B as the human operator; automated tests do not substitute for the final
  landscape/vertical review or publication approval.
- Provide the E5 source record/corpus inventory before authoring a claims-safe pilot storyboard.

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Manim section API friction for continuous sequences | Medium | High (flow guarantee) | WP-D task 3 spikes it first on 2 scenes; fallback = per-scene renders + compositor crossfades (flow degrades gracefully, contract unchanged) |
| MoviePy v1/v2 API drift | Medium | Medium | Pin version in WP-E; code to pinned major |
| ElevenLabs alignment quirks (punctuation/space chars) | Medium | Medium | WP-C reconstruction assertion catches drift at synth time |
| Windows ffmpeg/loudnorm availability | Low | Medium | WP-E preflight check with actionable error naming the binary |
| Agent contract drift across packages | Medium | High | Contracts frozen in this file; WP-G integrator owns changes |

## Notes
- Repo formatting: black/isort/ruff per python rules; type annotations on all signatures;
  prefer frozen dataclasses; no `print()` in library code (logging), CLI output excepted.
- Secrets only via env; `.env.example` gets empty-value keys (style: `.env.example:1-6`).
- Original phase plan (`P13-CONTENT-VIDEO-FLYWHEEL.plan.md`) remains the status ledger; this
  file is the implementation spec. T1→WP-A, T2→WP-A, T3→WP-B, T4→WP-C, T5→WP-D, T6→WP-E,
  T7→WP-F(+WP-B qc), T8→WP-G.

## Confidence Score
**8/10** for single-pass implementation per package — contracts and patterns are fully specified;
the two open-texture areas (Manim section behavior, loudnorm two-pass plumbing) have explicit
spike-first tasks and graceful fallbacks.
