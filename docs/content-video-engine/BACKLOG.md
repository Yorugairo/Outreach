# Backlog — content video engine

Hand-maintained. `STATE-OF-WORK.md` is the auto-generated worktree census; this is the
work itself. Opened 2026-09-04 because the engine outgrew its original scope in one
week and the context was living in a chat transcript.

## The scope shift, named

The engine was scoped to **assemble plates and dock evidence over narration**. It is
becoming **a narration-timed 2D animation system**. Three findings did it, all from
this week:

1. **The chart engine was never chart-specific.** `drawOn(path, k)` progressively draws
   any SVG path — `callout` and `squiggle` already use it and neither is a chart. And
   `resolveTarget({kind:"datum", index})` resolves to a bar's box in stage coordinates,
   so anything can be positioned *against data*.
2. **The ledger page is a working surface, not a chart surface.** Props drawn in ink on
   the cream, then the same sheet becomes the chart — metaphor→evidence as a
   transformation, not a cut.
3. **Cuts belong in acoustic gaps.** Two reference channels sit at 82%; ep1 is at 32%
   with 68% landing mid-word.

Consequence: **prop assets, not world plates, are the unit of visual work.** A world
plate is spent on one shot; a prop composes and is reusable forever.

---

## Blocked on an operator decision

| # | item | the decision |
|---|---|---|
| B1 | **Tokyo short is 118 s against a 90 s cap** | Which beat loses ~24%. Candidates: cut the archetype (−10.4 s; the head-fake now does "everyone is wrong" with data), compress the tell (−7 s), or accept ~105 s and take the Facebook algorithm hit. Per-paragraph durations in `tokyo-tea-break/scratch/SCRATCH-INDEX.md`. |
| B2 | **3.9 GB asset pool + `f10b` worktree** | `content-generation-system-52f077` holds a complete parallel `content/video_engine` (14,842 files). `f10b` holds 18.4 GB, of which 8.68 GB is regenerable animatic frames. Needs a durable home that is not a worktree. |
| B3 | **174 unpushed commits** | `main` is local-only; last push 2026-08-30. Everything this week exists on one disk. Push needs explicit authorization. |
| B4 | **Gitignore policy on `review/claims`** | `.gitignore:77` ignores `content/video_engine/**/review/` wholesale, so 46 plate waves' approval manifests are untracked. Un-ignoring `*.json`/`*.md` there adds hundreds of files to git. |

## Build queue — animation

| # | item | state |
|---|---|---|
| A1 | **Renderer side of the `object` page** | Spec side SHIPPED (`ledger_page.py --variant object`, 12 tests). The template cannot draw one yet: it needs a branch that draws registered props via `drawOn` on the LP clock. |
| A2 | **Prop asset library** | The five Tokyo props are declared and validating but **do not exist as art**: toll gate, empty chair + cold cup + bill, crate stamped with a future year, locked lever, lit fab. Needs to be channel-walled and indexed like plates. |
| A3 | **`object` → chart transform on one page** | Declared by two Tokyo pages (`lp-obj-customer-leaving`, `lp-obj-crate-dated-later`). This is the piece that makes the architecture pay — no plate change, so E25 becomes unbreakable rather than enforced. |
| A4 | **The recede species ("whirlpool")** | Operator's idea; **not outside reality.** `spotlight` already paints a radial gradient with a moving centre and feathered hole as a function of `t`. Recede = same primitive, stops swapped, radius → 0, optional slow rotation on the masked group. Reveals cream underneath. |
| A5 | **Actor on the page = hands** | Mike is full colour; the page is ink on cream — a register collision. The record-document species already strokes a highlighter in time with the narrator's words. `build-f/ledger-hands.html` is an existing untracked proof. |
| A6 | **Expose the chart's coordinate mapper** | Each builder defines `mx()`/`my()` locally. Lifting them lets props share the chart's scale rather than stage pixels — the general form of `at: "datum"`. |

## Build queue — gates and pipeline

| # | item | state |
|---|---|---|
| G1 | **M13: a scene boundary lands in a gap ≥0.30 s, or is declared** | Proposed, **not built**. Fails ep1 at 68%. Mechanical and checkable from the word timeline. |
| G2 | **Short-runtime mode for `gate_opening_structure.py`** | 17 of the Tokyo short's FAILs are P1/P2 phase-beat rows on a 90 s script whose P1 computes to 9 s. The gate assumes long-form geometry. |
| G3 | **Stop compressing inter-paragraph silence in `tempo_edit.py`** | On the short it buys 117.8 → 103.3 s against a 90 s target — does not reach the cap, costs the scene signal, and forces the whole `retime_to_take` pass. Keep the tempo curve; drop the dead-space collapse. |
| G4 | **Tokyo `timeline.json` on the 9:16 template** | The template renders 9:16 (SHIPPED). No timeline uses it yet. Retires `player.html`, which still renders three wrong TIC figures. |
| G5 | **The 8 carried P34 reviewer mediums** | Audit staleness deferral; unresolvable-species gate events; G45 opt-in without `--title`; M11/M12 chart-dock inference; `--timeline` truncation; G28's dead phase check; `_dock_live_at` vs `_dock_span` schema; P1/P2 tolerance overlap. |

## Research — open questions worth an experiment

| # | question | how to settle it |
|---|---|---|
| R1 | **Cut ON the pause or THROUGH it?** | The measurement says references cut on it; it does not say ours is wrong to sometimes cut through. A/B by ear on one scene pair. |
| R2 | **Wealth Logic's four composition claims, unverified** | The "unifying equation spine" (one mechanism across variants vs. six unrelated tips), ~10 s evidence holds, one persistent host, captions with no background pill. These are visual — they need the frames, not the timings. R2a: the equation spine is the one that could change *script* architecture. |
| R3 | **Does a prop library actually compose?** | The claim is that 5–8 props cover most metaphors and compose combinatorially. Testable by briefing three unrelated episodes against one prop set and counting misses. |
| R4 | **Flow Characters as identity lock** | The `@Mike` binding works for plates. Untested for motion — the identity test showed hair drift on a 6 s clip. |
| R5 | **Parallax + object page** | 2.5D parallax is proven on world plates. Unknown whether it helps or hurts an ink-on-cream page. |

## Carried debt

- **`f10b` plate rehome.** 55 indexed plates still resolve into the codex worktree; the main-checkout rehome (615 files) did not cover them. Must happen before that tree is removed.
- **Steel and Paper's timeline references assets by absolute worktree path** (`...\.claude\worktrees\sweet-villani-1c3a16\...`). Breaks when the worktree goes.
- **Flow driver has no README**, and a fresh checkout needs `npm install` in `tools/google-flow-driver` before either MCP server starts.
- **Drive connector needs reconnecting** — returned a permissions error on the master-prompt file.
- **Tokyo `plate-01-*`** — all three rolls are the photoreal stranger from before the character binding was fixed. Re-roll on bound `@Mike`.
- **The Steel and Paper re-script** (`REWRITE-ORDER-G`) — the original next task, now with M13, object pages and the E28 charts available to it.

## Shipped this week (so the next session knows the ground)

P34/P35/P36 complete · the viewer binds (recall FAILs, confusion WARNs, gain retired) ·
the generative-video stack rescued onto main and the MCP registered · the plate library
rehomed and rebuilt (326 plates, 0 worktree paths) · the template renders **9:16** ·
the break ration counts delivery marks only · Tokyo: script reframed on live TIC data,
four charts built from FRED/Treasury/yfinance, dossier, shot table, and the ledger
page's **`object` variant**.

## Rulings and rules opened this week

E22 add. 7 · E24 · E25 · E26 · E27 add. · E28 + addenda ·
`RULE-abstract-to-concrete.md` · `RULE-the-page-is-the-ground.md` ·
`FINDING-gaps-are-the-edit.md`
