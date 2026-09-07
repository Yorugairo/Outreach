"""The bridge's unattended tick: send what is queued, land what replied, close what Python can close (P46 T6).

    python content/video_engine/scripts/bridge_daemon.py --once --dry-run --json
    python content/video_engine/scripts/bridge_daemon.py --loop --poll-sec 60

Folder state is the only state - `docs/research/runs/bridge/{queue,sent,replied,done}/<packetId>/` - and a
pid lock (`bridge/daemon.lock`, stale when its pid is not alive) makes a restart idempotent. There is no
database, no broker, and **the daemon makes no model call**: the only model use is tier 1, the residue, and
only inside the day's budget.

One tick, in order:

  1. `queue/`   - a packet with an `order.json` and no `conversation.json` is sent (`bridge_send.py`'s own
                  functions; a follow-up packet written by the handler carries `from: claude` and a
                  `conversationId`, and continues that conversation through `bridge_reply.py` instead).
  2. `sent/`    - one watcher read per packet (`bridge_watch.py --once`): done moves it to `replied/`, still
                  working leaves it, past the deadline is a `timeout` and an escalation.
  3. `replied/` - tier 0 (`bridge_handlers.classify`): a pass writes `tier0.json`, moves the packet to
                  `done/` and ledgers `tier: 0`; a failure writes the reason and waits for the grace window.
  4. `replied/` - a tier-0 failure older than `grace_min` with no `tier1.json` is dispatched once to the
                  `bridge_handler` role headlessly; its usage is ledgered with `tier: 1`.
  5. escalation - one desktop toast per packet per condition (`escalated.json` is the marker): timeout, SLA,
                  the handler's own `DECISION: escalate`, or a spent residue budget.
  6. budget     - today's `tier1` ledger lines are the counter; over `residue_runs_per_day` or
                  `residue_tokens_per_day` tier 1 is skipped and the operator is told once.

Config (defaults below, overridden by `~/.claude/bridge-config.json` when it exists):
`{"grace_min": 10, "sla_min": 60, "residue_runs_per_day": 6, "residue_tokens_per_day": 200000, "poll_sec": 60}`.

`--dry-run` sends nothing, moves nothing, dispatches nothing, toasts nothing and writes no ledger line: it
prints what it would do. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Sequence

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import bridge_env as env_mod  # noqa: E402
import bridge_handlers as handlers  # noqa: E402
import bridge_reply as reply_mod  # noqa: E402
import bridge_send as send_mod  # noqa: E402
import bridge_watch as watch_mod  # noqa: E402

REPO = env_mod.REPO
LOCK_PATH = env_mod.BRIDGE_ROOT / "daemon.lock"
CONFIG_PATH = Path.home() / ".claude" / "bridge-config.json"
HANDLER_AGENT = "bridge_handler"
HANDLER_INSTRUCTION = "docs/runbooks/BRIDGE-REPLY-HANDLER.md"
RESULT_FILE = "result.md"
TOAST_APP_ID = "Claude Bridge"
DECISION_RE = re.compile(r"^\s*\**DECISION:?\**\s*:?\s*\**\s*(done|follow-up|followup|escalate)", re.IGNORECASE | re.MULTILINE)
LANDED_RE = re.compile(r"landedAt:\s*([0-9T:+\-\.]+)")
ESCALATIONS = ("timeout", "sla", "handler-escalate", "budget")
REPAIR_MARKER = "repair.json"   # P46 T7: the original packet's marker that ONE repair follow-up was queued for its form failure

DEFAULTS: dict[str, Any] = {
    "grace_min": 10,
    "sla_min": 60,
    "residue_runs_per_day": 6,
    "residue_tokens_per_day": 200_000,
    "poll_sec": 60,
}


# --------------------------------------------------------------------------- config, clock, json


def load_config(path: Path | str | None = None) -> dict[str, Any]:
    """The defaults, overridden by a JSON file. An absent or unreadable file is fine - defaults stand."""

    config = dict(DEFAULTS)
    target = Path(path) if path else CONFIG_PATH
    try:
        loaded = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return config
    if isinstance(loaded, dict):
        config.update({k: v for k, v in loaded.items() if k in DEFAULTS})
    return config


def now() -> dt.datetime:
    return dt.datetime.now().astimezone()


def stamp() -> str:
    return now().isoformat(timespec="seconds")


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def packets(repo: Path, state: str) -> list[Path]:
    """Every packet folder in one state, oldest name first - a stable order across ticks."""

    root = Path(repo) / env_mod.BRIDGE_ROOT / state
    return sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name) if root.is_dir() else []


# --------------------------------------------------------------------------- the lock


def pid_alive(pid: int) -> bool:
    """Windows asks `tasklist`; elsewhere signal 0. `os.kill` on Windows would TERMINATE, so it is not used."""

    if pid <= 0:
        return False
    if os.name == "nt":
        proc = subprocess.run(
            ["tasklist", "/FI", f"PID eq {int(pid)}", "/NH"], capture_output=True, text=True
        )
        return f" {pid} " in (proc.stdout or "").replace("\t", " ")
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def acquire_lock(repo: Path) -> Path | None:
    """One daemon per repo. A lock whose pid is dead is reclaimed; a live one refuses the tick."""

    path = Path(repo) / LOCK_PATH
    held = read_json(path)
    other = int(held.get("pid") or 0)
    if other and other != os.getpid() and pid_alive(other):
        return None
    env_mod.write_json(path, {"pid": os.getpid(), "startedAt": stamp()})
    return path


def release_lock(repo: Path) -> None:
    path = Path(repo) / LOCK_PATH
    if read_json(path).get("pid") == os.getpid():
        path.unlink(missing_ok=True)


# --------------------------------------------------------------------------- the toast


def toast(title: str, body: str) -> bool:
    """One Windows desktop notification. Tests monkeypatch this; `--dry-run` never reaches it."""

    if os.name != "nt":
        return False
    script = (
        "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime] > $null;"
        "$t=[Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
        "[Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
        "$n=$t.GetElementsByTagName('text');"
        f"$n.Item(0).AppendChild($t.CreateTextNode({_ps_quote(title)})) > $null;"
        f"$n.Item(1).AppendChild($t.CreateTextNode({_ps_quote(body)})) > $null;"
        f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier({_ps_quote(TOAST_APP_ID)})"
        ".Show([Windows.UI.Notifications.ToastNotification]::new($t))"
    )
    try:
        proc = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0


def _ps_quote(text: str) -> str:
    return "'" + str(text).replace("'", "''") + "'"


# --------------------------------------------------------------------------- the tick's context


class Tick:
    """One pass over the folders: the counters, the printed lines and the two switches."""

    def __init__(self, repo: Path, config: dict[str, Any], dry_run: bool = False) -> None:
        self.repo = Path(repo)
        self.config = config
        self.dry_run = dry_run
        self.lines: list[str] = []
        self.summary = {"sent": 0, "watched": 0, "tier0_done": 0, "tier1_runs": 0, "escalated": 0, "skipped_budget": 0, "repairs": 0}

    def say(self, line: str) -> None:
        self.lines.append(line)

    def ledger(self, record: dict[str, Any]) -> None:
        if not self.dry_run:
            env_mod.ledger_append(self.repo, record)


# --------------------------------------------------------------------------- 1. queue -> sent


def _send_args(tick: Tick, order: dict[str, Any]) -> SimpleNamespace:
    return SimpleNamespace(
        lane=order.get("lane") or "gemini",
        repo=tick.repo,
        dry_run=False,
        model=order.get("model"),
        profile=order.get("profile"),
    )


def send_packet(tick: Tick, folder: Path, order: dict[str, Any]) -> dict[str, Any]:
    """A new order opens a conversation; a handler's follow-up continues the one it names."""

    if order.get("conversationId"):
        return send_followup(tick, folder, order)
    sender = send_mod.send_gemini if (order.get("lane") or "gemini") == "gemini" else send_mod.send_claude
    lines: list[str] = []
    return sender(_send_args(tick, order), order, folder, lines)


def send_followup(tick: Tick, folder: Path, order: dict[str, Any]) -> dict[str, Any]:
    """`bridge_reply.py`'s send, on the conversation the follow-up packet names.

    `bridge_reply.locate_packet` refuses a packet in `queue/`, so its parts are used directly and the move
    is made here - a follow-up written by the handler starts life in the queue, which that CLI never sees.
    """

    packet = order["packetId"]
    lane = order.get("lane") or "gemini"
    conversation = str(order["conversationId"])
    text = order.get("brief") or ""
    argv, env, _shown = reply_mod.resolve(lane, conversation, text, tick.repo)
    reply_mod.send(argv, env, tick.repo)
    sent_at = stamp()
    moved = env_mod.move_packet(packet, "queue", "sent", repo=tick.repo)
    number = reply_mod.next_followup(moved)
    reply_mod.record_followup(moved, order, number, lane, conversation, text, sent_at)
    env_mod.write_json(
        moved / "conversation.json",
        {"packetId": packet, "conversationId": conversation, "sentAt": sent_at, "lane": lane, "followup": number},
    )
    reply_mod.ledger_followup(tick.repo, lane, packet, conversation, number, text, sent_at)
    return {"packetId": packet, "lane": lane, "conversationId": conversation, "status": "sent", "packetDir": str(moved)}


def step_queue(tick: Tick) -> None:
    for folder in packets(tick.repo, "queue"):
        order = read_json(folder / "order.json")
        if not order.get("packetId") or (folder / "conversation.json").exists():
            continue
        kind = "followup" if order.get("conversationId") else "new"
        label = f"{order['packetId'][:12]} lane={order.get('lane')} {kind}"
        if tick.dry_run:
            tick.say(f"SEND {label} (dry-run: nothing sent)")
            tick.summary["sent"] += 1
            continue
        try:
            result = send_packet(tick, folder, order)
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - one bad packet must not stop the tick
            tick.say(f"SEND-FAILED {label}: {type(exc).__name__}: {exc}")
            continue
        tick.summary["sent"] += 1
        tick.say(f"SENT {label} status={result.get('status')}")


# --------------------------------------------------------------------------- 2. sent -> replied


def watch_packet(tick: Tick, packet: str, lane: str, ident: str, once: bool = True) -> dict[str, Any]:
    """One read of the lane's transcript through the watcher, which owns the move and the ledger line."""

    argv = ["--lane", lane, "--id", ident, "--packet", packet, "--repo", str(tick.repo)]
    argv.append("--once" if once else "--replay")
    return watch_mod.run_watch(watch_mod.build_parser().parse_args(argv))


def step_sent(tick: Tick) -> None:
    for folder in packets(tick.repo, "sent"):
        order = read_json(folder / "order.json")
        conversation = read_json(folder / "conversation.json")
        packet = order.get("packetId") or folder.name
        ident = conversation.get("conversationId") or order.get("conversationId")
        lane = conversation.get("lane") or order.get("lane") or "gemini"
        if not ident:
            tick.say(f"WATCH-SKIP {packet[:12]}: no conversationId on disk")
            continue
        if tick.dry_run:
            tick.say(f"WATCH {packet[:12]} lane={lane} (dry-run: no read, no move)")
            tick.summary["watched"] += 1
            continue
        # a packet already escalated for timeout is read as a replay: the `timeout` line is written once.
        settled = "timeout" in _escalations(folder)
        try:
            watched = watch_packet(tick, packet, lane, str(ident), once=not settled)
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - a lane that cannot be read is not a crash
            tick.say(f"WATCH-FAILED {packet[:12]}: {type(exc).__name__}: {exc}")
            continue
        tick.summary["watched"] += 1
        status = watched["watch"]["status"]
        tick.say(f"WATCHED {packet[:12]} status={status}")
        if status == "timeout":
            escalate(tick, folder, packet, "timeout", f"{packet[:12]} passed its deadline with no reply")


# --------------------------------------------------------------------------- 3. tier 0


def landed_at(folder: Path) -> dt.datetime | None:
    """When the reply landed: the header the watcher wrote, else the file's mtime."""

    path = folder / "reply.md"
    if not path.exists():
        return None
    match = LANDED_RE.search(path.read_text(encoding="utf-8", errors="replace")[:400])
    parsed = watch_mod.parse_time(match.group(1)) if match else None
    return parsed or dt.datetime.fromtimestamp(path.stat().st_mtime).astimezone()


def minutes_since(when: dt.datetime | None) -> float | None:
    return None if when is None else (now() - when).total_seconds() / 60.0


def step_tier0(tick: Tick) -> None:
    for folder in packets(tick.repo, "replied"):
        if (folder / "tier0.json").exists():
            prior = read_json(folder / "tier0.json")
            if prior.get("pass") and not tick.dry_run:
                # checked on an earlier tick (or reopened by hand) and never moved: finish the move, no re-check, no ledger
                order = read_json(folder / "order.json")
                packet = order.get("packetId") or folder.name
                env_mod.move_packet(packet, "replied", "done", repo=tick.repo)
                tick.say(f"TIER0-DONE {packet[:12]} (prior verdict, moved)")
            continue
        order = read_json(folder / "order.json")
        packet = order.get("packetId") or folder.name
        reply_path = folder / "reply.md"
        text = reply_path.read_text(encoding="utf-8", errors="replace") if reply_path.exists() else ""
        if tick.dry_run:
            tick.say(f"TIER0 {packet[:12]} shape={order.get('replyShape')} (dry-run: no check, no move)")
            continue
        outcome = handlers.classify(order, text, tick.repo)
        env_mod.write_json(folder / "tier0.json", {**outcome, "checkedAt": stamp()})
        if not outcome["pass"]:
            tick.say(f"TIER0-FAIL {packet[:12]} shape={outcome['shape']} class={outcome.get('class')}: {outcome['reason']}")
            if outcome.get("class") == handlers.CLASS_FORM and not order.get("repairs") and not (folder / REPAIR_MARKER).exists():
                queue_repair(tick, folder, order, packet, outcome)   # P46 T7: one repair round, at zero Claude tokens, before tier 1
            continue
        env_mod.move_packet(packet, "replied", "done", repo=tick.repo)
        tick.summary["tier0_done"] += 1
        tick.say(f"TIER0-DONE {packet[:12]} shape={outcome['shape']}")
        if order.get("repairs"):
            close_repaired(tick, str(order["repairs"]), packet)   # the repair passed: the original it repairs is closed with it
        tick.ledger(
            {
                "lane": order.get("lane"),
                "packetId": packet,
                "event": "tier0",
                "tier": 0,
                "replyShape": outcome["shape"],
                "pass": True,
                "checks": len(outcome["checks"]),
            }
        )


# --------------------------------------------------------------------------- 3b. the repair round (P46 T7)


def repair_brief(order: dict[str, Any], outcome: dict[str, Any]) -> str:
    """What the addressee is asked for: the block, restated - never new evidence."""
    shape = order.get("replyShape") or "paths-written"
    return (
        f"Your reply to the order \"{order.get('title') or order.get('packetId', '')[:12]}\" could not be closed on its FORM: "
        f"{outcome.get('reason') or 'the grammar was not found'}.\n\n"
        "Reply with the block below and nothing else, filled in from what you ALREADY did - restate, add nothing new, invent "
        "nothing. One bare absolute path per line under PATHS WRITTEN: no markdown links, no backticks, no bullets.\n\n"
        "```\n" + handlers.template(shape) + "```\n"
        f"If you can, run `python content/video_engine/scripts/bridge_check.py --shape {shape} --reply <your reply file>` from "
        "the repo root first and paste its PASS line under the block.\n"
    )


def queue_repair(tick: Tick, folder: Path, order: dict[str, Any], packet: str, outcome: dict[str, Any]) -> None:
    """One follow-up on the original's conversation, queued for the next tick's send; the original waits for the repair.
    Nothing is queued without a conversation to continue on, and never twice."""
    conversation = str(read_json(folder / "conversation.json").get("conversationId") or order.get("conversationId") or "")
    if not conversation:
        tick.say(f"REPAIR-SKIP {packet[:12]}: no conversation to continue on")
        return
    brief = repair_brief(order, outcome)
    repair_id = env_mod.packet_id(brief)
    if tick.dry_run:
        tick.say(f"REPAIR {packet[:12]} -> {repair_id[:12]} (dry-run: nothing queued)")
        return
    queued = env_mod.packet_dir(tick.repo, repair_id, "queue")
    queued.mkdir(parents=True, exist_ok=True)
    env_mod.write_json(queued / "order.json", {
        "packetId": repair_id, "lane": order.get("lane") or "gemini", "from": "claude", "conversationId": conversation,
        "title": f"repair: {order.get('title') or packet[:12]}", "replyShape": order.get("replyShape") or "paths-written",
        "repairs": packet, "brief": brief, "createdAt": stamp(),
        **({"roots": order["roots"]} if order.get("roots") else {}), **({"verify": order["verify"]} if order.get("verify") else {}),
        **({"marker": order["marker"]} if order.get("marker") else {}),
    })
    env_mod.write_json(folder / REPAIR_MARKER, {"repairPacket": repair_id, "queuedAt": stamp(), "reason": outcome.get("reason")})
    tick.summary["repairs"] += 1
    tick.say(f"REPAIR {packet[:12]} -> {repair_id[:12]} queued ({outcome.get('reason')})")
    tick.ledger({"lane": order.get("lane"), "packetId": packet, "event": "repair", "repairPacket": repair_id,
                 "class": outcome.get("class"), "reason": outcome.get("reason")})


def close_repaired(tick: Tick, original: str, repair_packet: str) -> None:
    """The repair reply closed at tier 0 (or tier 1): the original moves to done with the repair named in its tier0.json."""
    folder = env_mod.packet_dir(tick.repo, original, "replied")
    if not folder.exists():
        return
    prior = read_json(folder / "tier0.json")
    env_mod.write_json(folder / "tier0.json", {**prior, "pass": True, "repairedBy": repair_packet, "closedAt": stamp()})
    env_mod.move_packet(original, "replied", "done", repo=tick.repo)
    tick.say(f"REPAIRED {original[:12]} by {repair_packet[:12]}")
    tick.ledger({"lane": None, "packetId": original, "event": "repaired", "repairPacket": repair_packet})


# --------------------------------------------------------------------------- 4. tier 1, the residue


def todays_tier1(repo: Path) -> dict[str, int]:
    """The budget's counter is the ledger itself - today's `tier1` lines, no second file to drift."""

    today = now().strftime("%Y-%m-%d")
    runs, tokens = 0, 0
    path = Path(repo) / env_mod.LEDGER
    if not path.exists():
        return {"runs": 0, "tokens": 0}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get("event") != "tier1" or not str(row.get("ts") or "").startswith(today):
            continue
        runs += 1
        tokens += int(row.get("inputTokens") or 0) + int(row.get("outputTokens") or 0)
    return {"runs": runs, "tokens": tokens}


def budget_spent(repo: Path, config: dict[str, Any]) -> str | None:
    spent = todays_tier1(repo)
    if spent["runs"] >= int(config["residue_runs_per_day"]):
        return f"{spent['runs']}/{config['residue_runs_per_day']} residue runs used today"
    if spent["tokens"] >= int(config["residue_tokens_per_day"]):
        return f"{spent['tokens']}/{config['residue_tokens_per_day']} residue tokens used today"
    return None


def tier1_prompt(folder: Path) -> str:
    return (
        f"Packet folder: {folder}\n"
        f"Read {folder / 'order.json'} (the order), {folder / 'reply.md'} (the lane's reply) and "
        f"{folder / 'tier0.json'} (what the deterministic check tried and why it failed).\n"
        f"Your standing instruction is {HANDLER_INSTRUCTION} - read it from disk first and follow it exactly.\n"
        "Verify against disk, decide done / follow-up / escalate, and write result.md as it says. Nothing else."
    )


def run_tier1(repo: Path, folder: Path) -> dict[str, Any]:
    """One headless run of the `bridge_handler` role from the repo root. Monkeypatched in tests."""

    # Windows installs `claude` as claude.CMD; CreateProcess does not search PATHEXT, so resolve it first
    exe = shutil.which("claude") or "claude"
    argv = [exe, "-p", "--agent", HANDLER_AGENT, "--output-format", "json", tier1_prompt(folder)]
    proc = subprocess.run(argv, cwd=str(repo), capture_output=True, text=True)
    try:
        payload = json.loads(proc.stdout or "")
    except ValueError:
        payload = {}
    return {"exit": proc.returncode, "payload": payload if isinstance(payload, dict) else {}}


def _usage(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Usage as the run reported it - absent stays null, never zero, so an average cannot be wrong."""

    usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}
    fields = {
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "total_cost_usd": payload.get("total_cost_usd"),
    }
    return None if all(value is None for value in fields.values()) else fields


def land_result(repo: Path, packet: str, folder: Path) -> tuple[Path | None, Path]:
    """`result.md` wherever the role wrote it, and the folder the packet ends in.

    The role is told to write `done/<packetId>/result.md`; it may instead write into the packet folder it
    was handed. Both are handled: the packet is merged into `done/` either way.
    """

    done = env_mod.packet_dir(repo, packet, "done")
    if done.is_dir() and done != folder:
        for item in folder.iterdir():
            target = done / item.name
            if not target.exists():
                shutil.move(str(item), str(target))
        shutil.rmtree(folder, ignore_errors=True)
        return (done / RESULT_FILE if (done / RESULT_FILE).exists() else None), done
    if (folder / RESULT_FILE).exists():
        moved = env_mod.move_packet(packet, "replied", "done", repo=repo)
        return moved / RESULT_FILE, moved
    return None, folder


def decision_of(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    match = DECISION_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    return match.group(1).lower().replace("followup", "follow-up") if match else None


def step_tier1(tick: Tick) -> None:
    grace = float(tick.config["grace_min"])
    for folder in packets(tick.repo, "replied"):
        tier0 = read_json(folder / "tier0.json")
        if not tier0 or tier0.get("pass") or (folder / "tier1.json").exists():
            continue
        if (folder / REPAIR_MARKER).exists():
            continue   # P46 T7: the original waits for its repair reply; the repair packet is what tier 1 sees if that fails too
        order = read_json(folder / "order.json")
        packet = order.get("packetId") or folder.name
        age = minutes_since(landed_at(folder))
        if age is not None and age < grace:
            tick.say(f"TIER1-WAIT {packet[:12]} {age:.1f}min < grace {grace}min")
            continue
        spent = budget_spent(tick.repo, tick.config)
        if spent:
            tick.summary["skipped_budget"] += 1
            tick.say(f"TIER1-SKIP {packet[:12]}: residue budget spent ({spent})")
            escalate(tick, folder, packet, "budget", f"{packet[:12]} needs tier 1 but {spent}")
            continue
        _dispatch_tier1(tick, folder, packet, order)


def _dispatch_tier1(tick: Tick, folder: Path, packet: str, order: dict[str, Any]) -> None:
    if tick.dry_run:
        tick.say(f"TIER1 {packet[:12]} (dry-run: no model call)")
        tick.summary["tier1_runs"] += 1
        return
    started = stamp()
    tier0_prior = read_json(folder / "tier0.json")   # read before the packet moves
    run = run_tier1(tick.repo, folder)
    usage = _usage(run.get("payload") or {})
    result_path, landed = land_result(tick.repo, packet, folder)
    env_mod.write_json(
        landed / "tier1.json",
        {
            "startedAt": started,
            "finishedAt": stamp(),
            "exit": run.get("exit"),
            "usage": usage,
            "resultPath": str(result_path) if result_path else None,
        },
    )
    decision = decision_of(result_path)
    tick.summary["tier1_runs"] += 1
    tick.say(f"TIER1 {packet[:12]} exit={run.get('exit')} decision={decision}")
    tick.ledger(
        {
            "lane": order.get("lane"),
            "packetId": packet,
            "event": "tier1",
            "tier": 1,
            "replyShape": order.get("replyShape"),
            "decision": decision,
            "reason": (f"{tier0_prior.get('class') or '?'}:{tier0_prior.get('reason') or ''}"[:200] if tier0_prior else None),   # P46 T7: the metric - tier 1 by cause
            "repairs": order.get("repairs"),
            "exit": run.get("exit"),
            "inputTokens": (usage or {}).get("input_tokens"),
            "outputTokens": (usage or {}).get("output_tokens"),
            "costUsd": (usage or {}).get("total_cost_usd"),
        }
    )
    if decision == "escalate":
        escalate(tick, landed, packet, "handler-escalate", f"{packet[:12]}: the handler escalated - read {result_path}")
    elif decision == "done" and order.get("repairs"):
        close_repaired(tick, str(order["repairs"]), packet)


# --------------------------------------------------------------------------- 5. escalation


def _escalations(folder: Path) -> dict[str, Any]:
    return read_json(folder / "escalated.json").get("reasons") or {}


def escalate(tick: Tick, folder: Path, packet: str, reason: str, body: str) -> bool:
    """One toast per packet per condition; `escalated.json` is the marker that stops the repeat."""

    marker = folder / "escalated.json"
    existing = _escalations(folder)
    if reason in existing:
        return False
    if tick.dry_run:
        tick.say(f"TOAST: bridge {reason} - {body}")
        tick.summary["escalated"] += 1
        return True
    env_mod.write_json(marker, {"packetId": packet, "reasons": {**existing, reason: stamp()}})
    toast(f"Bridge: {reason}", body)
    tick.summary["escalated"] += 1
    tick.say(f"ESCALATED {packet[:12]} reason={reason}")
    tick.ledger({"lane": None, "packetId": packet, "event": "escalated", "reason": reason})
    return True


def step_sla(tick: Tick) -> None:
    """A reply nobody closed inside `sla_min` is the operator's problem - said once."""

    sla = float(tick.config["sla_min"])
    for folder in packets(tick.repo, "replied"):
        order = read_json(folder / "order.json")
        packet = order.get("packetId") or folder.name
        age = minutes_since(landed_at(folder))
        if age is None or age < sla:
            continue
        escalate(tick, folder, packet, "sla", f"{packet[:12]} has been open {age:.0f}min (SLA {sla:.0f}min)")


# --------------------------------------------------------------------------- the tick


def tick_once(repo: Path, config: dict[str, Any], dry_run: bool = False) -> Tick:
    tick = Tick(repo, config, dry_run)
    step_queue(tick)
    step_sent(tick)
    step_tier0(tick)
    step_tier1(tick)
    step_sla(tick)
    return tick


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="one tick, then exit (the default)")
    mode.add_argument("--loop", action="store_true", help="tick forever, sleeping --poll-sec between ticks")
    parser.add_argument("--poll-sec", type=int, default=None, help="overrides the config's poll_sec")
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--config", type=Path, default=None, help=f"default {CONFIG_PATH}")
    parser.add_argument("--dry-run", action="store_true", help="print the tick; send, move, dispatch and toast nothing")
    parser.add_argument("--json", action="store_true", dest="as_json", help="one JSON summary per tick")
    return parser


def _report(tick: Tick, as_json: bool) -> None:
    if as_json:
        print(json.dumps(tick.summary, ensure_ascii=False))
        return
    for line in tick.lines or ["nothing to do"]:
        print(line)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    if args.poll_sec:
        config["poll_sec"] = args.poll_sec
    repo = Path(args.repo)

    # the lock is state; a dry run writes nothing at all, not even that.
    if not args.dry_run and acquire_lock(repo) is None:
        print(f"another bridge daemon holds {repo / LOCK_PATH}", file=sys.stderr)
        return 1
    try:
        while True:
            _report(tick_once(repo, config, args.dry_run), args.as_json)
            if not args.loop:
                return 0
            time.sleep(max(int(config["poll_sec"]), 1))
    except KeyboardInterrupt:
        return 0
    finally:
        if not args.dry_run:
            release_lock(repo)


if __name__ == "__main__":
    raise SystemExit(main())
