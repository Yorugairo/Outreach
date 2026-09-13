# The portable docs, audited against the later record (P54 T3, 2026-09-13)

The operator: *"those portable docs are probably more stale than we care to admit."* They are. Every file under
`docs/portable/` is loaded by any agent doing video work, so a stale claim there teaches every lane the wrong rule.

Three read-only explorers read each doc whole, listed its concrete claims, and checked each against the rulings dated
after the doc's last change, the superseded/conflict verdicts in `TRIAGE.jsonl`, and the canonical docs that moved on
(doc 29, 37, 39, 41, CAPABILITIES, PIPELINE, SHORT-FORM-SHAPE). Both sides are quoted in their reports; this page is
the ranked summary and the fix list. **A report, not a rewrite** - the operator orders the fixes (P54 "Not Building").
`OPERATOR-RULINGS.md` is the source the others are measured against and was not audited.

## Ranked

| # | doc | last change | stale claims | severity | the headline |
| --- | --- | --- | --- | --- | --- |
| 1 | `BUILD-PIPELINE.md` | 2026-08-30 | 14 | high | several gate-FAILing defaults: the 20 s ceiling E69 withdrew, the wipe on every plate (E47), a chart held across a boundary (E25/M12), lower-third captions (E21/E62/M08), ~3 break tags (doc 37 §21: zero), the old palette (E67), base64 assets (the split player) |
| 2 | `DOCTRINE-CORE.md` | 2026-09-03 | 9 | high | it is 10,725 characters against its own 10,000 cap; the promise window 0:30-1:00 (E24/G09: by 0:45); shorts held to the doc-29 bar (E35); plates-first worlds (E61); synthesized narration shipped on YouTube (E70); the triad written into a short (E41/S07); the chart kept off the hook (E44/E73) |
| 3 | `CHART-DISCIPLINE.md` | 2026-08-31 | 7 | high | it calls itself sufficient and has none of E28's amendments, E50, E52, E53, E56, E58, E60, E67; the combo as stacked tiers (E53 §4: overlay); end labels <= 6 chars (E52/E53: named at the end); "the ten failure classes" lists 11 |
| 4 | `VOICE-PACK.md` | 2026-09-12 | 4 | medium | "second person carries the payoff" vs the operator's shared-stake close; `align_take.py --script` shown as optional (R26-69: required); YouTube voice is OPEN, not just "not Chirp" (E70); 5-22-word sentences vs S08's 18 on a short |
| 5 | `SOUND-SOURCING.md` | 2026-08-31 | 3 | medium | Stable Audio for SFX (HG5: CC0 via Freesound); cues from CHOREOGRAPHY.md (now SOUND-PLAN.json, M29, the mount takes no cue); ATTRIBUTIONS.md pasted at upload (publish_package.py carries none); no levels at all (E54 -20 LU short, accents 8-10 dB under) |
| 6 | `OUTRO-CTA-PLAYBOOK.md` | 2026-08-30 | 3 | medium | "keep our slow holds" reversed by E69's pulse; the silent end card vs the stitched brand line on shorts (E41 §2); Script G cited as the example (frozen, superseded by rewrite H) |
| 7 | `PACKAGING-PLAYBOOK.md` | 2026-08-31 | 3 | medium | house-style thumbnails "banked" vs "we're A/B testing thumbnails now" (E61) and "the chart is the thumbnail" (E67 §4); the iron spike as thumbnail object (A1 already refused it); Bravos in the title (rejected for Steel and Paper) |
| 8 | `MOTION-GRAMMAR.md` | 2026-08-30 | 3 | low | "slow sine wander" vs E49's named idle; "full-frame, never framed" over a ledger page vs E45/E63; CSS eases vs the springs (E45) |

**46 stale claims in 8 docs.** The two always-loaded files (`DOCTRINE-CORE`, `VOICE-PACK`) carry 13 of them.

## Stale outside `docs/portable/`, found on the way

- `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §9.15 item 2 still lets evidence persist across a boundary (E25/§9.30 ban a chart held across plates); §9.23b names series "at the line's start" (E53 §8: at its end); §9.22 still describes the combo as a histogram band (E53 §4: an overlay).
- `docs/content-video-engine/37-TTS-DELIVERY-STANDARDS.md` §1 and §18 still carry the "~3 tags" cap that its own §21 retired.
- `docs/content-video-engine/39-EVIDENCE-CHART-SYSTEM.md` line ~165 lists "Part-to-whole: stacked bar, <= 4 segments" (E53 §2: no stacked bars); §10.1 rule 5 honours `prefers-reduced-motion` in the video (the operator: console only - TRIAGE conflict `02dbf7702cd8`).
- `docs/content-video-engine/08-TOOLING-ALTERNATIVES.md` §7 still adopts Magnific (cancelled - conflict `9821f0386743`).
- `docs/content-video-engine/21-ART-STYLE-REFERENCE-REVIEW.md` "What this does and does not prove" argues against winning on presentation (conflict `ee466c018002`), never marked overturned.
- `docs/content-video-engine/PIPELINE.md` "render contract" still says base64-embedded assets while its stage 8 describes the split player.
- `.agents/skills/brand-voice/SKILL.md` "Facebook dials": the bed 24-26 LU under on Facebook, 26-28 on YouTube (E54: -20 LU, no louder).
- `docs/agent-memory/operator/shorts-lane-phase1-standard.md`: the film reel "10 dB under the mix" (the operator set reel -22 / music -26).
- `docs/portable/OPERATOR-RULINGS.md` E52 §4 (plain signed bars beat a combo) was never amended for the fixed combo builder kept behind `FED_WITH_BARS=1`.

## What an order to fix these would look like (for the operator)

1. **BUILD-PIPELINE and DOCTRINE-CORE first** - they are loaded by every agent and several of their defaults FAIL a gate
   today. DOCTRINE-CORE must LOSE 725+ characters before it can gain the E24/E35/E41/E61/E70/E73 corrections.
2. **CHART-DISCIPLINE** - either fold E28/E50/E52/E53/E56/E58/E60/E67 in, or stop it claiming sufficiency and route to
   them; its combo and label rules contradict E53 outright.
3. The medium four, then the out-of-portable list above - most are one-line amendments pointing at the ruling.
4. Wherever a ruling candidate from `TRIAGE-DIGEST.md` is ruled (the 8-minute floor, the Facebook close, "your borrowing
   costs", the level-line axis floor, foley level, the shared-stake close, the stale officeholder), it lands in
   DOCTRINE-CORE, VOICE-PACK or CHART-DISCIPLINE - within DOCTRINE-CORE's cap.

Sources: the three explorer reports of 2026-09-13 (session 45114c3b), each quoting both sides with `path:heading` or an
E-id; the parent verified the DOCTRINE-CORE character count, the BUILD-PIPELINE 20 s line and the CHART-DISCIPLINE
class count on disk before writing this page.
