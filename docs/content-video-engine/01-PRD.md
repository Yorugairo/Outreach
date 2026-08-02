# PRD — Content-to-Video Flywheel Engine

> **Active scope: History Documentary V4.** Earlier technique requirements describe
> preserved V1–V3 compatibility, not the current acceptance target.

## V4 product override

The engine's primary product is an evidence-backed three-part History of BJJ
documentary-explainer series. Each approved episode targets a 10-minute research
master (8–12 minute acceptance band), two native vertical clips, and chapter-level
subvideos compiled from approved claim clusters. Armbar V3 is frozen R&D; automated technique
tutorials and `StickFigureScene` are excluded from V4 acceptance.

V4 adds fail-closed `history_episode.v1`, `research_packet.v1`, and
`asset_manifest.v1` inputs plus Research and Visual Direction gates before the
existing motion and publication gates. Every historical narration claim resolves
to the approved research hash and every rendered asset resolves through the
approved local asset manifest. Editorial acceptance is owned by
[`10-HISTORY-DOCUMENTARY-EDITORIAL-SPEC.md`](10-HISTORY-DOCUMENTARY-EDITORIAL-SPEC.md);
rights acceptance is owned by
[`11-ARCHIVAL-ASSET-AND-CITATION-SPEC.md`](11-ARCHIVAL-ASSET-AND-CITATION-SPEC.md).

*Date: 2026-07-28 · Status: draft for operator review · Decisions + assumptions: `00-BRAINSTORM-AND-DECISIONS.md` · Build plan: `.claude/PRPs/plans/P13-CONTENT-VIDEO-FLYWHEEL.plan.md`*

## 1. Problem

The operator owns two discovery properties (National BJJ Registry; the trades vertical) whose
moat is a deterministic fact layer rendered into programmatic articles. Video is the missing
surface: it is the highest-attention format for the registry's audiences, the only format that
feeds YouTube/Shorts discovery, and — embedded on pSEO pages — a differentiator no competitor
directory has. Manual video production costs hours per minute; commodity AI-video slop is
demonetized and brand-destroying. The gap is a **pipeline that renders the existing fact layer
into original animated video at near-zero marginal cost, without crossing the platform's
inauthentic-content line or the repo's never-fabricate line.**

## 2. Product

A run-centric render pipeline (`03-SYSTEM-ARCHITECTURE.md`) that turns corpus records and
registry articles into stick-figure/vector explainer videos (landscape + native vertical), with:

- a validated storyboard contract as the human/machine boundary (`04-STORYBOARD-CONTRACT.md`),
- two human gates (storyboard approval; publish approval) and hard guards between them,
- packaging + UTM-tagged funnel links + registry embed payloads as first-class outputs.

One YouTube channel at launch, organized as **series lanes** (per the operator's lane-rotation
research; single-channel breadth is precedented when persona/format is the brand — see
`05-COMPETITIVE-BRIEF.md`), starting with the *Physics of Grappling* / combat-science lane.

## 3. Users

| User | Interaction | What they need |
|---|---|---|
| **Operator** (primary) | runs CLI, reviews Gate A/B, uploads | ≤30 min/video; trustworthy guards; no babysitting renders |
| Registry visitor (parent / practitioner) | watches embeds on technique & location pages | clear, honest, useful video; faster answer than reading |
| Gym owner (B2B) | sees registry pages enriched with video | a directory worth claiming a profile on |
| YouTube viewer | watches channel/shorts | retention-grade original content; a reason to visit the registry |

## 4. Goals (ranked) and success metrics

**G1 — Upgrade the owned property (base case).** Every produced technique video embedded on its
technique × location pages with `VideoObject` JSON-LD.
*Metric:* ≥20 pages embedded in the pilot; engagement delta vs matched control pages measured at
4–6 weeks (assumption A2).

**G2 — Prove a retainable format.** *Metric:* pilot cohort hits the pass bars in
`07-PILOT-SEASON.md` §3 (shorts first-3s hold ≥75%, 30–60s shorts APV ≥45%, long-form APV ≥40%,
long-form CTR ≥3%).

**G3 — Prove the unit economics.** *Metric:* ≤30 min human time and ≤$5 marginal cost per
finished minute by pilot end (TTS confirmed ≈$0.17/min; compute + music are the variables).

**G4 — Measurable funnel.** *Metric:* UTM-attributed registry sessions from long-form
descriptions reported weekly; verbal-CTA lift observable in branded/direct search during pilot
weeks (directional only — Shorts links are not clickable, per confirmed 2026 mechanics).

**G5 — Channel optionality (upside, not base case).** *Metric tracked, not targeted:* subs,
watch time. Revenue modeling uses ~$4–8 blended long-form RPM (2026-corrected), NOT the $8–18
raw-spec figure; monetization application is deferred until eligibility + policy review.

**G6 — Launch with a coherent catalog.** *Metric:* three distinct videos are Gate-B-approved,
QC-passing, and packaged before the first public channel upload. Early analytics do not interrupt
production of this initial buffer.

## 5. Non-goals (v1)

1. YouTube upload API/OAuth automation (manual upload with generated checklist).
2. Monetization/YPP application, sponsorships, merch.
3. Finance/macro lane *in the pilot* — deferred, not dead: the policy blocker is resolved
   (the operator, ex-JPMorgan Chase, is the named human persona the 2026 enforcement bucket
   requires), with a hard no-recommendations/educational-only rule. Sequenced post-pilot because
   it has no owned conversion node and the combat lanes must prove the pipeline first.
4. Trades lane content (Phase 2, after pipeline proven; requires corpus that doesn't exist here).
5. Automated writes to registry tables (embed payloads go through the registry's own gated import).
6. Realistic re-creations of real people/events (format ban; also the disclosure trigger).
7. Multi-agent orchestration frameworks; parallel render farm.
8. Autonomous competitor/trend scraping or title copying. P0 accepts operator-supplied research;
   P1 may produce provenance-preserving angle candidates, but the operator chooses the thesis.

## 6. Functional requirements

| # | Requirement | Stage/artifact |
|---|---|---|
| F1 | Ingest corpus records + registry articles + queued essays into a `SourceBundle` | `ingesting_source` |
| F2 | Transform source → beat sheet per `06-SCRIPT-TRANSFORMATION-SPEC` (deterministic floor for corpus; guarded LLM for essays) | `transforming_script` |
| F3 | Compile beat sheet → schema-valid storyboard incl. claims ledger, packaging, shorts plans | `building_storyboard` |
| F4 | Reject storyboards failing schema/claims/structure/asset checks before human review | `storyboard_guard` |
| F5 | Gate A: operator edit + approve; edits re-validated; rubric scores persisted | `awaiting_storyboard_approval` |
| F6 | Per-scene TTS with character timestamps → word-timing arrays; content-hash cached | `synthesizing_audio` |
| F7 | Duration-locked Manim renders per aspect profile; draft ladder for previews | `rendering_scenes` |
| F8 | Assemble per-aspect finals: narration, music bed (−18 dB rel., ducked), −14 LUFS normalize | `compositing` |
| F9 | Burned captions (vertical) + `.srt` (landscape) from word timings | `generating_captions` |
| F10 | Packaging: title variants, thumbnail renders, UTM-injected descriptions, chapters, disclosure determination | `packaging` |
| F11 | Automated QC (duration drift, sync, loudness, safe zones, metadata completeness) | `running_qc` |
| F12 | Gate B: operator watches final, approves; publish emits upload checklist + embed payload | `publishing` |
| F13 | Resumable jobs; stage events persisted; `cli.py run/resume/status/approve` | pipeline |
| F14 | Per-stage cost + wall-time instrumentation into `job.json` | pipeline |
| F15 | Channel-launch checklist blocks the first public upload until three distinct runs are Gate-B-approved, QC-passing, and packaged | operator release checklist |

## 7. Non-functional requirements

- **Reproducibility:** same storyboard + configs ⇒ same video (schema major-version refusal;
  settings snapshots in cache keys; no wall-clock/randomness in scene code).
- **Honesty:** guards enforce the never-fabricate rule; claims ledger mandatory; credential
  framing banned without a real expert. (Repo hard-truth rules extended to video.)
- **Security:** API keys env-only, validated at startup; no secrets in storyboards or job
  artifacts; upload credentials out of scope v1.
- **Resumability & evidence:** every stage idempotent; DoD is artifacts on disk
  (`03-SYSTEM-ARCHITECTURE.md` §9).
- **Cost ceiling:** hard fail a run that projects >2× the per-minute cost target (config).
- **Graduated autonomy:** human-in-the-loop is minimized by design, not removed — P1 targets
  exception-based Gate A (auto-approve on green guards + model-scored rubric ≥ threshold), P2
  targets sampled Gate B. Review time trends toward seconds per video.
- **Editorial authority:** AI may organize research, propose outlier inversions, draft, and
  render; a human selects the angle, evidence, brand fit, and publish decision.
- **Story flow:** scene boundaries are authored (`transition` contract) and render as continuous
  sequences by default — no random cuts (architecture §6, script spec §3 flow rules).

## 8. Phases

| Phase | Contents | Exit criteria |
|---|---|---|
| **P0 — Thin slice + pilot** (≈ wks 1–6) | minimal path (deterministic corpus storyboard → TTS → 2 scene classes → composite → captions → manual publish); three-video pre-launch buffer; pilot season per `07-PILOT-SEASON.md`; embed test on ~20 pages | first three public-ready videos buffered before launch; pilot cohort published; metrics captured; kill criteria evaluated (`00` §5) |
| **P1 — Productization** (wks 6–12) | essay→storyboard LLM path + full guard; remaining scene classes; packaging automation; analytics snapshots; cost dashboard; exception-based Gate A; operator-approved outlier/inversion briefs and reference-recipe pacing presets (structure only, provenance retained); MCP access to queue/job store for agent runtimes | 5+ videos/wk sustainable at ≤30 min human each; embeds rolling out beyond pilot pages |
| **P2 — Scale + lane 2** | trades corpus + *Trade Science* lane (naming reconciled first); publish API + OAuth with momentum throttle (queue holds while prior upload climbs); sampled Gate B; render parallelism if needed | second lane live without pipeline changes; upload automation gated by sampled review |
| **P3 — Expansions** | *Systems & Blowups* finance lane under the operator's named persona (no-recommendations rule); additional channels per `05` breadth evidence; monetization application | explicit operator go/no-go per expansion |

## 9. Dependencies and open questions

- **Corpus inventory** (blocker for P0 scale): count of technique records with transcripts.
  Repo contains 1 sample; pilot needs ≥12.
- **Voice decision** (blocker for first render): cloned-own-voice (recommended — strongest
  persona ownership, disclosure-exempt, immune to ElevenLabs Default-voice retirement on
  2026-12-31) vs. custom-designed synthetic voice. Benchmark evidence: no comparable channel
  succeeded on a generic voice (`05-COMPETITIVE-BRIEF.md`).
- **Music licensing** (blocker for compositing): licensed library subscription vs. YouTube
  Audio Library; AI-generated music is a disclosure gray zone — avoided v1.
- **Trades property naming** (blocker for P2 only): `WashingtonLaborNetwork.com` (raw spec) vs
  **One Trade Network** (`docs/product-revenue-contract.md`).
- **Staging vs production registry** for embed test targets.
