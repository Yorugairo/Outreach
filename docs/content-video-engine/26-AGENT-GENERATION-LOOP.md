# 26 — The Agent Generation Loop

Image generation runs on the operator's subscription agents, not metered APIs.
The engine compiles **claims**; agents follow **work orders**; deterministic
arithmetic gates everything; a human appears exactly once — at the money.

```
Generate page ──work order──▶ codex exec / GPT desktop / Antigravity
                                 generate (best-of, opaque)
                                 extract (true-alpha matting)
                                 self-judge (2 attempts/slot, then unresolved)
                                 deliver sources + cutouts + manifest
                                            │ approvals.json (written last)
orchestrator scan ◀── or ── watchdog (fallback, debounced)
   deterministic: hashes, dimensions, alpha rim, style family
   └─▶ claim-resume: composites, editor lane hook, pack summary
         └─▶ PAID GATE ── ≤ceiling: Telegram approve │ above: machine only
```

## The two-gate rationale

The generating agent judges its own output — and proved calibrated under test
(it failed its own v1 probe delivery outright and caught its own v2 extraction
defect). That judgment is the first gate. The second is the deterministic
scan: sha256 against bytes, dimension classes, partial-alpha rim measurement,
style-family guard. **Independent failure modes**: vision judges "does this
look right", arithmetic judges "does this measure right", and neither can be
persuaded by the other. An asset the agent approved but the scan fails is a
named `CONFLICT` — the one case reserved for an escalation judge (Gemini) or
the operator.

There is deliberately **no second-model judge inline** (operator decision,
2026-08-23): Antigravity has no external trigger, so a Gemini leg would be a
permanent manual paste inside an otherwise hands-off loop.

## The relocated human gate

Per-asset triage is no longer the default path (operator decision,
2026-08-23). The operator sees nothing until a render-ready pack waits at the
paid gate. `/intake` triage remains as the manual override surface. The gate
itself is dual-mode: Telegram approval (allow-listed chat id, exact job-id
echo, at or under the ceiling — default $5) or on-machine release at any cost.
Flow-lane jobs refuse release through **every** channel while the Flow pause
stands; absence of config means paused. Every decision is appended to
`~/.video-engine/paid-audit.log`.

## Probe evidence (2026-08-23/24)

- Delivery mechanics: exact paths, verified hashes, honest `unresolved` — v1.
- Native alpha at generation: impossible; extraction is a stage — v1.
- Extraction quality: 1.6% partial rim passed, 12.6% dark rim failed; these
  calibrate the scan — v1/v2.
- Hard-alpha edges are fine at delivery scale (downscale resamples them) — v2.
- Headless invocation with the native image tool: proven file round-trip.
- Reference-conditioned generation: tighter family fit than text alone.
- `gpt-5.3-codex-spark` hangs through the alpha CLI; model/effort are
  claim-config values so the retest is a config edit.

## Machine state, not repo state

Claims (`~/.video-engine/claims/`), paid jobs (`~/.video-engine/paid-jobs/`),
config and audit log all live outside every repo: they track one operator's
machine, and must survive branch switches and worktree churn. Deliveries are
`review/`-class, previews and pack summaries `runtime/`-class, promoted assets
`canonical/`-class (doc 27).

## Work-order authoring

The claim service renders the work order; do not hand-write one. It encodes:
verbatim style blocks, reference images as read-only local paths, generation
best-of-3, extraction cap 2, sources always delivered, manifest shape,
`approvals.json` last. For a new style family, update the style blocks at the
pack level — the order inherits them.

**A corrected order leads with the rejection reason** (P54 K17). A rejected
plate keeps its reason in `approvals.json`, and the fresh order (E1: a
dispatched order is never edited) opens each slot with why v1 failed; the
self-judge checks that reason first. The fault is usually the prompt, not the
generator: two wave-7 plates were rejected because the order described the
composition and not the meaning, and the generator built paper output from a
hype machine and playing cards for disciplined de-risking (2026-08-29,
`af4da2221767`, `6f2329b79917`).

## Motion library

The animation pass resolves motion from the registered HyperFrames unit
library before authoring new motion — the catalogue's resolution-order
principle applied to movement. Design-authored HTML prototypes are a valid
*source*, but enter only as ported, validated HyperFrames units.

## Context quarantine & the subagent worker contract (2026-09-14)

Image and scene generation on interactive browser interfaces (Google Flow, Nano Banana Pro, Omni 1.1 Flash) must never run directly in the primary conversation thread. Multi-step CDP polling, DOM inspection, and trial-and-error post-processing burn millions of tokens in the parent context.

Generation runs under **strict subagent quarantine** (`invoke_subagent`):
- **Worker Subagent:** Absorbs 100% of the browser automation churn and local matting scripts (`prepare_props.py`). It is discarded upon completion.
- **Implementer-Auditor Split:** The worker cannot self-certify. An automated verification script enforces objective acceptance criteria (dimensions, background key distance < 48.0, 0 hole blowout, valid SHA-256).
- **Compact Receipt Contract:** The subagent returns only a compact JSON receipt (`id`, `sha256`, dimensions, alpha/edge stats, and pass/fail verdict) and path to `contact_sheet.html`.

Full doctrine specification: `.agents/skills/google-flow-production/SKILL.md §11`.

Runbook: `docs/runbooks/HEADLESS_CLAIM_RESUME.md`.

