# STUDIO READINESS REVIEW - before Astra or Fable plans the agentic-first production studio (2026-09-13)

Status: a readiness review, NOT a plan. The operator: *"i think we should ultimately have asrta or fable draw up the real
plans for this, you should just do the initial readiness review"*. The request it answers: *"seems like the next natural step
is to build out the actual agentic-first human-production studio interface system with timeline, proof player, LLM-in-session
awareness, etc"*. Written by the Claude lane from a read-only recall
(`docs/research/runs/studio_readiness/STUDIO-RECALL.md`), a documentation check of the session link
(`docs/research/runs/studio_session_link/findings.md`) and measured repo state. Every claim cites a path; "not found in
<places>" is stated where the record is silent.

**Inputs are gitignored** (`docs/research/runs/**`): a planner in its own worktree - Astra's rule (BACKLOG R26-84) - will not have
the recall map, the operator-decisions note or the session-link findings. This review therefore carries every fact the plan needs
from them; the run files are the fuller evidence on the machine that wrote them.

## 0. The operator's decisions so far (verbatim, 2026-09-13)

1. **The in-session agent:** *"I think we should have the claude code session (and would be great if it could be Claude Code
   session OR Codex Session--considering we can already use bridge & CLI capability and have both apps open at the same time,
   seems like it should be possible)"*. Not in-page API agents billed per call.
2. **v1's job:** cut an EXISTING build end to end - open a served build; proof player + track timeline (scenes, docks, species,
   captions, waveform, cues); drag effects from the P55 catalogue onto instants; retime and dial through the sidecar; the agent
   answers with the change report and frames.
3. **Direct manipulation in v1:** *full canvas editing* - drag/resize docks and draw species targets (rings, spotlights,
   brackets) on the frame, beyond a timeline + inspector.
4. **Who plans:** Astra (Codex lane) or Fable (the Claude parent), not this review.

## 1. Verdict

**Ready to PLAN now; not ready to BUILD until the prerequisites in section 3 are met.** About 70% of the studio already exists
as wired, tested pieces (section 2). The two genuinely new systems are (a) the session link - nothing streams editor state to a
coding-agent session today - and (b) the timeline/canvas edit grammar - the sidecar cannot yet express the edits the operator
chose (section 5). The largest decision the planner owns is the front-end fork in section 4: grow the scene-evidence engine's
thin editor, or harvest P30's React editor kernel onto it.

## 2. What already exists (reuse before building)

| piece | state | where | verdict for the planner |
|---|---|---|---|
| The renderer / proof player: `scene-evidence-engine.mjs` + the split shell, a pure function of t, `reload()`, `?t=` | WIRED, goldens byte-identical | P51 T1/T4; `docs/content-video-engine/samples/` | keep as-is - the studio's canvas IS this frame |
| The review server `serve_player.py`: `GET /reload` (25 s long-poll, `--watch` recompile + determinism check on changed instants), `POST /overrides` (the only write, validated by the compiler first), `GET /editor.html`, the P55 catalogue + golden-frame routes | WIRED | `content/video_engine/scripts/serve_player.py` | extend - the one server; keep the single write door |
| The override sidecar `overrides.json` + `apply_overrides` (keys `<scene>.plate / .exit / .camera / .dock.<slide> / .species.<index>`) | WIRED, 36 tests | `build_scene_timeline_f.py` `OVERRIDE_KEY_FORM`; P51 T5 | keep - extend its grammar (section 5) |
| The thin editor `editor.html` (iframe of the served player, scrub, scenes/docks/species lists, ghost drag outline for centred docks, read-only sidecar view, dials panel DISABLED, P55 card text per species) | WIRED, human gate 3 OPEN | `content/video_engine/editor/editor.html` | extend or replace per section 4 |
| The agent's eyes: `probe.py` (at t: docks, boxes, captions, type sizes, overlaps; <2 KB JSON), `self_watch.py`, `determinism_check.py`, M25 | WIRED | P51 T2/T3/T4 | keep as-is - the agent reads data, not pixels |
| The change report `change_report.py` (before/after frames at changed instants + gate delta) | WIRED, human gate 2 OPEN | P51 T6 | keep - the agent's reply to a human edit |
| The effects catalogue: 125 cards, `effects_card.py "<name>"`, `authoring/effects.py`, the drift gate | COMPLETE (P55), uncommitted | `content/video_engine/effects/cards/`, `docs/EFFECTS-CATALOG.*` | extend - the studio's elements palette |
| P30 Interactive Remotion Production Editor: React 18.3.1 + `@remotion/player` 4.0.502 + Vite; timeline scrub/zoom/drag/trim with snapping, canvas select/drag/resize/rotate, inspector, palette, 100-command undo, draft recovery; a framework-free TS kernel (`production_console/src/editor/`, 2,258 lines: commands, geometry, snapping, timeline, selection, keyframes, draft, validation - imports no React/Remotion package) | BUILT on main (merged 330c01e); plan `running`; gates A-D **no operator verdict recorded**; `node_modules` absent | `content/video_engine/production_console/`, `.claude/PRPs/plans/P30-...`, `.claude/PRPs/evidence/P30/` | the fork in section 4 |
| The bridge (P46): stdlib send/reply/watch/daemon, lanes gemini + claude, folder state machine, `bridge_handler` tier-1 agent | running; T4 packet contract (HG1) pending | `content/video_engine/scripts/bridge_*.py` | keep - lane-to-lane orders (research, composites); not a live UI channel |
| `video-engine` MCP server | it is the **Google Flow / ComfyUI generation driver** (8 tools: create/get Flow image, video, batch, status; Comfy parallax) - no engine, probe, sidecar or editor tool | `.mcp.json:10-15` -> `tools/google-flow-driver/mcp/server.mjs` | extend with a sibling server, or add studio tools (section 6) |
| P15 FastAPI console (intake, triage, promotion), P16 console/editor convergence (deep links, Studio lifecycle) | complete | `content/video_engine/console/` | keep, out of the timeline loop |
| Rejected already | an iframe of Remotion Studio (doc 25: "deep links. No iframe."); an editor holding live state; vision as the agent's eyes; writing a human's edit into the shot table; "a GUI-first tool for agents ... agents don't drag" | `25-EDITOR-EMBEDDING-SPIKE.md:6`; `GRILL-ANIMATOR-ITERATION-2026-09-11.md` s2 | do not re-open without the operator |

## 3. Prerequisites before building (in order)

1. **Commit the evening batch - needs the operator's word (BACKLOG R26-83).** Main is 4 commits ahead of origin with 70 modified
   tracked files and 259 untracked entries (`git status --short`, 2026-09-13). The studio would build on uncommitted P55 (routes,
   species panel, effects kit, catalogue), the uncommitted melt, E95 and R26-93/94. R26-84 requires Astra to work in its OWN
   worktree off a commit, and the runbook's lane rule forbids any lane committing another lane's files
   (`docs/runbooks/PRP_EXECUTION.md` "Lane write sets").
2. **Close P51's open human gates in the first studio session - RULED by the operator 2026-09-13: *"p51 gets closed in the first studio session"*.** HG2 (the change report: the operator's three hand edits, the report the agent
   gets, the reply that cites it) and HG3 (the thin editor on `tokyo-editor` :8744) are open (P51:234, :247; ledger
   `1a521410aaaa`). The operator chose "cut an existing build" for v1, which IS that session - the planner should either make the
   operator's first studio session the gate-closing session or record that the studio supersedes both gates.
3. **Rule on P30.** Its plan is `running` with no recorded verdict on gates A-D, while the operator praised it (*"we have a real drag
   and drop, editable timeline, plugged in with the remotion bits assets"*, ledger `95f31acf6f2d`) and P51 recorded it as *"a
   different runtime; only its remotion-ui components are reused, as a shell"* (P51:94). The studio decision in section 4 needs P30
   marked finished-as-reference, harvested, or retired.
4. **Establish the test baseline** before engine work (section 7).
5. **Decide the plan's home and lane.** A PRP lives in `.claude/PRPs/plans/`, which the lane table assigns to the Claude lane
   (`.claude/**`); Codex has its own `architect_sol` (`.codex/agents/architect_sol.toml`, `gpt-5.6-sol`). If Astra plans, the
   draft crosses lanes: name the landing path in a brief (or draft under `.codex/` and let the parent copy it, as P55's draft was
   copied from a worktree).

## 4. The front-end fork (the planner's biggest call; put it to the operator)

- **A - grow the thin editor** (`editor.html`, stdlib, no build step): keeps "the editor is plain HTML" (P51 Mandatory Reads) and
  the one-file law; every timeline, canvas and undo capability is new code.
- **B - a shell over the same server, harvesting P30**: the P30 TS kernel (commands, snapping, selection, keyframes, 100-step undo,
  draft recovery, geometry) is framework-free and liftable; its document model is shaped around Remotion props
  (`isRemotionBitProps`, `TimelineItem`) and must be re-targeted to the scene-evidence timeline + sidecar. The React/Remotion
  Player half does NOT carry over - the proof player is the scene-evidence engine (P51 T1), shown in the same-origin frame the
  thin editor already uses. The memory `steal-now-harvest-not-replace` is the rule: graft the idea, never swap a reviewed
  mechanism.
- Either way: the studio is a CLIENT of the served build (no engine state, no second engine), writes only through
  `POST /overrides`, and the canvas shows the real frame with a ghost outline during a drag (grill s1).

## 5. The edit grammar gap - what the chosen v1 cannot express today

Measured in `build_scene_timeline_f.py` (`OVERRIDE_KEY_FORM`, `_override_dock`, `_override_species`, `DOCK_OPTS`,
`SPECIES_CLOSED_FIELDS`):

| operator's v1 action | sidecar today | gap |
|---|---|---|
| retarget / move a ring, spotlight, bracket, callout | `<scene>.species.<index>` accepts every field except `kind` and `id` (targets included), validated by `validate_species` | none for editing an existing species; ADDING a species (dragging an effect from the catalogue) has no key - "a sidecar never changes what a species IS" |
| drag a card on the canvas | `<scene>.dock.<slide>` accepts `DOCK_OPTS` only: `centre_x/centre_y/centre_w` exist for CENTRED cards | a slotted (non-centred) dock has no free x/y/w/h; resize has no key |
| retime a dock (drag/trim its block on the timeline) | the dock tuple's `enter` / `exit` / `slot` are NOT option fields | no key - needs grammar + the E47/M-gate interactions |
| retime a scene boundary / reorder | row spans are the shot table's | no key; boundaries are anchored to the take's words (the gate-fit rule: move beats, never clip words) |
| change a plate, exit, camera | `.plate`, `.exit`, `.camera` | none |
| dials (the editor's disabled panel) | no `dials` key (`editor.html` dials fieldset) | no key |
| add a dock / an effect from the P55 palette | none | the biggest gap - the sidecar is an edit layer over AUTHORED rows; insertion is authoring. The planner must decide whether insertion writes the sidecar (new grammar) or a shot-table proposal the agent applies (the grill's "the agent applies" loop) |
| undo | the sidecar's own history is the file; P30's kernel has a 100-command undo | needs a model (sidecar revisions vs client-side command stack) |

## 6. The session link (Claude Code OR Codex)

Documentation check, 2026-09-13 (`docs/research/runs/studio_session_link/findings.md`; local `claude` 2.1.259, Codex
`codex-cli 0.154.0-alpha.6.2` from the desktop app, not on PATH). The operator's "Claude Code OR Codex" is feasible for READ and
WRITE in both; PUSH is not symmetric:

| capability | Claude Code | Codex |
|---|---|---|
| a local Streamable HTTP MCP server with a bearer token | CONFIRMED (`.mcp.json` `type: http`, `headers`) | CONFIRMED (`config.toml` `url`, `bearer_token_env_var`) |
| one server serving both clients at once | PLAUSIBLE (spec allows multiple clients; no doc shows both) | same |
| tools reach the model | CONFIRMED | CONFIRMED (the only documented surface) |
| resources / prompts | CONFIRMED | NOT FOUND |
| context injected on the next prompt (a hook) | CONFIRMED (`UserPromptSubmit`, `SessionStart`) | CONFIRMED (`UserPromptSubmit`, `SessionStart`) |
| push into a RUNNING session | CONFIRMED via "channels" - a stdio server emitting a channel notification; research preview, loaded with a development flag at launch, CLI only (desktop: NOT FOUND), no delivery ack; or PLAUSIBLE via an `asyncRewake` hook | NOT FOUND for an open window; a new headless turn on a thread via `codex exec resume <thread_id>` CONFIRMED; app-server `turn/steer` on a thread it owns (WebSocket "experimental and unsupported") |
| the bridge | a `claude` lane exists | **no `codex` lane** (`LANES = ("gemini", "claude")`) |

The researcher's recommended shape (an input, not a design decision): one 127.0.0.1 studio server - REST for the page with an
Origin allowlist, Streamable HTTP `/mcp` for agents with a bearer token; three tools as the contract (`studio_get_context`,
`studio_next_events(since)`, `studio_apply_override` writing the sidecar through the compiler's validation); events in a runtime
queue with a per-client cursor; a `UserPromptSubmit` hook in both clients announcing "N studio events waiting" (the
`bridge_inbox.py` pattern); Claude-only true push added later behind a pilot; a `codex` lane added to the bridge for headless
requests. **Design for pull first**: it is the only thing both clients document today. The MCP spec's security rules apply to a
localhost server (validate `Origin`, bind 127.0.0.1, authenticate).

What exists today (recall, measured): no event stream (no SSE / WebSocket / postMessage anywhere in scripts, editor, console,
production_console or the Flow MCP); no selection or playhead model; the only live endpoint is `/reload`'s long-poll. What an
agent can already READ: `<build>/overrides.json`, `CHANGE-REPORT.md`, `SELF-WATCH.md`, `layout-probe.json`, `/reload`, and
`probe.py` at any t. The bridge moves orders between lanes but is not a UI channel.

## 7. Test baseline (measured 2026-09-13)

`python -m pytest content/video_engine/tests -q --continue-on-collection-errors` on the main checkout's uncommitted tree:
**66 failed, 2,734 passed, 5 skipped, 2 errors in 13:17** (the earlier full run recorded in R26-91 was 66 failed / 2,568 passed).

- **The 2 errors are a collection collision, not missing code:** collecting the whole directory fails `test_pipeline.py` and
  `test_history_v4_pipeline.py` on `ModuleNotFoundError: No module named 'src.config'` (the repo-root `src/config.py` exists; another
  module's `sys.path` insert lets `content/video_engine/src` shadow it). Run alone they collect: 16 passed, 5 failed (the five
  `test_history_v4_pipeline.py` gate/hash tests, August lane).
- **Three of the 66 were regressions from P55 (2026-09-13), found by this baseline and FIXED the same evening** (81 passed on
  re-run): `test_authoring_kit::test_the_kit_is_the_five_modules_the_plan_names` (the pin did not move when P55 T8 added
  `authoring/effects.py`); `test_portrait_parity::test_no_landscape_literal_in_player_code` (P55 T7 lifted the verdict stack's
  landscape reference `REF_W: 1920` / `REF_H: 1080` out of a `STAGE_W` expression into named dials - proven used only as a fraction
  of the stage, allowlisted with that reason); `test_page_boxes::test_the_fixture_names_every_builder...` (the layout fixture is
  stamped with the player's hash; re-measured - every box identical, only `player_sha256` and the date moved).
- **Studio-relevant reds (the P30 lane):** `test_production_console.py` 4 (bridge loopback/static/snapshot, media resolution and
  traversal, the job API, hash mismatch), `test_production_editor_revisions.py` 2, `test_production_editor.py` 1,
  `test_production_console_snapshot.py` 1, `test_console_runs.py` 1 - **P30's own suite is red today**, which bears directly on the
  section 4 fork (a harvest must not import a broken bridge).
- **Other pre-existing reds** (R26-91 family and August lanes): the `test_finance_*` proofs (~30 across 14 files),
  `test_p33_first_five_evidence_obligation.py` 3, `test_self_watch.py` 2 (Tokyo's build is NOT CLEAN on M11/M27 - the known Tokyo
  M11), `test_bridge_handlers.py` 2, `test_bridge_send.py` 1, `test_audio_synth.py` 2, `test_full_episode_evidence_coverage.py` 2,
  `test_video_dock.py`, `test_dock_over_build.py`, `test_field_ink_e67.py`, `test_motion_gate_wiring.py`,
  `test_measure_motion_energy.py`, `test_path_contract_structural.py`, `test_remotion_editorial_fixture.py` (1 each).
- **`test_build_docs_layers::test_the_committed_tree_passes_check`** read the docs index one line stale mid-run (a memory export
  landed after the last layer write); the layers are regenerated when this review is published.
- The planner should treat "the suite is green" as false today: a studio slice proves itself on its own tests plus the goldens, and
  any slice touching the P30 code starts by triaging its 9 reds.

## 8. Constraints the plan must carry (from the record, not new rules)

- The player stays a pure function of t; a ghost outline may follow a drag, the real frame lands on release (grill s1; P51 Not
  Building "any runtime state in the engine").
- One write door: the sidecar through the compiler's validation; never write a human's edit into the shot table (grill s2).
- Agents read data (probe, change report, catalogue), not pixels; the studio is for the human and the agent is its second user
  (ledger `8ff33393ab6a`: "an agent doesn't drag").
- A served review link is a frozen copy; live editing happens on a private build (memory `review-link-frozen-copy`) - the plan
  must say how a live studio and a frozen review copy coexist.
- Effects are called by their P55 cards; composite effects keep every phase (memory `composite-effects-keep-every-phase`).
- Generated or pulled assets enter with provenance through the evidence intake; figures are never fabricated (grill s5).
- One engine/compiler writer at a time (R26-84); lane write sets; Fable spent only on judgement (runbook model policy).

## 9. Risks

- **Scope**: full canvas editing + timeline retiming + insertion + a two-client session link is a large v1; the grammar work in
  section 5 touches the compiler, the most contended file.
- **Determinism**: the editor's first gate proof found a determinism mismatch at 61.76 s on `build-short-t7` (the R26-46/47
  family) - live editing multiplies re-renders; the check must stay cheap.
- **Weight**: a long form's split build is heavy (Steel and Paper: `assets.json` 91 MB, engine 852 KB, timeline 587 KB) - the
  studio loads it once and must not re-fetch per edit.
- **Two editors diverging**: P30 and the thin editor both claim "the editor"; without the section 4 ruling the studio becomes a third.
- **Push into a running session** may not be supported identically by both clients (section 6) - design for pull first.
- **Uncommitted base**: building before prerequisite 1 risks lanes stepping on 329 dirty entries.

## 10. Open questions (for the operator unless marked planner)

1. Section 4: A (grow the thin editor) or B (harvest P30's kernel into a shell over the scene-evidence server)?
2. P30's disposition: finished-as-reference, harvested, or retired?
3. ~~Does the first studio session close P51 HG2/HG3?~~ RULED 2026-09-13: yes - *"p51 gets closed in the first studio session"*.
4. Insertion from the palette: sidecar grammar, or a shot-table proposal the agent applies? (planner proposes, operator rules)
5. Push vs pull for the session link where a client cannot receive push (planner, from section 6).
6. Live studio vs frozen review copies: separate ports and copies, or a "freeze this state" action that makes the copy? (planner)
7. The missing console doc: `23-REMOTION-PRODUCTION-CONSOLE.md` (named by P29 T10) is not found in `docs/content-video-engine/`
   (docs_find 0 hits); CAPABILITIES:118's "doc 29 s9.3 production route" was not found either (planner: fix or drop the cite).
