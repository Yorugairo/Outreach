"""Prepare and render the source-bound C3 thumbnail page for the current renderer.

This helper reads the frozen C3 claim, verifies the retained Federal Reserve
HTML hash, and asks the existing ``ledger_page`` builder for a signed,
common-zero bars page.  The thumbnail readability pass is a packaging-local
presentation override; this file never creates chart geometry.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import sys
import wave
from pathlib import Path
from typing import Any


EXPECTED_SOURCE_SHA256 = "7a201f7cad0a75ae840e93d5fc386c501e4774c31e8d1631d99dc9dc0c057da0"
EXPECTED_SOURCE_PATH = "evidence/sources/mpr_2025_06.html"
EXPECTED_SOURCE_URL = "https://www.federalreserve.gov/monetarypolicy/2025-06-mpr-part2.htm"
EXPECTED_TABLE = "xtable_balancesheet"
EXPECTED_COLUMN = "xsheeta5"
EXPECTED_WINDOW = {"start": "2022-06-01", "end": "2025-06-11"}
EXPECTED_UNITS = "USD billions"
EXPECTED_VALUES = {"Total assets": -2238, "Reserve balances": 72}
EXPECTED_DISPLAY_VALUES = ["-2238", "+72"]
CAPTURE_T = 12.0
STAGE_SIZE = (1920, 1080)
OUTPUT_SIZE = (1280, 720)
PROOF_SIZE = (320, 180)
OUTPUT_PNG = "c3_thumbnail_1280x720.png"
PROOF_PNG = "c3_thumbnail_320w.png"
TIMELINE_NAME = "c3_thumbnail.timeline.json"
URIS_NAME = "c3_thumbnail.uris.json"
PLAYER_NAME = "c3_thumbnail.player.html"
RENDER_PROOF_NAME = "c3_thumbnail.render.json"


# This is deliberately a presentation-only override in the diagnostic player.
# The existing ledger builder still owns the bars, scale, and positions; these
# type sizes are selected against the 320px derivative, not a new renderer.
THUMBNAIL_CSS = r"""
#stage .lp-title { font-size: 76px !important; line-height: 1.0 !important; top: 10% !important; }
#stage .lp-sub { font-size: 28px !important; line-height: 1.15 !important; top: 16.2% !important; }
#stage .lp-src.compact { font-size: 21px !important; }
#stage .lp-chart { width: 70% !important; height: 65% !important; }
#stage .lp-chart .fed-c3-value { font-size: 68px !important; }
#stage .lp-chart .fed-c3-category { font-size: 48px !important; }
#stage .lp-chart .fed-c3-tick { font-size: 30px !important; }
"""


THUMBNAIL_SCRIPT = r"""
(() => {
  const categories = new Set(["Total assets", "Reserve balances"]);
  let tries = 0;
  const apply = () => {
    const pages = document.querySelectorAll("#stage .lp-page");
    if (!pages.length) {
      if (tries++ < 200) setTimeout(apply, 10);
      return;
    }
    for (const page of pages) {
      page.querySelectorAll(".lp-chart .lab").forEach((el) => {
        el.classList.add(categories.has(el.textContent.trim()) ? "fed-c3-category" : "fed-c3-tick");
      });
      page.querySelectorAll(".lp-chart .val").forEach((el) => el.classList.add("fed-c3-value"));
    }
  };
  apply();
})();
"""


OVERFLOW_JS = r"""
() => {
  const stage = document.getElementById('stage').getBoundingClientRect();
  const page = document.querySelector('#stage .lp-page');
  const visible = (el) => {
    const cs = getComputedStyle(el);
    return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity || '1') > 0.01;
  };
  const isInk = (el) => el.matches('.lp-title, .lp-sub, .lp-src, .lp-title .g, .lp-sub .g, .lp-src .g')
    || (!!el.closest('.lp-chart') && (el.tagName.toLowerCase() === 'text'
        || el.matches('.bar, .ax, .grid, .hrule')));
  const nodes = page ? [...page.querySelectorAll('*')].filter(isInk) : [];
  let max = 0, offenders = [];
  for (const el of nodes) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    const sides = {
      left: Math.max(0, stage.left - r.left),
      top: Math.max(0, stage.top - r.top),
      right: Math.max(0, r.right - stage.right),
      bottom: Math.max(0, r.bottom - stage.bottom),
    };
    const over = Math.max(...Object.values(sides));
    if (over > max) max = over;
    if (over > 0.5) offenders.push({tag: el.tagName.toLowerCase(), cls: el.getAttribute('class') || '', sides});
  }
  return {stage: {x: stage.x, y: stage.y, w: stage.width, h: stage.height},
          ink_nodes: nodes.length,
          page: page ? (() => { const r = page.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; })() : null,
          max_overflow_px: Number(max.toFixed(3)), offenders: offenders.slice(0, 20)};
}
"""


def _episode_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_claim(episode: Path) -> dict[str, Any]:
    claims = json.loads((episode / "claims.v1.json").read_text(encoding="utf-8"))
    claim = next((item for item in claims.get("claims", []) if item.get("id") == "C3"), None)
    if not isinstance(claim, dict):
        raise ValueError("claims.v1.json has no C3 object")
    return claim


def _verify_claim_and_source(episode: Path) -> tuple[dict[str, Any], str]:
    claim = _load_claim(episode)
    source = claim.get("source")
    if not isinstance(source, dict):
        raise ValueError("C3 source metadata is missing")
    expected = {
        "path": EXPECTED_SOURCE_PATH,
        "sha256": EXPECTED_SOURCE_SHA256,
        "url": EXPECTED_SOURCE_URL,
        "table": EXPECTED_TABLE,
        "column": EXPECTED_COLUMN,
    }
    for key, value in expected.items():
        if source.get(key) != value:
            raise ValueError(f"C3 source {key} changed: {source.get(key)!r} != {value!r}")
    if claim.get("window") != EXPECTED_WINDOW:
        raise ValueError(f"C3 window changed: {claim.get('window')!r}")
    if claim.get("units") != EXPECTED_UNITS:
        raise ValueError(f"C3 units changed: {claim.get('units')!r}")

    values = {
        row.get("label"): row.get("change")
        for row in claim.get("values", [])
        if isinstance(row, dict)
    }
    for label, value in EXPECTED_VALUES.items():
        if values.get(label) != value:
            raise ValueError(f"C3 {label} changed: {values.get(label)!r} != {value!r}")

    source_path = episode / source["path"]
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    actual = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if actual != EXPECTED_SOURCE_SHA256:
        raise ValueError(f"source SHA-256 mismatch: {actual} != {EXPECTED_SOURCE_SHA256}")
    return claim, actual


def _page_input(claim: dict[str, Any]) -> dict[str, Any]:
    values = {
        row["label"]: row["change"]
        for row in claim["values"]
        if row.get("label") in EXPECTED_VALUES
    }
    return {
        "title": "WHERE DID IT GO?",
        "sub": "Fed balance-sheet change · 01 Jun 2022 → 11 Jun 2025",
        "src": "Fed MPR Jun 2025 · Table A · USD billions",
        "src_style": "compact",
        # Keep the axis as the unit declaration.  The existing bars painter
        # appends `unit` to every value/tick; putting the full phrase here
        # would duplicate it (`72USD billions`) and push ticks offstage.
        "unit": "",
        "from_zero": True,
        "ylabel": EXPECTED_UNITS,
        "bars": [
            {"label": "Total assets", "value": values["Total assets"], "color": "crimson"},
            {"label": "Reserve balances", "value": values["Reserve balances"], "color": "teal"},
        ],
    }


def _silent_wav_uri(seconds: float = 0.25) -> str:
    """Small deterministic audio URI required by the existing player shell."""
    frames = int(8000 * seconds)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        wav.writeframes(b"\x00\x00" * frames)
    return "data:audio/wav;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def _timeline(page: dict[str, Any]) -> dict[str, Any]:
    """One quiet page scene; the player remains the only chart painter."""
    return {
        "schema_version": "scene_evidence_timeline.v1",
        "runtime_s": 15.0,
        "title": "Fed liquidity C3 thumbnail diagnostic",
        "subtitle": "source-bound packaging diagnostic; not an episode build",
        "episode_id": "fed-liquidity-pressure",
        "project_id": "fed-liquidity-pressure-packaging",
        "narration": {"canonical_hash": "0" * 64, "words_path": ""},
        "captions": [],
        "caption_pages": [],
        "caption_modes": ["stage", "anchor"],
        "sound": [],
        "evidence": {"claim_id": "C3", "source_path": EXPECTED_SOURCE_PATH},
        "scenes": [{
            "scene_id": "c3-thumb",
            "exit": "cut",
            "span": [0.0, 15.0],
            "docks": [],
            "species": [],
            "world": {
                "kind": "ledger",
                "ken_burns": {"scale": 0, "x": 0, "y": 0},
                "page": page,
            },
        }],
    }


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def prepare(out_dir: Path) -> dict[str, Any]:
    episode = _episode_root()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    claim, source_sha = _verify_claim_and_source(episode)

    scripts = episode.parents[2] / "scripts"
    if not scripts.is_dir():
        raise FileNotFoundError(f"ledger_page scripts directory not found: {scripts}")
    sys.path.insert(0, str(scripts))
    import ledger_page  # pylint: disable=import-error,import-outside-toplevel

    series = _page_input(claim)
    errors = ledger_page.validate(series, "bars")
    if errors:
        raise ValueError("ledger_page rejected C3: " + " | ".join(errors))
    page = ledger_page.build_spec(series, "bars", quiet_zone="right")
    if page.get("builder") != "story" or page.get("variant") != "bars":
        raise ValueError(f"unexpected ledger page contract: {page.get('builder')!r}/{page.get('variant')!r}")
    # The numeric values remain source-bound; the positive sign is an honest
    # presentation cue for the common-zero chart at thumbnail scale.
    page["value_strings"] = list(EXPECTED_DISPLAY_VALUES)
    if page.get("value_strings") != EXPECTED_DISPLAY_VALUES:
        raise ValueError(f"exact value strings changed: {page.get('value_strings')!r}")
    # This is the existing full-stage ledger mode, the same stamp used by the
    # production timeline compiler.  It changes placement, never chart data.
    page["full_stage"] = True
    page["caption"] = "anchor"

    metadata = {
        "diagnostic": "fed-liquidity-c3-thumbnail",
        "status": "prepared_only",
        "render_status": "WAITING_FOR_T14_RENDERER_RELEASE",
        "source": {
            "path": EXPECTED_SOURCE_PATH,
            "sha256": source_sha,
            "url": EXPECTED_SOURCE_URL,
            "table": EXPECTED_TABLE,
            "column": EXPECTED_COLUMN,
        },
        "claim_id": "C3",
        "window": EXPECTED_WINDOW,
        "units": EXPECTED_UNITS,
        "values": EXPECTED_VALUES,
        "geometry_contract": {
            "variant": "bars",
            "builder": "story",
            "common_zero": True,
            "signed_values": True,
        "value_strings": page["value_strings"],
        },
        "renderer": "content/video_engine/scripts/render_baseline.py + current packaging renderer",
    }
    _write_json(out_dir / "c3_thumbnail.series.json", series)
    _write_json(out_dir / "c3_thumbnail.page.json", page)
    _write_json(out_dir / "c3_thumbnail.prep.json", metadata)
    return metadata


def render(out_dir: Path) -> dict[str, Any]:
    """Render through render_baseline's existing shell/player primitives."""
    out_dir = out_dir.resolve()
    metadata = prepare(out_dir)
    page = json.loads((out_dir / "c3_thumbnail.page.json").read_text(encoding="utf-8"))
    timeline = _timeline(page)
    uris = {"__audio__": _silent_wav_uri()}
    # The single-file form is the same form used by the golden harness.  No
    # chart or SVG is authored here; the current engine paints the page.
    scripts = _episode_root().parents[2] / "scripts"
    sys.path.insert(0, str(scripts))
    import render_baseline as rb  # pylint: disable=import-error,import-outside-toplevel

    player = rb.instantiate(timeline, uris)
    # Keep the renderer/player contract intact; add only a diagnostic-local
    # style/script layer for the phone derivative's reading size.
    # The reviewed player template is an HTML fragment (it has no </head>);
    # prepend the style so the browser parses it before the fragment's base CSS.
    player = "<style id=\"fed-c3-thumb-overrides\">" + THUMBNAIL_CSS + "</style>\n" + player
    player = player.replace("</body>", "<script id=\"fed-c3-thumb-labels\">" + THUMBNAIL_SCRIPT + "</script>\n</body>", 1)
    (out_dir / PLAYER_NAME).write_text(player, encoding="utf-8")
    _write_json(out_dir / TIMELINE_NAME, timeline)
    _write_json(out_dir / URIS_NAME, uris)

    from playwright.sync_api import sync_playwright  # pylint: disable=import-outside-toplevel
    from PIL import Image  # pylint: disable=import-outside-toplevel

    srv, port = rb.serve(out_dir)
    native: bytes
    dom: dict[str, Any]
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            browser_page = browser.new_context(viewport={"width": STAGE_SIZE[0], "height": STAGE_SIZE[1]},
                                                device_scale_factor=1).new_page()
            browser_page.goto(f"http://127.0.0.1:{port}/{PLAYER_NAME}", wait_until="networkidle", timeout=120000)
            rb.prepare_page(browser_page, *STAGE_SIZE)
            native = rb.frame_png(browser_page, CAPTURE_T, STAGE_SIZE)
            dom = browser_page.evaluate(OVERFLOW_JS)
            browser.close()
    finally:
        srv.shutdown()

    image = Image.open(io.BytesIO(native)).convert("RGB")
    if image.size != STAGE_SIZE:
        raise ValueError(f"native stage captured at {image.size}, expected {STAGE_SIZE}")
    image.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS).save(out_dir / OUTPUT_PNG, "PNG", optimize=False)
    image.resize(PROOF_SIZE, Image.Resampling.LANCZOS).save(out_dir / PROOF_PNG, "PNG", optimize=False)

    output_hash = hashlib.sha256((out_dir / OUTPUT_PNG).read_bytes()).hexdigest()
    proof_hash = hashlib.sha256((out_dir / PROOF_PNG).read_bytes()).hexdigest()
    player_hash = hashlib.sha256((out_dir / PLAYER_NAME).read_bytes()).hexdigest()
    render_metadata = {
        **metadata,
        "status": "rendered_diagnostic",
        "render_status": "CAPTURED_NO_APPROVAL",
        "capture_t_s": CAPTURE_T,
        "stage_size": list(STAGE_SIZE),
        "output": {"path": OUTPUT_PNG, "size": list(OUTPUT_SIZE), "sha256": output_hash},
        "phone_proof": {"path": PROOF_PNG, "size": list(PROOF_SIZE), "sha256": proof_hash},
        "player_sha256": player_hash,
        "overflow": dom,
    }
    _write_json(out_dir / RENDER_PROOF_NAME, render_metadata)
    return render_metadata


def check(out_dir: Path) -> dict[str, Any]:
    """Validate prepared/rendered artifacts without writing them."""
    out_dir = out_dir.resolve()
    episode = _episode_root()
    _claim, source_sha = _verify_claim_and_source(episode)
    prep = json.loads((out_dir / "c3_thumbnail.prep.json").read_text(encoding="utf-8"))
    proof = json.loads((out_dir / RENDER_PROOF_NAME).read_text(encoding="utf-8"))
    if prep.get("source", {}).get("sha256") != source_sha or proof.get("source", {}).get("sha256") != source_sha:
        raise ValueError("render metadata source hash does not match retained source")
    if proof.get("values") != EXPECTED_VALUES or proof.get("window") != EXPECTED_WINDOW:
        raise ValueError("render metadata C3 values/window changed")
    if proof.get("geometry_contract", {}).get("value_strings") != EXPECTED_DISPLAY_VALUES:
        raise ValueError("render metadata value strings changed")
    if proof.get("overflow", {}).get("max_overflow_px", 1) > 0.5:
        raise ValueError(f"page overflow exceeds 0.5px: {proof['overflow']}")

    from PIL import Image  # pylint: disable=import-outside-toplevel
    results = {}
    for name, expected, key in ((OUTPUT_PNG, OUTPUT_SIZE, "output"), (PROOF_PNG, PROOF_SIZE, "phone_proof")):
        path = out_dir / name
        with Image.open(path) as image:
            if image.size != expected:
                raise ValueError(f"{name} dimensions {image.size} != {expected}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if proof.get(key, {}).get("sha256") != digest:
            raise ValueError(f"{name} SHA-256 differs from render metadata")
        results[name] = {"size": list(expected), "sha256": digest}
    return {"source_sha256": source_sha, "overflow": proof["overflow"], "images": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--render", action="store_true", help="prepare and render the diagnostic PNGs")
    parser.add_argument("--check", action="store_true", help="validate rendered PNGs and metadata without writing")
    args = parser.parse_args()
    if args.render and args.check:
        parser.error("--render and --check are mutually exclusive")
    metadata = check(args.out_dir) if args.check else render(args.out_dir) if args.render else prepare(args.out_dir)
    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
