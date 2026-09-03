"""Dispatch batch.json to the video-engine MCP server over stdio and log everything.

Why stdio and not an MCP tool call: the server is registered in .mcp.json but loads on
session start, so the session that wrote this claim cannot call it as a tool. Speaking
JSON-RPC to it directly is the same contract the Claude Code client would use.

Precondition (checked here, never assumed): Chrome with --remote-debugging-port=9222,
signed in to Google Flow. The operator launches that; this script never touches
credentials.

    python review/claims/mp-host-transitions-v1/dispatch_batch.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

REPO = Path(r"C:/Users/Snipe/Downloads/Outreach Program")
CLAIM = REPO / "review/claims/mp-host-transitions-v1"
SERVER = REPO / "tools/google-flow-driver/mcp/server.mjs"
LOG = CLAIM / "dispatch.log"
RESULT = CLAIM / "dispatch-result.json"


FLOW_PROFILE = Path(r"C:/Users/Snipe/.flow-chrome-profile")   # the driver's dedicated automation profile


def cdp_up() -> str | None:
    """Mirror cdp-driver.getWsEndpoint(): dedicated profile on 9223 first, default 9222 last."""
    ports = []
    active = FLOW_PROFILE / "DevToolsActivePort"
    if active.exists():
        try:
            ports.append(int(active.read_text(encoding="utf-8").strip().splitlines()[0]))
        except (ValueError, IndexError):
            pass
    ports += [9223, 9222]
    for port in ports:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=3) as r:
                if r.status == 200:
                    return f"127.0.0.1:{port}"
        except Exception:  # noqa: BLE001
            continue
    return None


def main() -> int:
    if not cdp_up():
        print("ABORT: no Chrome CDP endpoint on 127.0.0.1:9222. Launch Chrome with "
              "--remote-debugging-port=9222 signed in to Flow, then re-run.")
        return 2

    batch = json.loads((CLAIM / "batch.json").read_text(encoding="utf-8"))
    args = {k: v for k, v in batch.items() if not k.startswith("_")}   # _contract/_style are for readers
    (CLAIM / "clips").mkdir(exist_ok=True)

    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "mp-host-transitions-v1", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "create_flow_batch", "arguments": args}},
    ]

    with LOG.open("a", encoding="utf-8") as log:
        log.write(f"\n=== dispatch {datetime.now().isoformat(timespec='seconds')} "
                  f"scenes={len(args['scenes'])} ===\n")
        proc = subprocess.Popen(["node", str(SERVER)], cwd=str(REPO), stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", bufsize=1)
        assert proc.stdin and proc.stdout
        for m in msgs:
            proc.stdin.write(json.dumps(m) + "\n")
        proc.stdin.flush()                       # keep stdin OPEN: EOF would end the server mid-batch

        started = time.time()
        result = None
        for line in proc.stdout:
            log.write(line)
            log.flush()
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("id") == 2:
                result = obj
                break
        elapsed = time.time() - started
        proc.stdin.close()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()

    if result is None:
        print(f"no tools/call response after {elapsed:.0f}s - see {LOG}")
        return 1
    RESULT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    err = result.get("error") or (result.get("result") or {}).get("isError")
    content = (result.get("result") or {}).get("content") or []
    text = "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
    print(f"{'ERROR' if err else 'OK'} after {elapsed/60:.1f} min -> {RESULT}")
    print(text[:2000])
    clips = sorted((CLAIM / "clips").glob("*.mp4"))
    print(f"clips on disk: {len(clips)}")
    for c in clips:
        print(f"  {c.stat().st_size/1048576:6.1f} MB  {c.name}")
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
