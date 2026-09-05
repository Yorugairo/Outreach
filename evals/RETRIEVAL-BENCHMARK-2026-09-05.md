# Retrieval benchmark — parent vs delegated lookup (2026-09-05)

**Question asked (operator):** measure cost, speed and success of "go find X in our docs / animation math"
when the Fable parent does it inline vs delegating to an Opus role, and name the highest-cost lookups
worth delegating. The two hard-coded eval suites (`evals/` here and the source repo's) score 50/50 by
construction and measure nothing about this — this file is the re-runnable seed for the real bench.

## Method

Five lookup questions with ground truth held by the parent (all answers known from the day's work).
Each question was dispatched **identically** to two agent types in the same session:

- `Explore` — the built-in read-only agent; inherits the session model (**Fable 5.1** here).
- `explorer` — the repo role in `.claude/agents/explorer.md` (**Opus 5**, same read-only tools).

Cost = `subagent_tokens` from the task notification (the agent's own context, none of it enters the
parent); tool uses and wall time from the same notification. Success = every requested fact correct and
located (`path:line`). Confound: the two types carry different system prompts (Explore reads excerpts;
the role carries the repo contract), so this compares *harness + model*, not the model alone.

## Results

| Q | lookup | Explore (Fable) tokens / tools / s | explorer (Opus) tokens / tools / s |
|---|---|---|---|
| 1 | M13 cut-gap rule: numbers, doc section, script, ruling | 45,784 / 7 / 25.7 ✓ | 31,275 / 6 / 26.7 ✓ |
| 2 | min-jerk easing: module, inliner + markers, flag, tests | 51,476 / 6 / 23.9 ✓ | 31,311 / 7 / 29.2 ✓ |
| 3 | the mount transition: compiler, grammar, template constants, doc | 54,768 / 6 / 24.8 ✓ | 34,294 / 8 / 32.3 ✓ |
| 4 | caption page budgets: defaults, the Tokyo override, style | 44,859 / 8 / 146.8 ✓ | 30,318 / 7 / 31.7 ✓ + found a stale comment |
| 5 | bed loudness per platform: values, gain formula, inputs | 46,528 / 5 / 22.1 ✓ | 28,790 / 3 / 18.4 ✓ |
| | **total** | **243,415 / 32 / 243 s — 5/5** | **155,988 / 31 / 138 s — 5/5** |

- Success: 5/5 on both. Every answer carried correct `path:line` references; the Opus role's Q4 answer
  also caught a stale comment in `build_caption_pages.py` (fixed by `speedster` in commit 276a2e8).
- Cost: the Opus role used **36 % fewer tokens** for the same answers, and none of them count against
  the Fable weekly cap. Wall time comparable (Q4's 147 s on Explore was one slow run).
- **Fixed overhead per dispatch ≈ 20–25 k tokens** (system prompt + repo instructions): `speedster` spent
  23,454 tokens / 3 tools / 19 s on a one-line comment edit. Below ~5 tool calls the parent should just do
  it; the saving is in the 10–40-call hunts.

## The parent's own cost on the same kind of task (this session's transcript, rough segmentation)

| operator ask | parent tool calls | tool output pulled into Fable's context |
|---|---|---|
| "we have the outro built already … it was the remotion kit … it's probably in the other worktree" | 36 + 16 | 0.3 MB + 1.75 MB |
| "why is the freesound token empty?" (it was not) | 12 | 16 KB |
| "did we ever add the 'short variant' of the script?" | ~40 | 118 KB |

Same class of question, 12–50 tool calls and up to 2 MB of output in the parent's context, against
3–8 calls and a 200-word return when delegated.

## What to delegate (by measured cost) and what not to

Delegate: asset / capability hunts across worktrees ("did we build X, where is it"), config and secret
presence checks, doc maintenance (stale comments, CAPABILITIES rows, BACKLOG strikes, gates-report
regeneration), diff review before a commit, test runs. Keep in the parent: design, planning, animation
reasoning, the operator's conversation, the brief and the review of every delegated diff.

## Harness findings

1. **The index does not cover the docs.** `sigmap_context.py query "animation math min-jerk spring easing"`
   ranks `content/video_engine/src/scenes/base.py` (the retired Manim scene) first; the kinetics modules and
   doc 47 do not appear. SigMap indexes declared symbols; the doctrine lives in Markdown headings and
   CAPABILITIES rows. A headings → `file:line` index over `docs/` is the missing piece; until then the
   explorer role's grep-first behaviour is what made 5/5 possible.
2. **ECC's agents add nothing here.** They are generic prompts on sonnet/haiku (code-explorer 2.6 KB,
   code-reviewer 13.9 KB, docs-lookup bound to a retired context7 connector) and were not loaded in this
   session. The repo roles (1.6–2 KB, the runbook contract, model pinned) are lighter per dispatch. Keep
   ECC for its skills and hooks; the model pin is the cost lever, not the agent file.
3. **Native subagents now carry model / tools / effort / memory / isolation and hot-reload from
   `.claude/agents/`** — the roles were dispatchable within the same session they were written.
4. The bench to keep is this one: questions with held ground truth, re-run per model or harness change.
   Next additions: a build task (regenerate a gates report; compile the short's timeline and diff it) and
   a doc-maintenance task (strike a BACKLOG row, add a CAPABILITIES row) with the same three metrics.
