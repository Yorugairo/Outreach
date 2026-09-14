# Runbook — Headless Claim Resume

What runs when a generation delivery lands, and how to drive the loop end to
end without opening the console.

## The loop, one claim

```bash
# 1. Open a claim (console Generate page, or explicit slots via the route).
#    Its work order lives at /generate/claims/<claim-id>.

# 2. Hand the work order to the generating agent. Headless:
#    (model_reasoning_effort=low — orchestration is mechanical; images render
#    on a separate backend regardless of the driving model)
codex exec --cd "<delivery_dir>" --skip-git-repo-check \
  -c model_reasoning_effort="low" \
  "Read and follow the work order at <path printed by the claim page>."

# 3. When codex exits (or the watchdog fires on approvals.json):
python -m content.video_engine.cli claim-resume <claim-id>
```

`claim-resume` re-runs the deterministic scan, renders placement composites
for every clean compositable asset (under `runtime/claim-previews/`), calls
the editor render lane when installed (absence is a recorded skip), writes the
pack summary to `runtime/claim-packs/<claim-id>.summary.json`, and registers
any declared paid follow-ups as **pending** gate jobs. It performs no network
call and releases nothing.

**A plate claim opens one slot per layer** (E98 s6, `docs/portable/OPERATOR-RULINGS.md:2878`). A new world plate is
ordered as its layers - background, mid, subject, occluder - each slot its own generation with one style, one sitting
and the E98 s5 intent line, so the four register; never one stacked image to be cut apart afterwards (the banker
apartment blurred exactly where a near object was removed from one). A flat plate is the exception and its order
says why. Name each layer's `role` in the order: `build_plate_library.py` reads the plate's `<plate>.layers.json` and
refuses an unknown role or generator by name.

## The watchdog (fallback trigger)

For batches run by hand in a desktop app:

```bash
python -m content.video_engine.watchdog            # foreground
python -m content.video_engine.watchdog --once     # single poll pass
python -m content.video_engine.watchdog --stop     # stop the running instance
powershell scripts/register_watchdog.ps1           # start at logon
powershell scripts/register_watchdog.ps1 -Remove   # unregister
```

It debounces until the delivery stops growing, scans, notifies (toast +
Telegram when configured), marks the delivery handled with
`.watchdog-scanned.json`, and launches the resume command named by
`VIDEO_ENGINE_CLAIM_RESUME_COMMAND` (e.g.
`python -m content.video_engine.cli claim-resume {claim_id}`).

## The paid gate

```bash
# On-machine (any cost): Runs view → Paid gate → Release, or the audit trail:
type %USERPROFILE%\.video-engine\paid-audit.log

# Telegram (≤ ceiling only): reply `approve <job-id>` from the allow-listed
# chat, then poll:
python -m content.video_engine.watchdog.telegram_approve --once
```

Config `~/.video-engine/config.json`: `telegram_ceiling_usd` (default 5),
`flow_queue_paused` (default **true** — the standing Flow constraint fails
closed). Env: `VIDEO_ENGINE_TELEGRAM_BOT_TOKEN`, `VIDEO_ENGINE_TELEGRAM_CHAT_ID`.

## Promotion

Triage/commit from `/intake` as always. Two extra guards hold on claimed
deliveries: the claim's project root and branch must match the serving
worktree, and promotion syncs to the R2 store (P18) before the catalogue
write — or requires the explicit unsynced opt-out.
