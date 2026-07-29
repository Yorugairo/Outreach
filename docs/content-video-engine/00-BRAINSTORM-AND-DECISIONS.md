# Content-to-Video Flywheel — Brainstorm, Challenges, and Decisions

*Date: 2026-07-28 · The decision record for the doc set in `docs/content-video-engine/`. Inputs:
the operator's raw "Automated Content-to-Video Flywheel Engine" spec + three follow-up research
drops, this repo's existing systems, and three research streams run today (benchmarks, emerging
channels, platform economics — synthesized in `05-COMPETITIVE-BRIEF.md`). Read this first; the
other docs implement these decisions.*

---

## 1. The reframe: Act 1 is already built

The raw spec describes "Write Once, Publish Thrice" as something to build. Repo evidence says
**step 1 exists and is production-shaped**: `content/bjj-registry/` is a working programmatic
article engine — deterministic fact layer with provenance, guarded LLM prose (`llm_guard.py`),
human publish gate, JSONL handoff into the registry's blog distribution. Its **technique axis**
(`corpus/armbar-from-guard.json`: transcript, steps, `common_errors`, `related`, `taught_at`) is
storyboards-in-waiting.

So this is not "build a content system" — it is **add a render axis to an existing corpus-driven
content system**. Honest slogan: *generate once, publish N* — fact layer → article (built) →
long-form video → native verticals → **embeds on every matching pSEO page**.

## 2. What survives from the raw spec

Stick-figure + Manim CE format (Manim confirmed healthy 2026; the style is uniquely suited to
leverage/biomechanics and deliberately-crude-drawings-with-strong-writing is precedented at 4.8M
subs) · JSON storyboard as the contract (rewritten as v2) · repurposing pipeline (extended with
embeds) · funnel tied to owned SaaS conversion nodes (the actual moat) · four scene-class
families (extended) · reusable CLI over one-off scripts (repo rule anyway).

## 3. Challenges and decisions

### 3.1 "100% automated" → human-gated automation with **graduated autonomy**
Fully-autonomous publish violates the repo's own import-gate rule and optimizes for YouTube's
channel-level "inauthentic content" enforcement (three 2026 buckets; mass-produced templates are
bucket #1). Decision: everything between two gates is automated; Gate A (storyboard) and Gate B
(QC/publish) start as full reviews and **shrink by design** — P1: exception-based Gate A
(auto-approve on green guards + model-scored rubric); P2: sampled Gate B. Per-video review time
trends toward seconds (operator directive: minimize human-in-the-loop). Target ≤30 min/video in
the pilot, falling after.

### 3.2 Four pillars on one channel → **lanes within one audience promise**
Evidence settles the operator's lane-rotation model vs my initial one-pillar-per-channel split:
Sam O'Nella proves breadth when persona/style is the brand; MinutePhysics proves spin-offs when
the promise is topical. Synthesis: **lanes rotate within one audience promise; new promises get
new channels.** Channel 1 = combat-science (Physics of Grappling · Combat History · Honest
Guide lanes, badge-coded, rotation days). Trades = Channel 2 at P2. Finance: see 3.8.

### 3.3 The missed coupling → **embeds are the base case, YouTube is the upside**
Confirmed harder than assumed: Shorts description/pinned links are **not clickable at all**
(since Aug 2023) — the raw spec's Shorts→site funnel was broken by design. Decision stands and
strengthens: every technique video embeds on its technique × location registry pages with
`VideoObject` JSON-LD (unique media no competitor pSEO site has, stacking on existing `HowTo`
rich results). Even a channel that never pops has already upgraded hundreds of owned pages.
Funnel measurement runs through long-form descriptions (UTM) + profile link + verbal CTAs.

### 3.4 Scripts are the bottleneck → **conflict-loop arc, enforced**
Retention is won in the script. The 3-act contract was upgraded on the operator's research to a
conflict-loop arc: `hook → develop → conflict → comeback → payoff → cta`, guard-enforced
(conflict in the first third for runs >90s, comeback paired). Conflicts are *found* in source
material, never invented — claims rules apply to conflicts too. Packaging (title/thumbnail
variants) is decided at Gate A because CTR precedes retention.

### 3.5 Story flow is a render-level guarantee (operator directive: no random cuts)
`transition` contract per scene (default `continuous`); consecutive compatible scenes render as
ONE Manim sequence via the section API — motion, camera, cast carry across beats; music bed
never cuts; every scene opens in motion within 0.5s (entrance contract); hard cuts are counted
and budgeted. Adapted from the operator's pasted findings with one pushback: the 1–3s hard cut
cap applies to **verticals** (≤3s micro-beats); landscape keeps ≤6s with always-in-motion —
benchmark channels win on internal motion + compression, not cut rate, and leverage diagrams
need dwell time to land.

### 3.6 The voice is the moat — and our biggest exposure
Strongest single finding across all eight researched channels: **zero success examples with
AI-sounding narration; the persona voice is the asset** (Sam O'Nella's channel grew 3M subs
through a 2.7-year hiatus on catalog + persona alone). Mitigations: clone the operator's own
voice (disclosure-exempt per official policy; immune to ElevenLabs Default retirement
2026-12-31; persona-bearing); persona lives in the writing (recurring cast as pose-library
assets, catchphrases, running gags); voice A/B is pilot-critical (A5); fallback =
operator-recorded VO, natively supported.

### 3.7 Claims risk → ledger + guard (repo hard-truth rules, extended to video)
Every number/medical/financial/historical assertion needs a sourced, verified `claims[]` entry
or it doesn't ship. Credential framing requires a real named `expert`. Medical (orthopedic lane)
ships with literature citations + operator review. Raw-spec titles like "An Orthopedic Doctor's
Breakdown" are banned unless a real doctor is involved.

### 3.8 Finance: un-parked by the operator's credentials
Original decision parked finance (named 2026 enforcement bucket: "AI personas on
health/finance/legal/politics"). The operator is ex-JPMorgan Chase with a business degree — a
real, namable human persona, which is precisely the mitigation the policy describes. Revised:
***Systems & Blowups* lane, post-pilot**, educational/historical/mechanistic only, hard
no-recommendations rule, operator credentials on-screen (`expert` object = operator). Sequenced
after combat lanes prove the pipeline (finance has no owned conversion node; RPM $8–22 is
top-quartile upside, not baseline).

### 3.9 Agent org chart ≠ architecture
"Claude = architect, GPT = developer, Hermes = runtime" became: model-agnostic stages with
contracts (mirrors `InsightRunPipeline` + `llm_writer.py` env-swap). Any stage runs with any
provider, a template, or a human. P1+ adds MCP access (queue/configs/job store as tools) so
agent runtimes prepare and monitor runs without prompt plumbing — approval and publish stay
human. Reference-recipe extraction (operator-curated viral-video pacing presets — structure
only, never content) also lands P1.

## 4. Assumption register (ranked by risk × uncertainty)

| # | Assumption | If wrong | Confidence | Cheapest test |
|---|---|---|---|---|
| A1 | Programmatic stick-figure video can hit retention bars (shorts 30–60s APV ≥45%, first-3s ≥75%; long-form APV ≥40%) | Channel play dead; embeds-only fallback | Unknown — **the riskiest** | Pilot cohort (`07`), fresh channel |
| A2 | Embeds measurably lift pSEO page engagement | Base case weakens to rich-results + inventory value | Medium-high | ~20 embedded vs matched control pages, 4–6 wks |
| A3 | Marginal cost ≤$5/finished-min | Scale economics break | High (TTS ≈$0.17/min confirmed; compute is the variable) | Instrument per-stage in pilot |
| A4 | Gates hold at 5+ videos/wk within ≤30 min/video | Throughput capped | Medium | Time the gates in pilot |
| A5 | A cloned/custom voice reads as persona, not slop | Fallback: operator-recorded VO | **Medium-low — zero market precedent for synthetic voice success in these niches** | Voice A/B + 1 human-VO video inside pilot |
| A6 | Human-gated pipeline passes channel-level YPP review later | Ad revenue delayed; embeds + funnel unaffected | Medium | Catalog variation by design; apply late |
| A7 | Corpus depth ≥12 usable technique records now, ~50+ for 6 months | Cadence starves; corpus expansion becomes P0 work | Unknown — repo shows 1 sample; **operator input needed** | Corpus inventory count |
| A8 | Meaningful click-through YouTube → registry | Treat as upside only | Low (Shorts links dead; long-form desc is the path) | UTM from day 1 |

## 5. Pre-committed kill / pivot criteria

Evaluated **once, at pilot end** (~5 long-form + 12–16 shorts over 4–6 weeks) — and only on
retention/cost, not growth (cold-start evidence says growth verdicts before month ~6 are noise):

1. **Retention floor:** median shorts APV <40% (30–60s) after one format-iteration round →
   stop channel scale; pivot to embeds-only mode.
2. **Labor ceiling:** >45 min human/video after tooling polish → automation-gap analysis before
   any scale.
3. **Embed signal:** no engagement delta on embedded pages after 6 weeks → demote embeds from
   base case; channel metrics must carry ROI alone.
4. **Cost ceiling:** >2× per-minute target after pilot → renegotiate stack before P1.
5. **Voice check:** if A5 fails both TTS variants but the human-VO video retains → switch to
   operator VO permanently (pipeline unchanged) rather than killing the format.

## 6. Adopted / adapted / rejected (operator's pasted findings, disposition ledger)

| Finding | Disposition |
|---|---|
| Conflict Loop Arc | **Adopted** — schema enum + guard + rubric (3.4) |
| 1–3s cut cap, first-frame motion | **Adapted** — ≤3s verticals only; ≤6s landscape; first-0.5s motion contract everywhere (3.5) |
| Viral recipe extraction (`--reference-url`) | **Adapted** — P1, operator-curated, structural presets only (3.9) |
| 48h "let videos breathe" throttle | **Adopted** — pilot guidance now; P2 API throttle (anecdotal-tagged) |
| MCP brand/context autonomy | **Adopted P1+** — bounded by gates (3.9) |
| Lane rotation + badges + playlists | **Adopted** as the channel model, scoped to one audience promise (3.2) |
| Custom-cloned voice guidance | **Adopted & strengthened** by voice finding + Default-voice retirement (3.6) |
| Blurred-background 9:16 padding | **Rejected** — recognizable slop pattern; vertical is a first-class layout |
| "$8–18 RPM" planning number | **Rejected** — corrected to $4–8 blended; finance top-quartile only |
| Shorts description/pinned-comment CTAs | **Rejected as impossible** — links not clickable since Aug 2023 |

## 7. Parked (explicitly, with reasons)

Reddit/X distribution automation (policy minefield; manual, value-dense only) · Substack Notes
loops (human relationship work) · DTC supplements/affiliates (registry monetization planning,
not this engine) · orchestration frameworks/render farm (until stage contracts prove out) ·
fight-choreography spectacle (Jhanzou territory — we win on diagrams + persona, not choreography)
· realistic re-creations of real people/events (brand + disclosure trigger).

## 8. Inputs needed from the operator (blockers for P0, not for doc approval)

1. **Corpus inventory** — how many technique records with transcripts exist? (Pilot needs ≥12.)
2. **Voice** — record clone source audio (recommended) or pick 2 candidate synthetic voices for
   the A/B; both paths need the pilot A/B.
3. **Music library** — pick licensed library (or YouTube Audio Library to start); no mainstream
   licensed tracks (monetization wound), no AI-generated music v1 (disclosure gray zone).
4. **Trades naming** — `WashingtonLaborNetwork.com` (raw spec) vs **One Trade Network**
   (`docs/product-revenue-contract.md`) before any Channel 2 work.
5. **Embed targets** — staging vs production registry for the A2 test.

## 9. Doc map

| Doc | Holds |
|---|---|
| `00` (this) | decisions, assumptions, kill criteria, disposition ledger |
| `01-PRD.md` | product definition, goals/metrics, requirements, phases |
| `02-CONTENT-STRATEGY.md` | funnel, lanes, editorial standards, voice policy, compliance |
| `03-SYSTEM-ARCHITECTURE.md` | run-centric pipeline, services, guards, continuity rendering |
| `04-STORYBOARD-CONTRACT.md` + `storyboard.schema.json` | the v2 data contract |
| `05-COMPETITIVE-BRIEF.md` | benchmark + cold-start evidence, 2026 economics table |
| `06-SCRIPT-TRANSFORMATION-SPEC.md` | conflict arc, pacing hierarchy, flow rules, rubric |
| `07-PILOT-SEASON.md` | 5 episodes + technique shorts, measurement bars, upload rules |
| `08-TOOLING-ALTERNATIVES.md` | Higgsfield / Gemini verdicts; Gemini QC pre-screener adoption; Explainer threat |
| `.claude/PRPs/plans/P13-CONTENT-VIDEO-FLYWHEEL.plan.md` | build plan, task slices, verification |
