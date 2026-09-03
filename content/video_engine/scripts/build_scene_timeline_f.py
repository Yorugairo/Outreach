"""Steel and Paper — convert the Script F build into `scene_evidence_timeline.v1`
and render through the established player.

There is already a player: `samples/scene-evidence-player.template.html`.
This script feeds it. It does NOT write a new one — a bespoke player was
built and discarded once already, and it rendered black because it
referenced assets by path instead of embedding them.

The schema encodes things a flat cue list does not: a scene OWNS its world
plate and that plate's Ken Burns move; docks carry a semantic SLOT so
evidence roams while the caption anchor never moves; evidence carries badges
and a source line.

A shot-table plate id of the form ``ledger:<series-id>:<variant>[:<emphasize>
[:<quiet_zone>]]`` is a LEDGER PAGE world (doc 29 s9.26 / s9.28, P35 T4): the
world is DRAWN by the player from ``world.page`` (the ``ledger_page.v1`` spec
built from ``evidence/objects/<series-id>.series.json``), so the scene carries
no ``asset_id`` / ``sha256`` and embeds no plate PNG. The compiled timeline
lists every species present in ``species`` (``["ledger"]`` or ``[]``).
"""
from __future__ import annotations

import base64
import io
import hashlib
import json
import mimetypes
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
BUILD = EP / "build-f"
TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
sys.path.insert(0, str(Path(__file__).parent))
import build_render_f as R  # noqa: E402  (asset resolver + doc-29 durations)
import gate_motion_density as MG  # noqa: E402  (E21 motion gate -> GATES-MOTION.md)
import ledger_page as LPG  # noqa: E402  (series.json -> ledger_page.v1 spec, doc 29 s9.26)

LEDGER_PREFIX = "ledger:"          # shot-table plate id prefix for a LEDGER PAGE world (s9.28 surface = page)
LEDGER_ID_PARTS = (3, 5)           # ledger:<series>:<variant>[:<emphasize>[:<quiet_zone>]]
SPECIES_LEDGER = "ledger"          # timeline["species"] entry; the player keys on world.kind == "ledger"

TIMELINE_NAME = "steel-and-paper.timeline.json"  # the compiled scene_evidence_timeline.v1 the gate reads

# Ken Burns: doc 29 §1.4 — the world plate drifts while evidence holds locked,
# so the eye separates narrative world from evidence data with no labelling.
KEN = {"scale": 0.04, "x": 14, "y": -10}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def parse_ledger_id(plate_id: str) -> tuple[str, str, int | None, str]:
    """``ledger:<series>:<variant>[:<emphasize>[:<quiet_zone>]]`` -> its parts.
    ValueError names the id; the caller names the row."""
    parts = plate_id.split(":")
    lo, hi = LEDGER_ID_PARTS
    if parts[0] != LEDGER_PREFIX[:-1] or not (lo <= len(parts) <= hi) or not parts[1]:
        raise ValueError(f"{plate_id!r}: expected ledger:<series-id>:<variant>[:<emphasize>[:<quiet_zone>]]")
    series_id, variant = parts[1], parts[2]
    if variant not in LPG.VARIANTS:
        raise ValueError(f"{plate_id!r}: variant {variant!r} is not one of {'|'.join(LPG.VARIANTS)}")
    emphasize: int | None = None
    if len(parts) > 3 and parts[3] != "":
        if not parts[3].lstrip("-").isdigit():
            raise ValueError(f"{plate_id!r}: emphasize {parts[3]!r} is not an integer index")
        emphasize = int(parts[3])
    quiet_zone = parts[4] if len(parts) > 4 else "right"
    if quiet_zone not in LPG.QUIET_ZONES:
        raise ValueError(f"{plate_id!r}: quiet_zone {quiet_zone!r} is not one of {'|'.join(LPG.QUIET_ZONES)}")
    return series_id, variant, emphasize, quiet_zone


def ledger_world(plate_id: str, ken: tuple, ep_dir: Path) -> dict:
    """The LEDGER PAGE world for a ``ledger:`` plate id: ``world.page`` is the
    ``ledger_page.v1`` spec from ``<ep_dir>/evidence/objects/<series>.series.json``
    (doc 29 s9.26: data only from a series.json; s9.28: surface x builder are
    two axes). No asset_id / sha256 - the player draws the page."""
    series_id, variant, emphasize, quiet_zone = parse_ledger_id(plate_id)
    path = Path(ep_dir) / "evidence/objects" / f"{series_id}.series.json"
    if not path.exists():
        raise ValueError(f"{plate_id!r}: series file missing: {path}")
    try:
        series = LPG.load_series(path)
    except (OSError, ValueError) as exc:
        raise ValueError(f"{plate_id!r}: cannot read {path}: {exc}") from exc
    errors = LPG.validate(series, variant)
    if errors:
        raise ValueError(f"{plate_id!r}: {path.name} is not a page ({variant}): " + "; ".join(errors))
    page = LPG.build_spec(series, variant, emphasize, quiet_zone)
    return {"kind": SPECIES_LEDGER, "page": page,
            "ken_burns": {"scale": ken[0], "x": ken[1], "y": ken[2]}}


def world_for_plate(plate_id: str, ken: tuple, ep_dir: Path) -> dict:
    """A scene's ``world`` for a shot-table plate id: a ledger page (``ledger:``
    prefix) or an image plate resolved by the asset resolver. Pure apart from
    reading the series / plate file; ValueError on a bad or missing id."""
    if plate_id.startswith(LEDGER_PREFIX):
        return ledger_world(plate_id, ken, ep_dir)
    wp = R.find_asset(plate_id)
    if wp is None:
        raise ValueError(f"{plate_id!r}: no plate asset found")
    return {"asset_id": plate_id, "sha256": sha(wp),
            "ken_burns": {"scale": ken[0], "x": ken[1], "y": ken[2]}}


# Embedding source PNGs verbatim produced a 366 MB player that no browser
# would open. The stage is 1920x1080 and a world plate never draws larger
# than that, so anything beyond it is bytes the viewer cannot see. Evidence
# caps at 1400 (drawn at most 880 wide, so still ~1.6x for crisp text).
STAGE_W, CARD_W, Q = 1920, 1400, 90


def data_uri(p: Path, cap: int | None = None) -> str:
    """Embed an asset, downscaled to what the stage can actually show."""
    if cap is None:
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"
    from PIL import Image
    im = Image.open(p).convert("RGB")
    if im.width > cap:
        im = im.resize((cap, round(im.height * cap / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=Q, optimize=True, progressive=True)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"


def title_for(asset: str) -> tuple[str, str]:
    """Human title and source line for an evidence asset."""
    if asset.startswith("ev-"):
        return asset[3:].replace("-", " ").replace(" v1", "").replace(" v2", "") \
            .replace(" v3", "").title(), "Money Physics — built evidence"
    stamped = json.loads((BUILD / "stamped-index.json").read_text(encoding="utf-8"))
    if asset in stamped:
        deck = asset.split("-s")[0].replace("-", " ").title()
        return asset.replace("-teacher-stamped", "").split("-")[-1].upper(), deck
    return asset.replace("-", " ").title(), "Research deck"


def narration_key_delays(chart: dict, dock_enter: float, tl: dict) -> dict:
    """NARRATION-KEYED DRAW: a delayed series erupts at its claim's word
    time, not at a hard-coded offset (doc 29 - the deferred item; the
    tempo field made every static offset stale by construction)."""
    import re as _re
    norm = lambda x: _re.sub(r"[^a-z0-9' ]", " ", x.lower()).split()
    wt = [(t, w) for w in tl["words"] for t in norm(w["w"])]
    wtoks = [t for t, _ in wt]
    targets = list(chart.get("series", []))         + list(chart.get("checklist", {}).get("rows", []))
    for sr in targets:
        anc = sr.get("delay_anchor")
        if not anc:
            continue
        toks = norm(anc)
        n = len(toks)
        for i in range(len(wtoks) - n + 1):
            if (wtoks[i:i + n - 1] == toks[:-1]
                    and wtoks[i + n - 1].startswith(toks[-1])):
                at = wt[i][1]["start"]
                if at >= dock_enter - 1.0:
                    sr["delay"] = round(max(0.0, at - dock_enter - 0.2), 2)
                    break
    return chart


def main() -> int:
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    # THE AUTHORED SHOT TABLE is the source. Not an allocator.
    import importlib.util
    sp = importlib.util.spec_from_file_location("shot", EP / "SHOT-TABLE-F.py")
    shot = importlib.util.module_from_spec(sp); sp.loader.exec_module(shot)
    plan = sorted(shot.W)
    dock = json.loads((BUILD / "evidence-dock.json").read_text(encoding="utf-8"))
    META = {d["asset"]: d for d in dock}
    pages = json.loads((BUILD / "caption-pages.json").read_text(encoding="utf-8"))
    # the timeline names its own audio: after insert_edit_pauses.py it is
    # the PAUSED file - embedding the unpaused one desyncs every word
    audio = BUILD / tl.get("paused_audio", "audio/episode.mp3")         if tl.get("edit_pauses_applied") else BUILD / "audio/episode.mp3"
    if not audio.exists():
        print(f"FAIL: {audio} missing — join the chained parts first")
        return 1
    print(f"  audio: {audio.name}")

    evidence, uris, scenes = {}, {}, []
    for i, row in enumerate(plan):
        # exit style is HYBRID (operator, 2026-08-29): mechanical default
        # (docks -> wipe, bare -> cut), with an optional authored 6th element
        # per window for boundaries where the MEANING differs - doc 29 Part 6:
        # cut = contrast/correction, wipe = process continuation.
        a, b, plate, ken, ds = row[:5]
        authored_exit = row[5] if len(row) > 5 else None
        # each window runs to the next so the world layer never drops out
        b = plan[i + 1][0] if i + 1 < len(plan) else tl["runtime_s"]
        # a ledger page is drawn, not embedded (doc 29 s9.26); a bad or
        # missing series is a hard build error naming the row
        try:
            world = world_for_plate(plate, ken, EP)
        except ValueError as exc:
            raise SystemExit(f"FAIL: shot row {i + 1} ({a}-{b}s): {exc}") from exc
        if "asset_id" in world:
            uris[plate] = data_uri(R.find_asset(plate), STAGE_W)
        docks = []
        for aid, slot, enter, exitt in ds:
            d = META.get(aid, {"title": aid, "source": "", "species": "deck",
                               "badges": []})
            if True:
                if aid not in evidence:
                    ap = R.find_asset(aid)
                    evidence[aid] = {
                        # Authored in the dock - a machine-mangled asset id is
                        # not a title, and empty badges leave the card's whole
                        # information layer blank (ruling B3: a badge numeral
                        # must appear verbatim in the document behind it).
                        "title": d["title"], "source": d["source"],
                        "species": d["species"],
                        "document": {"path": str(ap.relative_to(ap.anchor)),
                                     "sha256": sha(ap)},
                        "badges": d["badges"],
                        # a record document carries its typed-word payload;
                        # the player renders it as live type + highlighter
                        # instead of a static image (doc 29 record species)
                        **({"record": d["record"]} if "record" in d else {}),
                        # a STACK payload: the verdict pile-up - member
                        # ids resolve against the asset-data map in the
                        # player (every member is docked elsewhere)
                        **({"stack": d["stack"]} if "stack" in d else {}),
                        # a LIVE CHART payload: series emitted by the chart
                        # builder from the same data as the PNG. The player
                        # DRAWS the line; the PNG stays the static fallback.
                        **({"chart": narration_key_delays(json.loads(
                            ap.with_suffix(".series.json").read_text(
                                encoding="utf-8")), enter, tl)}
                           if ap.with_suffix(".series.json").exists() else {}),
                    }
                    # BADGE-CHART SYNC: chart data refetches on rebuild, so
                    # an authored badge value can silently drift from the end
                    # label on the document behind it (caught 2026-08-30:
                    # badges said +601% while a fresh fetch drew +613%). A
                    # badge whose accent maps to a series color takes the
                    # series' CURRENT label - B3 by construction.
                    ch = evidence[aid].get("chart")
                    if ch and ch.get("series"):
                        amap = {"coral": "crimson", "teal": "teal",
                                "cobalt": "cobalt", "ink": "deemph",
                                "sunflower": "amber"}
                        for bd in evidence[aid]["badges"]:
                            sc_col = amap.get(bd.get("accent", ""))
                            for sr in ch["series"]:
                                if sr.get("color") == sc_col and sr.get("label"):
                                    bd["value"] = sr["label"]
                    uris[aid] = data_uri(ap, CARD_W)
                # Spans come from the dock: evidence enters before its claim
                # and holds through the whole discussion. A flat hold drops the
                # document mid-argument, which is what left 42% of claims naked.
                docks.append({
                    "slide": aid, "slot": slot,
                    "enter": round(enter, 2), "exit": round(exitt, 2),
                    "badge_at": [round(enter + 0.75 + 1.3 * (n + 1), 2)
                                 for n in range(len(d["badges"]))],
                })
        scenes.append({
            "scene_id": f"s{i+1:02d}",
            # Ken Burns is AUTHORED per shot in the table, not one constant.
            "world": world,
            "exit": authored_exit or ("wipe_right" if docks else "cut"),
            "span": [round(a, 2), round(b, 2)],
            "docks": docks,
        })

    uris["__audio__"] = data_uri(audio)

    # SOUND REVIEW LAYER (operator, 2026-08-31: "i can't judge the audio
    # without also seeing what actions are happening on the screen") -
    # cues from sound/SOUND-PLAN.json embed as data URIs; the player
    # schedules them on the master clock with live A/B variant toggles.
    sound_cues = []
    sp_path = EP / "sound/SOUND-PLAN.json"
    if sp_path.exists():
        plan = json.loads(sp_path.read_text(encoding="utf-8"))
        for ci, cue in enumerate(plan.get("cues", [])):
            variants = {}
            for vk, fname in cue.get("variants", {}).items():
                fp = EP / "sound" / fname
                if fp.exists():
                    key = f"__snd_{ci}_{vk}__"
                    uris[key] = data_uri(fp)
                    variants[vk] = key
            if variants:
                sound_cues.append({"slot": cue["slot"], "at": cue["at"],
                                   "gain": cue.get("gain", 0.5),
                                   "fade_in": cue.get("fade_in", 0),
                                   "variants": variants})
        print(f"  sound cues  : {len(sound_cues)} embedded from SOUND-PLAN.json")

    timeline = {
        "schema_version": "scene_evidence_timeline.v1",
        "runtime_s": tl["runtime_s"],
        "title": "Steel and Paper",
        "subtitle": "Money Physics · answer to Bravos Research",
        "episode_id": "steel-and-paper", "project_id": "systems-and-blowups",
        "narration": {"canonical_hash": sha(audio),
                      "words_path": "build-f/timeline.json"},
        # Block captions for the template's own layer; the kinetic layer reads
        # caption_pages. Both carry CANONICAL timings — never resampled onto
        # beat boundaries (doc 29 Part 5, and the standing correction).
        "captions": [{"at": p["s"], "until": p["e"],
                      "text": " ".join(t["w"] for t in p["t"])} for p in pages],
        "caption_pages": pages,
        "sound": sound_cues,
        "evidence": evidence,
        "scenes": scenes,
        # every world species present, so downstream (gate, render) can see it
        "species": [SPECIES_LEDGER] if any(s["world"].get("kind") == SPECIES_LEDGER for s in scenes) else [],
    }
    (BUILD / TIMELINE_NAME).write_text(
        json.dumps(timeline, indent=1), encoding="utf-8")

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("{{TIMELINE}}", json.dumps(timeline, separators=(",", ":")))
    html = html.replace("{{URIS}}", json.dumps(uris, separators=(",", ":")))
    out = BUILD / "player.html"
    out.write_text(html, encoding="utf-8")

    dur = float(subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio)], capture_output=True, text=True).stdout or 0)
    print(f"scene_evidence_timeline.v1")
    print(f"  scenes      : {len(scenes)}  (one per world plate)")
    print(f"  species     : {timeline['species'] or 'none'}  "
          f"({sum(1 for s in scenes if s['world'].get('kind') == SPECIES_LEDGER)} ledger pages)")
    print(f"  docks       : {sum(len(s['docks']) for s in scenes)} across "
          f"{sum(1 for s in scenes if s['docks'])} scenes")
    print(f"  evidence    : {len(evidence)} assets")
    print(f"  captions    : {len(timeline['captions'])} lines / "
          f"{sum(len(p['t']) for p in pages)} tokens")
    print(f"  audio       : {dur:.2f}s embedded as __audio__")
    print(f"  URIs        : {len(uris)} embedded, {out.stat().st_size/1e6:.0f} MB player")
    print(f"  wrote {out}")

    # THE PLATE CADENCE, measured. Two pieces per plate with two badges each,
    # or one big piece - never a pair padded out to make a count. This reports
    # against the pattern; it does not author it.
    thin = [(s["span"][0], round(s["span"][1] - s["span"][0], 1),
             len({d["slide"] for d in s["docks"]}))
            for s in scenes if s["span"][1] - s["span"][0] >= 12.0]
    off = [x for x in thin if x[2] == 1]
    nb = [a for a, e in evidence.items() if not e["badges"]]
    per = [len({d["slide"] for d in s["docks"]}) for s in scenes]
    print("")
    print(f"  CADENCE  {per.count(2)} plates carry a pair, "
          f"{per.count(1)} carry one, {per.count(0)} carry none")
    if off:
        print(f"  [WARN] {len(off)} plates hold >=12s on a single piece - pair "
              f"them or let the solo card go wide:")
        for a, d, _ in off[:6]:
            print(f"           {int(a//60)}:{int(a%60):02d}  {d}s")
    if nb:
        print(f"  [WARN] {len(nb)} evidence cards carry no badges - their whole "
              f"information layer is blank: {', '.join(nb[:4])}"
              f"{' ...' if len(nb) > 4 else ''}")
    motion_gate_report()
    return 0


def motion_gate_report() -> int:
    """E21 / doc 29 s9.25: every compiled timeline gets the motion-density
    gate run on it and the verdict written to build-f/GATES-MOTION.md. The
    build still completes on FAIL - the shot table is authored against the
    report - and render_episode.py refuses a full render while it says FAIL."""
    path, n_fail = MG.write_report(BUILD, TIMELINE_NAME)
    print("")
    print(f"  motion gate : {path}")
    if n_fail:
        print(f"MOTION GATE: {n_fail} FAIL - see {MG.REPORT_NAME}")
    else:
        print("MOTION GATE: PASS")
    return n_fail


if __name__ == "__main__":
    raise SystemExit(main())
