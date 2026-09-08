# How Japan Tricked Trump — v3 build (own worlds, five distinct charts) and the pre-review pass (Claude, 2026-09-07)

The short is BUILT and watchable, quarantined until the operator's word (no render yet).

- Player: `python serve_player.py 8734 build-short` → http://127.0.0.1:8734/player.html (also `.claude/launch.json` → `japan-short-player`)
- Build: `python build_short.py` → `build-short/player.html`, `build-short/japan-short.timeline.json`, `build-short/GATES-MOTION.md`
- Clock: `vo-short/audio/scene_1.mp3` = the Chirp scratch take (83.26 s), word-timed locally by the new
  `content/video_engine/scripts/align_take_whisper.py` (faster-whisper small.en, 89% verbatim match, the numerals interpolated).
  Gemini's `scratch-kokoro.words.json` was the KOKORO take's clock (118 s) and could not drive this audio.
- Motion gate: 0 FAIL / 2 WARN / 12 PASS. M06 caption density 42/min at 4.0 words a page (Chirp's 170 WPM);
  M11 no sound cue on the hook page's mount (the same WARN Tokyo carries: a mount is silent by ruling). M21 INFO: the parts page
  sits 10.0 s after its last data mark (0:21 → 0:31), inside the 12 s ceiling.
- Runtime 89.36 s: the take, 0.7 s, the brand line, the card from 83.16 s.

## The shape (E44 / E45 / E50, the Tokyo v3 grammar) — v2, on this story's own stills

**Five distinct charts, none reused** (operator, 2026-09-07: "we still need new charts/graphs instead of re-using the treasury over and over"): the holdings line once, at the hook; the parts and receipt bars (DERIVED); Japan's monthly selling (REAL); US customs duties (REAL). Twelve stills generated 2026-09-07 in Flow (Nano Banana Pro, 0 credits) on the bound **HollowStickMike**, two arms in
`omni-video/stills/` (`CONTACT-SHEET.png`): `still-*` charcoal on cream with one red accent (the cut is built on these),
`sig-*` the operator's signature line verbatim ("A light application of woodblock print and vox newspaper meets rich anime
colors"). Build the other arm with `python build_short.py --arm sig` — same rows.

| # | span | world | what happens on which word |
|---|---|---|---|
| 1 | 0:00–0:02 | the victory lap at the podium (still-a) | "Trump announced he beat Japan on tariffs" |
| 2 | 0:02–0:14 | **Japan's holdings page** mounts on "Instead" (E44) | the line draws to the Feb peak, the June stroke follows the landing, the −$122.6B bracket writes on "what nobody explained" |
| 3 | 0:14–0:18 | the red truck before six barriers (still-b) | "its parts cross the border six separate times" |
| 4 | 0:18–0:31 | **parts page** mounts on "An engine block" | the engine bar spotlit as the bars land, the harness called out after; the two lanes (still-c) DOCK on "In the left lane"; the title rewrites to "The right lane: Detroit's parts bill" on "In the right" |
| 5 | 0:31–0:37 | the car carrier, one ramp, one stamp (still-d) | "Toyota crosses once. Tokyo pays a flat fifteen percent" |
| 6 | 0:37–0:48 | **receipt page** mounts on "the math breaks Detroit" | Detroit's $6,240 bar spotlit on "six thousand dollars"; the page's own badge: BUILT IN AMERICA +$1,740 |
| 7 | 0:48–0:50 | the vault, shelves emptying (still-e) | "the second lever" |
| 8 | 0:50–1:04 | **Japan's selling page** (NEW: four monthly bars, Mar −$47.7B, Apr +$18.3B, May −$66.8B, Jun −$26.4B, from the live TIC table) mounts over the vault on "Instead of reinvesting" | the bars land under "of Washington's debt", May is called out; the page's badge: FEB TO JUN 2026 −$122.6B; the gate-to-the-fab clip docks on "pledging" |
| 9 | 1:04–1:09 | two fingers to camera (Tokyo's clip-g) | "the double squeeze" |
| 10 | 1:09–1:13 | the blank cheque pushed across the desk (still-h) | "we wrote them a blank check anyway" |
| 11 | 1:13–1:23 | **customs duties page** (NEW: FRED B235RC1Q027SBEA, quarterly since 2015 — $97bn/yr in early 2025, $364bn/yr by late 2025) mounts over the cheque on "the policy backfired" | the podium docks on "Washington signed", the vault on "Then Tokyo checked" (E48 callbacks as cards); the line lands under "America used the tariff", the peak is spotlit on "tax its own cars", "$364bn a year" is written on "while Tokyo funded" |
| 12 | 1:23–1:29 | the outro card | the brand line under it |

**Character drift, the finding of the day:** the hollow face holds in a simple frame and drifts to a solid-faced variant, or
to a stranger, when the scene is busy (the ship, the six gates in colour, the vault in colour). Arm A picks: a, b, e, h clean;
c and d needed a retry with the character named FIRST in the prompt (c fixed; d's retry lost him entirely, so the drifted first
ship stays). Arm B: a, c, h clean; b, d, e drifted. Rule that follows: name the character before the scene, keep the scene to
one prop, and expect a retry on any frame with a crowd, a machine or a vehicle.

## Evidence pass (E18) — what I verified myself vs. what the hand-off asserts

| figure | verdict |
|---|---|
| −$122.6B (Feb 2026 $1,239.3B → Jun 2026 $1,116.7B) | **VERIFIED live** against `ticdata.treasury.gov/Publish/slt_table5.txt` today; the Tokyo object `ev-japan-holdings-v1` already carries both points and is reused. (`mfh.txt`, the URL the dossier cites, serves a stale Jan-2023 table — cite `slt_table5.txt`.) |
| 15% on finished autos, 25% on parts (HTS 8708), ¥10T METI package, 6–8 crossings | cited by the dossier, **not re-fetched by me**. The 25%-on-an-Ontario-engine line is the editorial soft spot: USMCA-compliant parts are taxed on non-US content, not the whole part. |
| $6,240 "stacked duties" | **DERIVED and not reproducible from its stated inputs**: $18,000 × 25% = $4,500, and the three named components ($1,450 + $820 + $1,680) sum to $3,950. On screen it is labelled DERIVED and the model is named in the source line. |
| "a bankrupt Detroit" | archetype hyperbole, unsourced. |
| dossier hygiene | one row says holdings fell $1,153.1B → $1,116.7B (stale, contradicts the proof line); two rows ("Toyota stock +14%", "Detroit lobbied") are not in the script. Every "Verified 2026-09-07" stamp is Gemini's, not a fetch log. |

Packaging QC: title A's "$122 billion" is the verified figure — good. The thumbnails' figures ($6,240 / $4,500) are the derived ones.

## DECISIONS (each with a recommendation; the baseline ships as built)

1. **The $6,240.** Recommend keeping the spoken line ("over six thousand dollars") only if the operator accepts the CAR-style
   model on screen as labelled; otherwise the honest line is the parts cascade as spoken (25% at each crossing) without a total,
   and the receipt page becomes $4,500 vs "$1,450 + $820 + $1,680, and three more crossings". Script edits are Gemini's file — I did not touch it.
2. **The voice.** The take is Chirp 3 HD Charon, the Facebook-lane ship voice; YouTube masters are ElevenLabs (voice-lane ruling).
   Recommend: watch v1 on Chirp, and on the cut's approval record with `record_short_take.py --go` — every row re-times itself from the new words.
3. **The worlds.** RESOLVED — generated (see the shape above). Open only: which arm (charcoal vs signature), and whether the drifted ship still is acceptable or gets a third pass.
4. **The thumbnail.** The `$122B TRAP` vault-to-wafer composition (`thumbnails/thumb_hollowmike_02_vault_silicon.png`) answers title A and sentence 1 best (J12). (My first note called the HollowStickMike reference off-model — wrong: HollowStickMike is the bound character; the thumbnails are on-model.)
5. **J50 / the [new]@0:50 tag.** The [post-key] names a compound mechanism (the tariff funded Japan's chips AND cost $122B). The
   engine, the harness and "Toyota crosses once" are one mechanism (a tariff at a crossing); the Treasury sale is a second one,
   joined by "the double squeeze". Verdict on `[new]@0:50`: **laundered** (a new mechanism, not a new variable); the other nine
   declared tags read true. Not a build blocker; a script call.

## The SCREENS declared tags — verdicts (CHECK-RESPONSIBILITIES R2)

- `[rehook]@0:11` true · `[new]@0:18` true · `[archetype]@0:28` true · `[catalyst]@0:32` true · `[rehook]@0:38` true
- `[rehook]@0:50` true · `[new]@0:50` **laundered** (see DECISION 5) · `[catalyst]@1:02` true · `[rehook]@1:18` true · `[ring]@1:24` true
- The G13/G22 "FAIL" windows on the first two are long-form windows; G2 short mode does not bind them (E41).

## Known limits of v1

- Story bars render in the template's green regardless of the series colour token (red Detroit / blue Toyota intended) — a template rule, backlog.
- The cadence report warns the return page holds 13.6 s on one dock (the Tokyo shape has the same row).
- `measure_frozen_frames.py` not run (M18 INFO).
- Render, after the word: `RENDER_BUILD=<build-short> RENDER_URL=http://127.0.0.1:8734/player.html RENDER_NAME=japan-short RENDER_ASPECT=9:16 python content/video_engine/scripts/render_episode.py` (1440×2560 once, every platform).
