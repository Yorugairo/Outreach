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

**What this establishes (labelled after Astra's review, 2026-09-05):** the controlled comparison is Fable-subagent vs Opus-subagent under DIFFERENT prompts (built-in Explore vs the repo role), so it measures harness+model, not the model alone; the inline-parent baseline below is a rough transcript segmentation, not a controlled run; persistent-session savings were NOT measured (continuation is unavailable in this build). The false-negative case in round 2 is now disclosed and belongs in the development/regression set, never a held-out set.

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

## Round 2 — the hard retrievals (same day, same method)

Operator: "what about difficult retrievals - deep in the evidence layer, obscure maths research in sections
not labelled on the evidence layer, unknown animation problems, new animation opportunities from the research?"
Five harder questions; ground truth established by the parent verifying every cited `path:line` after the fact.

| Q | lookup | Explore (Fable) tokens / tools / s | explorer (Opus) tokens / tools / s | verdict |
|---|---|---|---|---|
| 6 | analytic spring: the derivation doc, regimes, params, where each lands in code | 58,352 / 9 / 46 ✓ found the research bundle (`sources/.../07_academic_literature_…md:218-229`, §5.3 at :311) | 42,136 / 7 / 34 ✗ on one claim: called doc 42's pointer to "07 §5.3" a **dangling reference** - it exists | Fable deeper |
| 7 | Kubelka-Munk: the research, the K/S choice, constants, why ruled OFF, what the flag is kept for | 58,608 / 8 / 209 ✓ (+ the P43 plan) | 38,298 / 7 / 39 ✓ (+ noted the ruling is absent from OPERATOR-RULINGS) | tie |
| 8 | evidence layer: which record established the hedged-yield figure, source, date, consumer | 57,194 / 10 / 57 ✓ | 55,704 / 11 / 65 ✓ same conclusion ("no gate consumes it") | tie |
| 9 | caption boil/lift constants, boil fps, the tone-down and its previous values, the flashes lesson | 65,478 / 18 / 191 ✓ (three git generations of values) | 38,308 / 9 / 81 ✓ (one generation, via `git show 301d7c8`) | Fable deeper |
| 10 | THREE documented-but-unimplemented drawing techniques with absence proofs | 60,327 / 12 / 64 ✓ clothoid (42 §42.4), ARAP (flag declared at template :446, never read), syllable-locked type | 46,907 / 12 / 71 ✓ Deegan dark rim (44 §44.2), clothoid, ARAP | both valid |
| | **total** | **299,959 / 57 / 567 s — 5/5** | **221,353 / 46 / 290 s — 4.5/5** | |

- On hard questions the Opus role still costs **26 % fewer tokens and half the wall time**, and both found the
  obscure material (the research bundle, the evidence finding files, git history for values no doc records).
- **The one Opus error is the failure mode to guard: a false negative** ("that section does not exist"). Fable
  went one directory deeper (the `sources/` research bundle) and one more git generation back. Rule for the
  brief: a delegated agent may report "not found in the places I searched", never "does not exist"; the parent
  verifies every negative claim (one grep) before acting on it.
- Open-ended synthesis (Q10) works on both: every opportunity named was doc-grounded and its absence proof
  reproduced (the ARAP flag is declared and never read; no clothoid anywhere; the dark rim is spec'd in 44 §44.2
  and absent from `ink.mjs`). Two of the three are already BACKLOG rows (D1, T4); the Deegan rim and the
  syllable-locked type are documented but unlisted.

## The persistence question

"Don't we save dispatch tokens with a named agent that persists?" Could not be measured in this build: the
`SendMessage` continuation tool is not exposed here, so every dispatch was fresh. What is known: the fixed
overhead (~20-25 k) is the system prompt + rules + repo instruction files; a continued agent pays it once as
fresh tokens and afterwards as prompt-cache reads, but each continued turn re-sends its whole accumulated
context, so a long-lived explorer gets heavier per turn, not lighter. The saving a persistent agent really
offers is fewer *tool calls* (it already knows the tree). ECC's agents are the same frontmatter mechanism and do
not persist either; the native lever is the `memory` frontmatter key (per-agent memory across sessions) - the
next experiment: enable it on `explorer`, run rounds 1-2 again in a later session, compare tool calls.

## Round 3 — Sonnet 5 as the searcher (same day; the easy five again, with the docs index available)

Operator: "does it make sense to have a Sonnet 5 file searcher?" Same five questions as round 1, `Explore` with
`model: sonnet`, each prompt told about `docs/DOCS-INDEX.jsonl`.

| Q | Sonnet tokens / tools / s | verdict |
|---|---|---|
| 1 | 47,662 / 2 / 9 | ✗ half: numbers right, ruling mislabelled **"E46 §46.3"** (doc 46 is not a ruling; the answer is E38) |
| 2 | 46,828 / 3 / 20 | ✗ half: flag default found, "what turns it on in a build" (build_short.py:352) missed |
| 3 | 50,548 / 9 / 155 | ✓ |
| 4 | 48,432 / 8 / 138 | ✓ (line 282 for 284, right statement) |
| 5 | 44,691 / 3 / 13 | ✓ |
| | **238,161 / 25 / 336 s — 3.5/5** | Opus explorer on the same five: **155,988 / 31 / 138 s — 5/5** |

- Sonnet is not cheaper per lookup: the ~20-25 k fixed overhead plus a full prompt dominates, so its five cost
  **more** tokens than Opus's five, and two runs were slow. Its errors are the expensive kind - a confidently
  wrong label - which the parent then has to catch.
- **Decision: no Sonnet searcher.** The Opus `explorer` is the searcher; Haiku stays on `speedster` for
  edits with the exact line given. The `searcher.md` variant was removed.

## Persistence — verified

`memory: project` on `explorer` produced `agent-memory/explorer/{MEMORY.md, map_audio_bed.md}` on the first
dispatch: six `path:line - what` lines plus two traps no doc records ("the dir is tokyo-tea-break but the ids
say il-tea-break - grep both"; "the index's 'bed' hits are 'embed' noise - search lufs/bed_gain"). It landed in
the **worktree** (`project` scope = the session's project dir), so the roles now use `memory: user`
(`~/.claude/agent-memory/<role>/`), keyed by repo; the map moved there. Continuation (`/resume`) is CLI-only.

## Round 4 — the discoverability delta (same day, same prompts, same Opus `explorer`, the layers present)

Layers added between rounds 2 and 4: the docs index with body terms (roots: docs, the sources bundle, the projects' evidence
layer), the manifest, the topic index + citation graph, the gates / animation / craft registries, `memory: local` on the role.
Nine of the ten questions re-run (Q7 not re-run). "Before" = the Opus role's rounds 1-2 figures.

| Q | before tokens / tools / s | after tokens / tools / s | verdict |
|---|---|---|---|
| 1 cut-gap rule | 31,275 / 6 / 27 | 33,865 / 4 / 24 | ✓ |
| 2 min-jerk | 31,311 / 7 / 29 | 40,883 / 5 / 26 | ✓ |
| 3 mount | 34,294 / 8 / 32 | 42,642 / 7 / 30 | ✓ |
| 4 caption budgets | 30,318 / 7 / 32 | 33,720 / 5 / 19 | ✓ |
| 5 bed loudness | 28,790 / 3 / 18 | 35,071 / 6 / 146 | ✓ (one slow run) |
| 6 spring derivation | 42,136 / 7 / 34 — **false negative** | 46,090 / 5 / 37 | ✓ — found the research bundle; the gap phrased "not found in the roots searched" |
| 8 hedged-yield evidence | 55,704 / 11 / 65 | 54,970 / 11 / 94 before the projects root; **47,955 / 11 / 60 after** | ✓ — the evidence layer had to be IN the roots |
| 9 caption constants | 38,308 / 9 / 81 | 41,424 / 10 / 66 | ✓ |
| 10 documented-but-unbuilt | 46,907 / 12 / 72 | 70,164 / 12 / 82 | ✓ — richer (cites the day's new backlog rows), heavier |
| | **338k / 70 / 390 s — 8.5/9** | **392k / 65 / 488 s — 9/9** | |

- **Accuracy:** the false negative is gone; every negative claim now names the roots searched. That was the failure mode the
  operator flagged, and the layers closed it.
- **Tool calls:** down 7 % overall, down 25-40 % on the well-specified questions (Q1, Q2, Q4).
- **Tokens: up 16 %.** A grep on a layer returns whole JSONL records (an index record carries lead + labels + up to 12
  terms; a manifest record carries headings, labels and leads), so each hit costs more than a `grep -n` line did. The
  layers buy accuracy and fewer hops at a per-hit price. Fix queued: a query helper that prints one compact line per hit
  (`path:line — heading`) with a hit cap, so the agent reads a window only where it decides to.
- **Time:** mixed; two slow runs (Q5, the first Q8) were the built-in-grep straggler pattern, not the layers.
- **What this establishes:** same harness, same model, same prompts, layers added - a clean before/after on accuracy and
  hops; the token line is the honest cost of the current output shape, not of the idea.

## Round 5 — the compact query helper (`docs_find.py`) in the roles

| Q | round 4 tokens / tools / s | round 5 tokens / tools / s | read |
|---|---|---|---|
| 3 mount (one target, code windows) | 42,642 / 7 / 30 | 46,827 / 7 / 32 | no change: the cost is the fixed dispatch overhead plus the code windows it must open, not the layer hits |
| 10 documented-but-unbuilt (spans layers) | 70,164 / 12 / 82 | 57,841 / 14 / 87 | **−18 % tokens** where a hunt touches several layers |

- The helper cuts what it targets (a layer hit is 12x cheaper) and nothing else. The floor of a dispatch is ~30 k
  tokens on this harness (system prompt, rules, repo instructions, the role file, the auto-loaded durable memory) plus
  every window the answer needs; the layers cannot move that floor. The next lever on cost is the always-loaded layer
  (AGENTS.md 9.9 KB, CLAUDE.md, the ECC rules, the growing role files), not retrieval.
- Both runs correct; the Q10 answer now cites the day's backlog rows (R1-R3) by number.

## Round 6 — the dispatch floor, decomposed (grill 2026-09-05)

Measured from subagent transcripts (`~/.claude/projects/<session>/subagents/agent-*.jsonl`, first assistant turn):

| component | tokens | evidence |
|---|---|---|
| first-turn prompt of a bare `explorer` ("reply pong", no tools) | **27,647** | three probes: 27,649 / 27,653 / 27,653 |
| harness system prompt + tool schemas + connector listing | **≈ 16.3k** | the remainder after the attachments |
| the `instructions` attachment (CLAUDE.md → AGENTS.md, the ECC rules, the memory index) | **≈ 10.8k** | 41,385 chars: AGENTS.md 15,018 (the WORKTREE branch's old copy, not main's), MEMORY.md 10,120, the rules 13,429 across 9 files, CLAUDE.md 1,153, ~/CLAUDE.md 348 |
| session context + date | ≈ 0.5k | 2,073 + 83 chars |

Three facts that overturn earlier assumptions:
1. **The instructions block is snapshotted at session start.** Rules moved aside mid-session: 27,653. All 47 user skills moved aside: 27,653. AGENTS.md and the role file trimmed: 27,649. Every cut lands at the next session start, none in a running one.
2. **The rules DO load into every subagent** (3.2k), and so does the parent's memory index (2.5k): a read-only lookup was paying for the TDD checklist and 45 memory hooks. The user skills do NOT load (only their listing, inside the harness share).
3. **AGENTS.md is read from the session's project dir**: in a worktree session that is the worktree branch's copy, so trimming main's does nothing for a session started in an old-branch worktree.

Cuts made (land next session; verify as round 7 from a fresh session's first probe): AGENTS.md on main 15.0 → 3.9 KB; the always-loaded rules 13.4 → 1.5 KB (security + git), the rest as the `quality-rules` skill preloaded only by the implementing roles; MEMORY.md 10.8 → 6.8 KB (hooks capped); role files 4.4 → 1.3 KB (the retrieval discipline is the `retrieval-layers` skill, preloaded by the read-only roles); `maxTurns` per role. Expected instructions block for a read-only dispatch: ≈ 10.8k → ≈ 3k. The harness share moves only when the account connectors are disabled in the app (AOY 30 tools, Vercel ~40, Supabase ~30, Google Drive 11, claude-in-chrome, computer-use - the operator's ruling). The worktree copy of AGENTS.md is the remaining lever: start sessions on main or on a worktree fast-forwarded to it.

## Round 7 — fresh session after the cuts (2026-09-06, 00:00)

| probe | first-turn prompt | read |
|---|---|---|
| `probe_min` (tools: Read, `mcpServers: []`) | 13,214 | |
| `probe_mcp` (tools: Read, MCP inherited) | 13,214 | **connectors / MCP add nothing to a subagent's prompt** |
| `explorer` (Read, Grep, Glob, Bash + the retrieval-layers skill + memory) | 26,386 (was 27,647) | the tool schemas + role body + skill + memory ≈ 13k; unmeasured split - `probe_tools` (same tools, no skill/memory) runs next session |

The instructions block was still 38.3 KB in this session, for two reasons the round-6 cuts missed: (1) the rules
loader reads every `.md` under `~/.claude/rules` recursively, so the seven files moved into a subfolder still loaded -
they are now deleted (the `quality-rules` skill holds their content); (2) the session's project dir is the worktree, whose
AGENTS.md is the old branch's 15 KB - `git checkout main -- AGENTS.md CLAUDE.md` in the worktree fixes that for the
next session here. The memory-index cap did land (10.1 → 7.1 KB). Expected next session: instructions block ≈ 3.9 + 7.1
+ 1.5 + 1.2 KB ≈ 13.7 KB ≈ 3.5k tokens (from 38.3 KB ≈ 10k), i.e. a bare explorer near 19k and a minimal role near 6k.
