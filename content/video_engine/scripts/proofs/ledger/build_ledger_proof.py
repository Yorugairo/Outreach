"""Synthetic player for the LEDGER PAGE species (P35 T3 proof).

Substitutes the reviewed template with a three-scene timeline: a story-bars
page (trim proof), a dense-line page (the divergence), then a plain plate
with no docks - so the wipe out of a page is exercised. No episode assets:
the plate is a generated PNG, the audio a silent WAV. Output goes to build-f
so the episode-player server (:8731) can serve it. Nothing here is committed.
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

REPO = Path(sys.argv[1])
sys.path.insert(0, str(REPO / "content/video_engine/scripts"))
import ledger_page as LPG  # noqa: E402

EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
OBJ = EP / "evidence/objects"
TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
OUT = EP / "build-f/ledger-species-proof.html"
RUNTIME = 36.0


def png_solid(w: int, h: int, rgb: tuple[int, int, int]) -> bytes:
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def silent_wav(seconds: float) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
        w.writeframes(b"\x00\x00" * int(8000 * seconds))
    return buf.getvalue()


def plate_uri(path: Path) -> str:
    """Opaque plates ship as JPEG q88 in the proof so the hosted copy stays under the 16MB artifact cap."""
    from PIL import Image
    im = Image.open(path).convert("RGB"); buf = io.BytesIO(); im.save(buf, "JPEG", quality=88, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def spec(name: str, variant: str, emphasize: int, quiet_zone: str) -> dict:
    series = LPG.load_series(OBJ / f"{name}.series.json")
    return LPG.build_spec(series, variant, emphasize, quiet_zone)


def main() -> int:
    bars = spec("ev-trim-proof-v1", "bars", 7, "right"); bars["field"] = "soak"
    line = spec("ev-divergence-v1", "line", 0, "right"); line["field"] = "scribble"
    line["focus"] = {"kind": "spotlight", "target": {"kind": "datum", "series": 0, "index": 234, "count": 235}}
    kb = {"scale": 0.04, "x": 0, "y": 0}
    # MOTION MENU species (P35 T6/T7): declared targets only (the targeting law)
    # the HOST at the board (C5, 2026-09-03): until the host-on-board plates land, the host cutout throws in
    # on the page's quiet zone via plate life and points at the board while the focus action fires
    sp1 = [{"kind": "squiggle", "at": 10.2, "dur": 1.6, "target": {"kind": "span", "from_word": 1, "to_word": 2}}]
    bars["focus"] = {"kind": "callout", "label": "the trim"}   # E22 addendum 6: the page's own focus action, on the emphasized datum
    sp2 = [{"kind": "spotlight", "at": 20.0, "dur": 5.0, "glide_at": 2.0, "target": {"kind": "point", "x": 0.30, "y": 0.62}, "target2": {"kind": "point", "x": 0.62, "y": 0.40}}]
    sp3 = [{"kind": "plate_life", "at": 26.5, "dur": 9.0, "cutouts": [{"asset": "cut-coin", "x": 0.30, "y": 0.86, "w": 0.16}, {"asset": "cut-share", "x": 0.68, "y": 0.84, "w": 0.14, "delay": 0.4}]},
           {"kind": "punch", "at": 30.0, "dur": 2.4, "target": {"kind": "point", "x": 0.30, "y": 0.70}}]
    scenes = [
        {"scene_id": "s01", "world": {"kind": "ledger", "page": bars, "ken_burns": kb}, "exit": "wipe_right", "span": [0.0, 12.0], "docks": [], "species": sp1},
        {"scene_id": "s02", "world": {"kind": "ledger", "page": line, "ken_burns": kb}, "exit": "wipe_right", "span": [12.0, 26.0], "docks": [], "species": sp2},
        {"scene_id": "s03", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0.0, "x": 0, "y": 0}}, "exit": "cut", "span": [26.0, RUNTIME], "docks": [], "species": sp3},
    ]
    cut = REPO / "content/video_engine/projects/systems-and-blowups/assets/generated/cutouts"
    cuts = {}
    for key, name in (("cut-coin", "object-coin-stack-v1.png"), ("cut-share", "object-single-share-v1.png"), ("cut-host-point", "actor-host-point-right-v1.png")):
        f = cut / name
        if f.exists():
            # cutouts shrink to 720px wide for the proof (the artifact cap is 16MB; alpha stays, so PNG)
            from PIL import Image
            im = Image.open(f).convert("RGBA"); im.thumbnail((720, 720)); buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
            cuts[key] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    pages = [{"s": 1.0 + 3 * i, "e": 3.8 + 3 * i, "t": [{"w": w, "k": j == 1, "s": 1.0 + 3 * i + 0.4 * j, "e": 1.4 + 3 * i + 0.4 * j} for j, w in enumerate(["the", "ledger", "page", "builds"])]} for i in range(11)]
    timeline = {
        "schema_version": "scene_evidence_timeline.v1", "runtime_s": RUNTIME,
        "title": "Ledger species proof", "subtitle": "P35 T3 synthetic", "episode_id": "proof", "project_id": "proof",
        "narration": {"canonical_hash": "0" * 64, "words_path": ""},
        "captions": [{"at": p["s"], "until": p["e"], "text": " ".join(t["w"] for t in p["t"])} for p in pages],
        "caption_pages": pages, "caption_modes": ["stage", "anchor"], "sound": [], "evidence": {}, "scenes": scenes,
    }
    claim = REPO / "review/claims/steel-and-paper-ledger-page-v1/objects"
    plates = {}
    for pid in ("world-ledger-blank-page-v1", "world-ledger-inked-board-v1"):
        f = claim / f"{pid}.png"
        if f.exists():
            plates[pid] = plate_uri(f)
    if plates:
        # scene 1 takes the two-plate path (generated cream + generated inked board cross-fade); scene 2 keeps the scribble fallback on the generated cream
        # THE DECKLE IS THE FEATURE (operator): the charcoal fills the paper up to its deckle edge, the line traces the deckle
        edge = json.loads(Path(__file__).with_name("deckle-edge.json").read_text(encoding="utf-8"))
        f = claim / "world-ledger-inked-deckle-v1.png"
        plates["world-ledger-inked-deckle-v1"] = plate_uri(f)
        # operator 2026-09-03: the line goes INSIDE the deckle as the clean stabilising edge; compare the white
        # ground (scene 1) with the cream ground (scene 2) where the charcoal reads as fill on a scroll
        for pid in ("world-ledger-blank-page-cream-v1", "world-ledger-inked-deckle-cream-v1"):
            plates[pid] = plate_uri(claim / f"{pid}.png")
        # DECIDED: cream ground; the line is the deckle's innermost boundary - it just touches the cream at the deepest points
        inner = edge["inner"]
        for pg in (bars, line):
            pg["plate"] = "world-ledger-blank-page-cream-v1"; pg["field_plate"] = "world-ledger-inked-deckle-cream-v1"; pg["board"] = inner
        # THE HOST AT THE BOARD (C5 addendum): scene 1 uses the generated pointing pose; the blank state is derived,
        # the board is measured, the host's side is the quiet zone, the punch is skipped (his gesture is the direction)
        hb = json.loads(Path(__file__).with_name("host-boards.json").read_text(encoding="utf-8"))
        hc = REPO / "review/claims/steel-and-paper-host-board-v1/objects"
        pose = "host-board-point-v1"
        for pid, fname in ((pose, f"{pose}.png"), (pose + "-blank", hb[pose]["blank"])):
            plates[pid] = plate_uri(hc / fname)
        bars["plate"] = pose + "-blank"; bars["field_plate"] = pose; bars["board"] = hb[pose]["inner"]
        bars["chart_box"] = hb[pose]["chart_box"]; bars["quiet_zone"] = None; bars["punch"] = False; bars["caption"] = "anchor"   # the host and the stage caption never share the plate
    uris = {
        **plates, **cuts,
        "plate-plain": "data:image/png;base64," + base64.b64encode(png_solid(64, 36, (43, 52, 60))).decode(),
        "__audio__": "data:audio/wav;base64," + base64.b64encode(silent_wav(RUNTIME)).decode(),
    }
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("{{TIMELINE}}", json.dumps(timeline, separators=(",", ":")))
    html = html.replace("{{URIS}}", json.dumps(uris, separators=(",", ":")))
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes); builders: {bars['builder']}, {line['builder']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
