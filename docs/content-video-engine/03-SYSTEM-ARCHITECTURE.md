# Content-to-Video Engine — System Architecture

> **V4 architecture overlay:** V1–V3 remain resumable. New History V4 jobs use the
> pipeline and contracts below; they never enter the legacy technique-manifest
> stage and may not resolve `StickFigureScene`.

## V4 history pipeline

```text
history episode intake
→ research validation
→ asset resolution and rights validation
→ research review packet
→ Research Gate
→ editorial_coverage.v1
→ quarantined stock candidates and contact sheet
→ Asset Selection Gate
→ selected asset download, hash, and manifest promotion
→ documentary script transformation
→ art-direction resolution
→ documentary shot plan
→ visual treatments
→ Storyboard 2.3
→ six-frame style board
→ Visual Direction Gate
→ motion animatic
→ Gate A
→ narration and final rendering
→ documentary QC
→ Gate B
```

`research_packet.v1`, `asset_manifest.v1`, and `art_bible.v2` are independently
hashed. `shot_plan.v3`, `visual_treatment.v2`, and Storyboard 2.2 capture those
immutable hashes. Renderer-facing treatments receive approved asset IDs only.
Research URLs, study sources, consultant text, and unresolved asset paths are
invalid renderer inputs. Remotion owns editorial assembly, citations, captions,
and credits; Manim owns maps, timelines, relationship graphs, and concept diagrams.

Gate states are independent and ordered. A stale upstream hash invalidates every
downstream approval. See [`README.md`](README.md) for authoritative rule ownership.

*Date: 2026-07-28 · Status: draft for operator review · Parent: `00-BRAINSTORM-AND-DECISIONS.md` · Contract: `04-STORYBOARD-CONTRACT.md` + `storyboard.schema.json`*

The video engine adds a **render axis** to the existing corpus-driven content system. It converts
approved source content (technique corpus records, registry blog articles, essays dropped in a
queue) into finished landscape + vertical videos with captions, packaging metadata, and registry
embed payloads — through a run-centric, stage-evented pipeline with two human gates.

Design principles are inherited from this repo, not invented:

| Principle | Source precedent |
|---|---|
| Run-centric, stage events persisted per job | `src/pipeline.py` (`InsightRunPipeline`, `RunStageEvent`) |
| Deterministic before generative; guarded LLM steps with fallback | `content/bjj-registry/src/llm_writer.py` + `llm_guard.py` |
| Human gate before anything publishes | Import gate in `content/bjj-registry/README.md` |
| Evidence-first definition of done (artifacts on disk, not claims) | `AGENTS.md` §5 |
| Repository abstraction; file-backed store first, DB later | `src/repositories/` |
| Model-agnostic LLM stages via env vars (OpenRouter-first) | `llm_writer.py` env contract |

---

## 1. System context

```
                       ┌────────────────────────────────────────────┐
   SOURCES             │            VIDEO ENGINE (this doc)         │           DESTINATIONS
                       │                                            │
 corpus/*.json ──────► │ ingest → script → storyboard ─[GATE A]─►   │ ──► YouTube (manual upload v1,
 registry blog md ───► │   TTS → render → composite → captions →    │      API in Phase 2)
 content_queue/*.md ─► │   package → QC ─[GATE B]─► publish/embed   │ ──► Registry page embeds
                       │                                            │      (VideoObject JSON-LD)
                       └────────────────────────────────────────────┘
```

The engine never invents content: sources are the fact layer. For corpus records the storyboard
has a **deterministic floor** (transcript steps → scene beats, no LLM required); for essays the
script transformation is LLM-assisted but guarded (§7).

---

## 2. Monorepo layout

The operator's draft proposed a standalone `video-flywheel/` tree with `tools/*.py` and a root
`orchestrator.py`. Kept: `content_queue/`, `runtime/jobs/`, the three tool responsibilities, the
schema-first config. Changed: flat scripts become **services under a single pipeline**, mirroring
`src/services/` — same responsibilities, repo-native shape.

```
content/video-engine/
├── configs/
│   ├── storyboard.schema.json        # canonical v2 contract (checked in, versioned)
│   ├── channels/combat-science.json  # per-channel: theme colors, voice_id, CTA set, badge color
│   └── render_profiles.json          # draft/final ladders per aspect (see §6)
├── content_queue/                    # inbox: .md posts or corpus-ref .json awaiting a run
├── src/
│   ├── models.py                     # VideoRun, VideoStageEvent, Claim, SceneSpec dataclasses
│   ├── pipeline.py                   # single orchestrator — sequences stages, records events
│   ├── repositories/                 # file-backed job store (Protocol, mirrors src/repositories)
│   ├── services/
│   │   ├── ingest.py                 # queue intake; parse md/corpus; build SourceBundle
│   │   ├── script_transform.py       # essay → beat sheet (LLM, guarded; corpus → deterministic)
│   │   ├── storyboard_build.py       # beat sheet → storyboard.json (schema-validated + guarded)
│   │   ├── audio_synth.py            # ElevenLabs with-timestamps → per-scene mp3 + word timings
│   │   ├── manim_render.py           # headless per-scene renders, duration-locked to audio
│   │   ├── compositor.py             # MoviePy/FFmpeg assembly per aspect profile
│   │   ├── captions.py               # word timings → burned captions (9:16) / .srt (16:9)
│   │   ├── packaging.py              # thumbnail render, titles/desc/tags, UTM links, chapters
│   │   └── publish.py                # v1: emits upload checklist + embed payload; v2: YouTube API
│   ├── scenes/                       # Manim CE scene-class library (the only place Manim lives)
│   │   ├── base.py                   # ThemedScene: palette, fonts, aspect frames, first-0.5s motion contract
│   │   ├── bjj_action.py             # BJJActionScene: color-coded cast + articulated state changes
│   │   ├── stick_figure.py           # legacy/simple cast scene; not used for intertwined limbs
│   │   ├── joint_leverage.py         # JointLeverageScene (levers, fulcrums, torque vectors)
│   │   ├── map_network.py            # MapNetworkScene (geo nodes, migration lines)
│   │   └── title_card.py            # TitleConceptCard (titles, stat cards)
│   ├── assets/cast/                  # anchorable practitioner parts and color-coded gi/belt variants
│   ├── assets/poses/                 # reviewed pose/reference assets, not arbitrary generated limbs
│   ├── assets/diagrams/              # frames, wedges, levers, arrows, wrong/right overlays
│   ├── assets/references/            # licensed operator-supplied pose/video references + provenance
│   └── guards/
│       ├── storyboard_guard.py       # claims ledger + banned framing + budget checks (§7)
│       └── qc_checks.py              # automated QC before Gate B (§8)
├── runtime/jobs/<job_id>/            # per-run artifacts (gitignored; layout in §4)
├── AGENTS.md                         # subtree guardrails for any agent working here
└── cli.py                            # one entrypoint: run / resume / status / approve
```

Mapping from the operator draft: `tools/audio_synth.py` → `services/audio_synth.py`,
`tools/manim_render_engine.py` → `services/manim_render.py` + `scenes/`,
`tools/video_compositor.py` → `services/compositor.py`, `orchestrator.py` → `pipeline.py` + `cli.py`,
`configs/schema_contract.json` → `configs/storyboard.schema.json`, `CLAUDE.md` → `AGENTS.md`
(repo already standardizes on AGENTS.md as the always-loaded layer).

---

## 3. Pipeline stages

```python
DEFAULT_STAGES = [
    "ingesting_source",        # SourceBundle from queue item / corpus ref
    "transforming_script",     # beat sheet per 06-SCRIPT-TRANSFORMATION-SPEC
    "building_storyboard",     # storyboard.json — schema-valid + guard-passed
    "awaiting_storyboard_approval",   # ── GATE A (human, ~5-10 min)
    "synthesizing_audio",      # per-scene TTS + word timestamps  ← runs BEFORE render
    "rendering_scenes",        # Manim, duration-locked, per aspect profile
    "compositing",             # concat + audio + music bed per aspect
    "generating_captions",     # burned (9:16) / sidecar .srt (16:9)
    "packaging",               # thumbnails, metadata, UTM links, chapters, embed payload
    "running_qc",              # automated checks (§8)
    "awaiting_publish_approval",      # ── GATE B (human, ~5 min)
    "publishing",              # v1 checklist emit; v2 API upload + registry embed enqueue
]
```

Every stage emits a `VideoStageEvent` (`stage_name`, `status`, `started_at`, `completed_at`,
`output_summary`) persisted to `runtime/jobs/<job_id>/events/` — same contract as
`RunStageEvent`. Gates are modeled as stages that park the run in `awaiting_*` status; `cli.py
approve <job_id> --gate a|b` (or editing then re-validating the storyboard) resumes it. A run is
never "done" by assertion: the DoD is files on disk (§9).

**Graduated autonomy (design goal: minimize human-in-the-loop without removing judgment).**
Gate friction must trend toward seconds: pilot = full review at both gates; P1 = exception-based
Gate A (auto-approve when guard is green AND a model-scored rubric clears the operator-set
threshold — humans see only flagged storyboards) plus a `review_model` Gate-B pre-screen
(Gemini video understanding watches the assembled final against the rubric for ~$0.02–0.23 per
5-min video — see `08-TOOLING-ALTERNATIVES.md` §2, calibrated against human review during the
pilot); P2 = sampled Gate B (spot-check rate the operator ratchets down as trust accumulates). Gates are never *removed* — publishes stay
human-accountable — but per-video review time is a pilot posture, not a permanent tax.

Editorial authority is independent of gate latency. AI may propose and execute against an angle
brief, but the operator owns the thesis and source selection. Exception-based Gate A may approve
only a storyboard derived from an operator-approved brief; it may not autonomously choose or
change the channel's point of view.

The three-video pre-launch buffer is a **release-queue policy**, not a thirteenth per-run stage:
P0 uses the operator checklist in `07-PILOT-SEASON.md` §2.1; a later publish queue may count
persisted Gate-B-approved/package-complete runs before enabling the first external upload.

**Why TTS precedes render (timing inversion).** Narration audio length is unknowable until
synthesized; animation length is fully controllable. So audio is the clock: each scene's measured
audio duration (+ configured padding) is passed to its Manim scene as `audio_duration`, and the
scene scales its animation plan to fit. Rendering first would mean re-rendering every time the
voice track drifts — the expensive stage would absorb the error instead of the cheap one.

---

## 4. Job artifact layout (`runtime/jobs/<job_id>/`)

```
job.json                    # VideoRun: status, source ref, storyboard path, config snapshot
events/*.json               # stage events (append-only)
storyboard.json             # the approved contract (edits at Gate A land here, re-validated)
audio/scene_<id>.mp3        # per-scene narration
audio/scene_<id>.words.json # word-level [word, start_s, end_s] arrays from character timings
video/<profile>/scene_<id>.mp4
video/<profile>/draft.mp4   # Gate A preview render (draft ladder)
video/<profile>/final.mp4
captions/<profile>.srt      # + burned into vertical final
package/thumbnail_<variant>.png
package/metadata.json       # titles[], description (UTM'd), tags, chapters, disclosure flags
package/embed_payload.json  # registry page slugs + VideoObject JSON-LD block
qc/report.json              # automated QC results (§8)
```

TTS results are cached by `sha256(voice_id + narration_text + voice_settings)` — storyboard edits
at Gate A only re-synthesize changed scenes. Renders are cached by scene-spec hash per profile.
Idempotent stages + persisted events = `cli.py resume <job_id>` restarts at the first incomplete
stage after any crash.

---

## 5. Service specs (the operator's three tools, hardened)

**`audio_synth.py`** — calls ElevenLabs `POST /v1/text-to-speech/{voice_id}/with-timestamps` per
scene; aggregates character start/end times into word-level arrays; writes mp3 + words.json.
Voice settings (stability/style) come from channel config, not code. Failure: retry w/ backoff
(3×); on hard failure the run fails at this stage with the event recorded — never silently
substitutes a different voice. Validates `ELEVENLABS_API_KEY` at startup (repo security rule).
The video CLI loads provider settings from the repository-root `.env` on every invocation;
already-set process environment variables take precedence.
The words.json format is the input contract for `captions.py` — no re-transcription step exists.

**`manim_render.py`** — renders each scene headlessly via the Manim CE Python API (not shell
strings), passing `audio_duration`, aspect frame config, and theme. One correction to the draft
spec: `manim -ql` is **draft quality (854×480@15fps)** in Manim CE — `-ql --fps 60` is a
contradiction. The ladder in `render_profiles.json` (§6) uses draft quality for Gate A previews
and `-qh`-equivalent (1080p60) for finals. Scene classes must respect `audio_duration` exactly;
the renderer asserts output duration within tolerance (±1%) and fails the scene otherwise.

**`compositor.py`** — MoviePy/FFmpeg: concat scene clips per profile, lay narration track, mix
music bed at **−18 dB relative to voice** with sidechain-style ducking optional, normalize to
**−14 LUFS integrated** (YouTube's loudness target), export finals. One strategic correction to
the draft: **no blurred-background padding of 16:9 into 9:16.** Blur-padding is the visually
recognizable low-effort pattern the operator's own "3 Golden Rules" forbid (Rule 1: no
recognizable generic canvas). Vertical is a first-class layout, not a crop (§6).

### 5.1 Technique visual system (P13 v2)

The first Armbar render exposed a contract gap: a narration beat can pass schema validation while
remaining visually generic. Technique scenes therefore use a `BJJActionScene` contract instead of
the legacy `StickFigureScene`:

```json
{
  "shot": "grip_closeup",
  "cast": {"attacker": "white_gi_blue_belt", "defender": "black_gi_purple_belt"},
  "state_from": "closed_guard_posture_broken",
  "action": "two_on_one_wrist_control",
  "state_to": "wrist_control_hip_frame",
  "camera": {"move": "push_in", "focus": "attacker_wrist"},
  "overlays": ["wrist_lock", "hip_frame_arrow"]
}
```

Required properties:

1. **Anchored cast** — two practitioners have persistent IDs, opposing gi/belt colors, separate
   depth layers, and reviewed body-part assets. White-line overlap is never treated as anatomy.
2. **State change** — every instructional clause names a before/after position or a conceptual
   diagram. A scene that only changes narration fails the visual-beat guard.
3. **Shot coverage** — each 30–60 second explainer includes wide setup, one or more grip/hip
   cut-ins, a transition shot, a wrong/right contrast, and a force/leverage diagram where relevant.
4. **Reference provenance** — complex positions may use operator-supplied or licensed pose/video
   references, recorded in `assets/references/` with source and permission metadata.
5. **Generative boundary** — image/video models may propose keyframes or short atmospheric cut-ins;
   they do not author limb placement, technique correctness, or safety-critical visuals. Manim/2D
   vector assets remain the source of truth for instructional mechanics.

The storyboard guard and QC must reject repeated pose-only beats, missing `state_from`/`state_to`,
unresolved cast IDs, and a visual-change interval above the lane's configured budget.

---

## 6. Dual-format rendering (9:16 is a layout, not a crop)

`render_profiles.json`:

| Profile | Resolution | FPS | Use |
|---|---|---|---|
| `landscape_draft` | 854×480 | 15 | Gate A preview |
| `landscape_final` | 1920×1080 | 60 | YouTube long-form |
| `vertical_draft` | 480×854 | 15 | Gate A preview (only when shorts planned) |
| `vertical_final` | 1080×1920 | 30 | Shorts/Reels (30fps halves render cost; motion here is simple) |

`ThemedScene` (`scenes/base.py`) reads the aspect from frame config and lays out accordingly:
vertical stacks title-zone / action-zone / caption-zone; landscape uses left-diagram/right-figure
composition. Scene classes receive per-aspect `layout_hints` from the storyboard rather than
branching internally. Shorts are **selected scene subsets** (the storyboard's `shorts[]` plans,
each with its own hook line), re-rendered vertically — not center-cuts of the landscape master.

**Sequence rendering (anti-random-cut).** Consecutive scenes whose `transition.in` is
`continuous` and whose classes are compatible render as **one** Manim scene using the section
API — motion, camera, and cast genuinely carry across storyboard-scene boundaries instead of
hard-cutting. The compositor honors `crossfade`/`match_cut`/`hard_cut` only where the storyboard
says so, keeps the music bed continuous across the entire video, and carries `transition.motif`
elements across cut boundaries. Story flow is a render-level guarantee, not an editing hope.

---

## 7. Guards (the no-slop enforcement layer)

`storyboard_guard.py` runs before Gate A and again after any Gate A edit. Extends the
`llm_guard.py` philosophy (model may reword, never author facts):

1. **Schema validation** against `storyboard.schema.json` (hard fail).
2. **Claims ledger enforcement** — every number, superlative, medical or financial statement in
   `narration_text` must match a `claims[]` entry with `source` + `verified: true`. Unverified
   claim → reject with the offending sentence. (Direct extension of the article engine's
   "hard numbers stay out of prose unless sourced" rule.)
3. **Credential-framing ban** — "doctor explains", "orthopedic surgeon breaks down" etc. are
   rejected unless a named `expert` object with a real credential is attached to the run.
4. **Structure budgets** — hook scene ≤ 12s; conflict-loop arc shape (≥1 `conflict` in the first
   third for runs >90s, `comeback` paired with it); visual-change cadence within per-aspect
   bounds (vertical tightens to ≤3s); total duration within format budget; CTA scene present
   and last.
5. **Pose/asset resolution** — every referenced pose/SVG and `manim_class` exists; unknown
   reference → reject before any render spend.

`qc_checks.py` runs before Gate B: final duration vs storyboard sum (±2%), audio/caption sync
spot-check on 3 random scenes, loudness within −14 ±1 LUFS, no >500ms silent gaps, no black or
frozen frames, vertical safe-zone check (captions clear of UI overlays), metadata completeness
(synthetic-content disclosure determination recorded — forced true when any `realistic_recreation`
scene exists; UTM links resolve; thumbnail variants present).

---

## 8. LLM stages are configuration, not architecture

Only two stages may call an LLM: `transforming_script` and `storyboard_build` assembly prose.
Both follow the `llm_writer.py` env contract — `LLM_MODEL` / `LLM_PROVIDER` / `LLM_API_KEY` /
`LLM_BASE_URL`, OpenRouter-first, swappable without code changes. Corpus-sourced runs have a
deterministic template floor (transcript steps → beats) and the LLM only rewords; essay-sourced
runs are LLM-first but guard-gated. Any "which model plays which role" doc (Claude/GPT/Hermes) is
a deployment note, not architecture — every stage must run identically with any provider, a
template, or a human doing it by hand.

**Agent access via MCP (P1+).** For agent runtimes operating the pipeline, an optional MCP
server exposes the content queue, channel/brand configs, and job store as tools/resources —
structured context instead of per-run prompt plumbing. Autonomy stays bounded by the gates: MCP
lets an agent *prepare, run, and monitor* jobs end-to-end; approval and publish remain the
operator's (graduated autonomy, §3).

**Reference recipes (P1+).** An optional `recipe_extract` service turns operator-curated
reference videos into *structural* pacing presets — cut cadence, hook timing, overlay density —
stored as named configs a storyboard can adopt. Structure only, never content: recipes shape
`timing`/`beats` budgets, and the claims/information-gain rules still apply in full.

---

## 9. Definition of done (per run)

A run may be reported complete only when ALL exist on disk:

- [ ] `job.json` with `status == "published"` (or `"packaged"` in v1 manual mode)
- [ ] All stage events `completed` (gates included)
- [ ] `video/landscape_final/final.mp4` (+ `vertical_final` when shorts were in scope)
- [ ] `captions/`, `package/metadata.json` (disclosure determination recorded), `package/embed_payload.json`
- [ ] `qc/report.json` with `overall: pass`

Point to the artifact, not the claim.

---

## 10. Not building (v1)

- **YouTube upload API / OAuth** — v1 publish emits a checklist + metadata for manual upload
  (10 min/video, removes an entire credential class from scope). Phase 2 decision; P2
  auto-publish will include a momentum throttle (hold the queue while the previous upload is
  still climbing).
- **Orchestration frameworks / multi-agent runtimes** — `pipeline.py` is a sequential stage
  loop; parallelism arrives only if render throughput demands it.
- **Auto-embed writes to the registry** — `embed_payload.json` is handed to the registry's own
  import flow with its existing human gate; this engine never writes to registry tables.
- **Per-frame LLM "creative" decisions** — all creative variance lives in the storyboard
  (reviewed at Gate A); render stages are deterministic functions of the contract.
