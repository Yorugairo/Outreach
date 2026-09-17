# The director-critic report - `<build>/CRITIC.md` (P67, E99 s68 Q6 = C)

Status: current (2026-09-16)
Owner: the parent; written by the `reviewer` role on Opus, never by the parent and never by the builder.

**The ruling.** E99 s68 (`docs/portable/OPERATOR-RULINGS.md`, "E99 s68"): agents are held to the docs by a VERIFIED
receipt and a director-critic that reads the built cut against the mechanism list before the queue and reports
**two scores, never one verdict** - mechanism correctness and attribution quality. The research behind the second
score: "answer correctness should be separated from evidence support and attribution quality", and "document-level
citation may hide unsupported or partially supported claims" (arXiv 2606.04990, quoted in
`docs/content-video-engine/GRILL-AGENTS-HARNESS-EFFECTS-2026-09-16.md`, appendix A section 3).

**Why a different reader.** One-shot #3 (E99 s67) was read by its own builder through `self_watch.py`'s O1-O11 and
was CLEAN by that read; the operator refused it in four messages. The builder reading its own cut is the thing that
failed (memory `judge-the-frame-not-the-diff`). The critic is the `reviewer` role in a fresh context with the cut,
the table and the receipt - and nothing the builder concluded. `SELF-WATCH.md`'s rows are DATA to the critic, never
authority.

## What the critic reads

1. The BUILT cut, read-only, at instants it chooses: the frozen player served for the card (`serve_player.py <build>
   --port <p> --no-check`, the parent's link) or contact sheets from `probe.py <build> <t...> --sheet <png>`; never a
   rebuild, never a re-render, never a served build touched (E99 s11's practice, `review-link-frozen-copy`).
2. The shot table the cut was compiled from (`<build>/SHOT-TABLE-SHORT.py` or the project's `build_short.py`
   `shot_table`), the compiled `timeline.json`, and `<build>/overrides.json` if present.
3. The project's `## Recall` receipt (`PRODUCTION-LEDGER.md`; the grammar in `docs/runbooks/ONE-SHOT.md` "Before
   step 1" and the verifier `content/video_engine/scripts/recall_verify.py`) - the last `## Recall` heading's block.
4. The mechanism list (below), and the BEAT-PLAN.jsonl the cut was authored from (M41), which says what each beat
   OWES.

## Table 1 - MECHANISM CORRECTNESS

One row per mechanism on the list. Columns:

| mechanism | owed by | verdict | t | read from |
|---|---|---|---|---|
| the name from the list | the beat(s) whose shape calls for it, by beat number and sentence - or `not owed` when no beat in this cut's plan calls for it | `present` / `absent` / `replaced by <what>` | the instant (s) the verdict was read at | `frame` (a sheet path) or `probe` (the probe's line) |

The rules of the verdict:

- `present` only when the critic SAW it at the instant named - the frame or the probe line is cited (R5). A mechanism
  the critic cannot see at that instant is `absent`, never "unclear" or "probably".
- `replaced by <what>` names the mechanism the cut carries in that beat's place (a light where a build was owed; a
  chart card where a page was owed; `enter=built` where the axes were owed) - the replacement is named, not scored.
- `not owed` is a full row, not a blank: it states which shapes the plan holds and why none calls for the mechanism.
  M45 (P66) reads the same way - the list is read against the cut's own plan, never as a fixed checklist, so the
  approved cuts read `present` or `not owed` on every line.
- The denominator of score 1 is the count of OWED mechanisms in this cut, stated on the score line.

**The mechanism list until M45 lands (P66 T5 derives the list from the approved tables with `path:line` cites; this
is the E99 s67 list plus the two approved shorts' mechanisms, and the critic cites it by date `list of 2026-09-16`):**

| # | mechanism | the rule | source |
|---|---|---|---|
| 1 | the open STARTS ON THE CHART: the ledger page is the first frame, on its axes, its line drawing under the hook | s67 Apply 6; P53 T1 | `memory-trades-the-calendar/build_short.py` v9b R1; Tokyo `build_short.py` `shot_table` docstring; Japan `:170` |
| 2 | every page BUILDS with the effects (axes entry, the mount's own build, `build_to`, bars in stagger, slices arriving) and HOLDS BUILT while its number is spoken; `enter=built` is not an answer | s67 Apply 2 | the three approved tables |
| 3 | a page whose number lands 7 s or more in MOUNTS over the world (`mount=<s>`) and builds under the setup sentence | s67 Apply 5-6; E45 (the mount) | Japan `:172-174`; Tokyo `:235` |
| 4 | the axes entry elsewhere (`:axes`) - a page enters by its own signature, never zoomed up from a card | s67 Apply 5 | `memory-trades-the-calendar/build_short.py:141-147` |
| 5 | the dip only on a WORLD change; never a dock's transition, never into a mount | E47 | memory `dip-is-a-world-change` |
| 6 | page to page by `suck` or `cut` with no empty cream between (a chart-to-chart transform) | E96 M36; recipe `chart-to-chart-with-no-cream` | `memory-trades-the-calendar/build_short.py:145-147` |
| 7 | the return by the SPIRAL, the page unwound, the ring on the chart (its one use) | E40 s4; E56 | Japan `:174`; Tokyo `:222`; memory `:150-152` |
| 8 | a DOCK is an evidence still or document that reads then parks in the page's own room - never a chart page thrown as a card, no rails and no park at 9:16 | s67 Apply 5; E65; R26-171/172 | Japan `:173` (the ship); Tokyo `:221-222` |
| 9 | a plate carries its card for six seconds with directional life (Ken Burns + the drift), never a bare still | M44; E99 s65 | `PLATE-LIBRARY.md`; memory `plate-life-is-directional` |
| 10 | a light is PUNCTUATION on a sentence that points, placed after the page's build - never filler for M16 | s67 Apply 1, 3; E56 | the casebook `the-thin-one-shot` |
| 11 | old and new BLEND: a new mechanism (the compare melt, the ticker, the verdict wall) sits inside the approved shape and does not replace it | s67 Apply 8 | one-shot #3's rework (4473d62) |

## Table 2 - ATTRIBUTION QUALITY

One row per row of the shot table (the compiled rows, in order; a sidecar override is its own row marked `override`).
Columns:

| row | what it does | attribution | note |
|---|---|---|---|
| the row number and its window | the row's tokens in one line (`ledger:...:axes`, `mount=`, the dock and its options, the species, the exit) | `Recall(<stage>) <path>:<line>` - the receipt line whose cited span IS the rule this row obeys; or `UNATTRIBUTED: <the choice, named>` | claim-level only |

The rules of the attribution:

- **Claim-level, never document-level** (arXiv 2606.04990). A receipt line that cites a whole document ("doc 29",
  "the runbook") attributes nothing; the row is `UNATTRIBUTED` and the note says the cite was document-level. A
  row is attributed when the receipt line's quoted span states the rule the row's token obeys (the axes entry ↔ a
  span about the axes entry; the six-second plate ↔ a span about M44).
- A row obeying a rule the receipt never cited is `UNATTRIBUTED: <the choice>` even when the choice is right - the
  score measures whether the record was READ, not whether the row is good (that is table 1's question).
- A legacy receipt (`- Recall: <path>:<line> (note)` lines with no stage, before P67) is read the same way; the note
  marks `UNSTAGED`. The calibration case (P67 T7, one-shot #3) reads against the appended verified block.
- The denominator of score 2 is the count of shot-table rows including overrides, stated on the score line.

## The two scores - the last two lines of the report

    mechanisms present <p>/<owed> (list of <date>)
    rows attributed <a>/<rows>

Two fractions, each with its denominator on the same line, and **no third number and no verdict word**: no
"CLEAN", no "PASS", no average, no grade. They are JUDGE rows (`patterns/CHECK-RESPONSIBILITIES.md` section 4): they
ride the operator's card as INFO beside the clip, and no gate, no `self_watch.py` row and no `build_review_queue.py`
verdict ever reads them into a mechanical result (R1/R3). The operator judges the cut, not the scores.

## What the critic never does

- Never a FAIL row, never a verdict word, never a fix, never an edit to the table, the sidecar or the ledger.
- Never a rebuild, a re-render, a re-serve; never `--watch` on the operator's link.
- Never the builder's read repeated: `SELF-WATCH.md` is input, and where the critic disagrees with an O-row it says
  so in the row's note with the instant.
- Never the parent (Fable) and never the same context that built the cut.

## The brief the parent dispatches (`docs/runbooks/PRP_EXECUTION.md` "The brief")

Plan path and task id; role `reviewer`, read-only; the build dir and the served link (or the sheet command); the
project dir (the table and the ledger); this page as the contract; the mechanism list's date; the exact validation
(`test -f <build>/CRITIC.md` and the two score lines present, unpiped); the answer cap (≤ 200 words: the two
fractions and the three rows the operator should look at first); the report path (`<build>/CRITIC.md`, untracked -
a build artifact, cited by the queue card's `critic` field).

## See also

`docs/runbooks/ONE-SHOT.md` step 9 (the critic between the self-watch read and the hand-over);
`docs/content-video-engine/SELF-WATCH.md` (the builder's read - a different reader); `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md`
section 4; `.claude/agents/reviewer.md` "The director-critic pass"; `docs/runbooks/RECALL-RECEIPT.md` (the receipt the
attribution reads); BACKLOG R26-181.
