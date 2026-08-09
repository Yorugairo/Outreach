# Plan: Google Flow Extension — Trusted Submit + Flow-Owned Generation Proof

## Summary

The Flow driver's prompt entry was fixed with trusted CDP input, but the **Create-button click is
still an untrusted content-script `element.click()`** — the same input class Flow provably ignores.
Implement a trusted CDP mouse click beside the existing `Input.insertText` path, derive
`generating` exclusively from Flow-owned DOM evidence (the media-observer diff that already
exists), and prove one zero-credit image end-to-end per the handoff's 5 acceptance items.

## User Story

As the operator, I want the extension's submit action to be accepted by Flow exactly like my own
click, so that one observed zero-credit generation unblocks the paused queue with real evidence
instead of state-machine fiction.

## Problem → Solution

Trusted prompt lands, button enabled, click "dispatched" → **no Flow generation ever observed**
(8 failed queue items) → trusted `Input.dispatchMouseEvent` at the button's live center + ack
derived only from media-observer codes → one receipted zero-credit image in quarantine.

## Metadata

- **Complexity**: Medium (4–5 files, ~150–250 lines + tests)
- **Source PRD**: N/A — live-defect fix per `docs/content-video-engine/28-GOOGLE-FLOW-EXTENSION-CLAUDE-HANDOFF.md`
- **Working tree (critical)**: implementation lives UNCOMMITTED in
  `C:\Users\Snipe\.codex\worktrees\f10b\Outreach Program\tools\google-flow-driver\` — the native
  host + extension ID (`aigaggeolhimkhmbdhoempnbghdgkoka`) are registered against that tree's
  build output (`.codex/flow-extension-build/extension`). Edit THERE; do not port code into this
  worktree. This plan file is the only artifact that lives here.
- **UX**: N/A — internal driver

## Root-cause hypotheses (ranked; T2 discriminates before code lands)

| # | Hypothesis | Prior | Evidence |
|---|---|---|---|
| H1 | Flow's submit handler requires trusted input (isTrusted / real pointer sequence); synthetic `.click()` at `content-script.js:213` is silently ignored | ~0.80 | Exact precedent: synthetic `beforeinput/input/execCommand` looked correct while Flow returned "prompt wasn't provided"; only CDP `Input.insertText` worked (handoff §Verified 2–3). SW has **no** `Input.dispatchMouseEvent` anywhere (grep-verified) |
| H2 | Click accepted but Flow rejects for a non-click reason (settings not committed, toast shown, quota gate) | ~0.15 | Settings popup stays open by design (handoff §1); no toast capture exists post-click |
| H3 | Generation happens but the observation window/selectors miss it | ~0.05 | media-observer diffs by provider/card identity and predates URLs — robust, but must start BEFORE the click |

## Hard constraints (from handoff — restate in every task)

Queue stays **paused**; zero-credit Nano Banana Pro 16:9 ×1 only; no paid/video path changes; no
permission or host-allowlist broadening; no cookie/token/page-script inspection; extension acts in
background (visible Chrome tab on Flow is fine; no extension tab in the loop); every output
quarantined, nothing promoted to the asset catalog; a click/state-change/readback is **not** proof
— only a Flow-owned busy state or new media card is.

## Mandatory Reading (before implementing)

| Priority | File (in the codex worktree) | Why |
|---|---|---|
| P0 | `docs/content-video-engine/28-GOOGLE-FLOW-EXTENSION-CLAUDE-HANDOFF.md` | The contract this plan implements |
| P0 | `extension/src/service-worker.js:400–470` | Existing debugger attach + `Input.insertText` lifecycle to mirror |
| P0 | `extension/src/image-runner.js` (all 430 lines) | The arm→submit→observe orchestration this plan rewires |
| P1 | `extension/src/media-observer.js:150–280` | Snapshot diff + `fresh_media_settled` / `generation_failed` codes — the ONLY legal `generating` source |
| P1 | `extension/src/selectors.js:400–410, 525–545, 120–145` | Create-button matcher, `aria-busy`/`data-flow-generation-status`, generated-media grid |
| P1 | `extension/src/state-machine.js:480–520` | `submitted → generating` now observation-gated — do not regress |
| P2 | `tools/google-flow-driver/package.json` + build script | How `.codex/flow-extension-build/extension` is produced (find before first reload) |

## External Documentation

| Topic | Source | Key takeaway |
|---|---|---|
| CDP mouse input | chromedevtools.github.io/devtools-protocol → `Input.dispatchMouseEvent` | Coordinates are **CSS pixels relative to the main-frame viewport** (no DPR scaling); emit `mouseMoved` → `mousePressed` → `mouseReleased` with `button:"left"`, `clickCount:1`; Chrome synthesizes the full trusted pointer/mouse/click sequence (`isTrusted: true`) |
| Debugger co-use | developer.chrome.com/docs/extensions/reference/api/debugger | One attach per target; reuse the existing insertText attach/detach lifecycle — a second `attach` to the same tab throws |

KEY_INSIGHT: CDP input is dispatched to the tab regardless of window focus, but React apps may
gate on `document.visibilityState` — keep the Flow tab active (`chrome.tabs.update(tabId,
{active:true})` is within current permissions) before the click.
APPLIES_TO: Task 3.
GOTCHA: if the button center moves (layout shift after settings popup), re-measure immediately
before dispatch; never cache the rect across await points.

## Patterns to Mirror

### TRUSTED_INPUT_LIFECYCLE (extend, don't duplicate)
```js
// SOURCE: extension/src/service-worker.js:427-433
await chrome.debugger.sendCommand(target, 'Input.dispatchKeyEvent', {...});
await chrome.debugger.sendCommand(target, 'Input.insertText', { text: String(prompt || '') });
```
→ add `trustedClick(target, {x, y})` beside it: same attach guard, same error/detach path.

### THE DEFECT SITE (replace for submit only)
```js
// SOURCE: extension/src/content-script.js:213
element.click();
```
→ for the Create action becomes: measure `getBoundingClientRect()` center (+ `visualViewport`
offsets if nonzero) → return coords to SW → SW dispatches trusted sequence. Keep the old
`.click()` recorded as a diagnostic fallback attempt, never as the primary.

### OBSERVATION-GATED STATE (do not regress)
```js
// SOURCE: extension/src/state-machine.js:506-508
if (this.state === 'submitted' && normalized === 'generating') {
  this.transition('generating', { code: 'generation_started', observation });
```

### FLOW-OWNED ACK CODES (the only proof)
```js
// SOURCE: extension/src/media-observer.js:219
code: settled.length ? 'fresh_media_settled' : diff.failures.length ? 'generation_failed' : 'fresh_media_pending',
```

## Files to Change (all under the codex worktree's `tools/google-flow-driver/`)

| File | Action | Justification |
|---|---|---|
| `extension/src/service-worker.js` | UPDATE | `trustedClick` via `Input.dispatchMouseEvent`; tab-activate before dispatch; message handler for click requests |
| `extension/src/content-script.js` | UPDATE | Button-center measurement (rect + visualViewport), pre-click media snapshot trigger, post-click toast/error capture; demote `.click()` to diagnostic |
| `extension/src/image-runner.js` | UPDATE | Submit step = measure → trustedClick → bounded ack poll (media-observer + `aria-busy`) → observation-gated transition |
| `extension/src/selectors.js` | UPDATE | Toast/error-surface selector + structural (redacted) capture helper; any card attributes learned in T7 |
| `tests/` (image-runner, content-bridge, media-observer) | UPDATE | Coord math, message contract, ack gating, toast-failure path; fixture from live card DOM |
| `docs/content-video-engine/28-…-HANDOFF.md` | UPDATE | Append live-run findings + captured selectors (or add a 29-doc) |

## NOT Building

Queue architecture changes · paid/video lane changes · permission/manifest changes · broad
automation (no Puppeteer/whole-browser driving) · media download/import selector repair **until**
one generation is visibly complete (handoff step 5) · queue resume (operator decision after
acceptance evidence).

## Step-by-Step Tasks

### Task 1: Checkpoint instrumentation (no behavior change)
- **ACTION**: Before any click, record a diagnostic event: resolved button outerHTML (redacted to
  tag/attrs), rect, `disabled`/`aria-disabled`, pre-click media snapshot id from media-observer.
- **MIRROR**: media-observer snapshot API; existing diagnostic event shape in image-runner.
- **VALIDATE**: `npm --prefix tools/google-flow-driver test` stays green (64 baseline); one live
  arm (no click) shows the event with a non-empty rect.

### Task 2: Differential probe — manual vs synthetic click (decides H1 before code)
- **ACTION**: Temporary capture (via existing `capability-capture.js` channel): listen on the
  Create button for `pointerdown/pointerup/mousedown/mouseup/click` logging `isTrusted`, sequence,
  target. Operator clicks once manually (expected: generation starts — also revalidates the lane);
  then one synthetic `.click()` run. Diff the two logs.
- **GOTCHA**: This consumes one zero-credit generation on the manual click — that is acceptable
  and doubles as the "Flow still works at all" control the 8 failures never established.
- **VALIDATE**: Two captured event logs archived in the run's diagnostics; H1 confirmed if the
  synthetic log lacks trusted pointer sequence AND manual click generates while synthetic doesn't.

### Task 3: `trustedClick` in the service worker
- **ACTION/IMPLEMENT**: `async function trustedClick(target, point)` → ensure Flow tab active →
  `Input.dispatchMouseEvent` ×3 (moved/pressed/released, CSS-px coords). Reuse the exact
  attach/detach + error paths of the insertText block (service-worker.js:400–470). Coordinate
  message: content script measures at dispatch time, returns `{x, y, devicePixelRatio,
  visualViewport: {offsetLeft, offsetTop}}`; SW uses CSS px as-is (DPR recorded for diagnostics
  only).
- **GOTCHA**: single debugger attach per tab — if insertText attach is live, reuse it; never
  parallel-attach. Re-measure after `tabs.update` (activation can reflow).
- **VALIDATE**: unit test for the message contract + coord passthrough (mock `chrome.debugger`);
  live: click visibly depresses the button (screen), no `flow_root_not_found`.

### Task 4: Rewire the image-runner submit step
- **ACTION**: Replace the synthetic click call for Create with measure→trustedClick; record the
  old `.click()` result only as `diagnostic.fallback_click`. Keep paid/video paths untouched
  (zero-credit lane only, per handoff).
- **MIRROR**: THE DEFECT SITE pattern above; bounded-arm contract in state-machine.js.
- **VALIDATE**: tests green; live run reaches `submitted` with a `trusted_click_dispatched` event.

### Task 5: Flow-owned ack (the only path to `generating`)
- **ACTION**: After trustedClick, bounded poll (e.g. 15s, 500ms interval): media-observer diff
  (`fresh_media_pending`/`fresh_media_settled`), `aria-busy`/`data-flow-generation-status`
  (selectors.js:534-536), toast/error surface. Map: pending/settled → `generating`/`settling`;
  toast/`generation_failed` → failure event with redacted structural capture; timeout → failure
  `no_flow_ack` (NEVER `generating`).
- **MIRROR**: OBSERVATION-GATED STATE + FLOW-OWNED ACK CODES patterns.
- **VALIDATE**: unit tests for all three ack outcomes with fixture snapshots; live: state history
  shows `submitted → generating` only after a real card/busy observation.

### Task 6: Live acceptance run (operator present; queue still paused)
- **ACTION**: One zero-credit Nano Banana Pro 16:9 ×1 on the verified project URL through the new
  path. Capture: prompt readback, trusted click event, Flow busy/card observation, downloaded
  file → immutable quarantine, receipt `{item_id, file_hash, provider_media_id?, credits: 0}`.
- **VALIDATE**: all 5 handoff acceptance items hold; artifacts on disk; only then repair
  card-discovery/download selectors if they failed (handoff step 5) and add the redacted DOM
  fixture + test.

### Task 7: Documentation + handback
- **ACTION**: Append findings (H1/H2/H3 verdict, captured selectors, receipt path) to the 28-doc
  or a new 29-doc in the codex worktree; note explicitly whether queue resume is now justified —
  that decision stays with the operator.
- **VALIDATE**: doc lists the exact evidence paths; queue left paused.

## Testing Strategy

| Test | Input | Expected | Edge |
|---|---|---|---|
| coord contract | mocked rect + visualViewport offsets | SW receives CSS-px center | scrolled page, zoomed page |
| ack: fresh card | observer diff fixture with new provider id | `generating` transition | pre-existing cards ignored |
| ack: failure toast | toast fixture | failure event, no `generating` | — |
| ack: timeout | empty diffs | `no_flow_ack` failure | never promotes state |
| attach reuse | insertText attach live | no double-attach error | detach on thrown command |

Edge checklist: [ ] button re-measured after activation · [ ] settings popup overlapping button
center (dispatch hits popup → detect via ack timeout + capture) · [ ] MV3 worker suspension
mid-poll (alarm/keepalive already exists per handoff recovery hooks — verify) · [ ] second run
without extension reload.

## Validation Commands

```bash
npm --prefix "C:\Users\Snipe\.codex\worktrees\f10b\Outreach Program\tools\google-flow-driver" test
```
EXPECT: 64 baseline + new tests, zero failures.

Live (operator-gated, one zero-credit item): the 5 acceptance items from the handoff, evidenced by
files + events, not logs of intent.

## Acceptance Criteria
- [ ] H1/H2/H3 discriminated with captured event logs (T2)
- [ ] `generating` unreachable without a Flow-owned observation (tests prove it)
- [ ] One zero-credit image: accepted prompt → trusted click → visible Flow generation → new card
      → quarantined file + receipt with zero credits
- [ ] Queue still paused; paid paths untouched; no manifest/permission diffs
- [ ] Test suite green; findings written back to the handoff doc

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| H2 is the real cause (click fine, settings/quota reject) | Medium | Medium | T2 differential catches it before any code; toast capture in T5 names the reason |
| Flow DOM changes between sessions | Medium | Medium | Role/aria/text selectors already preferred (selectors.js:8); capture attributes in T6 fixture |
| Debugger bar/UX friction ("started debugging this browser") | High | Low | Expected banner; already accepted for insertText |
| MV3 worker suspends during ack poll | Medium | Medium | Bound poll ≤15s; verify existing keepalive/recovery hooks fire |
| Codex tree drifts while we edit | Low | High | Coordinate: only this task touches `tools/google-flow-driver/` until handback |

## Notes

The handoff's own instinct (step 4: "prefer a narrowly scoped CDP `Input.dispatchMouseEvent`") is
exactly what the code lacks — grep confirms no mouse dispatch exists anywhere in the extension.
This plan is that step, made checkpointed and evidence-first. If T2 falsifies H1 (synthetic click
DOES generate), stop and re-plan from the captured toast/settings evidence instead of coding T3–T5.

## Confidence Score
**7/10** for single-pass implementation — the code change is small and pattern-anchored; the
uncertainty is Flow's live behavior, which T2 resolves for one zero-credit image before the main
implementation lands.
