# Storyboard Data Contract (v2) — Rationale and Usage

> **STATUS: RECORD.** A point-in-time research note, review, or planning document. Not maintained, and not current doctrine — read it for how a decision was reached, not for what to do now. Live doctrine is indexed in [README.md](README.md).

> **Current extension: Storyboard 2.3.0.** Existing 2.0/2.1/2.2 artifacts
> remain immutable and resumable. History V4.1 uses the additions below.

## Storyboard 2.3 living-editorial extension

Storyboard 2.3 adds immutable `coverage_plan_hash` and
`asset_selection_hash` fields. Each evidence-backed narration scene retains
one voiceover and contains one or more `visual_beats`. A beat binds a semantic
coverage slot to approved asset IDs, a deterministic motion recipe,
micro-event timing, and a transition. This permits sentence/clause-level cuts
without repeating narration or converting nouns into literal asset requests.

Candidate preview URLs, provider metadata, licenses, and prices remain in the
Asset Selection packet. The storyboard sees only promoted local asset IDs.

## Storyboard 2.2 documentary extension

Storyboard 2.2 adds `history_episode` as a source kind and records immutable
`research_hash`, `asset_manifest_hash`, and `art_bible_hash`. A documentary scene
references one or more approved research claim IDs, approved asset IDs, and its
`visual_treatment.v2` ID. Multi-source claims preserve all citation references.

Allowed documentary visual functions are `artifact_cold_open`,
`archival_portrait`, `illustrated_reconstruction`, `document_quote_closeup`,
`migration_map_timeline`, `lineage_graph`, `concept_mechanics_cutaway`, and
`chapter_cta`. `StickFigureScene` and instructional technique sequences are
invalid for `history_episode` storyboards. Citation overlays resolve claim IDs;
visuals resolve asset IDs. The two resolution domains never substitute for one
another.

*Date: 2026-07-28 · Schema: `storyboard.schema.json` (spec-of-record copy in this folder; canonical runtime copy will live at `content/video-engine/configs/`) · Consumers: `storyboard_guard.py`, every render-side service, both human gates.*

The storyboard is the **single contract between judgment and machinery**. Everything upstream of
Gate A (script transformation, claims sourcing, packaging choices) exists to produce this file;
everything downstream (TTS, render, composite, captions, packaging) is a deterministic function
of it. If it isn't in the storyboard, the pipeline doesn't do it.

---

## 1. What changed from the draft (v1 → v2)

The operator's draft schema had the right skeleton (job id, global theme, typed scenes with
`manim_class` + `parameters`). Nine structural gaps are closed in v2:

| # | v1 gap | v2 fix | Why it matters |
|---|---|---|---|
| 1 | No timing model | `scene.timing` (target/min/max/padding) + TTS-first rule (§3) | Without a clock owner, every voice change forces re-renders of the expensive stage |
| 2 | No aspect handling | `global_settings.targets` + `scene.layout_hints` + top-level `shorts[]` | 9:16 as a blurred-pad crop is the recognizable slop pattern the Golden Rules ban; vertical must be a layout |
| 3 | No captions provision | Word-timing artifacts from TTS are a first-class stage input (`beats.at_word` anchors) | Most vertical viewing is muted; burned captions are table stakes |
| 4 | No provenance | `source` (kind/ref/content_hash) + `claims[]` ledger + `scene.claim_refs` | Extends the repo's never-fabricate rule to video; guard can block unsourced numbers/medical/financial statements |
| 5 | No packaging | `packaging` (title variants, thumbnail concept, description with UTM placeholders, tags, chapters, CTA) | Packaging decides CTR before retention gets a vote; it must be reviewed at Gate A, not improvised at upload |
| 6 | No act structure | `scene.act` conflict-loop enum (`hook/develop/conflict/comeback/payoff/cta`) with guard-enforced shape | Linear summaries retain worse than conflict arcs; structure must be checkable, not aspirational |
| 7 | No voice policy hook | `voice.provider` + `is_custom_voice` + `packaging.synthetic_content_disclosure` | Stock voices are a slop fingerprint *and* retired by ElevenLabs 2026-12-31; disclosure is policy-triggered (realistic depictions, other-person voice clones), so it's recorded as a determination, not a blanket flag |
| 8 | No reproducibility | `schema_version` (major-version refusal), `content_hash`, settings snapshots as cache keys | Same storyboard must render the same video next month |
| 9 | Enum too narrow | `visual_type` adds `chart_data`, `timeline`, `comparison` | Trades and finance lanes need charts/timelines; adding enum values later is a schema migration, adding scene classes isn't |

Also removed: `$schema` value pointing at a markdown-linked URL (draft artifact), and
`on_screen_text` demoted to optional-nullable (most scenes shouldn't carry it; captions do that job).

---

## 2. Authoring workflow (who writes which fields, when)

```
script_transform  →  beat sheet (acts, narration, [VISUAL] markers, claims list)
storyboard_build  →  full storyboard.json: scenes, parameters, packaging draft, shorts plan
storyboard_guard  →  schema + claims + structure + asset checks (machine, hard fail)
GATE A (human)    →  edit narration/titles/hook freely; re-guard on save; approve
audio_synth       →  writes audio/scene_<id>.mp3 + .words.json  ← measured clock lives here
render → … → QC   →  deterministic from storyboard + audio artifacts
GATE B (human)    →  watch final, approve publish
```

Two rules keep this sane:

1. **The storyboard is immutable after Gate A.** Measured audio durations and resolved
   `at_word` timestamps live in `runtime/jobs/<id>/audio/` artifacts — never written back into
   the contract. Intent (storyboard) and measurement (artifacts) stay separate; a re-approved
   edit is a new guard pass and invalidates only the affected scene caches.
2. **`timing.target_s` is an estimate, not a promise.** It's derived from word count ÷ WPM at
   authoring time so the guard can check pacing budgets and total-duration fit *before* spending
   on TTS. The renderer obeys the measured duration; the guard flags scenes whose measured
   duration lands outside `[min_s, max_s]` at QC.

---

## 3. The TTS-first timing rule (restated once, normatively)

Narration length is unknowable until synthesized; animation length is fully controllable.
Therefore **audio is the clock**: `audio_synth` runs immediately after Gate A, and every Manim
scene receives its measured `audio_duration` (+ `padding_s`) as a parameter it must fill exactly
(±1% asserted by the renderer). No stage may stretch, trim, or time-warp audio to fit video.

---

## 4. Worked example (abridged) — corpus technique → storyboard

Source: `content/bjj-registry/corpus/armbar-from-guard.json`. Deterministic floor: transcript
steps become `develop` beats; `common_errors` becomes the payoff segment; `related` feeds end
screens. The CTA uses the registry-level URL; academy attribution is deferred until a verified
registry join exists. LLM (if enabled) rewords narration only.

```json
{
  "schema_version": "2.0.0",
  "job_id": "6f1c9a2e-6a1b-4b2f-9d3e-0c8b7a5d4e21",
  "source": {
    "slug": "armbar-from-guard",
    "kind": "corpus_technique",
    "ref": "content/bjj-registry/corpus/armbar-from-guard.json",
    "content_hash": "sha256:…"
  },
  "channel": { "id": "combat-science", "series": "physics-of-grappling" },
  "global_settings": {
    "voice": { "provider": "elevenlabs", "voice_id": "CUSTOM_CLONE_01", "is_custom_voice": true },
    "theme": { "background_color": "#0F0F12", "accent_color": "#3B82F6" },
    "music": { "track_id": "lofi-bed-03", "gain_db_rel_voice": -18 },
    "pacing": { "wpm_target": 140, "pattern_interrupt_max_s": 25 },
    "targets": ["landscape", "vertical"]
  },
  "claims": [
    { "id": "c1", "text": "The armbar attacks the elbow's hinge — a class-1 lever with the fulcrum at your hips.",
      "kind": "biomechanical", "source": "corpus", "verified": true }
  ],
  "scenes": [
    { "scene_id": 1, "act": "hook",
      "narration_text": "This is the first submission you'll ever learn — and the one that still finishes black belts.",
      "visual_type": "stick_figure_action", "manim_class": "StickFigureScene",
      "parameters": { "poses": ["closed_guard", "armbar_extension"], "reaction": "tap_frantic" },
      "timing": { "target_s": 6 }, "claim_refs": [] },
    { "scene_id": 2, "act": "conflict",
      "narration_text": "Your instinct says yank the arm free. Wrong — pulling straightens the elbow for them. The escape everyone tries IS the finish.",
      "visual_type": "stick_figure_action", "manim_class": "StickFigureScene",
      "parameters": { "poses": ["arm_yank_fail"] },
      "beats": [ { "at_word": 4, "action": "pose:arm_yank_fail" } ],
      "timing": { "target_s": 8 }, "claim_refs": [] },
    { "scene_id": 3, "act": "payoff",
      "narration_text": "Here's the physics: your hips are the fulcrum, their elbow is the load. It's a lever — leverage beats strength.",
      "visual_type": "joint_leverage_diagram", "manim_class": "JointLeverageScene",
      "parameters": { "lever": { "fulcrum": "hips", "load": "elbow", "effort": "hip_drive" } },
      "timing": { "target_s": 10 }, "claim_refs": ["c1"] },
    { "scene_id": 4, "act": "cta",
      "narration_text": "Full step-by-step, common mistakes, and where to learn it near you — National BJJ Registry, link below.",
      "visual_type": "title_card", "manim_class": "TitleConceptCard",
      "parameters": { "headline": "Learn it properly." },
      "timing": { "target_s": 6 }, "claim_refs": [] }
  ],
  "shorts": [
    { "clip_id": "armbar-lever-short", "scene_ids": [3, 1], "hook_line": "Your hips are a fulcrum. Their elbow is the load.",
      "title": "The armbar is just a lever", "max_duration_s": 45 }
  ],
  "packaging": {
    "titles": [ "The Armbar Is Just Physics", "Why the First Submission You Learn Never Stops Working" ],
    "thumbnail": { "concept": "lever diagram over stick-figure armbar, torque arrow", "variant_texts": ["JUST A LEVER"] },
    "description_md": "Full written breakdown: {ARTICLE_URL}\nFind verified academies near you: {REGISTRY_URL}",
    "tags": ["bjj", "armbar", "biomechanics"],
    "cta": { "line": "Find verified academies near you at NationalBJJRegistry.com", "url": "https://nationalbjjregistry.com", "utm_campaign": "armbar-from-guard" },
    "synthetic_content_disclosure": { "required": false, "reason": "fully animated, non-realistic; own-voice clone" }
  }
}
```

Note what the example demonstrates: the shorts clip **reorders** scenes (payoff first — the
lever diagram is the scroll-stopper) and carries its own hook line; claims ledger has exactly one
entry because the script makes exactly one checkable assertion; everything else is instruction,
which needs no source beyond the corpus transcript.

---

## 5. Guard obligations (summary — full list in `03-SYSTEM-ARCHITECTURE.md` §7)

Schema-valid is necessary, not sufficient. The guard additionally enforces: arc shape (one hook
first, one cta last, ≥1 develop, conflict + comeback pairing for runs >90s, ≥1 payoff — the
worked example above is abridged and below that threshold), claims cross-referencing in both directions,
credential-framing ban without an `expert` object, custom-voice requirement for synthetic
providers, pose/class existence, pacing budgets, shorts scene-id validity, and total-duration fit
against the format budget. A storyboard that fails any check never reaches a human — Gate A
reviews candidates, not drafts.
