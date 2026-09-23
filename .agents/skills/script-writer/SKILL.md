---
name: script-writer
description: Unified script drafting, channel positioning, 6-phase architecture, multi-scale strength loop (L0-L6), mechanical gate verification, and Google Chirp scratch take preflight. Use for writing, reviewing, or linting any VO script.
---

# Script Writer & Speech Engine

Unified production engine: combines **Channel Positioning & Architecture** with the **Multi-Scale Strength Loop (L0–L6)**, **Mechanical Gates**, and **Stage Zero Voice Testing**.

A script is never approved simply because a linter passed. Linters measure mechanical syntax; only the full loop tests comprehension, retention, and ear delivery.

---

## The 7-Stage Production Lifecycle

```
[1. Intake & Positioning] -> [2. Drafting] -> [3. Humanizer]
          |
          v
[4. Mechanical Gates] -> [5. Doctrinal Judge] -> [6. Blind Viewer] -> [7. Scratch Voice & Fixpoint]
```

### Stage 1: Channel Intake & Packaging Contract
1. **Select Channel**: Money Physics, Building Money, or Martial Matters. (See [references/CHANNELS-AND-PERSONA.md](references/CHANNELS-AND-PERSONA.md)).
2. **Lock Package Contract (Ruling E27)**: Title + Thumbnail + **Sentence 1 Answer**. The promise made in the title must be answered deeply in the very first sentence.
3. **Calibrate Narrator Biography (Ruling A1)**: Resumé arrives *after* the paradox in a subordinate clause; never its own sentence. Systems over charts.

### Stage 2: Drafting (Flexible Mode)
- **Mode A: The 1:30 Unit of Proof (Ruling E27 Addendum)**: Draft P1 Open (0:00–1:30) in isolation. Test voice, pacing, and hook at the still-image tier before drafting the rest.
- **Mode B: Full 6-Phase Architecture**: Draft P1–P6 using the 15–90s retention micro-rules or the Doc 35 8-Beat Answer Format. (See [references/SIX-PHASE-AND-ANSWER-FORMAT.md](references/SIX-PHASE-AND-ANSWER-FORMAT.md)).

### Stage 3: Anti-AI Humanizer Quality Gate

Read [references/humanizer-rules.md](references/humanizer-rules.md) after drafting and after substantive revisions. Apply the full editorial checklist, not just a banned-word scan: remove corporate fluff, robotic passive structures, chatbot filler, repeated explanations and unneeded technical nouns. Read for the ear; vary vocabulary only where meaning and referents stay clear. Preserve numbers, account identities, sources, the operator's voice and deliberate callbacks. Record representative before/after changes and retained technical terms. This is a required editorial review, not an AI-authorship detector or a substitute for mechanical gates and blind comprehension.

### Stage 4: Mechanical Tool Gates (In-Process)
Author `<script-stem>-NARRATIVE-MAP.json` (`narrative_map.v1`) before asking
for semantic clearance. Then run the diagnostic from repo root:
```bash
python content/video_engine/scripts/run_script_gates.py <script_path> --stage diagnostic --title "<title>" [--pivot "<line>"] [--ring "<phrase>"] [--counterparty "<name>"]
```
* **Enforces**: `lint_script_pattern.py` (G01–G49 line gates), `audit_script_doctrine.py --pivot` (45–55% chiastic reversal), `gate_opening_structure.py`, and `enumerate_strength_screens.py`.
* **Output**: Writes `<script>-GATES.md` with separate `MECHANICAL`, `REVIEW COMPLETENESS`, and `CLEARANCE[diagnostic]` lines plus `<script>-SCREENS.md`. A clean diagnostic can exit 0 while review remains `INCOMPLETE`; it is not recording clearance.

### Stage 5: Doctrinal Judge (Agent Ledger)
1. **Anti-Tag-Laundering (Rule R2)**: Verify every declared tag (`[catalyst]`, `[rehook]`, `[loop]`) is genuinely delivered in the text, not just stamped to pass a gate. A falsifiable tell is an editorial obligation; do not invent a spoken tag unsupported by the repository's parser.
2. **Line-by-Line JUDGE Verdicts (Rule R3)**: Every JUDGE row evaluated individually with quoted lines:
   - `J01`: Counterparty named as a mechanism, not a villain.
   - `J02`: Head-fake planted straight without tipping the hand.
   - `J06`: Image tensions concrete and non-metaphorical.
3. Write one `script_review.v1` receipt covering every due obligation from
   `script_review_contract.py`, including every declared occurrence, JUDGE row,
   craft-map row, every emitted strength-screen candidate and narrative-map
   relationship. Each semantic row names its exact obligation ID in the
   rationale, carries an obligation-specific finding object, a bounded exact
   quote/span, and the reviewer with the required role. Exact script, screen,
   viewer and map hashes bind the findings. A generic score, repeated
   boilerplate, whole-script citation or legacy J13/J14 sidecar is partial
   input, not a complete receipt.
4. Validate the map as one continuous argument: its micro loops cover the full
   runtime, all spans remain inside that runtime, and `next_loop` advances
   through every loop exactly once to a single `end`. A gap, cycle, self-link,
   unreachable loop or beyond-runtime payoff blocks clearance.

### Stage 6: The Blind Viewer Audit (Ruling E26)
Execute the isolated headless viewer test (Window 0 = package; 15s rolling windows):
```bash
python content/video_engine/scripts/viewer_windows.py <script_path> [--timeline <word-clock.json>]
python content/video_engine/scripts/viewer_run.py <script_path> --title "<title>" [--thumb-file <path>]
python content/video_engine/scripts/viewer_score.py <script_path>
```
* **Beat Recall Score binds as FAIL**: If the blind reader did not feel a declared beat within +-1 window, it is laundered. Blocks recording.
* **Confusion Score binds as WARN**: Flags referent drift and lost counterparty context.
* **Information Gain stays INFO**: Recorded for telemetry, does not bind.

### Stage 7: Scratch Voice & Fixpoint Convergence
1. **Stage Zero Scratch Audio (Free Tier)**: Never spend ElevenLabs credits on iteration. Test timing and ear delivery with Google Chirp 3 HD or local Kokoro:
   ```bash
   python content/video_engine/scripts/scratch_take.py --engine chirp
   # Or local word-timestamped take:
   python content/video_engine/scripts/scratch_take.py --engine kokoro
   ```
2. **Multi-Scale Strength Loop**: Review scales L0 through L6 and cross-checks X1–X5. (See [references/STRENGTH-SCALES.md](references/STRENGTH-SCALES.md)).
3. **Convergence**: A fixpoint is reached when zero edits were made and zero gates fired in the round.
4. **Speech Reflow (Doc 37)**: Reflow 1-beat-per-line display text into ~45–75s movement paragraphs for TTS. Cap `<break>` tags at <= 3. Compile settles into `<script>-EDIT-PAUSES.json`.
5. **Final recording clearance**: after the aligned scratch and measured word
   clock exist, bind their raw/normalized hashes in the receipt and run:
   ```bash
   python content/video_engine/scripts/run_script_gates.py <script_path> --stage recording --review <receipt.json> --narrative-map <map.json> --viewer-artifact <script-VIEWER.md> --timeline <word-clock.json> --scratch-take <scratch-audio>
   ```
   Final recorders accept only a current `CLEARANCE[recording]: CLEAR` whose
   receipt, map, complete viewer windows/raw reports/score chain, clock and scratch still validate. Free-text `--force` cannot supply
   missing review custody.

---

## Standing Guardrails

- **Precedence**: Comprehension > Structure > Line-Craft.
- **Rewrite Budget**: Any sentence rewritten more than **twice** stops and goes to the operator. Prevents over-sanitizing the voice.
- **Oscillation Guard**: If an edit reverts to a prior state, stop and escalate as a DECISION between conflicting gates.
- **Chart Discipline (Ruling E28)**: Charts must carry X and Y axes with unit ticks. Drops are blood red (`--lp-neg`), rises are green (`--lp-pos`), sunflower yellow only for focus callouts.
