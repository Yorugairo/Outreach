# REWRITE ORDER B — "The Myth of Historical Normal"

**Status: DRAFT — awaiting the operator's approval.**

Scope: the three open requests of BACKLOG **R26-109** (bridge reply `f4541f7f6808`, REQUEST CHANGES, read
2026-09-13). This order collects them into one artifact and hands them to **letter B**. Letter A —
the on-disk `SCRIPT-VO.txt` — is not patched (`docs/agent-memory/operator/script-changes-go-to-next-letter.md:20`:
"when more than one change is due, write them into a rewrite order and draft the next letter from it; leave the
previous letter and its take byte-identical").

**Letter naming:** the project's scripts carry no letter (`SCRIPT-VO.txt`, `SCRIPT-PRODUCTION.md`,
`SCRIPT-SCREENS.md`, `SCRIPT-GATES.md`). The on-disk `SCRIPT-VO.txt` is treated as **letter A**; this order
names **letter B** (`SCRIPT-VO-B.txt`). `timing_source: estimated (no take on disk)` — no take exists yet, so
no audio is desynchronised by B; the byte-identical rule still binds on A.

**Measurement commands (run 2026-09-13, read-only: the script was copied to a scratch dir so the runner's
`SCRIPT-GATES.md` never lands in the project; no git state changed):**

```
python content/video_engine/scripts/run_script_gates.py <scratch>/SCRIPT-VO.txt --long --ring percent
python content/video_engine/scripts/run_script_gates.py <scratch>/SCRIPT-VO.txt --long --ring weight \
    --title 'The Myth of "Historical Normal": How Small Changes Break Big Markets'
```

Verbatim tail (the `--ring percent` run):

```
=== SCRIPT GATES: SCRIPT-VO.txt ===
TOOLS      lint: exit 0, 0 fails | audit: exit 0, 0/0, timing=estimated |
           opening gate: exit 1, 1/1/46/12 | screens: SCRIPT-SCREENS.md, 90 items
VERDICT: FAIL (1 failing tools)
```

`lint_species_choice.py` was **not** run: this project has no build directory (only `assets/` and `edit/`),
so there is no timeline for it to read.

---

## 1. The three requests, quoted, with their evidence on disk

### Request (5) — the ERP contradicts itself three ways

> "**5. ERP contradicts itself three ways:** `-0.95%` (blueprint, Bravos pack, EVIDENCE-COVERAGE), `-0.97%`
> (`VISUAL-CHOREOGRAPHY.md:36`, computed off a 5.00% 10Y), and `-0.5% to +0.2%` (`EVIDENCE-DOSSIER.md:22`) — a
> range that doesn't contain either."
> — `docs/research/runs/bridge/replied/f4541f7f6808…/reply.md:28`

On disk today:

| value | where | how it is reached |
|---|---|---|
| **-0.97%** | `VISUAL-CHOREOGRAPHY.md:36` | `1/24.8 = 4.03%` earnings yield minus a **5.00%** 10Y — reproduces exactly |
| **-0.95%** | `BRAVOS-STYLE-EVIDENCE-PACK.md:50`, `edit/EVIDENCE-COVERAGE.md:33` (`BADGE-08`), `REVIEW_BRIEF_FOR_CLAUDE.md:49` | **reproduces from no pair stated anywhere in the package** (see §2) |
| **-0.5% to +0.2%** | `EVIDENCE-DOSSIER.md:22` | a stated 2024-2026 range; it contains neither point estimate |

Confirmed still open by the packet's own close: `docs/research/runs/bridge/done/f4541f7f6808…/result.md:16` —
"Still open on disk: `VISUAL-CHOREOGRAPHY.md:36` carries `Equity Risk Premium = -0.97%` and zeta = 0.82
(blockers 5 and 7)."

### Request (6) — ~39 s of narration has no scene

> "**6. ~39s of narration has no scene.** The cut table runs `0:00–8:00` across 11 scenes = **480s**. The
> doctrine gate measures the script at **518.6s (8:38)**. `EVIDENCE-COVERAGE.md:5` asserts "Runtime: 8:00
> (480.0s)". Every downstream allocation is budgeted against a runtime the script doesn't have."
> — `reply.md:30`

The gap is **wider now, not fixed** (`result.md:14`). Measured today:

- `audit_script_doctrine.py` via the runner: **`runtime_s: 565.4`** (`runtime: 9m 25s`), `timing_source:
  estimated (no take on disk)`.
- `VISUAL-CHOREOGRAPHY.md:32-42` — 11 scenes, `0:00–8:00`, "Hard stop at 8:00" (`:42`) = **480.0 s**.
- `edit/EVIDENCE-COVERAGE.md:5` — "**Runtime: 8:00 (480.0s)** · 11 Scenes".
- **565.4 − 480.0 = 85.4 s of narration with no scene row.**

Second contradiction found while measuring (flagged, not ordered): the two scene tables also disagree with
**each other** — `VISUAL-CHOREOGRAPHY.md:32` puts SC-01 at `0:00–0:08` and `:36` puts SC-05 at `2:15–2:50`,
while `edit/EVIDENCE-COVERAGE.md:28` puts SC-01 at `0:00–0:45` and `:32` puts SC-05 at `3:10–4:00`. Both claim
480.0 s over 11 scenes; neither interior can be the other's.

### Request (7) — the spring spec contradicts itself

> "**7. Spring spec contradicts itself.** `VISUAL-CHOREOGRAPHY.md:8` declares ζ=0.82, ω₀=14.5 rad/s; line 61
> declares `revealSpring {damping: 18, stiffness: 130}` → ζ=0.789, ω₀=11.40. To match the header it needs
> `stiffness≈210, damping≈23.8`. Also SC-09 uses ζ=0.88 without explanation."
> — `reply.md:34`

On disk: `VISUAL-CHOREOGRAPHY.md:8` (`zeta = 0.82`, `omega_0 = 14.5 rad/s`), `:61`
(`"revealSpring": { "damping": 18, "stiffness": 130 }`), `:40` (SC-09 `zeta = 0.88`), and the header pair is
echoed a third time as a PASS row in `edit/EVIDENCE-COVERAGE.md:19`.

---

## 2. The ERP — which value letter B carries

**What the raw payload settles.** `docs/research/runs/treasury_yield_spike_september_2026/raw_payloads/`
holds `DGS2.csv`, `DGS10.csv`, `DGS30.csv`, `GFDEGDQ188S.csv`, `A091RC1Q027SBEA.csv`. `DGS10.csv`'s last
observation is **`2026-09-09,4.83`**. So the payload settles the **10Y leg at 4.83%** — which is neither the
5.00% behind -0.97% nor the 4.95% the brief and the coverage table lean on.

**What the payload does not settle.** There is **no S&P 500 P/E or earnings series in `raw_payloads/`**. The
earnings-yield leg (24.8x → 4.03% at `VISUAL-CHOREOGRAPHY.md:36`; ~24.5x → 4.08% at `EVIDENCE-DOSSIER.md:18`)
has no retrieved payload on disk. **`[verify]`**.

Arithmetic (computed, both legs stated):

| P/E | earnings yield | 10Y | ERP |
|---|---|---|---|
| 24.8x | 4.03% | 5.00% (choreography) | **-0.97%** |
| 24.8x | 4.03% | **4.83% (DGS10 payload)** | **-0.80%** |
| 24.5x | 4.08% | 4.83% (DGS10 payload) | -0.75% |
| 24.8x | 4.03% | 4.95% (brief) | -0.92% |

**-0.95% reproduces from no pair stated in the package.** It is the most-cited of the three and the only one
with no derivation on disk.

**The order proposes:**

1. **One ERP figure across the package, and it is derived at the payload's 10Y.** Letter B's evidence layer
   carries **ERP = -0.80% `[verify]`** — sourced leg `10Y 4.83% (FRED DGS10, 2026-09-09,
   raw_payloads/DGS10.csv)`, unsourced leg `S&P 500 trailing P/E 24.8x → EY 4.03% [verify]`. The `[verify]`
   tag stays until a P/E payload lands beside the FRED CSVs.
2. **Preferred on screen: draw the gap, don't print a third decimal.** The badge states the two legs it can
   name and the balance scale renders the spread; a printed ERP decimal enters only when both legs have a
   payload. (Operator's call — 1 and 2 are compatible; 2 is the safer screen.)
3. **-0.95% is retired**, not re-derived: it has no stated pair.

**Where the other two get corrected** (documents, not letter A):

| file:line | today | letter B |
|---|---|---|
| `VISUAL-CHOREOGRAPHY.md:36` | `Equity Risk Premium = -0.97%`, "right pan slams down with 5.00% weight", "Left pan drops at 4.08%" vs badge "Earnings Yield = 4.03%" | the single value; 10Y leg **4.83%** with its payload cite; the pan figure and the badge figure made the same number |
| `edit/EVIDENCE-COVERAGE.md:33` | `BADGE-08`: Sept 2026 ERP `-0.95%` | the single value + `[verify]` |
| `BRAVOS-STYLE-EVIDENCE-PACK.md:50` | `-0.95%` (and a `-0.62%` prior) | the single value + `[verify]`; the prior carries its own source or goes |
| `EVIDENCE-DOSSIER.md:22` | `2024-2026: -0.5% to +0.2%` | restated so it contains the point estimate, or dropped as unsourced |

**Script line: none.** Letter A speaks no ERP number — `SCRIPT-VO.txt:51` says only "The equity risk premium
has turned upside down." Letter B keeps that sentence as-is; request (5) is an evidence-layer correction, not
a rewrite of spoken text.

---

## 3. The uncovered narration — 85.4 s with no scene

No build exists, so the spans below come from the **script's paragraph clock**, computed with the gate's own
estimator (`audit_script_doctrine.secs`, `CHARS_PER_SEC = 16.29`) over `SCRIPT-VO.txt`. Paragraph clock
accounts 84.5 s of the 85.4 s; the 0.9 s remainder is inter-paragraph rounding against the whole-text
measure. Every scene proposal is a **RECIPE** from `docs/EFFECTS-CATALOG.md` §Recipes, quoted from
`effects_card.py`. **These are proposals. The author binds.**

| # | script | span (paragraph clock) | s | narration |
|---|---|---|---|---|
| U1 | `SCRIPT-VO.txt:49` (tail) | 8:00.00–8:11.52 | 11.5 | "In twenty twenty-six, a system burdened with one hundred and twenty-four percent debt treats that same yield like an anvil." |
| U2 | `SCRIPT-VO.txt:51` | 8:11.52–8:25.68 | 14.2 | "The mechanical facts are open to anyone who verifies them. The equity risk premium has turned upside down. Federal interest outlays now outpace the entire defense budget. And corporate balance sheets face a three-trillion-dollar rollover shock." |
| U3 | `SCRIPT-VO.txt:53` | 8:25.68–8:46.71 | 21.0 | "Which is why my allocation stance is deliberate. … Yet broad index funds, dominated by long-duration companies priced for permanent zero-rate liquidity, carry the unrecognized shock." |
| U4 | `SCRIPT-VO.txt:55` | 8:46.71–8:52.62 | 5.9 | "The debt gets accumulated. The yield gets normalized. And the carrying cost breaks the balance sheet." |
| U5 | `SCRIPT-VO.txt:57` | 8:52.62–9:22.55 | 29.9 | "You now have the three-question diagnostic. Subscribe for the quarterly tripwire monitor … You will already know the resilience of the bridge when a five percent rate tests it." |
| U6 | `SCRIPT-VO.txt:59` | 9:22.55–9:24.46 | 1.9 | "The line stays on the chart." |

### Proposed scenes (recipes)

**U1 → `recipe:emphasized-bar-lit` — "The emphasized bar, badged then lit"** (proven, count 2, acts
COMPARES/TURNS, window 8s). Members: `+0s page_builder:bars` · `+0s dock_option:badge` ·
`+7.55s species:spotlight` (the light lands on the datum whose index equals `emphasize`).
Why: two eras, one axis — 1981's 30% deck against 2026's 124%; the 2026 bar is badged as the page builds and
lit as the word "anvil" lands. Proof: `japan-tariff-trick/build-short` @ 35.26s.

**U2 → `recipe:badge-ladder`** (proven, count 41 — a grammar; QUOTES/EXPLAINS, window 6s). Members:
`+0s dock_kind:image` · `+2.05s / +3.35s / +4.65s dock_option:badge` (dials `FIRST_BADGE_S`=2.05,
`BADGE_GAP_S`=1.3). Why: the paragraph is three verifiable facts in three clauses — one badge per clause on
the measured beat. The ERP badge here is the one §2 governs. Proof: `steel-and-paper/build-f` @ 50.4s.

**U3 → `recipe:held-dock-across-the-cut` — "The dock outlives the world change"** (proven, count 16;
EXPLAINS/QUOTES, window 22s). Members: `+0s dock_payload:chart` · `+0..21.9s exit:wipe wipe_right`. Why: 21.0 s
is one argument (fortress balance sheet vs index fund) — one card carries it while the world wipes beneath,
rather than three cuts. Proof: `steel-and-paper/build-f` @ 50.4s.

**U4 → `recipe:trace-callout-ladder`** (proven, count 4; NAMES, window 6s — exactly the 5.9 s span). Members:
`+0s species:trace` · `+0.55s species:callout` · `+1.26s` · `+1.81s` · `+2.52s` · `+3.07s` — three
hop-and-label pairs on the 1.26 s beat, one per clause of the tricolon. Proof: `japan-tariff-trick/build-short`
@ 9.22s. **Alternate** if the tricolon should land on one number instead of three marks:
`recipe:punch-then-callout` (proven, TURNS, 6s; `+0s page_enter:spiral` · `+0.12s species:punch` ·
`+3.88s species:callout`).

**U5 → `recipe:verdict-recap` — "The nine-proof recap"** (proven; SETS/QUOTES, window 26s) at 8:52.62, then
**`recipe:outro-clip-life`** (proven; SETS, window 6.5s) from ~9:18. Members (recap): `+0s dock_payload:stack`
· `+1.14s dock_payload:stack` (each proof flies in on its own phrase) · `+25.25s dock_payload:stack` (the rail
bursts on the pivot line). Why: the close re-enters every proof the episode made, which is exactly what the
recipe does. Proof: `steel-and-paper/build-f` @ 701.73s.

**U6 → folded into `recipe:outro-clip-life`** (proven; `+0s plate_option:clip` · `+0s species:life` ·
`+6.2s exit:dip` — the clip runs its whole 6.2 s and the cut dips through black on its last frame). The
1.9 s final line rides the outro clip's own life; no separate scene. Proof: `japan-tariff-trick/build-short`
@ 79.08s.

**The table's own repair (letter B's choreography):** the scene table stops declaring `Hard stop at 8:00` and
is rebuilt against the measured clock — 565.4 s while `timing_source: estimated`, then re-cut against the
take's measured timeline the moment one is recorded (`reply.md:30`: "record a take to settle this before
choreography is trusted"). `edit/EVIDENCE-COVERAGE.md:5` states the measured runtime and its source, never a
round 480.0.

---

## 4. The spring spec — which pair the order keeps

**Assumption stated:** ζ = c / (2·√(k·m)) needs a mass. Remotion's spring takes **mass = 1** by default, and
`VISUAL-CHOREOGRAPHY.md:61` states no mass, so **m = 1 (unit mass)** is assumed throughout below.

| pair | ζ | ω₀ | overshoot Mp | settle (ζ·ω₀) |
|---|---|---|---|---|
| `:8` header ζ=0.82, ω₀=14.5 | 0.82 | 14.5 rad/s | 1.11% | 11.89 |
| `:61` damping 18 / stiffness 130, m=1 | **0.7894** | **11.4018 rad/s** | 1.76% | 9.00 |
| `:40` SC-09 ζ=0.88 | 0.88 | — | 0.297% | — |
| house default (`kinetics/spring.mjs:14`, Mp 0.04 / settle 6) | 0.7156 | 8.384 rad/s | 4.00% | 6 |

**The free parameter does not reconcile them.** Solving c=18, k=130 for ζ=0.82 gives m = 0.9266, and that mass
gives ω₀ = 11.844 rad/s — still not 14.5. No single mass satisfies both lines.

**The order keeps the header pair: ζ = 0.82, ω₀ = 14.5 rad/s.** Grounds, in order:

1. The engine is parameterised that way. `content/video_engine/scripts/kinetics/spring.mjs` is the source of
   truth for the settle (`:1-12`) and its one entry point `springParams(Mp, settle)` returns **`{ z, w, wd }`**
   (`:17-21`); `springEval` consumes `z` and `w` (`:24`). **Nothing in the repo reads `damping`/`stiffness`** —
   that JSON is a Remotion-shaped parameterisation the engine never sees.
2. The header pair is declared in three places (`VISUAL-CHOREOGRAPHY.md:8`, `:36`, `edit/EVIDENCE-COVERAGE.md:19`);
   the damping/stiffness pair in one.

**Letter B's corrections:**

- `VISUAL-CHOREOGRAPHY.md:61` — `revealSpring` restated in the engine's own terms: **`{ "Mp": 0.0111,
  "settle": 11.89 }`** → `springParams` gives ζ = 0.82, ω₀ = 14.5. If the Remotion JSON shape must be kept for
  a component that genuinely consumes it, it becomes **`{ "mass": 1, "stiffness": 210.25, "damping": 23.78 }`**
  — the same spring, and the mass is stated rather than implied.
- `VISUAL-CHOREOGRAPHY.md:40` — SC-09's ζ = 0.88 either carries its reason on the page (a tighter settle for
  the pass/fail tags: Mp 0.297% against 1.11%) or moves to 0.82. **Operator's call; the order does not decide
  a second dial in the same episode.**
- **Open for the operator:** whether this episode keeps its own dial at all, or moves to the house
  `SPRING = { MP: 0.04, SETTLE: 6 }` (ζ = 0.7156, ω₀ = 8.384) that every other build uses. The order does not
  assume a per-episode dial is wanted.

---

## 5. Doctrine points kept from the same review

1. **Attributions match their URLs.** `reply.md:22,24`: a Sept 10 event sourced to a CNBC URL dated
   2026-08-10-or-earlier, and 10Y/2Y figures attributed to "U.S. Department of the Treasury" behind an
   `ecmsource.com` URL (an aggregator). Letter B's evidence order names **the publisher the URL actually
   resolves to**, and notes that `ecmsource.com` soft-redirects 404s to its homepage with HTTP 200, so
   `--verify-urls` cannot distinguish a real slug from an invented one there. *Not re-probed here:*
   `result.md:19-22` — this pass is disk-only, and `BLUEPRINT.md` is not on disk under `docs/` or `content/`,
   so those two anchors rest on the reply alone. **`[verify]`**.
2. **A brief never overclaims a gate.** `reply.md:38`: the brief claimed "0 FAIL, **0 WARN**" against 1 WARN
   actually measured. This order quotes its own tails verbatim, including the FAIL it found (§7), and claims
   nothing the runner did not print.
3. **Commands must run as written.** `reply.md:40`: the brief's three commands all exit on argparse error.
   The commands at the head of this order are the ones that were run, verbatim, with their positional `script`
   and valued flags.
4. **Figures are never fabricated.** Every number here is either cited `file:line` / payload row, or computed
   from stated inputs, or tagged **`[verify]`**.

---

## 6. What this order does NOT do

- **It does not patch letter A.** `SCRIPT-VO.txt` and `SCRIPT-GATES.md` stay byte-identical; every change
  lands in letter B. No take exists yet, and none is touched.
- **It introduces no new figure.** -0.80% is arithmetic on two stated legs, one payload-sourced and one
  `[verify]`; nothing else new is asserted. -0.95% is retired rather than re-derived.
- **It does not run a build, a render or a git operation.** Nothing was written outside this file; the gate
  runner's report was produced in a scratch directory so it could not land in the project.
- **It does not decide the second spring dial** (SC-09's ζ = 0.88) or whether the episode keeps a per-episode
  dial at all — both are marked operator's call in §4.
- **It does not reconcile the two scene tables' interiors** (§1, request 6) — that contradiction is flagged,
  and it is repaired as a consequence of rebuilding the table against the measured clock, not as a separate
  decision here.
- **It does not touch the review's closed items** — the raw CSV payloads with sha256 cites, the ring number
  and the hook were already handled (`result.md:11-15`, BACKLOG R26-109).
- **It does not decide the ring token**, which the gates now FAIL either way (§7). That is a letter-B question
  the order raises and the operator answers.

---

## 7. Could not be settled here (raised, not decided)

**The ring token now FAILs the opening gate whichever token is declared.** Measured today on letter A:

```
$ run_script_gates.py <scratch>/SCRIPT-VO.txt --long --ring weight
  [FAIL ] G15 'weight' never mentioned in P1
  [FAIL ] G15b no P1 sentence carries the token, so there is no claim to return to
RESULT: 2 FAIL / 1 WARN / 46 PASS / 12 JUDGE (read these) / 1 INFO

$ run_script_gates.py <scratch>/SCRIPT-VO.txt --long --ring percent
  [FAIL ] G27 'percent' 3x in P2
RESULT: 1 FAIL / 1 WARN / 46 PASS / 12 JUDGE (read these) / 2 INFO
```

The brass weight is still the declared ring token in `SCRIPT-PRODUCTION.md:5` ("The brass weight stamped five
point five percent"), `VISUAL-CHOREOGRAPHY.md:32` (SC-01) and `:42` (SC-11), and its asset card is at `:48-51`
— but the 2026-09-12 edit that removed the unsourced 5.5% from the hook also removed the weight from P1, so
letter A's spoken text and its choreography no longer share a ring. Letter B needs a token the operator picks;
this order does not pick it.

Also unsettled: the **earnings-yield leg** of the ERP (no P/E payload on disk) and the **CNBC date /
ecmsource attribution** (`BLUEPRINT.md` not found under `docs/` or `content/`; no outbound probe in scope).
Both carry `[verify]`.
