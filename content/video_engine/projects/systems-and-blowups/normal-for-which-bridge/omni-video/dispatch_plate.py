"""Dispatch the crossings-map plate order to the video-engine MCP server over stdio.

Same contract as review/claims/mp-host-transitions-v1/dispatch_batch.py: the server is
registered in .mcp.json but loads on session start, so a session that did not get it
speaks JSON-RPC to it directly - the contract the Claude Code client would use.

Precondition (checked here, never assumed): the driver's dedicated automation profile is
up - Chrome launched with
    --user-data-dir=C:\\Users\\Snipe\\.flow-chrome-profile --remote-debugging-port=9223
signed in to Google Flow. The operator launches that; this script never touches
credentials. 9222 on the default profile is only the driver's fallback.

    python content/video_engine/projects/systems-and-blowups/japan-tariff-trick/omni-video/dispatch_crossings_map.py

The order is FROZEN in sig-b-crossings-map.order.json. Output lands in stills/ next to the
other signature plates, quarantined until the operator approves the frame.
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
HERE = Path(__file__).resolve().parent
ORDER = HERE / (sys.argv[1] if len(sys.argv) > 1 else "sig-b-crossings-map.order.json")   # a variant is its own order file
SERVER = REPO / "tools/google-flow-driver/mcp/server.mjs"
LOG = HERE / "dispatch-crossings-map.log"   # one log, every order appended
RESULT = HERE / (ORDER.name.replace(".order.json", ".result.json"))
FLOW_PROFILE = Path(r"C:/Users/Snipe/.flow-chrome-profile")   # the driver's dedicated automation profile


def cdp_up() -> str | None:
    """Mirror cdp-driver.getWsEndpoint(): dedicated profile on 9223 first, default 9222 last."""
    ports: list[int] = []
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
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # the pill text carries the banana emoji; cp1252 consoles choke on it
    endpoint = cdp_up()
    if not endpoint:
        print("ABORT: no Chrome CDP endpoint (9223 automation profile / 9222 fallback). Launch:\n"
              '  & "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" '
              "--user-data-dir=C:\\Users\\Snipe\\.flow-chrome-profile --remote-debugging-port=9223\n"
              "signed in to Google Flow, then re-run. The operator launches it; this script never enters credentials.")
        return 2

    order = json.loads(ORDER.read_text(encoding="utf-8"))
    args = {k: v for k, v in order.items() if not k.startswith("_") and k not in ("budget", "review_state")}
    out = REPO / args["outputPath"]
    args["outputPath"] = str(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        print(f"ABORT: {out} already exists - a re-roll is a new order file, not an overwrite.")
        return 3
    print(f"dispatching {ORDER.name} via {endpoint} -> {out.name}")

    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "sig-b-crossings-map", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "create_flow_image", "arguments": args}},
    ]

    with LOG.open("a", encoding="utf-8") as log:
        log.write(f"\n=== dispatch {datetime.now().isoformat(timespec='seconds')} {ORDER.name} ===\n")
        proc = subprocess.Popen(["node", str(SERVER)], cwd=str(REPO), stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", bufsize=1)
        assert proc.stdin and proc.stdout
        for m in msgs:
            proc.stdin.write(json.dumps(m) + "\n")
        proc.stdin.flush()                       # keep stdin OPEN: EOF would end the server mid-roll

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
    meta = out.with_name(out.stem + "_meta.json")
    print(f"plate on disk: {out.exists()}  meta: {meta.exists()}  (quarantined - operator approves the frame)")
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
