---
id: P17-AGENT-GENERATION-LOOP
title: Subscription-agent generation loop — claims, watchdog, headless re-entry, paid gate
status: complete
operation: feature
risk: high
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-08-23
updated: 2026-08-24
---

# Agent Generation Loop

## Summary

Image generation moves from metered APIs to the operator's existing
subscription agents (Antigravity/Gemini, GPT desktop via Codex), both of which
confirmed they can write named files to arbitrary local paths. The engine
compiles a **work order** (prompts + acceptance rubric + delivery
instructions); the agent generates opaque best-of candidates, **extracts**
true-alpha cutouts (matting is a distinct stage — the v1 probe proved the
image surface cannot produce native alpha, and the rubric must judge each
stage on what it controls), self-judges the cutouts with a 2-attempt cap per
stage, and delivers **both sources and cutouts** into a claim's delivery
folder. The raw source render is the irreplaceable artifact: a failed cutout
with a delivered source is recoverable locally without regeneration. A local **watchdog** detects the approval marker, runs the
deterministic intake scan (hashes, scale band, placement, style-family guard —
no model, no tokens), notifies (Windows toast + Telegram), and launches a
**headless Claude session** that assembles the render-ready pack and advances
all free compositional work — composite previews, quarantined HyperFrames
animatics, Remotion headless renders — then stops hard at the **paid gate**.

The human gate relocates from per-asset triage to spend authorization. This is
an explicit operator decision (2026-08-23), recorded here so it is not
relitigated: the operator sees nothing until a render-ready pack is waiting at
the paid gate. The console triage screen remains as the manual override
surface, not the default path.

**Generation is directly invocable — no scheduling choreography** (verified
2026-08-24). `codex exec --cd <dir> <work order>` runs headlessly against the
operator's subscription (`~/.codex/auth.json`) **with the native image
generation tool available** — proven by a generated file round-trip, not
assumed. The loop is therefore driven by direct invocation: orchestrator
calls `codex exec`, waits, scans. Claude routines and ChatGPT scheduled tasks
were considered and rejected — cloud schedulers cannot see local disk and a
subprocess gives exit codes, captured output, and synchronous error
propagation. The watchdog (T3) is thereby **demoted from backbone to
fallback**: it exists for batches the operator runs manually in the desktop
app, while the primary path is the orchestrated call. Version pin risk:
`codex-cli 0.148.0-alpha.9` is prerelease; the invocation goes through one
monkeypatchable boundary like every other process edge in this plan.

**Invocation economics** (verified 2026-08-24): the operator's global codex
config runs `gpt-5.6-luna` at `model_reasoning_effort = "xhigh"`, which cost
21–56k orchestration tokens per probe run on work that is mechanical. Work
orders therefore invoke with `-c model_reasoning_effort="low"`; image quality
is unaffected because generation runs on a separate image backend regardless
of the driving model. Model and effort are **claim-config values, not
hardcoded flags** — `gpt-5.3-codex-spark` (a valid slug with its own quota
pool) hung when driven headless through the alpha CLI, and retesting it after
a CLI update must be a config edit, not a code change. Where the image tool
itself bills is account-side and unobservable locally; any "free via Spark"
claim is verified only by the operator's usage meters, never assumed.

**No second-model judge in the loop** (operator decision, 2026-08-23, after
the v2 probe). The generating agent's self-judgment proved calibrated under
test — it failed its own v1 delivery and caught its own v2 extraction defect —
and the deterministic scan sits behind it as the gate that cannot be
persuaded. Decisive structurally: Antigravity has no external trigger, so a
Gemini judge leg would be a permanent manual paste in the middle of an
otherwise hands-off loop. Gemini remains available as an **escalation judge on
FLAG only** — when the scan disagrees with the self-judge, that conflict is
the one case worth a second model's eyes, and it is occasional by
construction.

## Intent And Acceptance

Accepted when:

1. A claim can be opened from the console Generate page or CLI: it compiles
   the prompt pack (existing `visual_prompt_pack`), creates a `delivery_dir`,
   and exports a work order containing prompts, per-slot acceptance rubric,
   the 2-attempt retry rule, target paths, naming (`<asset_id>.png`), format
   requirements, manifest shape, and **reference images as local paths** —
   style boards and character sheets resolved from the catalogue, passed to
   the generator's image-input conditioning (verified working 2026-08-24: a
   reference-conditioned generation matched the family more tightly than
   text-only prompts). Reference paths are read-only inputs; the work order
   never points the generator's write access at catalogue directories. Multiple claims may be open concurrently;
   the registry lives outside any repo at `~/.video-engine/claims/`.
2. A pack delivered by an agent (files + manifest + `approvals.json` marker)
   is detected by the watchdog within seconds, scanned deterministically, and
   the result notified via toast and Telegram with counts. Agent-declared
   hashes and approvals are verified, never trusted: `delivery_intake`
   fail-closes on any mismatch.
3. The watchdog launches a headless Claude session with the claim context.
   That session: re-runs the scan, binds the delivery, produces the free
   artifacts (composites, animatic previews under quarantine, Remotion props
   + headless render where a script exists), writes a pack summary, and stops
   at the paid gate. It never releases paid work.
4. Paid release is dual-mode: Telegram approve for jobs at or under the
   configured ceiling (default $5, configurable), on-machine console/CLI for
   everything above. Telegram approval requires exact job-id echo and the bot
   only accepts commands from the operator's chat id. The Flow queue pause is
   honoured independently of this gate.
5. Slots failing their rubric twice ship in the pack marked `unresolved`; the
   pack proceeds partial with gaps named in the summary and notification.
6. Wrong-project promotion is structurally blocked: promote-time check
   verifies the claim's `project_root` and branch against the current
   worktree, and the style-family guard runs as the independent second gate.
7. Watchdog is registered via Task Scheduler at login, survives reboot, and
   has a named stop command; no orphaned process after console exit (the
   watchdog is independent of the console by design).

## Scope

- `generation_claim.py` service: claim registry, work-order compile/export.
- Generate route addition: open/close claims, render work order for copy.
- `delivery_watchdog.py` + Task Scheduler registration script.
- Deterministic scan wiring (existing `delivery_intake` verdict layer).
- Toast + Telegram notification adapters (notify-only bot half).
- Headless re-entry runbook + entry command.
- Motion library: a registry of reusable HyperFrames motion units (overlays,
  evidence layers, title treatments) the animation pass draws from and adds
  to. Design-authored HTML motion prototypes are a valid source — they are
  already in the target medium — but they enter the library only as ported,
  validated HyperFrames units, never consumed raw.
- Paid-gate service with dual-mode release and job registry.
- Policy/process doc updates recording the relocated human gate.

## Patterns To Mirror

- **Single monkeypatchable boundary per edge** — `preview.py::_run_command`;
  here `_run_git`, `_run_powershell`, `_post_json`, `_get_updates`,
  `_launch_resume`, and the claim-resume editor hook.
- **Fail-closed with the fix named** — the P18 store errors; the gate's
  refusals state ceiling, channel, or pause by name.
- **Registry as files outside the repo** — machine state (claims, paid jobs)
  mirrors nothing in git, like `~/.codex` itself.
- **Compile/record split** — work orders are compiled artifacts; approvals and
  scans are records; no hidden state between them.

## Not Building

- No provider API clients, no API keys, no metered image generation.
- No scraping of app caches (Chromium cache formats are eviction-prone).
- No CDP automation of ChatGPT/Gemini desktop surfaces.
- No auto-release of paid work by any automated component, ever.
- No Flow queue resumption — separate standing block, observed-submit-path
  prerequisite unchanged.
- No change to `approved` review-state semantics in the catalogue: promotion
  still flows through the same service path; what changes is who triggers it.

## Human Gates

| Gate | Who | Rule |
| --- | --- | --- |
| Paid release > ceiling | Operator, on-machine | Console/CLI only; Telegram cannot approve above the ceiling |
| Paid release ≤ ceiling | Operator, Telegram | Exact job-id echo from allow-listed chat id |
| Ceiling value | Operator | Default $5; changed only by explicit config edit |
| Flow queue | Operator | Stays paused; this plan does not touch it |
| Policy change (triage → spend gate) | Recorded | Operator decision 2026-08-23; console triage remains as override |

## Mandatory Reads

- `backend-patterns` — service boundaries, process handling at the edge
- `content/video_engine/src/services/visual_prompt_pack.py` — pack compile the work order wraps
- `content/video_engine/src/services/delivery_intake.py` — the verdict layer that is the independent gate; fail-closed hash semantics
- `content/video_engine/console/routes/generate.py` — the compile/export seam and its "deferred provider" comment this plan retires
- `content/video_engine/console/routes/preview.py::_run_command` — single monkeypatchable process boundary to mirror
- `docs/content-video-engine/19-HYPERFRAMES-LANE.md` — renderer ownership; `animatic_preview` quarantine
- `docs/content-video-engine/24-COMPOSITION-AND-SCALE-SPEC.md` — source of per-slot rubric criteria

## Execution Path

**Gated by P18** (`P18-DURABILITY-AND-PATH-CONTRACT`): claims registry,
delivery dirs, watchdog watch-paths, and the motion library all resolve
through the P18 path contract and its durability classes — deliveries are
`review/`-class, animatics and pack summaries `runtime/`-class. Only the
manual probe (Verification) may run before P18 lands. This ordering is the
operator's 2026-08-23 decision.

Order: T1 → T2 → (T3, T4 parallel) → T5 → T6 → T7. T3/T4 have disjoint
write sets. T6 depends on T4 (Telegram transport) and T5 (job registry
contents).

```
content/video_engine/src/services/
  generation_claim.py     claims: open/list/close; work-order compile
  delivery_scan.py        deterministic scan entry (wraps delivery_intake)
  paid_gate.py            job registry, ceiling, dual-mode release
content/video_engine/watchdog/
  __main__.py             watchdog service (filesystem events, debounce)
  notify.py               toast + telegram adapters
scripts/
  register_watchdog.ps1   Task Scheduler registration / removal
~/.video-engine/          claims registry, config, job registry (outside repo)
```

## Task Slices

### T1: Claim service and work-order compile
- Status: complete
- Depends on: none
- Evidence: 9 tests green; registry outside the repo with env override; work order self-contained (probe-v2 staging, caps, sources-always, approvals-last); promote-time worktree check implemented as `verify_claim_matches_worktree`
- Owner: parent
- Write set: `content/video_engine/src/services/generation_claim.py`, `content/video_engine/tests/test_generation_claim.py`
- Acceptance: claims open with project_root, branch, catalog_path, style_family, delivery_dir, slots; registry under `~/.video-engine/claims/` (override via env for tests); concurrent claims supported; work order renders prompts + rubric (from pack acceptance + 24-spec bands) + 2-attempt rule + delivery instructions + manifest shape as one copyable document; close is explicit; stale-branch detection at read time reported, not fatal.
- Validate: `python -m pytest content/video_engine/tests/test_generation_claim.py -q`

### T2: Generate route — open claim, render work order
- Status: complete
- Evidence: 14 tests green; claims open from a compiled pack or explicit slots; work order rendered for copy at /generate/claims/<id>; the module's 'deferred provider' docstring retired; promote-time claim check wired into the commit route
- Owner: junior_developer
- Depends on: T1
- Write set: `content/video_engine/console/routes/generate.py`, `content/video_engine/console/templates/generate.html`, `content/video_engine/tests/test_console_generate.py`
- Acceptance: open-claim POST creates claim + delivery_dir and renders the work order for copy; open claims listed with their delivery paths; close-claim POST; routes thin over T1; the module docstring's "deferred until a provider and spend control are chosen" comment is retired with a pointer to this plan.
- Validate: `python -m pytest content/video_engine/tests/test_console_generate.py -q`

### T3: Watchdog + deterministic scan + toast
- Status: complete
- Evidence: 9 tests green (scan 4, watchdog 5); WatchdogCore side-effect-injected; debounce, restart-safe markers, single-instance lock, --stop; register_watchdog.ps1 registers/removes the logon task; demoted to fallback per the direct-invocation finding
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/watchdog/__main__.py`, `content/video_engine/watchdog/notify.py` (toast half), `content/video_engine/src/services/delivery_scan.py`, `scripts/register_watchdog.ps1`, `content/video_engine/tests/test_delivery_scan.py`, `content/video_engine/tests/test_watchdog.py`
- Acceptance: watches all open claims' delivery_dirs; fires on `approvals.json` arrival, debounced until file sizes stabilise; runs scan producing FAIL/FLAG/CLEAN verdicts; agent-declared sha256 verified against bytes; unresolved slots surfaced; toast with counts; headless launch is a config-named command through one monkeypatchable process boundary; watchdog runs without the console and has a stop command; Task Scheduler script registers at login and removes cleanly; tests use fake filesystem events and a fake process boundary, never a real scheduler entry.
- Validate: `python -m pytest content/video_engine/tests/test_delivery_scan.py content/video_engine/tests/test_watchdog.py -q`

### T4: Telegram notify (notify-only half)
- Status: complete
- Evidence: 7 tests green; env-only credentials; failures log the exception type never the token; unconfigured is a quiet no
- Owner: junior_developer
- Depends on: T3
- Write set: `content/video_engine/watchdog/notify.py` (telegram half), `content/video_engine/tests/test_notify.py`
- Acceptance: bot token and chat id from env only; message carries claim id, counts, unresolved slots, and the waiting-gate state; network failure logs and never blocks the scan path; no inbound command handling in this slice.
- Validate: `python -m pytest content/video_engine/tests/test_notify.py -q`

### T5: Headless re-entry
- Status: complete
- Evidence: 4 tests green; claim-resume scans, composites clean compositable assets under runtime/, records the editor lane's absence as a skip (P16 boundary), writes the pack summary, registers declared paid follow-ups as pending; motion-arithmetic structural test extended over claim_resume, delivery_scan, generation_claim, paid_gate and the watchdog package; runbook `docs/runbooks/HEADLESS_CLAIM_RESUME.md`
- Owner: parent
- Depends on: T3
- Write set: `docs/runbooks/HEADLESS_CLAIM_RESUME.md`, `content/video_engine/cli.py` (claim-resume subcommand), `content/video_engine/tests/test_claim_resume.py`
- Acceptance: a single command (`python -m content.video_engine.cli claim-resume <claim-id>`) that the watchdog invokes headlessly: re-scan, bind delivery, compose free artifacts (composite previews; HyperFrames `animatic_preview` under existing quarantine; Remotion props + headless render when an editor script exists), write pack summary JSON, register the pending paid job(s) in the T6 registry, exit. The animation pass resolves motion from the motion library first — a registered HyperFrames unit matched by semantic tags beats authoring new motion, mirroring the asset catalogue's own resolution-order principle — and any new unit authored for a claim is registered so later claims inherit it. Composition remains pure translation (P15 structural motion-arithmetic test extended over new modules); motion arithmetic lives inside HyperFrames units per the 19-lane ownership table, never in claim-resume itself. The command performs no network calls and releases nothing paid.
- Validate: `python -m pytest content/video_engine/tests/test_claim_resume.py content/video_engine/tests/test_console_motion_preview.py -q`

### T6: Paid gate — dual-mode release
- Status: complete
- Evidence: 10 tests green covering spoofed chat, wrong echo, over-ceiling, Flow refusal on both channels, absent-config-means-paused, audit log; inbound approvals in `watchdog/telegram_approve.py` answer only the allow-listed operator
- Owner: parent
- Depends on: T4, T5
- Write set: `content/video_engine/src/services/paid_gate.py`, `content/video_engine/watchdog/telegram_approve.py`, `content/video_engine/console/routes/runs.py` (release control), `content/video_engine/tests/test_paid_gate.py`
- Acceptance: job registry with estimated cost per job; ceiling default $5 in `~/.video-engine/config.json`; Telegram approval accepted only from the allow-listed chat id, only for jobs ≤ ceiling, only with exact job-id echo; above-ceiling jobs releasable solely from on-machine console/CLI; every release decision (who, channel, job, cost) appended to an audit log; Flow-lane jobs refuse release while the Flow pause flag stands, regardless of channel; tests cover spoofed chat id, wrong job id, over-ceiling Telegram attempt, and the Flow refusal.
- Validate: `python -m pytest content/video_engine/tests/test_paid_gate.py -q`

### T7: Policy and process docs
- Status: complete
- Evidence: `26-AGENT-GENERATION-LOOP.md` written and indexed; AGENTS.md carries the loop and relocated-gate policy; probe evidence recorded in the doc
- Owner: junior_developer
- Depends on: T6
- Write set: `docs/content-video-engine/26-AGENT-GENERATION-LOOP.md`, `AGENTS.md` (gate table row)
- Acceptance: the loop documented end-to-end with the two-gate rationale (agent vision judgment + deterministic arithmetic, independent failure modes); the relocated human gate recorded as an operator decision with date; work-order authoring guidance for both agent surfaces; the Downloads fallback tray documented as the manual path.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P17-AGENT-GENERATION-LOOP.plan.md`

## Verification

```bash
python -m pytest content/video_engine/tests/ -q
python scripts/prp_validate.py .claude/PRPs/plans/P17-AGENT-GENERATION-LOOP.plan.md
```

- Full suite green apart from the five pre-existing `test_history_v4_pipeline.py` failures.
- Manual probe before T3 lands: one two-image work order through Antigravity end-to-end — files land named and placed, style guard shows no family drift against `ep1-index-funds-vox-newsprint-v3`. If the probe shows drift, pause and decide provider before building T3–T6.
- Manual: kill the watchdog mid-scan, restart, verify no duplicate notifications and no half-bound delivery.

## Risks

| Risk | Level | Mitigation |
| --- | --- | --- |
| Generator judges its own output | High | Deterministic scan is the independent second gate; unresolved slots ship named, not hidden |
| Style drift vs ChatGPT-app-generated v3 library | High | Two-image probe gates the build; style-family guard fails closed at bind |
| Telegram token becomes a spend credential | Medium | Ceiling + allow-listed chat id + exact id echo + audit log; above-ceiling on-machine only |
| Orphaned/duplicated watchdog | Medium | Task Scheduler owns lifecycle; single-instance lock; stop command |
| Headless session scope creep | Medium | claim-resume is a fixed command with no network and no release path; paid work only enters the T6 registry |
| Claim/branch mismatch after worktree churn | Medium | Promote-time root+branch verification; stale-branch warning at claim read |
| Agent writes outside delivery_dir | Low | Work order names absolute target; scan binds only files under the claim's delivery_dir |

## Deviations

- **Release control lives in `console/routes/gate.py`, not `runs.py`** — the
  plan named runs.py, but P15's tested read-only invariant on the runs view
  ("never approves a gate") is the older, better rule. The runs view lists
  gate jobs read-only; the write route is its own module.
- **Paid follow-ups come from the claim's `paid_followups` field**, not from
  inference: claim-resume registers exactly what the claim declares, nothing
  speculative.
- **The editor render lane is a hook** (`_editor_render_hook`): P16 owns
  `editor_render`; until it lands, claim-resume records the skip by name.

## Evidence And Handoff

All seven slices implemented and validated: 772 tests pass (5 pre-existing
`test_history_v4_pipeline` failures unrelated). The loop was probed end-to-end
before building (v1/v2 work orders, capability tests) — every stage's contract
is evidence-backed, not assumed. Operator setup that remains optional:
Telegram env vars for phone notify/approve, watchdog Task Scheduler
registration, and the Spark model retest after a codex CLI update (config
edit).
