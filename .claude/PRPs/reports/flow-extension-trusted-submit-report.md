# Implementation Report: Flow Extension — Trusted Submit

*Date: 2026-08-09 · Plan: `flow-extension-trusted-submit.plan.md` · Code tree: `C:\Users\Snipe\.codex\worktrees\f10b\Outreach Program\tools\google-flow-driver\` (branch `codex/stickly-woodblock-variant`)*

## Summary

Implemented the trusted CDP mouse-click submit path the handoff identified but never built, plus
the evidence plumbing that makes a live run readable. Confirmed by inspection that the extension
contained **no `Input.dispatchMouseEvent` anywhere** — the Create action was still
`element.click()` at `content-script.js:213`, exactly the untrusted input class Flow already
proved it rejects for prompt entry.

**Status: code complete and unit-verified; the live proof (T2, T6) is operator-gated and NOT
done.** The queue remains paused. No generation has been observed.

## Assessment vs Reality

| Metric | Predicted | Actual |
|---|---|---|
| Complexity | Medium, 4–5 files, 150–250 lines | Medium — 4 files, ~200 lines + 13 tests |
| Confidence | 7/10 | Code landed cleanly; H1 still unproven live |
| Tests | 64 baseline + new | **77 pass, 0 fail** (64 baseline preserved) |

## Tasks

| # | Task | Status | Notes |
|---|---|---|---|
| T1 | Checkpoint instrumentation | ✅ | Folded into T3/T4 rather than a separate pass — `measureSubmitTarget` returns the redacted control description, live rect, and pre-click media snapshot in one diagnostic payload |
| T2 | Differential probe (manual vs synthetic) | ⛔ **NOT RUN** | Requires the operator at the browser. The instrumentation it needs now exists |
| T3 | `trustedClick` in service worker | ✅ | `dispatchTrustedClickAt()` mirrors the `insertText` attach/detach lifecycle exactly |
| T4 | Rewire submit step | ✅ | Bounded zero-credit lane only; paid/video path byte-identical |
| T5 | Flow-owned ack gating | ✅ | Added `no_flow_ack` as a distinct failure from `generation_timeout` |
| T6 | Live acceptance run | ⛔ **NOT RUN** | Operator-gated; all 5 acceptance items still outstanding |
| T7 | Docs / handback | ✅ | This report + handoff doc addendum |

## What changed

| File | Change |
|---|---|
| `extension/src/service-worker.js` | `dispatchTrustedClickAt(point)` — CDP `Input.dispatchMouseEvent` ×3 (moved/pressed/released) at CSS-pixel coords, activating the existing Flow tab first; `submitBoundedZeroCreditImageWithTrustedClick()` sequencing measure → click → commit; `makeContentDriver.submit` routes the bounded lane to it |
| `extension/src/content-script.js` | `elementViewportPoint()` (viewport-centre math, off-screen/zero-area rejection), `describeControl()` (redacted structural capture), `pointHitsElement()` (occlusion guard), `measureSubmitTarget()`, `commitTrustedSubmit()`, two new message cases, `no_flow_ack` branch in `waitForGeneration` |
| `extension/src/state-machine.js` | `submitArmedBoundedZeroCreditImage(submitter, { captureMedia })` — lets the trusted flow keep its pre-click media snapshot |
| `tests/trusted-submit.test.mjs` | 13 new tests (NEW FILE) |

## Design decisions worth reviewing

1. **Measure → click → commit, in that order.** The pre-click media snapshot is taken during
   *measure*. Committing first, or re-snapshotting at commit, would fold the card Flow just
   created into `beforeMedia` and erase the only evidence a generation started — the same class
   of self-deception as the original false `generating` promotion. There is a regression-guard
   test asserting the default path *does* fold the card in, documenting why the option exists.
2. **DPR is recorded but never multiplied in.** CDP takes CSS pixels; scaling by
   `devicePixelRatio` would land the click at roughly double the intended position on this
   HiDPI machine. Test locks this.
3. **Occlusion guard (`pointHitsElement`).** The handoff notes Flow's settings popover stays
   mounted. If it covers the arrow's centre, the trusted click would hit the popover and look
   like another silent failure. This now fails fast with `point_obscured` plus a redacted
   description of the occluder.
4. **`no_flow_ack` ≠ `generation_timeout`.** The 8 historical failures are unreadable partly
   because both collapsed into one code. Now: no fresh media and still `submitted` after 20s →
   `no_flow_ack` (input never accepted); anything else timing out → `generation_timeout`.

## Constraints honored

- Manifest **unchanged**: `["storage","sidePanel","downloads","nativeMessaging","debugger"]`,
  host `https://labs.google/fx/*`. `tabs.update` on an already-open tab needs no new permission.
- Paid/video runners untouched; trusted click gated behind `isBoundedZeroCreditImage(job)`.
- No page scripts, cookies, or tokens inspected. Captures are structural attributes only, with a
  test asserting prompt text and account-like values never appear in a control description.
- Queue left paused; no job released.

## Validation

| Level | Status | Notes |
|---|---|---|
| Unit tests | ✅ | 77 pass / 0 fail (`npm --prefix tools/google-flow-driver test`) |
| Baseline regression | ✅ | All 64 pre-existing tests still green |
| Build | ✅ | `npm run build` → `.codex/flow-extension-build/extension`, manifest hash `adfd8c22…`, archive 76,353 B |
| Live behavior | ⛔ | **Not validated.** H1 remains a hypothesis |

## Issues encountered

1. **`tools/google-flow-driver/` is entirely untracked in git** (`?? tools/google-flow-driver/`).
   GPT's work and mine exist only as working-tree files — no baseline diff was possible, and a
   `git clean -fd` in that worktree would destroy all of it. Recommend committing it before
   further live work.
2. The state machine's submitter callback is synchronous, so an out-of-page async click could not
   be threaded through it directly. Resolved with the explicit measure/commit split rather than
   by making the state machine async.

## Next steps (operator-gated)

- [ ] **T2 differential probe** — one manual click (expected to generate; also the missing
      "does this lane work at all" control) vs one extension run, comparing `isTrusted` and the
      pointer sequence
- [ ] **T6 acceptance run** — one zero-credit Nano Banana Pro 16:9 ×1 producing all five handoff
      acceptance items
- [ ] Only after a visible generation: repair media-card discovery/download selectors and add the
      redacted DOM fixture
- [ ] Commit `tools/google-flow-driver/`
- [ ] Queue resume remains an operator decision, not implied by this work
