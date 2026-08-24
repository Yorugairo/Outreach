"""The delivery watchdog — fallback trigger for manually-run batches.

The primary P17 path is direct invocation (orchestrator calls ``codex exec``
and scans synchronously). This process exists for batches the operator runs by
hand in a desktop app: it polls every open claim's delivery directory for the
``approvals.json`` completion signal, waits for the delivery to stop growing
(debounce), runs the deterministic scan, notifies, and optionally launches the
configured resume command.

Design constraints, honoured explicitly:

- **Single instance** — a lock file with the live pid; a second start exits.
- **No orphan risk** — the watchdog owns no children beyond short-lived
  subprocesses; stopping it is ``--stop`` (reads the lock, kills the pid).
- **Stateless restarts** — handled deliveries are remembered by a marker file
  *in the delivery folder* (``.watchdog-scanned.json``), so a restart neither
  re-notifies nor misses anything delivered while it was down.

Side effects (scan, notify, launch, clock) are injected into ``WatchdogCore``
so the loop is testable without a filesystem event or a process.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

from content.video_engine.src.services.delivery_scan import (
    APPROVALS_FILENAME,
    scan_claim_delivery,
    summary_line,
)
from content.video_engine.src.services.generation_claim import list_claims
from content.video_engine.watchdog import notify

MARKER_FILENAME = ".watchdog-scanned.json"
DEFAULT_INTERVAL_S = 2.0
#: A delivery is settled when its total size is unchanged across one interval.
ENV_RESUME_COMMAND = "VIDEO_ENGINE_CLAIM_RESUME_COMMAND"

LOCK_FILE = Path.home() / ".video-engine" / "watchdog.lock"


def _tree_size(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def _launch_resume(claim_id: str, env: Mapping[str, str]) -> None:
    """Launch the configured headless resume command; the single process boundary."""

    template = env.get(ENV_RESUME_COMMAND)
    if not template:
        return
    subprocess.Popen(template.format(claim_id=claim_id), shell=True)


@dataclass
class WatchdogCore:
    """The decision loop with every side effect injected."""

    scan: Callable[[Mapping[str, Any]], dict] = scan_claim_delivery
    send: Callable[[str], Any] = notify.notify_all
    launch: Callable[[str], None] = lambda claim_id: None
    clock: Callable[[], float] = time.monotonic
    pending: dict[str, int] = field(default_factory=dict)  # claim_id -> last size

    def poll_once(self, claims: list[dict]) -> list[dict]:
        """One pass over open claims. Returns the scans performed."""

        performed: list[dict] = []
        for claim in claims:
            if claim.get("status") != "open":
                continue
            delivery = Path(str(claim["delivery_dir"]))
            claim_id = str(claim["claim_id"])
            if not (delivery / APPROVALS_FILENAME).exists():
                continue
            if (delivery / MARKER_FILENAME).exists():
                continue
            size = _tree_size(delivery)
            if self.pending.get(claim_id) != size:
                # First sighting, or still growing: wait one more interval.
                self.pending[claim_id] = size
                continue
            del self.pending[claim_id]
            summary = self.scan(claim)
            (delivery / MARKER_FILENAME).write_text(
                json.dumps({"counts": summary["counts"], "conflicts": summary["conflicts"]}),
                encoding="utf-8",
            )
            self.send(summary_line(summary))
            self.launch(claim_id)
            performed.append(summary)
        return performed


def _acquire_lock() -> bool:
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text(encoding="utf-8").strip())
            os.kill(pid, 0)  # raises when the pid is gone
            return False  # a live watchdog holds the lock
        except (ValueError, OSError):
            pass  # stale lock: fall through and take it
    LOCK_FILE.write_text(str(os.getpid()), encoding="utf-8")
    return True


def _stop() -> int:
    if not LOCK_FILE.exists():
        print("no watchdog lock; nothing to stop")
        return 0
    pid = LOCK_FILE.read_text(encoding="utf-8").strip()
    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    LOCK_FILE.unlink(missing_ok=True)
    print(f"stopped watchdog pid {pid}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    parser.add_argument("--once", action="store_true", help="one poll pass, then exit")
    parser.add_argument("--stop", action="store_true", help="stop the running watchdog")
    args = parser.parse_args(argv)

    if args.stop:
        return _stop()
    if not args.once and not _acquire_lock():
        print("another watchdog is already running (see ~/.video-engine/watchdog.lock)")
        return 1

    core = WatchdogCore(launch=lambda claim_id: _launch_resume(claim_id, os.environ))
    try:
        while True:
            performed = core.poll_once(list_claims())
            for summary in performed:
                print(summary_line(summary))
            if args.once:
                return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0
    finally:
        if not args.once:
            LOCK_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
