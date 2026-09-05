"""The four golden surfaces (P39 T3): small, synthetic, deterministic timelines that exercise
what P37 and P38 touch - a ledger page mid-build, a chart carrying a callout, a 16:9 dock
pair, a 9:16 dock pair.

Everything is derived from committed inputs (the template, one committed `.series.json`
sidecar, generated solid plates, a two-second silent WAV) so the frames can be re-rendered
on any checkout. No episode assets, no quarantine. Run as a script to (re)write the source
JSON beside this file; the tests read those files, never this module's output at test time,
so a change here is a deliberate golden refresh.
"""
from __future__ import annotations

import base64
import io
import json
import struct
import sys
import wave
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SCRIPTS = REPO / "content/video_engine/scripts"
SERIES = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-divergence-v1.series.json"
SOURCES = HERE / "sources"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import ledger_page as LPG  # noqa: E402

RUNTIME = 30.0
# the frame each surface is judged at - chosen so the thing under test is on screen and mid-motion
FRAME_T = {
    "ledger-page-mid-build": 6.0,   # field filled, outline drawn, ink and bars building
    "chart-callout": 12.0,          # the line has drawn, all four badges have landed
    "dock-pair-16x9": 12.0,         # both cards up, badges landed
    "dock-pair-9x16": 12.0,
}


def png_solid(w: int, h: int, rgb: tuple[int, int, int]) -> bytes:
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def silent_wav(seconds: float) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(1); w.setframerate(8000)
        w.writeframes(b"\x80" * int(8000 * seconds))
    return buf.getvalue()


def uri(mime: str, data: bytes) -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def _pages() -> list[dict]:
    words = ["the", "frame", "under", "test"]
    return [{"s": 1.0 + 3 * i, "e": 3.8 + 3 * i,
             "t": [{"w": w, "k": j == 1, "s": 1.0 + 3 * i + 0.4 * j, "e": 1.4 + 3 * i + 0.4 * j} for j, w in enumerate(words)]}
            for i in range(9)]


def _timeline(title: str, scenes: list[dict], evidence: dict, aspect: str | None) -> dict:
    pages = _pages()
    tl = {
        "schema_version": "scene_evidence_timeline.v1", "runtime_s": RUNTIME,
        "title": title, "subtitle": "P39 golden surface", "episode_id": "golden", "project_id": "golden",
        "narration": {"canonical_hash": "0" * 64, "words_path": ""},
        "captions": [{"at": p["s"], "until": p["e"], "text": " ".join(t["w"] for t in p["t"])} for p in pages],
        "caption_pages": pages, "caption_modes": ["stage", "anchor"], "sound": [],
        "evidence": evidence, "scenes": scenes,
    }
    if aspect:
        tl["aspect"] = aspect
    return tl


def _base_uris() -> dict:
    return {
        "plate-plain": uri("image/png", png_solid(64, 36, (43, 52, 60))),
        "__audio__": uri("audio/wav", silent_wav(2.0)),
    }


def _badges() -> list[dict]:
    return [{"label": "MAMAA", "value": "+20%", "tag": "matches the index", "accent": "cobalt"},
            {"label": "S&P 500", "value": "+21%", "tag": "12 months", "accent": "ink"},
            {"label": "SEMICONDUCTORS", "value": "+102%", "tag": "their divergence", "accent": "teal"},
            {"label": "MEMORY BUILDERS", "value": "+613%", "tag": "our layer", "accent": "coral"}]


def _dock(aid: str, slot: int, enter: float, exit_: float, n_badges: int) -> dict:
    return {"slide": aid, "slot": slot, "enter": enter, "exit": exit_,
            "badge_at": [round(enter + 0.75 + 1.3 * (n + 1), 2) for n in range(n_badges)]}


def ledger_page_mid_build() -> tuple[dict, dict]:
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", 0, "right")
    page["field"] = "scribble"
    page["focus"] = {"kind": "callout", "label": "the divergence"}
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0.04, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: ledger page mid-build", scenes, {}, None), _base_uris()


def _chart_evidence() -> dict:
    chart = json.loads(SERIES.read_text(encoding="utf-8"))
    return {"ev-golden-chart": {"title": "Golden chart", "source": "golden series sidecar", "species": "chart",
                                "document": {"path": "golden", "sha256": "0" * 64},
                                "badges": _badges(), "chart": chart}}


def chart_callout() -> tuple[dict, dict]:
    ev = _chart_evidence()
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0.0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME],
               "docks": [_dock("ev-golden-chart", 0, 2.0, RUNTIME, 4)],
               "species": [{"kind": "callout", "at": 10.0, "dur": 6.0, "target": {"kind": "point", "x": 0.72, "y": 0.42}}]}]
    uris = _base_uris(); uris["ev-golden-chart"] = uri("image/png", png_solid(64, 36, (22, 24, 28)))
    return _timeline("Golden: chart with a callout", scenes, ev, None), uris


def _dock_pair(aspect: str | None) -> tuple[dict, dict]:
    ev = {
        "ev-golden-card-a": {"title": "Golden card A", "source": "golden", "species": "deck",
                             "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[:2]},
        "ev-golden-card-b": {"title": "Golden card B", "source": "golden", "species": "deck",
                             "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[2:]},
    }
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0.05, "x": 10, "y": -6}},
               "exit": "cut", "span": [0.0, RUNTIME],
               "docks": [_dock("ev-golden-card-a", 0, 2.0, RUNTIME, 2), _dock("ev-golden-card-b", 1, 5.0, RUNTIME, 2)],
               "species": []}]
    uris = _base_uris()
    uris["ev-golden-card-a"] = uri("image/png", png_solid(640, 360, (23, 105, 194)))
    uris["ev-golden-card-b"] = uri("image/png", png_solid(640, 360, (23, 140, 131)))
    return _timeline(f"Golden: dock pair {aspect or '16:9'}", scenes, ev, aspect), uris


SURFACES = {
    "ledger-page-mid-build": ledger_page_mid_build,
    "chart-callout": chart_callout,
    "dock-pair-16x9": lambda: _dock_pair(None),
    "dock-pair-9x16": lambda: _dock_pair("9:16"),
}


def write_sources() -> list[Path]:
    SOURCES.mkdir(parents=True, exist_ok=True)
    out = []
    for name, fn in SURFACES.items():
        tl, uris = fn()
        for suffix, payload in (("timeline", tl), ("uris", uris)):
            p = SOURCES / f"{name}.{suffix}.json"
            p.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
            out.append(p)
    return out


if __name__ == "__main__":
    for p in write_sources():
        print(f"{p.stat().st_size:>9,}  {p.relative_to(REPO)}")
