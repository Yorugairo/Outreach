"""THE MORPH'S INVARIANTS - the measurement behind the motion gate's M17 row (P47 T3; the brief B4).

A page that enters by `morph` turns a prop outline into the area under its series by ARAP. Whether that reads as ONE
thing changing is the brief's three match-cut invariants - centroid shift <= 6 % of W, dominant axis turn <= 15 deg,
bounding area min/max >= 0.60 - plus det J(t) > 0 (the ARAP guarantee, checked on the solved mesh too). The player
computes them from its own morph (`window.__morphInvariants`, 25 frames of the outline); this tool drives a built player
through render_baseline's harness, seeks into each morph page, and writes them beside the timeline for the gate.

    python measure_morph.py <build-dir> [--timeline NAME.timeline.json] [--html player.html] [--out morph-invariants.json]

Writes <build-dir>/morph-invariants.json: {"html_sha256", "timeline", "scenes": {scene_id: {...invariants}}}.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import render_baseline as RB  # noqa: E402

MORPH_INVARIANTS_NAME = "morph-invariants.json"


def morph_scenes(tl: dict) -> list[dict]:
    return [s for s in tl.get("scenes", []) if (s.get("world") or {}).get("kind") == "ledger"
            and ((s["world"].get("page") or {}).get("enter") == "morph")]


def measure_html(html: Path, aspect: str, scenes: list[dict]) -> dict:
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE[aspect]
    srv, port = RB.serve(html.parent)
    out: dict = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": w, "height": h}).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            for sc in scenes:
                ms = float((sc["world"].get("page") or {}).get("morph_s") or 2.0)
                t = float(sc["span"][0]) + ms / 2
                RB.frame_png(page, t, (w, h))   # seek: the page builds its morph on first paint
                inv = page.evaluate("() => window.__morphInvariants ? window.__morphInvariants() : null")
                out[sc.get("scene_id", "?")] = inv or {"error": "no morph on the page at its midpoint"}
            browser.close()
    finally:
        srv.shutdown()
    return out


def measure(build: Path, timeline_name: str | None = None, html_name: str = "player.html", out_name: str = MORPH_INVARIANTS_NAME) -> tuple[Path, dict]:
    tls = [build / timeline_name] if timeline_name else sorted(build.glob("*.timeline.json"))
    if not tls or not tls[0].exists():
        raise SystemExit(f"no timeline in {build}")
    tl = json.loads(tls[0].read_text(encoding="utf-8"))
    html = build / html_name
    if not html.exists():
        raise SystemExit(f"no {html_name} in {build}")
    scenes = morph_scenes(tl)
    res = measure_html(html, str(tl.get("aspect") or "16:9"), scenes) if scenes else {}
    doc = {"timeline": tls[0].name, "html_sha256": hashlib.sha256(html.read_bytes()).hexdigest(), "scenes": res}
    out = build / out_name
    out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return out, res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("build", type=Path)
    ap.add_argument("--timeline")
    ap.add_argument("--html", default="player.html")
    ap.add_argument("--out", default=MORPH_INVARIANTS_NAME)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    out, res = measure(a.build, a.timeline, a.html, a.out)
    print(f"morph-invariants: {out}")
    for sid, r in res.items():
        print(f"  {sid}: " + (r.get("error") or f"centroid {100 * r['centroid_shift']:.1f} % W ({'ok' if r['centroid_ok'] else 'FAIL'}), axis {r['axis_deg']:.1f} deg ({'ok' if r['axis_ok'] else 'FAIL'}), area {r['area_ratio']:.2f} ({'ok' if r['area_ok'] else 'FAIL'}), min det {r['min_det']:.3f}, end error {r['end_error']:.4f}"))
    if not res:
        print("  no morph page in the timeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
