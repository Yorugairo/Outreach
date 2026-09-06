# CHECK RESPONSIBILITIES — what the tools decide, what the agent decides

The kit has four tool-enforced checkers and one reading-enforced loop. This
file is the contract between them: **which verdicts belong to a tool, which
belong to whoever is running the script at the time (the runtime agent),
and how each side reports so the other cannot be skipped.**

Established 2026-09-02, after the Steel and Paper retention read. The
opening gate had encoded the platform layer and only implied the classical
one; the roster said "by hand" for the rest and by hand the promise landed
at 1:20 with nothing to stop it. Operator: *"we need to write the rules that
provide whoever the run-time agent is what their check responsibilities are
vs what the gate can cover."*

---

## 0. The four verdict kinds

Every check in the kit is exactly one of these. The kind decides the owner.

| Kind | Meaning | Owner | Example |
|---|---|---|---|
| **mechanical** | decidable from text + timing: a count, a position, a duration, an adjacency | **tool** — final | promise lands after 0:60 (G09); AND-THEN chain (G23); pivot outside 45–55% (audit) |
| **declared** | the beat has no textual signature, so the writer TAGS it; the tool checks presence and window | **tool** checks the claim exists and sits in its window; **agent** verifies the claim is TRUE | `[catalyst]` present in P2's first 60s (G40) — the agent confirms the tagged line is an inciting event told as anecdote, not exposition wearing a tag |
| **PERCEIVED** | did a reader who knows NOTHING actually feel it? | **the viewer** (P36) — a blind agent reports, a deterministic scorer judges | a declared `[rehook]` that never shows up in the blind reader's new information or held question is *laundered*: tagged, not delivered |
| **JUDGE** | only a reader can decide | **agent** — every row verdicted individually, with the quoted line | opponent is a mechanism not a villain (J01); the head-fake is offered straight (J02); the image tensions the line (J06) |

The fourth kind is the outside check on the second. `declared` trusts the
writer's tag and asks only *is it present, and in its window*; `PERCEIVED`
asks whether a cold reader felt it at all. That is rule R2's laundering,
measured from outside the doctrine instead of inside it. The viewer is never
asked when it would drop off: an LLM's patience is not a human's, so it is
asked only for perception reports it can give stably, and the judging is the
scorer's, deterministically (P36; ruling E26).

STRENGTH-LOOP §8 is the standing rule behind this: *automate only what is
unambiguous — counts, positions, durations, antecedent adjacency — and
surface the rest.* A regex proxy for "concrete" returned confident wrong
verdicts. The tools therefore never pretend to judge; they print JUDGE rows
so the agent cannot forget them.

## 1. The rules

**R1 — A tool's mechanical verdict is final.** The agent does not re-derive
it, soften it, or reason around it. If the agent believes a mechanical row is
wrong, that is a *doctrine finding*: escalate as DECISION, and the fix lands
in the tool (same commit as the ruling), never in the report.

**R2 — A declared beat is a claim, and tag-laundering is the failure mode.**
The tool proves the tag exists where the shape requires it. The agent proves
the sentence under the tag *is the beat* — a `[loop]` that never closes, a
`[reflect]` that is more anecdote, a `[debate]` that lectures instead of
showing the play fail. The agent's report lists every declared tag with a
one-line verdict: **true / laundered**. A laundered tag is a FAIL at the
phase, not a note.

**R3 — JUDGE rows are the agent's and are never summarized.** Each is
verdicted on its own line with the quoted text it judged. "JUDGE rows
reviewed" is not a review (STRENGTH-LOOP §8a: a summary of a review is
indistinguishable from a review unless the enumeration is the deliverable).

**R4 — Everything the tools do not reach is the agent's, by name.** §3
lists it. The agent reports those rows with a verdict each; rows it did not
run are listed as NOT RUN, never omitted. The report states which sections
ran (script-writer skill §6) — this file is the list it checks itself
against.

**R5 — Tool outputs are cited, not paraphrased.** The report carries each
tool's exit status and FAIL/WARN counts, and the screens file with its
counts. A convergence claim that does not cite them did not converge.

**R6 — Every check the agent runs by hand that turns out to be
mechanical moves into a tool.** When a by-hand row is decidable from
counts/positions/durations/adjacency, it ships as a gate in the same commit
as the defect that exposed it (the standing instinct: every operator-caught
defect ships a gate). A by-hand row that cannot be mechanized stays a JUDGE
row printed by the nearest tool so it is surfaced every run.

**R7 — When a tool and a doc disagree, neither wins silently.** The tool
prints the conflict in its source line; the agent raises it as DECISION with
a recommendation. Standing example: A3 at ~10% of runtime (P2.md, MAP §4)
versus 3:00 absolute (`audit_script_doctrine.py`). The opening gate follows
the docs and says so.

**R8 — Timing is measured when a take exists.** The agent passes
`--timeline` (opening gate) and lets the audit find `vo/*.words.json`. An
estimated verdict on a 3-second cap is a soft verdict; the report says
which it was.

**R9 — Lane capabilities come from the docs and the template, never from
memory.** Any claim about what this lane can or cannot do (what the
player draws, which renderer a lane uses, whether a species exists, what
a gate checks) cites the file it was read from - `PIPELINE.md`,
`CAPABILITIES.md`, doc 29, the player template, the checker - before it
is stated. A recalled capability is a hypothesis to verify, not a fact to
report. Operator ruling 2026-09-02, after two same-day assertions the
repo contradicted ("our charts are static PNGs" - the template draws
them; "we haven't used hyperframes" - doc 19 is the lane). Enumerate
before you grep; read before you claim.

## 2. The tools and what each decides

| Tool | Command | Decides (mechanical) | Checks presence of (declared) | Prints for the agent (JUDGE) |
|---|---|---|---|---|
| `lint_script_pattern.py` | `lint …py <script>` | sentence stats, passive scan, CTA count, mark ration, stage-direction ↔ narration **tautology**, crude ring echo, rehook-family presence | — | — |
| `audit_script_doctrine.py` | `… <script> --pivot "<line>"` | unknown marks, break ration, digit numerals, carrying mean / spread / over-20 share, trailing attribution, 3s hook + 8s paradox (measured if a take exists), greetings, "you" by 0:30, promise regex in 60s (WARN), CTA count + windows, A1–A3 anchors (**3:00 absolute — conflict R7**), break tags per paragraph, tell presence (doc 35), **pivot pin 45–55%** | — | hook concreteness (named in the WARN) |
| `gate_opening_structure.py` | `… <script> --ring <token> --counterparty <name> [--timeline …] [--title "<t>" --thumb "<words>" --thumb-file <png>]` | G01–G06, G09–G11 (G09 WARNs a promise past 0:45 — E24, DECISION R7 vs doc 38's 0:60; the FAIL past 0:60 stands), G13, G15 (with `--ring`), G17–G18, G23, G25, G27 (with `--ring`), G29 (with timeline), G30, G33–G36, G43 (WARN), G45 packaging echo (with `--title`/`--thumb`: the title-word proxy for "the first sentence answers the thumbnail" — E24 / doc 29 §9.29; INFO when no title is given); **short mode (G2, 2026-09-05)**: a measured clock under 3:00 or `--short` replaces the long-form geometry with S01–S03, S05–S08 (+ G04/G05, G45) and prints J50/J51 — read them; the runner passes the same decision to the audit (`--short`: doc 35 rule 2 and the P1 pin are INFO) | G07 stakes · G08 payoff · G12/G32 tricolon · G14 opponent · G16/G31 reflect · G19/G21 loop · G20/G22 new · G24 head-fake · G26 foreshadow · G28 loop-close · G37 archetype · G38 desire · G39 map · G40 catalyst · G41 debate · G42 signpost · anaphora · dip | J01 mechanism · J02 head-fake straight · J03 hook concrete/terminal stress · J04 context-dump · J05 gap opens · J06 irony counterpoint · J07 contextual mapping · J08 phonetic anchor · J09 archetype not stereotype · J10 map not TOC · J11 debate as gap · J12 the first sentence answers what the thumbnail poses (prints the `--thumb-file` path to open — E24) |
| `enumerate_strength_screens.py` | `… <VO>` → `<script>-SCREENS.md` | *enumerates only*: X1 connective/pronoun openers with predecessors, deixis openers, additive junctions, phonetic-anchor candidates, per-paragraph cadence runs | — | every listed item — the agent verdicts each (ok / FIXED / licensed / carryover) |
| `run_script_gates.py` (**the runner — stages 3–4**) | `… <script> --pivot "<line>" --ring <t> --counterparty <n> [--timeline …] [--title … --thumb … --thumb-file …]` | *decides nothing itself*: runs the four rows above in order through their own `main()`, cites each exit + RESULT line, and writes `<script>-GATES.md` (the §5 TOOLS block, every tool's stdout verbatim, `script_hash` of the spoken text, `VERDICT`); exit 1 on any FAIL. `record_*_take.py` refuse a script whose report is missing / stale / FAIL (`--force "<reason>"` overrides, reason into the take manifest) | — | — |
| `gate_motion_density.py` (**stage 7/8, on the BUILT timeline**) | `… <build-dir>` | M01 no stretch > 12s without a visual event (a LEDGER PAGE's build beats — scene start +0 / 0.7 / 1.5 / 3.9 / 4.7 / 5.2 / 8.2s: roll-out, savor, field, line, punch, build start, build end + focus (§9.26, E22 addendum 6) — count; its hold does not, §9.28 C5 / D1) · M02 > 8s (WARN) · M03 evidence enters ≤ 45s apart, every phase (a page START counts as an entry, D2) · M04 plates ≥ runtime/12s (a page is its own plate) · M05 20s hold ceiling · M06 caption cadence · M07 the opening minute is not the thinnest · M08 stage captions on every still stretch (once the timeline carries `cap_mode`) · M09 one camera move per window (§9.27 / §9.28 C3) · M10 no still stretch > 6s begins in the first 60s (E24 / §9.29) · M11 the first chart (chart/data dock, or ledger page; any dock when the timeline carries no evidence species) enters 0:08–0:20 with a spotlight / callout / punch / focus_zoom declared within 1.5s of the enter; a sound cue (motion-plan cue or timeline `sound` entry) within 1.5s or WARN (E24 / §9.29) · M12 a chart dock never spans a scene boundary and holds ≤ 10s (≤ 6s inside the opening minute) — re-enter it spotlit on the new datum instead (E25 / §9.30: the chart is the proof, not the homework). The dock clock is the timeline's own `scenes[].docks`; `evidence-dock.json` only when the timeline carries none (`dock_source` in the stats) | — | J01 savor beats keep their picture · J02 stage captions centred/large/explosive (until the template carries the mode) |
| `viewer_windows.py` + `viewer_run.py` + `viewer_score.py` (**stage 4b, the VIEWER**) | `viewer_windows.py <script> [--timeline …]` → `viewer_run.py <script> [--thumb-file …] [--title …]` → `viewer_score.py <script>` → `<script>-VIEWER.md` | V01 beat recall (every declared beat felt within ±1 window, citing the reader's line), V02 dead-runs, V03 open-loop coverage, V04 confusion, V05 gain per window | *nothing* — the viewer is never shown a tag; if it can see the doctrine the test is void | **binds since P36 HG1 (2026-09-03)**: V01 recall is a FAIL, V04 confusion a WARN, V05 gain INFO-only (it read green on the episode we know failed); `--no-viewer-gate` reports without binding |

The opening gate covers **P1–P2 only** and says so in its header. Nothing
mechanical exists for P3–P6 beyond the audit's pivot pin, CTA windows, tell
presence, and the lint's crude ring echo.

## 3. The agent's territory — verdicted by name, every run

### 3a. Verify the declared beats (R2)
For each tag the gate found: quote the line, verdict true / laundered.
The usual launderings: a `[loop]` with no resolution; a `[new]` that
re-phrases; a `[payoff]` that is a promise; a `[debate]` that explains why
the plan fails instead of showing it fail; a `[reflect]` that is anecdote;
a `[catalyst]` that is exposition.

### 3b. Verdict the JUDGE rows (R3)
J01–J11 from the opening gate, each with the quoted line. J06/J07 need the
plate plan or shot table open — they judge picture against voice.

### 3c. The classical nodes outside the gate (P3–P6)
| Node | Where | What the agent decides |
|---|---|---|
| Truby **Battle** | P4 | the pivot is a reversal *fought* — the head-fake demolished, the token recontextualized (same object, opposite meaning) |
| Truby **Self-Revelation** | P5 | the chiastic center carries THE transformative thesis, not a recap |
| Truby **New Equilibrium** | P6 | the opening image returns transformed; nothing new after the CTA |
| Snyder **midpoint** | P4 | reversal inside the 45–55% pin (audit measures the pin; the agent judges that it IS a reversal) |
| McKee gap engine | P3 units | every u2 is a gap (result violates expectation), every u3 a THEREFORE |
| Glass ratios | P3–P6 | 60/40-in-unit → 50/50 → 30/70 → 40/60; a stretch of pure reflection with no anecdote under it |
| Ring **close** | P6 | token-verifiable echo, closes LAST (LIFO ledger); lint's ring check is crude — the agent confirms |
| Counterpoint modes | P3–P6 | subtext → visual register shift → abstract synthesis → ring symmetry; a line that captions its visual fails |
| Foreshadow F3 → delivery | ~27% → 60–70% | three references, ONE delivery, zero re-promises after it |
| Anaphora arc | P3 → P6 | constant opening, evolving tails, resolves ONLY in P6's triad |
| The tell, four parts | P5 | one variable · one threshold · where we sit · what flips us (audit checks presence only) |
| Savor beats ≥2, breathing dips 1/unit | P5 / P2–P5 | present, carrying `[post-key]` |
| Best evidence banked → spent | P3 last unit | U5 |

### 3d. The roster rows the audit does not count
Foreshadows · macro loops (LIFO) · STR micros outside P2 · callback tokens ·
head-fake demolition · dips · savor beats · tricolon terminality (P6 triad
lands last) · anaphora arc · Glass ratio per phase.

### 3e. The loop scales with no tool
L1 P1–P6 (phrase) · L2 B1–B4 (beat; the gate's G19–G23 cover P2's loop and
cadence *counts* — the agent judges that loops close and charge shifts) ·
L3 U1–U5 (U6 is gated in the opening only) · L6 C1–C3 · X1–X5 after every
edit (X1 from the screens file; X2–X4 by re-running the tools).

### 3f. L0 — the reader's five
S2/S3/S5/S7/S9 are screenable; **S1, S4, S6, S8, S10 need a reader**, every
sentence, in order, with the log as the deliverable
(SENTENCE-STRENGTH-CHECK).

### 3g. Surface choice per window (doc 29 §9.28)
For every shot-table row: PAGE (A1 ours + A2 owned series + A3 turning
beat or a still window) / DOCK (B1 theirs; B2 ours but not turning) /
PLATE LIFE / NONE, with the rule letters that decided it and the builder
where a chart is drawn (dense-line / story / race / decline / combo, never
merged). A NONE longer than 12s cites D4 (stage captions) or is a defect.
The census form is `build-f/SURFACE-CENSUS.md`; the motion gate now counts
a PAGE's build beats as visual events and its start as an evidence entry
once the row is a `ledger:<series>:<variant>` id (P35 T4; M01 / M03 on the
timeline's own dock clock), and reports `ledger_pages` in its stats. Plate
life is still uncounted, and whether a window SHOULD be a page (A1–A3 vs
B1–B4) is never the gate's - this row stays the agent's, declared by the
table and verdicted per window (R2).

### 3h. Not structural, still the agent's
Evidence tracing (every figure → dossier row; ledger figures re-checked
against the ledger) · verbatim quotes · source-strength matching · the
persona pass (doc 36 §5, six checks) · thesis lens T1–T12 · dated
references · promises the script makes about itself · number density ·
register read aloud · the ear (scratch VO).

### 3i. Devices the craft map holds as judge-only with no owner row above (added 2026-09-05)
P45 D1 (`docs/content-video-engine/TRIAGE-2026-09-05.md` §1d, row C8). `docs/CRAFT-MAP.md`
is the **generated** roster — every craft device, its scale, the gate ids that
enforce it, where it is defined, one exemplar (`build_craft_map.py --check`).
Fourteen of its `judge` devices are named by no row in §3a–§3h: no tool decides
them and nobody was told to. By **R4** they are the agent's *by name*, verdicted
every run like every other §3 row (NOT RUN is a verdict; omission is not), and
reported under §5. This block points at the craft map rather than copying its
columns — the map is generated, and a second hand-kept roster would drift.

| Device | Scale | Defined (the section that states it) | Craft map |
|---|---|---|---|
| the answer format | L6 | `35-ANSWER-FORMAT-DOCTRINE.md:87` · `docs/portable/DOCTRINE-CORE.md:152` | `docs/CRAFT-MAP.md:35` |
| the assignment | L5 | `patterns/phase-guides/P6.md:83` · `docs/portable/DOCTRINE-CORE.md:40` | `docs/CRAFT-MAP.md:48` |
| peak-end | L5 | `31-FACELESS-CHANNEL-DOCTRINE.md:188` · `patterns/FULL-VIDEO-MAP.md:227` | `docs/CRAFT-MAP.md:49` |
| the dopamine ladder | L5 | `31-FACELESS-CHANNEL-DOCTRINE.md:39` · `patterns/FULL-VIDEO-MAP.md:69` | `docs/CRAFT-MAP.md:53` |
| the never-repeat rule | L5 | `31-FACELESS-CHANNEL-DOCTRINE.md:116` | `docs/CRAFT-MAP.md:57` |
| the enumeration mandate | L6 | `patterns/STRENGTH-LOOP.md:165` · this file §5 (the enumeration mandate; line numbers move, cite the section) | `docs/CRAFT-MAP.md:63` |
| instrument continuity | L6 | `patterns/STRENGTH-LOOP.md:96` | `docs/CRAFT-MAP.md:66` |
| mechanisms not prescriptions | L6 | `docs/portable/DOCTRINE-CORE.md:172`, `:191` | `docs/CRAFT-MAP.md:67` |
| the camera test | L0 | `31-FACELESS-CHANNEL-DOCTRINE.md:116` · `32-WRITING-FOR-THE-EAR.md:148` | `docs/CRAFT-MAP.md:97` |
| the cadence wave | L1 | `32-WRITING-FOR-THE-EAR.md:75` · `patterns/STRENGTH-LOOP.md:42` | `docs/CRAFT-MAP.md:103` |
| the named-subject rule | L1 | `patterns/SENTENCE-STRENGTH-CHECK.md:37`, `:77` | `docs/CRAFT-MAP.md:108` |
| the referent test | L1 | `docs/portable/VOICE-PACK.md:156` · `patterns/STRENGTH-LOOP.md:42` | `docs/CRAFT-MAP.md:110` |
| the aside voice | L1 | `31-FACELESS-CHANNEL-DOCTRINE.md:134` · `docs/portable/VOICE-PACK.md:156` | `docs/CRAFT-MAP.md:111` |
| the rewrite budget | L0 | `patterns/STRENGTH-LOOP.md:138` | `docs/CRAFT-MAP.md:114` |

Bare `NN-NAME.md` and `patterns/…` are under `docs/content-video-engine/`. The
craft-map line numbers are its 2026-09-05 generation; the device name is the
stable key (`rg -i "<device>" docs/CRAFT-MAP.md`). §4 step 2 reads
"3c–3i by name" — this block is part of that pass.

## 4. The runtime sequence

```
1. run_script_gates.py <script> --pivot "<line>" --ring <t> --counterparty <n> [--timeline …]
       runs, in order:  lint_script_pattern.py          -> exit + FAIL count
                        audit_script_doctrine.py        -> exit + FAIL/WARN + timing source
                        gate_opening_structure.py       -> exit + FAIL/WARN/PASS/JUDGE counts
                        enumerate_strength_screens.py   -> <script>-SCREENS.md + item counts
       writes <script>-GATES.md: the §5 TOOLS line, each tool's stdout verbatim,
       script_hash, VERDICT; exit 1 on any FAIL. Recording refuses without a
       current PASS report (--force "<reason>" overrides, reason into the take manifest).
2. AGENT: 3a declared-beat verdicts · 3b JUDGE rows · 3c–3i by name
3. Fix; re-run 1 (X2–X4 are re-runs, not memory); loop to a fixpoint
4. Report per §5
```

## 5. The report contract

The report is not accepted without every block below.

```
TOOLS      lint: exit N, F fails | audit: exit N, F/W, timing=<measured|estimated> |
           opening gate: exit N, F/W/P/J | screens: <file>, K items
DECLARED   <tag>@<mm:ss> "<line>" -> true | laundered      (one per tag)
VIEWER     V01 recall N/M (unperceived: [tag]@w…) · V04 confusion · V05 gain
           (V01 FAIL and V04 WARN bind since P36 HG1; NOT RUN is legal, with a reason)
JUDGE      J01 "<line>" -> verdict … J11                     (one per row)
P3–P6      each §3c node -> verdict / NOT RUN
ROSTER     each §3d row -> count + verdict / NOT RUN (and, since 2026-09-05, the §3i devices the craft map holds as judge-only: one verdict line each, by name)
LOOP       L1/L2/L3/L6 findings; X1 from screens (K verdicted); X2–X4 re-run
L0         log: original -> gates failed -> final, every rewrite
EVIDENCE   figures traced: n/n; quotes verbatim: y/n
DECISIONS  tool-vs-doc conflicts and rewrite-budget stops, with recommendation
```

"Linter clean" on its own means the review did not run (script-writer
skill, first paragraph). A FAIL anywhere in the TOOLS line blocks recording.
NOT RUN is allowed only with a reason the operator can rule on.

## 6. Moving a row across the line (R6)

A row moves from §3 into a tool when all of these hold: the verdict is a
count, position, duration or adjacency; the false-positive case is
enumerable; and the writer can declare what the text cannot signal. It
ships with a red test on a known-real failure and a green test on a
conforming case (doc 40 MEDIA-TDD), and the row here moves from §3 to §2 in
the same commit. Rows that fail the test stay JUDGE and get printed.
