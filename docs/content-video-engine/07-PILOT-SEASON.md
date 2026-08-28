# Pilot Season — Phase 0 Validation Cohort

> **STATUS: RECORD.** A point-in-time research note, review, or planning document. Not maintained, and not current doctrine — read it for how a decision was reached, not for what to do now. Live doctrine is indexed in [README.md](README.md).

> **Superseded cohort:** the technique-heavy cohort below is retained as historical
> planning context. The active V4 cohort is the three-part series defined here.

## History Documentary V4 cohort

1. **How Judo Became Brazilian Jiu-Jitsu** — approximately 10-minute acceptance
   pilot (8–12 minute band) covering
   Kano, Maeda, and early Brazilian development. Popular one-line origin stories
   remain hypotheses until the Research Gate approves exact claims.
2. **The Branches BJJ History Forgot** — George Gracie, São Paulo, and Lotus Club
   are research questions only in this PRP.
3. **How BJJ Became a Global Sport** — Brazil, the United States, modern
   competition, and Pacific Northwest arrival; no named academy promotion.

Each episode targets one landscape research master, two native vertical clips, and
chapter-level subvideos built from self-contained approved claim clusters. Episode 1
alone proceeds through the acceptance pipeline. It stops for the operator at
Research, Visual Direction, Gate A, and Gate B. The release buffer still requires
three Gate-B-approved packages before a public launch, but does not authorize
publication.

Armbar V3 is frozen R&D. No stick-figure technique tutorial, corpus technique short,
or generated grappling choreography is part of the V4 acceptance cohort.

Length is earned by evidence, not padding. Each chapter must introduce a distinct
historical question, source cluster, and visual progression. A subvideo preserves
the qualification and citations required to stand alone; it is not an arbitrary
excerpt from the master.

*Date: 2026-07-28 · Purpose: the content plan for Phase 0. The pilot exists to answer assumption
A1 (can this format retain viewers?) with real data before any orchestration is built. Episodes
are produced through the thin-slice pipeline as it comes online — the pilot IS the pipeline's
acceptance test.*

**Cohort:** 5 long-form episodes (4–6 min) + 2 vertical clips each + 4–6 corpus technique shorts
(deterministic floor, e.g. armbar-from-guard) ≈ **5 long-form + 12–16 shorts over 4–6 weeks.**

---

## 1. The five episodes (operator-defined, production-annotated)

### E1 — "The Bizarre History of BJJ: From Samurai Battlefields to Tacoma"
- **Sources:** registry BJJ history + Gracie-migration articles (national history corpus).
- **Visual spine:** armored samurai discover punches don't work on iron → Kano keeps the leverage,
  discards the armor → Maeda circles the globe in a bowler hat → the Gracie branch split → PNW
  pioneers land in Washington. `StickFigureScene` + `MapNetworkScene` + `timeline`.
- **Claims profile:** MEDIUM — dates, names, lineage links all go in the ledger with sources from
  the article fact layer. Named living/recent figures (e.g. PNW pioneers) must be sourced from
  the registry's own published articles, not model memory.
- **Why it's in the pilot:** tests the history/story format + map scenes; the strongest
  "shareable to non-practitioners" candidate.

### E2 — "Why Basic BJJ Beats Complex Guard Systems (The Science of Roger Gracie)"
- **Sources:** national history + Gracie migration article (technique-philosophy sections).
- **Visual spine:** side-by-side stick-figure comparison — inverted 50/50 spaghetti vs. basic
  mount + cross-collar; `JointLeverageScene` shows why pressure compounds and inversion leaks
  force. The signature-format episode.
- **Claims profile:** MEDIUM — competitive-record statements about a real, named athlete must be
  ledger-sourced; biomechanics claims stay qualitative ("more contact area, shorter lever")
  unless sourced.
- **Why it's in the pilot:** this is the thesis video for the *Physics of Grappling* series; if
  this format doesn't retain, the differentiation premise needs rework.

### E3 — "How Not to Ruin Your Joints by 35 (Orthopedic BJJ)"
- **Sources:** National BJJ Registry strategic guide — orthopedic & joint-protection section.
- **Visual spine:** anatomical stick figures under load — finger/knee/cervical stress patterns,
  when to tap vs. when damage compounds. `JointLeverageScene` in anatomy mode.
- **Claims profile:** **HIGH — the medical episode.** Every injury/physiology statement needs a
  literature-grade source in the ledger. **No credential framing** ("orthopedic surgeon
  explains") unless a real named expert reviews the script (`expert` object) — the guard enforces
  this. The subtitle stays honest: it's sports-medicine literature, summarized and cited.
- **Why it's last in production order:** it forces the claims-sourcing workflow to exist. Also
  the named 2026 enforcement bucket ("AI personas on health topics") means this episode ships
  with maximum human fingerprints: operator-reviewed script, cited sources on screen.

### E4 — "The Pacific Northwest Grappling Boom"
- **Sources:** Washington/PNW BJJ pollination article + **registry region aggregates** —
  academy counts and density by region are real registry data no competitor has.
- **Visual spine:** animated Washington map — grappling spreads Seattle → Tacoma → Spokane →
  Olympia with dated nodes; density/count callouts from the registry fact layer.
  `MapNetworkScene` showcase.
- **Claims profile:** LOW-MEDIUM — numbers come straight from the registry aggregates with
  provenance (the same derived-counts rule as the article engine: counts are derived, never
  fabricated).
- **Why it's in the pilot:** proves the only-here-data premise on screen, and it's the most
  natural registry CTA of the five ("find every verified academy on the map — link below").

### E5 — "The Open Mat Survival Guide"
- **Sources:** Washington BJJ Registry playbook (etiquette/drop-in sections).
- **Visual spine:** comedic etiquette vignettes — the drop-in checklist, navigating unfamiliar
  rooms, the `gym_enforcer` running gag debuts. Pure `StickFigureScene`.
- **Claims profile:** LOW — advice/instruction, nearly claim-free.
- **Why it's first in production order:** lowest risk on every axis; the pose library and comedy
  register get built here; fastest path to a first finished artifact.

**Production order ≠ episode order: E5 → E2 → E4 → E1 → E3** (rising claims complexity, one new
scene-class per episode: poses → leverage → map → timeline → anatomy).

---

## 2. Technique shorts (the deterministic floor, in parallel)

4–6 corpus records (starting `armbar-from-guard`) → vertical-first storyboards via the
deterministic path (transcript steps → beats; LLM rewording optional). These exist to (a) test
the shorts surface with zero LLM risk, (b) become the first **embeds** on their technique ×
location registry pages (assumption A2 test starts here), (c) exercise the pipeline weekly while
long-form episodes are in review.

### 2.1 Pre-launch batch gate

Do not make the first public channel upload until **three distinct videos** are
Gate-B-approved, QC-passing, and packaged with final metadata/thumbnails. They remain private
artifacts until the buffer is complete; automated tests or draft renders do not count. The
three should collectively exercise both landscape and native-vertical outputs.

This is an operator release checklist for P0, not a new per-run stage. Once the buffer is ready,
publish from it at the cadence below and continue production so early view counts do not dictate
the unfinished catalog. A later publish-queue implementation may enforce the same policy from
persisted run evidence.

---

## 3. Measurement targets (calibrated to 2026 benchmarks, sourced in `05-COMPETITIVE-BRIEF.md`)

| Metric | Pass | Strong | Context |
|---|---|---|---|
| Shorts: first-3s hold | ≥75% | ≥80% | the "swipe or stay" gate |
| Shorts (30–60s): avg % viewed | ≥45% | ≥55–65% | 40–55% is typical; platform-tracked Shorts average ≈74% APV skews to sub-30s clips |
| Long-form (4–6 min): avg % viewed | ≥40% | ≥50–60% | platform-wide average retention ≈24%; >50% puts a video in roughly the top sixth |
| Long-form CTR (impressions) | ≥3% | ≥5% | packaging variants at Gate A exist for this |
| Human time per video | ≤30 min | ≤20 min | timed at both gates (assumption A4) |
| Marginal cost per finished minute | ≤$5 | ≤$2 | TTS is ~$0.17/min (confirmed) — render compute and music licensing dominate |
| Embed test (A2) | engagement delta measurable on ~20 embedded vs matched control pages after 4–6 weeks | | run from the technique shorts |

Numbers are pre-committed pass bars, not predictions. Kill/pivot rules live in
`00-BRAINSTORM-AND-DECISIONS.md` §5 and are evaluated once, at cohort end — not per-video.

---

## 4. Distribution constraints the pilot must respect (confirmed 2026 mechanics)

- **Shorts carry no clickable links** (descriptions and pinned comments — links disabled
  platform-wide since Aug 2023). Registry funnel from shorts = verbal/on-screen CTA + channel
  profile link + the related-video link to our own long-form. **UTM-measured clicks are a
  long-form-description phenomenon; plan reporting accordingly.**
- **No disclosure checkbox needed** for the core format (fully animated, non-realistic,
  own-voice clone) — determination recorded per-run in the storyboard; any
  `realistic_recreation` scene flips it on.
- **Let uploads breathe.** In the first ~10 uploads, space posts ≥48h apart and hold the queue
  while the previous video is still visibly climbing. Evidence is single-creator anecdote, but
  spacing costs nothing and the pilot cadence already fits it.
- **Launch from a buffer.** The first public upload waits for the three-video gate in §2.1; the
  ≥48h spacing rule begins only after that buffer exists.
- **Monetization is not a pilot goal.** YPP thresholds and review come much later; the pilot
  optimizes retention + funnel evidence. Voice: custom/cloned only — ElevenLabs Default voices
  retire 2026-12-31 and are the mass-production fingerprint regardless.

---

## 5. Per-episode definition of done

- [ ] Storyboard approved at Gate A (rubric scores recorded in `job.json`)
- [ ] Claims ledger 100% verified (E3: literature sources; E1/E2/E4: fact-layer/article sources)
- [ ] Landscape final + vertical clips rendered, captioned, QC-passed
- [ ] Published with UTM-tagged long-form description links; shorts CTA verbal/on-screen only
- [ ] Technique shorts: embed payload delivered for registry page placement
- [ ] Analytics snapshot captured at 7 and 28 days into `runtime/jobs/<id>/analytics/`

A video counts toward the pre-launch buffer only after every pre-publication item above is
complete through Gate B; the publish and analytics items occur after release.
