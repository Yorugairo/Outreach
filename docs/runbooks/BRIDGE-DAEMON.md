# The bridge daemon — the tick that makes a landed reply actionable (P46 T6)

`bridge_send.py` sends an order, `bridge_watch.py` lands the reply. Nothing between them was unattended: a reply sat in a folder
until a human remembered it. `content/video_engine/scripts/bridge_daemon.py` is that memory. It ticks over the folder state
machine, closes with Python everything Python can close, spends a model only on the residue, and toasts the operator when a
packet is genuinely stuck. **The daemon itself makes no model call** — the only model use is tier 1, inside the day's budget.

```
python content/video_engine/scripts/bridge_daemon.py --once --dry-run --json      # what it would do, writes nothing
python content/video_engine/scripts/bridge_daemon.py --once                       # one tick
python content/video_engine/scripts/bridge_daemon.py --loop --poll-sec 60         # the installed form
```

## 1. One tick, in order

| step | folder | what happens |
| --- | --- | --- |
| 1 send | `queue/` | a packet with an `order.json` and no `conversation.json` goes out through `bridge_send.py`'s own functions. A follow-up written by the tier-1 role carries `from: claude` + `conversationId` and continues that conversation through `bridge_reply.py`'s send instead of opening a new one. |
| 2 watch | `sent/` | one read of the lane's transcript (`bridge_watch.py --once`, no polling). Done → the watcher writes `reply.md`, `steps.jsonl`, `watch.json` and renames the packet into `replied/`. Working → left alone. Past the order's `deadline` → the watcher ledgers `timeout` and step 5 escalates; from then on the packet is read as a replay so the timeout is recorded once. |
| 3 tier 0 | `replied/` | `bridge_handlers.classify()` runs the handler the order's `replyShape` names, at zero tokens. Pass → `tier0.json`, rename into `done/`, one ledger line with `tier: 0`. Fail → `tier0.json` with the reason, and the packet waits for the grace window. |
| 4 tier 1 | `replied/` | a tier-0 failure older than `grace_min` with no `tier1.json` is dispatched **once**: `claude -p --agent bridge_handler --output-format json` from the repo root, its standing instruction read from `BRIDGE-REPLY-HANDLER.md`. `tier1.json` records `startedAt / finishedAt / exit / usage / resultPath`; the ledger records `tier: 1` with the usage. `result.md` (in `done/` or in the packet folder — both are handled) moves the packet to `done/`. `DECISION: follow-up` leaves a new packet in `queue/` for the next tick; `DECISION: escalate` toasts. |
| 5 escalate | any | one Windows toast per packet per condition — `timeout`, `sla`, `handler-escalate`, `budget` — with `escalated.json` as the marker that stops the repeat, and one `escalated` ledger line carrying the `reason`. |
| 6 budget | ledger | today's `tier1` lines are the counter. Over `residue_runs_per_day` or `residue_tokens_per_day`, tier 1 is skipped, the packet is toasted once as `budget`, and the tick keeps running. |

Folder state is the only state: no database, no broker, no queue server. A pid lock at
`docs/research/runs/bridge/daemon.lock` (stale when its pid is not alive) makes a restart idempotent; a second daemon exits 1.
`--dry-run` performs no send, no move, no dispatch, no toast and writes no ledger line — not even the lock file — and prints
`SEND / WATCH / TIER0 / TIER1 / TOAST:` lines instead. `--json` prints one summary per tick:
`{sent, watched, tier0_done, tier1_runs, escalated, skipped_budget}`.

## 2. Config

Defaults live in the module and are overridden by a JSON file — `~/.claude/bridge-config.json` by default, `--config <path>`
otherwise. An absent file is normal. Unknown keys are ignored.

| key | default | meaning |
| --- | --- | --- |
| `grace_min` | 10 | how long a tier-0 failure waits before a model looks at it. Long enough for the operator to catch it first. |
| `sla_min` | 60 | a packet still in `replied/` this long raises one desktop toast. |
| `residue_runs_per_day` | 6 | tier-1 dispatches per calendar day, counted off the ledger. |
| `residue_tokens_per_day` | 200000 | input + output tokens per day across tier-1 runs. |
| `poll_sec` | 60 | seconds between ticks under `--loop` (`--poll-sec` overrides). |

HG3 defaults, adopted by the operator 2026-09-06.

## 3. The Task Scheduler entry (install by hand, once)

Nothing installs itself. Open Task Scheduler → *Create Task* (not *Basic Task*):

- **General**: name `Claude Bridge Daemon`; *Run only when user is logged on*; leave *Run with highest privileges* unchecked.
- **Triggers**: *At log on* (this user), *Delay task for* 1 minute.
- **Actions**: *Start a program*
  - Program: `pythonw.exe` (full path, e.g. `C:\Users\Snipe\AppData\Local\Programs\Python\Python313\pythonw.exe`)
  - Arguments: `content\video_engine\scripts\bridge_daemon.py --loop`
  - Start in: `C:\Users\Snipe\Downloads\Outreach Program`
- **Conditions**: uncheck *Start the task only if the computer is on AC power*.
- **Settings**: *If the task is already running, do not start a new instance* (the pid lock says the same thing twice, on purpose).

The equivalent one-liner, if the dialog is not to hand:

```powershell
schtasks /Create /TN "Claude Bridge Daemon" /SC ONLOGON /DELAY 0001:00 /RL LIMITED ^
  /TR "pythonw.exe content\video_engine\scripts\bridge_daemon.py --loop" /F
```

`schtasks` has no *Start in* field: set the working directory in the GUI afterwards, or pass `--repo "C:\Users\Snipe\Downloads\Outreach Program"`.

To see what it is doing without waiting: `python content/video_engine/scripts/bridge_daemon.py --once --json` from the repo root.
To rerun one tier-0 check by hand, with no move and no ledger line:
`python content/video_engine/scripts/bridge_handlers.py --packet <packetId>` (exit 0 = tier 0 closes it, 2 = it does not).

## 4. Reading the ledger's tier column

`evals/BRIDGE-LOG.jsonl` (per machine, gitignored) is one JSON line per event. `sent`, `replied`, `followup` and `timeout` come
from the sender and the watcher; `tier0`, `tier1` and `escalated` come from the daemon. The `tier` field is on the last three:
`0` = closed by Python for nothing, `1` = a model was paid to look, and `escalated` = neither could close it.

```bash
# the escape rate: how much of what lands needs judgment
python -c "import json;rows=[json.loads(l) for l in open('evals/BRIDGE-LOG.jsonl',encoding='utf-8')];\
t0=sum(r['event']=='tier0' for r in rows);t1=sum(r['event']=='tier1' for r in rows);\
print(f'tier0={t0} tier1={t1} escape={t1/max(t0+t1,1):.0%}')"
```

A tier-1 row carries `inputTokens`, `outputTokens`, `costUsd` and `decision` (`done` / `follow-up` / `escalate`); anything the
run did not report is `null`, never `0`, so an average over the column cannot be quietly wrong. An escape rate that stays low
and mechanical is the argument for moving the residue role off Opus; a rate dominated by `disagreements` and `escalate` is the
argument for keeping it there.
