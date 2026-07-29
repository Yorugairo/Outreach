# Content Strategy — Channel Architecture, Editorial Standards, Compliance

*Date: 2026-07-28 · Evidence base: `05-COMPETITIVE-BRIEF.md` (benchmarks + cold-start comps) and the 2026 policy/economics fact-check summarized there · Decisions trace to `00-BRAINSTORM-AND-DECISIONS.md`.*

## 1. The funnel, corrected for 2026 mechanics

```
TIER 1 · DISCOVERY      Shorts/Reels (native-designed, own hooks) · community posts (manual)
                        ⚠ Shorts carry NO clickable links (since Aug 2023): funnel from shorts =
                        verbal/on-screen CTA + channel profile link + related-video → our long-form
TIER 2 · TRUST          Long-form channel (UTM-tagged description links) · registry articles ·
                        Substack/Medium essays (existing, manual)
TIER 3 · OWNED          Registry technique & location pages WITH VIDEO EMBEDS (VideoObject JSON-LD)
                        ← the base case: pages get unique media no competitor pSEO site has
TIER 4 · REVENUE        B2B profile claims + SaaS (primary) · ads/sponsors later (upside; blended
                        long-form RPM modeled at ~$4–8, not the raw-spec $8–18)
```

The strategic inversion from the raw spec: **Tier 3 embeds are the guaranteed payoff; Tier 1
virality is the option.** Every produced video improves owned pages on day one.

## 2. Channel architecture: one audience promise per channel, lanes within it

Evidence cuts both ways and the resolution is scoped breadth:

- Sam O'Nella (~4.8M subs) proves one channel can span history/biology/food when the **persona +
  art style is the product**. The operator's lane-rotation research (series badges, playlist
  shelves, predictable rotation days) is the operationalization of that model.
- MinutePhysics proves the opposite discipline: its creator launched *separate* channels
  (MinuteEarth, MinuteFood) rather than dilute one brand's promise.
- The synthesis: **lanes rotate within one audience promise; new audience promises get new
  channels.** BJJ parents, adult grapplers, and combat-history nerds share a promise ("the
  science and story of fighting, in stick figures"). Data-center electricians do not.

**Decision:**

| Channel | Promise | Lanes (badge-coded, rotation-scheduled) | Status |
|---|---|---|---|
| **Channel 1 — combat-science** | stick-figure science & story of grappling | *Physics of Grappling* (blue) · *Combat History* (green) · *The Honest Guide* (kids/parents + gym-culture, red) | launch now; pilot = first two lanes |
| Channel 2 — trades | how the physical economy gets built | *Data-Center Trades* · *Licensing & Pay* | Phase 2, after pipeline proven + naming reconciled |
| Finance lane — *Systems & Blowups* | how markets break (educational/historical) | famous blowups · market mechanics · energy/grid economics | post-pilot: **unblocked** — the operator (ex-JPMorgan Chase, business major) is the named human persona the 2026 policy bucket requires; hard no-recommendations rule; lane-vs-sister-channel placement decided at post-pilot review |

Rotation applies within Channel 1 (e.g., Physics on Fridays, History on Saturdays), preserving
the operator's predictable-return-day insight without mixing audience promises.

## 3. Editorial standards (the accretive tier, enforced)

1. **Information gain is mandatory.** ≥3 only-here specifics per long-form video, drawn from the
   fact layer (registry counts, named lineages with provenance, real lever mechanics). "Wikipedia
   with jokes" fails Gate A regardless of polish (`06-SCRIPT-TRANSFORMATION-SPEC` §5).
2. **Persona lives in the writing.** Benchmark warning: none of the four comparable channels
   succeeded on a generic voice — the comic persona is the moat. Ours must be carried by script
   craft: recurring cast from video one (`tap_frantic` uke, `gym_enforcer`, `bowler_hat_maeda`),
   catchphrases, running gags that compound across videos, tonal whiplash (deadpan narration,
   absurd visuals). Gags are pose-library assets, so comedy compounds into brand.
3. **Claims policy.** Every number/medical/financial/historical assertion → sourced claims-ledger
   entry or it doesn't ship. Medical content (joint safety, kids safety) requires literature
   sources and ships with maximum human fingerprints; credential framing requires a real named
   expert. Finance content: educational, historical, mechanistic only — **no stock or asset
   recommendations, no forward-looking advice**, standard not-financial-advice disclaimer; the
   operator's real credentials (ex-JPMorgan Chase) are the named persona and satisfy the `expert`
   object for finance runs.
4. **Native-first shorts.** Repurposed long-form clips are unproven among benchmarks; verticals
   are designed as their own 40–55s pieces (own hook line, reordered scenes) even when built
   from long-form scene subsets.
5. **No realistic re-creations** of real people/events — brand rule and the disclosure trigger.

## 4. Voice policy

- **Recommended: clone the operator's own voice.** Strongest persona ownership; explicitly
  exempt from YouTube's synthetic-content disclosure; immune to ElevenLabs Default-voice
  retirement (2026-12-31); fixable pacing via re-records of source samples.
- Acceptable: a custom-designed synthetic voice (never library Defaults — they are the
  mass-production audio fingerprint and are being retired anyway).
- Script-side: punctuation-driven pauses, contractions, short sentences (140 WPM basis);
  stability/style settings snapshotted per run for reproducibility.
- One voice across all lanes of Channel 1 — the voice IS the channel identity.

## 5. Platform compliance posture (YPP "inauthentic content," 2026 state)

Enforcement is **channel-level** (theme, top videos, newest uploads, metadata) with three
buckets: generic/repetitive template content; manipulative/interchangeable content; AI personas
on sensitive topics (health, **finance**, legal, politics). YouTube states it is tool-agnostic:
AI assistance is fine where the output carries original, authentic insight.

Our mitigations, by design rather than by exception:

1. Two human gates per video; rubric scores persisted (auditable editorial judgment).
2. Per-video unique storyboards, scene mixes, and gags — catalog-level variation is the actual
   review surface, so lane rotation also serves compliance.
3. Fact-layer information gain = "original, authentic insights" made literal.
4. Custom/cloned voice; no stock-voice fingerprint.
5. Health-adjacent content (orthopedic lane) gets literature citations on screen + operator
   review; finance ships only under the operator's named, real persona with the
   no-recommendations rule.
6. Monetization application deferred until the catalog demonstrates the pattern (per-video
   originality is necessary but not sufficient — the channel must read as varied).

## 6. Cadence

- **Pilot (wks 1–6):** ~2–3 shorts/week + 1 long-form per ~10 days (5 episodes total), per
  `07-PILOT-SEASON.md`. Production order rises in claims complexity.
- **Post-pilot target (P1):** hold long-form at 1/week (quality-gated), shorts 3–5/week — the
  volume-funnel lane suits a programmatic pipeline (marginal cost is where we're unbeatable);
  the event-upload lane (OverSimplified: 3–4/yr spectacle) is not our comparative advantage.
- Cadence never overrides Gate A: a missed week is cheaper than a slop upload on a
  channel-level-reviewed catalog.

## 7. Distribution beyond the channel

- **Embeds first:** every technique video → its technique page + technique × location pages via
  the registry's gated import (`embed_payload.json`). Rich-result stacking: `HowTo` + `VideoObject`.
- Article ↔ video cross-linking both directions (long-form descriptions carry UTM'd article links;
  articles gain a "watch the breakdown" block).
- Substack/Medium essays and community posts (Reddit/X) remain **manual, value-dense, human** —
  no automation; they are relationship surfaces, not pipeline outputs.

## 8. Measurement discipline

- UTM taxonomy: `utm_source=youtube&utm_medium={longform|profile}&utm_campaign={job_slug}`.
- Weekly one-page report (pilot): retention vs bars, funnel sessions, embed-cohort engagement
  delta, cost + human-minutes per video, rubric score trend.
- Analytics snapshots at day 7/28 per video into `runtime/jobs/<id>/analytics/` — the evidence
  base for the kill/pivot evaluation in `00` §5.
