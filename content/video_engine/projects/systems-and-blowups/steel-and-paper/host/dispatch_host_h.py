"""P68 - the three HOST plates for Steel and Paper H (E99 s81: "We could incorporate mike into the studio, newsroom
scenes etc. flow is available and if we add character+image prompt should be good to go.").

Same contract as japan-tariff-trick/omni-video/dispatch_crossings_map.py: JSON-RPC over stdio to the video-engine MCP
server (tools/google-flow-driver/mcp/server.mjs), create_flow_image (Nano Banana Pro, zero credit) over CDP to the
operator's automation Chrome on 9223. The orders are FROZEN below; a re-roll is a new order id. Output lands in
steel-and-paper/host/ (gitignored png), quarantined until the operator approves the frame (E10).

    python dispatch_host_h.py            # all three
    python dispatch_host_h.py H-2        # one
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
PROJ = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
HOST = PROJ / "host"
SERVER = REPO / "tools/google-flow-driver/mcp/server.mjs"
LOG = HOST / "dispatch-host-h.log"
FLOW_PROFILE = Path(r"C:/Users/Snipe/.flow-chrome-profile")
PROJECT_URL = "https://labs.google/fx/tools/flow/project/d171ec1f-d4a2-4b79-b76e-32460193dccc"
STYLE = "A light application of woodblock print and vox newspaper with rich anime colors."   # the recognised directive, verbatim (mp-host-identity)
NEG = ("Negative: no borders, no margins, no outer frame, no paper matting, no photorealism, no 3D render, no text, "
       "no numbers, no words, no letters, no logos, no captions.")

ORDERS = {
    "H-1": {
        "_beat": "0:54-1:09 'The three questions read for one thing. Not Bravos Research... Capital arriving faster than the value it's chasing.' HOST WINDOW 1 - the studio (REBUILD-TREATMENT-H.md row 7).",
        "prompt": ("full bleed edge-to-edge 16:9 horizontal. the character seated at the anchor desk of an empty finance broadcast "
                   "studio between takes, three-quarter view, calm and direct, one hand resting on a printed chart on the "
                   "desk, the other gesturing toward the viewer; dark studio monitors switched off behind him, a single key "
                   "light from the left, the rest of the set in shadow; wide composition with the desk's left third empty "
                   "for a card to land. " + STYLE + " " + NEG),
        "references": ["Mike"],
        "ratio": "16:9",
        "outputPath": "content/video_engine/projects/systems-and-blowups/steel-and-paper/host/H-1-studio.png",
    },
    "H-2": {
        "_beat": "7:52-8:20 'Now the test - the one I promised at the top. Take any holding and ask it three questions.' HOST WINDOW 2 - the desk (row 20).",
        "prompt": ("full bleed edge-to-edge 16:9 horizontal. the character leaning over a heavy wooden workbench, an old iron "
                   "railway spike and a slate chalkboard on the bench, holding up three fingers, half-smiling, looking at "
                   "the viewer; warm lamp light from above, a brick wall far behind in shadow; the bench's right half kept "
                   "clear for a list to land. " + STYLE + " " + NEG),
        "references": ["Mike"],
        "ratio": "16:9",
        "outputPath": "content/video_engine/projects/systems-and-blowups/steel-and-paper/host/H-2-desk.png",
    },
    "H-3": {
        "_beat": "12:30-12:50 'Decide for yourself which of those you believe. More worried: the index they sold you as the safe version...' HOST WINDOW 3 - the newsroom (row 23).",
        "prompt": ("full bleed edge-to-edge 16:9 horizontal. the character standing in a quiet newsroom after hours, holding a "
                   "single antique share certificate up to the viewer with one hand, the other in his jacket pocket; rows "
                   "of empty desks and dark screens behind him, one window with city light at the far right; wide "
                   "composition with the left third of the frame empty for a card to land. " + STYLE + " " + NEG),
        "references": ["Mike"],
        "ratio": "16:9",
        "outputPath": "content/video_engine/projects/systems-and-blowups/steel-and-paper/host/H-3-newsroom.png",
    },
}


def cdp_up() -> str | None:
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


def rpc(proc, msg):
    proc.stdin.write((json.dumps(msg) + "\n").encode("utf-8"))
    proc.stdin.flush()


def read_until(proc, want_id, timeout_s):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.2)
            continue
        line = line.decode("utf-8", "replace").strip()
        if not line.startswith("{"):
            with LOG.open("a", encoding="utf-8") as f:
                f.write(f"  [server] {line}\n")
            continue
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        if m.get("id") == want_id:
            return m
    return None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    which = [a for a in sys.argv[1:] if a in ORDERS] or list(ORDERS)
    endpoint = cdp_up()
    if not endpoint:
        print("ABORT: no Chrome CDP endpoint (9223 automation profile / 9222 fallback); the operator launches it.")
        return 2
    HOST.mkdir(parents=True, exist_ok=True)
    (HOST / "HOST-ORDERS-H.json").write_text(json.dumps(ORDERS, indent=1), encoding="utf-8")   # the frozen record
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n=== {datetime.now().isoformat(timespec='seconds')} dispatch {which} via {endpoint}\n")
    proc = subprocess.Popen(["node", str(SERVER)], cwd=str(REPO), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=open(HOST / "dispatch-host-h.stderr.log", "ab"))
    try:
        rpc(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                   "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                              "clientInfo": {"name": "steel-and-paper-host-h", "version": "1"}}})
        init = read_until(proc, 1, 60)
        if not init:
            print("ABORT: the server did not answer initialize")
            return 4
        rpc(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        rc = 0
        for i, oid in enumerate(which, start=10):
            order = ORDERS[oid]
            out = REPO / order["outputPath"]
            if out.exists():
                print(f"{oid}: SKIP - {out.name} exists (a re-roll is a new order id)")
                continue
            args = {k: v for k, v in order.items() if not k.startswith("_")}
            args["outputPath"] = str(out)
            args["projectUrl"] = PROJECT_URL
            print(f"{oid}: dispatching -> {out.name}", flush=True)
            t0 = time.time()
            rpc(proc, {"jsonrpc": "2.0", "id": i, "method": "tools/call",
                       "params": {"name": "create_flow_image", "arguments": args}})
            res = read_until(proc, i, 900)
            dt = time.time() - t0
            with LOG.open("a", encoding="utf-8") as f:
                f.write(f"{oid} {dt:.0f}s {json.dumps(res)[:2000]}\n")
            ok = bool(res) and not res.get("error") and out.exists()
            print(f"{oid}: {'OK' if ok else 'FAILED'} in {dt:.0f}s -> {out if ok else json.dumps(res)[:400]}", flush=True)
            if ok:
                (out.with_name(out.stem + "_meta.json")).write_text(json.dumps(
                    {"schema_version": "google_flow_output.v1", "created_at": datetime.now().isoformat(timespec="seconds"),
                     "order": oid, "prompt": order["prompt"], "references": order["references"], "ratio": order["ratio"],
                     "projectUrl": PROJECT_URL, "beat": order["_beat"], "review_state": "quarantined until the operator approves the frame"},
                    indent=1), encoding="utf-8")
            else:
                rc = 1
        return rc
    finally:
        try:
            proc.stdin.close()
        except Exception:  # noqa: BLE001
            pass
        proc.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
