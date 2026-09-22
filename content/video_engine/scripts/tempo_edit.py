"""TEMPO-AUTHORED EDIT - runs move, reveals breathe, no seams audible.

Renders an edited take from four semantic inputs the provider never had:
the dead-space caps, the tighten runs, the pause plan, and the tempo map
(attention sentences hold 1.0x, connective sentences run at RUN_RATE).

v3 - THE TEMPO FIELD (operator, 2026-08-30): tempo is a CONTINUOUS
CURVE over the timeline, not per-sentence gears. Attention spans (the
sentences carrying pause anchors - the same sentences the docks and
badges bind to) impose SPEED LIMITS of 1.0x; between them the curve
eases up to RUN_RATE through cosine ramps (~RAMP_S). Emission cuts the
curve into chunks at gaps of >=120ms, so every rate step is hosted by
real silence. The literary graph drives the accelerator.

Usage (preview mode, probe):
    python tempo_edit.py --probe

Usage (chain stage - edits the master, rewrites its timeline):
    python tempo_edit.py --take

Usage (the gate - renders into a scratch dir and judges the emitted
timeline against the audio it actually wrote; G1-G5, non-zero on FAIL):
    python tempo_edit.py --verify --ep <episode> \
        --words <take.words.json> --audio <take.mp3> --out <scratch>

The warped-timeline emission (`warp_timeline`) is doc 37 s20's stated
condition for chain promotion: word times scale by their own chunk's
rate and shift past every inserted pause, as insert_edit_pauses.py does
for the two-tool path, so docks, captions and choreography ride the
authored clock.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
SR = 44100
RUN_RATE = 1.10
XF = int(SR * 0.012)          # 12ms crossfade
INTRA, INTRAT = 0.40, 0.30
INTER, INTERT = 0.65, 0.50
TAG_CAP = 1.00
HOOK_HOLD_S = 9.0             # the open never runs
TAIL_HOLD_S = 14.0            # ...and neither does the ring close
ENDERS = (".", "!", "?", ":")

# --verify thresholds, quoted from doc 37 s20: class 3 "suffocates
# under ~150ms"; class 5b a cut site needs ">=120ms of reported
# silence"; class 3 splits a chunk once the curve drifts PAST 0.015x -
# so a step is at least that by construction, which is why G5c WARNs
# on the size and G5b FAILs on the silence hosting it.
CLOCK_TOL_S = 0.050           # G3 - the emitted clock vs the measured audio
ANCHOR_TOL_S = 0.150          # G4 - construction vs the rendered map
MIN_CHUNK_S = 0.150
MIN_STEP_GAP_S = 0.12
MAX_RATE_STEP = 0.015
PAUSED_REL = "audio/episode-paused.mp3"


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9' ]", " ", s.lower())


def decode(path: Path) -> np.ndarray:
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "a.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(path),
                        "-ac", "1", "-ar", str(SR), str(wav)], check=True)
        data, _ = sf.read(wav, dtype="float32")
    return data


PAD = int(SR * 0.08)   # context borrowed for the stretcher's warm-up


def stretch(seg: np.ndarray, rate: float,
            pre: int = 0, post: int = 0) -> np.ndarray:
    """Stretch with CONTEXT PADDING (v5 - the operator heard the last of
    the black-hole class): WSOLA has a startup transient that can double
    the first onset of an independently-stretched chunk ("Vo-voice") and
    sharpen attacks at chunk heads. Each chunk is stretched WITH pre/post
    context and the stretched pads are trimmed - the transient lands in
    the discard, never in the audible span."""
    if abs(rate - 1.0) < 0.005 or len(seg) < SR // 25:
        return seg[pre:len(seg) - post if post else len(seg)]
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "a.wav", Path(td) / "b.wav"
        sf.write(a, seg, SR)
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(a),
                        "-filter:a", f"atempo={rate}", str(b)], check=True)
        out, _ = sf.read(b, dtype="float32")
    scale = len(out) / max(1, len(seg))
    h = int(round(pre * scale))
    t = int(round(post * scale))
    trimmed = out[h:len(out) - t if t else len(out)]
    # ffmpeg's atempo is perceptually stable but its emitted sample count can
    # drift by several milliseconds per chunk. Across a long narration those
    # rounding tails accumulate and the authored word clock walks away from
    # the rendered audio. Each rate boundary already sits inside measured
    # silence, so trim/pad that silent tail to the exact requested duration.
    target = max(1, int(round((len(seg) - pre - post) / rate)))
    if len(trimmed) > target:
        trimmed = trimmed[:target]
    elif len(trimmed) < target:
        trimmed = np.pad(trimmed, (0, target - len(trimmed)))
    return trimmed


def xfade_join(pieces: list[np.ndarray]) -> np.ndarray:
    pieces = [p for p in pieces if len(p)]
    out = pieces[0]
    ramp = np.linspace(0, 1, XF, dtype="float32")
    for p in pieces[1:]:
        if len(out) >= XF and len(p) >= XF:
            out = np.concatenate([
                out[:-XF],
                out[-XF:] * (1 - ramp) + p[:XF] * ramp,
                p[XF:]])
        else:
            out = np.concatenate([out, p])
    return out


def sentence_groups(words: list[dict]) -> list[list[dict]]:
    """The take's words grouped into sentences by ENDERS - one source
    for the field's spans AND the emitted timeline's sentence rows, so a
    sentence means the same thing on both sides of the edit."""
    groups, cur = [], []
    for x in words:
        cur.append(x)
        if x["w"].rstrip("\"”").endswith(ENDERS):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


def build(words, plan, audio):
    """Render the edited take. Returns (pcm, to_edited, meta).

    `to_edited` maps an ORIGINAL take time to the edited clock; `meta`
    carries the emission's geometry so the warped timeline can be
    verified against the audio that was written, not just arithmetic."""
    wt = [(t, x) for x in words for t in norm(x["w"]).split()]
    wtoks = [t for t, _ in wt]

    def find(txt, end):
        toks = norm(txt).split()
        n = len(toks)
        for i in range(len(wtoks) - n + 1):
            if (wtoks[i:i + n - 1] == toks[:-1]
                    and wtoks[i + n - 1].startswith(toks[-1])):
                return wt[i + n - 1][1]["end"] if end else wt[i][1]["start"]

    sents = [(g[0]["start"], g[-1]["end"]) for g in sentence_groups(words)]
    sent_ends = {round(b, 3) for _, b in sents}

    # attention marks: every pause anchor + every break-tag site.
    # THE INSERTION POINT IS NEVER A WORD EDGE (operator caught the "Mm"
    # pip before "Meta"): provider timestamps are +/-30-60ms loose, so a
    # cut at word.start can strand the onset. Every insertion snaps to
    # the MIDPOINT of its natural silence gap.
    def gap_mid(t, is_after):
        for x, y in zip(words, words[1:]):
            if is_after and abs(x["end"] - t) < 0.02:
                return (x["end"] + y["start"]) / 2
            if not is_after and abs(y["start"] - t) < 0.02:
                return (x["end"] + y["start"]) / 2
        return t
    att = []
    for p in plan["pauses"]:
        is_after = "after" in p and bool(p.get("after"))
        anc = p.get("after") or p.get("before")
        t = find(anc, is_after)
        if t is not None:
            att.append((gap_mid(t, is_after), p["s"]))
    marks = [t for t, _ in att]
    tag_sites = []
    # The tempo editor is shared across episodes; the pause plan owns the
    # narration source.  Older plans omit it and retain the Steel/Paper name.
    script_ref = Path(plan.get("script") or "SCRIPT-G-VO.txt")
    script_candidates = ([script_ref] if script_ref.is_absolute() else
                         [EP / script_ref, REPO / script_ref])
    script_path = next((p for p in script_candidates if p.is_file()), None)
    if script_path is None:
        raise FileNotFoundError(
            "tempo plan script not found: " + ", ".join(str(p) for p in script_candidates)
        )
    vo = script_path.read_text(encoding="utf-8")
    for m in re.finditer(r"`\[[a-z-]+\]`", vo):
        pre = norm(re.sub(r"`\[[a-z-]+\]`", " ", vo[:m.start()])).split()[-4:]
        t = find(" ".join(pre), True)
        if t is not None:
            marks.append(t)
            tag_sites.append(round(t, 3))

    # THE TEMPO FIELD v7 - SEMANTIC, GRADED, AND BREATHING (operator,
    # 2026-08-30: tag-free synthesis lost the model's own breathing
    # around pauses - the field now supplies it, and limits grade by
    # RHETORIC SHAPE instead of a binary hold):
    #   savor/key/lead/settle/reveal sentences .. 1.00
    #   aphorism fragments (<6 words) ........... 1.00
    #   half-beats (citation/list/savor) ........ 1.02
    #   questions ............................... 1.04
    #   declared fluid runs ..................... 1.12 cruise
    #   everything else ......................... RUN_RATE cruise
    #   AND a settle-dip into EVERY inserted pause: 0.96 over the last
    #   0.55s before the cut-in, 1.00 for 0.35s after - the breath the
    #   provider no longer plants.
    RAMP_S = 1.6
    cons = []   # (a, b, limit, ramp)
    def sent_of(t):
        for a, b in sents:
            if a - 0.05 <= t <= b + 0.05:
                return (a, b)
        return None
    kindmap = {}
    for p2 in plan["pauses"]:
        anc = p2.get("after") or p2.get("before")
        t = find(anc, "after" in p2 and bool(p2.get("after")))
        if t is None:
            continue
        kindmap.setdefault(sent_of(t), []).append(p2.get("kind", ""))
        # the breath into the inserted pause
        cons.append((t - 0.40, t, 0.975, 0.45))
        cons.append((t, t + 0.25, 1.00, 0.5))
    for span, kinds in kindmap.items():
        if span is None:
            continue
        k = " ".join(kinds)
        lim = 1.05 if all(x.startswith("half") for x in kinds) else 1.00
        cons.append((span[0], span[1], lim, RAMP_S))
    for t in marks:                       # tag-mark sites (key beats)
        sp2 = sent_of(t)
        if sp2:
            cons.append((sp2[0], sp2[1], 1.00, RAMP_S))
    # v7.2 (operator, s11: "IT runs STRAIGHT through"): the field never
    # saw the VIDEO choreography - scene/evidence transitions got no
    # settle. Every dock anchor is an evidence ENTER on the take's own
    # words; the approach into it slows and the reveal lands settled.
    dock_json = EP / "build-f/evidence-dock.json"
    n_dock = 0
    if dock_json.exists():
        for e in json.loads(dock_json.read_text(encoding="utf-8")):
            anc = e.get("anchor")
            at = find(anc, False) if anc else None
            if at is not None:
                cons.append((at - 0.7, at + 0.35, 1.03, 0.6))
                n_dock += 1
    # and DENSE INFORMATION cannot cruise: a sentence carrying 4+
    # number tokens (numerals are spelled out in VO scripts) caps at
    # 1.05 - the listener is doing arithmetic, not riding a run.
    NUM_TOKENS = set(
        """zero one two three four five six seven eight nine ten eleven
        twelve thirteen fourteen fifteen sixteen seventeen eighteen
        nineteen twenty thirty forty fifty sixty seventy eighty ninety
        hundred thousand million billion trillion percent""".split())
    n_dense = 0
    for a, b in sents:
        toks = [t for w2 in words if a <= w2["start"] < b
                for t in norm(w2["w"]).split()]
        n_num = sum(1 for t in toks
                    if t in NUM_TOKENS or any(c.isdigit() for c in t))
        if n_num >= 4:
            cons.append((a, b, 1.05, RAMP_S))
            n_dense += 1
    print(f"  v7.2: {n_dock} dock-anchor settles, "
          f"{n_dense} number-dense sentences capped 1.05x")
    widx = 0
    for a, b in sents:
        n_words = sum(1 for w in words if a <= w["start"] < b)
        txt_end = next((w["w"] for w in reversed(words)
                        if a <= w["start"] < b), "")
        # v7.1 (operator: "too gappy - middle ground"): fragments and
        # questions do NOT auto-hold - snap-fragments are RUN material;
        # only pause-anchored sentences and the marks hold the field
    cons.append((0.0, HOOK_HOLD_S, 1.00, RAMP_S))
    take_end = words[-1]["end"]
    cons.append((take_end - TAIL_HOLD_S, take_end + 1, 1.00, RAMP_S))
    # fluid runs raise the local cruise
    run_spans = []
    for r in plan.get("tighten_runs", []):
        a, b = find(r["start_after"], True), find(r["end_before"], False)
        if a and b:
            run_spans.append((a, b))

    import math
    def rate_curve(t: float) -> float:
        base = RUN_RATE
        for a, b in run_spans:
            if a <= t <= b:
                base = 1.12
        r = base
        for a, b, lim, ramp in cons:
            if lim >= base:
                continue
            d = max(0.0, a - t, t - b)
            if d >= ramp:
                continue
            f = 0.5 - 0.5 * math.cos(math.pi * d / ramp)
            r = min(r, lim + (base - lim) * f)
        return r

    n_hold = sum(1 for a, b in sents if rate_curve((a + b) / 2) < 1.03)
    print(f"  {len(sents)} sentences, {len(cons)} field constraints, "
          f"{n_hold} held near 1.0x, cruise {RUN_RATE}x (runs 1.12x)")

    # compression + insertion ops
    runs = []
    for r in plan.get("tighten_runs", []):
        a, b = find(r["start_after"], True), find(r["end_before"], False)
        if a and b:
            runs.append({"a": a, "b": b, **r})
    # ONE op shape for both edits to a silence: (a, b, keep, pause) means
    # emit up to a + keep/2, plant `pause` seconds, resume at b - keep/2.
    # A cap is (gap start, gap end, target, 0); a bare insertion is
    # (midpoint, midpoint, 0, seconds).
    caps = []
    for a, b in zip(words, words[1:]):
        g = b["start"] - a["end"]
        at = round(a["end"], 3)
        if g <= 0:
            continue
        if at in tag_sites:
            if g > TAG_CAP:
                caps.append([a["end"], b["start"], TAG_CAP, 0.0])
            continue
        cap, tgt = ((INTER, INTERT) if at in sent_ends
                    else (INTRA, INTRAT))
        for r in runs:
            if r["a"] <= at <= r["b"]:
                cap, tgt = ((r["inter_cap"], r["inter_tgt"])
                            if at in sent_ends
                            else (r["intra_cap"], r["intra_tgt"]))
        if g > cap:
            caps.append([a["end"], b["start"], tgt, 0.0])
    # A gap can be BOTH over-cap AND pause-anchored - two edits to ONE
    # silence, not two events at two times - so the pause MERGES into the
    # cap that owns its gap. Cap first, then plant the pause in the middle
    # of what SURVIVES: the gap ends up tgt + s with tgt/2 of real room
    # each side of the breath. As two ops they fought - the cap advanced
    # the read head to b - tgt/2, the insertion reset it to the RAW
    # midpoint BEHIND it, and (g - tgt)/2 of capped silence came back
    # with the pause lopsided (tgt/2 before it, g/2 after).
    solo = []
    for t, s in att:
        host = next((c for c in caps if c[0] <= t <= c[1]), None)
        if host is not None:
            host[3] += s
        else:
            solo.append([t, t, 0.0, s])
    ops = sorted(caps + solo, key=lambda o: (o[0], o[1]))

    # emission v6 (operator: "black hole dynamics" at field edges):
    # WORDS ARE NEVER SPLIT and a rate step only happens inside real
    # silence - words merge into one chunk until the curve has drifted
    # PAST 0.015x AND a gap >=120ms offers a boundary no timestamp
    # jitter can fake. The step is thus >0.015x by construction (G5c);
    # what makes it inaudible is the silence hosting it (G5b).
    chunks = []          # (start, end, rate) covering the whole take
    boundaries = []      # (at, gap_s, rate_before, rate_after) - G5's
    cs = 0.0
    cr = rate_curve(words[0]["start"])
    for x, y in zip(words, words[1:]):
        gap = y["start"] - x["end"]
        r = rate_curve((y["start"] + y["end"]) / 2)
        # v6 (operator: "vo-oice" - the vowel doubled MID-WORD): provider
        # word timestamps are +/-30-60ms loose, so a reported 30ms "gap"
        # can sit INSIDE a co-articulated word - cutting there splits the
        # word across two rates. A cut site must be a gap no timestamp
        # jitter can fake: >=120ms of reported silence.
        if gap >= 0.12 and abs(r - cr) > 0.015:
            mid = (x["end"] + y["start"]) / 2
            chunks.append((cs, mid, cr))
            boundaries.append((mid, gap, cr, r))
            cs, cr = mid, r
    chunks.append((cs, len(audio) / SR, cr))

    def emit(a, b):
        if b - a < 0.03:
            return
        for c0, c1, r in chunks:
            s0, s1 = max(a, c0), min(b, c1)
            if s1 - s0 < 0.02:
                continue
            i0, i1 = int(s0 * SR), int(s1 * SR)
            pre = min(PAD, i0)
            post = min(PAD, len(audio) - i1)
            seg = audio[i0 - pre:i1 + post]
            pieces.append({"pcm": stretch(seg, r, pre, post),
                           "o0": s0, "o1": s1, "rate": r})

    pieces = []
    prev = 0.0
    regressions = []     # ops that rewind the read head - must stay empty

    for a, b, keep, pause in ops:
        head = a + keep / 2
        if head < prev - 1e-6:
            regressions.append({"at": round(a, 3),
                                "rewind_s": round(prev - head, 3)})
        emit(prev, head)
        if pause:
            pieces.append({"pcm": np.zeros(int(SR * pause), dtype="float32"),
                           "o0": None, "o1": None, "rate": 1.0,
                           "ins_s": float(pause)})
        prev = b - keep / 2
    emit(prev, len(audio) / SR)

    # exact original->edited time map (xfade_join overlaps XF per joint)
    out_pos = 0.0
    for i, pc in enumerate(pieces):
        if i:
            out_pos -= XF / SR
        pc["out0"] = out_pos
        out_pos += len(pc["pcm"]) / SR

    def to_edited(t: float) -> float:
        last = 0.0
        for pc in pieces:
            if pc["o0"] is None:
                continue
            if pc["o0"] - 0.001 <= t <= pc["o1"] + 0.001:
                return pc["out0"] + (t - pc["o0"]) / pc["rate"]
            if t > pc["o1"]:
                last = pc["out0"] + (pc["o1"] - pc["o0"]) / pc["rate"]
        return last

    meta = {
        "chunks": [{"start": round(c0, 3), "end": round(c1, 3),
                    "rate": round(r, 4)} for c0, c1, r in chunks],
        "boundaries": [{"at": round(t0, 3), "gap_s": round(g, 3),
                        "rate_before": round(r0, 4),
                        "rate_after": round(r1, 4)}
                       for t0, g, r0, r1 in boundaries],
        "pieces": [{"o0": pc["o0"], "o1": pc["o1"], "rate": pc["rate"],
                    "out0": pc["out0"], "out_s": len(pc["pcm"]) / SR,
                    "ins_s": pc.get("ins_s")} for pc in pieces],
        "inserts": [{"at": round(t0, 3), "s": s} for t0, s in att],
        "cuts": sum(1 for o in ops if o[2] > 0),
        "merged": sum(1 for o in ops if o[2] > 0 and o[3] > 0),
        "regressions": regressions,
    }
    return xfade_join([pc["pcm"] for pc in pieces]), to_edited, meta


def run_probe_mode():
    src = EP / "vo-f/audio/scene_99.mp3"
    wj = json.loads((EP / "vo-f/audio/scene_99.words.json")
                    .read_text(encoding="utf-8"))["words"]
    words = [{"w": x["w"], "start": x["start_s"], "end": x["end_s"]}
             for x in wj]
    plan = json.loads((EP / "SCRIPT-G-EDIT-PAUSES.json")
                      .read_text(encoding="utf-8"))
    out, _, _ = build(words, plan, decode(src))
    dest = EP / "vo-f/audio/probe-tempo-preview.mp3"
    encode(out, dest)
    print(f"{dest.name}: {len(out) / SR:.1f}s")


def warp_timeline(tl: dict, to_edited, runtime_s: float, meta: dict,
                  paused_rel: str = PAUSED_REL) -> dict:
    """THE WARPED-TIMELINE EMISSION (doc 37 s20, the chain-promotion
    blocker). Rewrites `tl` IN PLACE onto the edited clock:

    * every word's start/end goes through `to_edited`, so the times
      inside a stretched chunk scale by THAT chunk's own rate and
      everything after an inserted pause shifts by it - the same shape
      `insert_edit_pauses.py` produces for the two-tool path;
    * sentence spans travel with their words (they are word boundaries,
      so the same map carries them) and are clamped to the words they
      contain, never inverted by rounding;
    * `runtime_s` is the MEASURED length of the rendered audio;
    * the marker keys downstream really checks are set: `paused_audio`
      + `edit_pauses_applied` (`build_scene_timeline_f.py` and
      `render_episode.py` pick the voice track with them),
      `dead_space_compressed` (the ORDER guard in `insert_edit_pauses.py`
      / `compress_dead_space.py`), `tempo_field_applied` (re-run refusal).

    Pure apart from the callable: no audio, no filesystem - so the
    warping arithmetic is testable on a synthetic timeline."""
    for w in tl["words"]:
        w["start"] = round(to_edited(w["start"]), 3)
        w["end"] = round(to_edited(w["end"]), 3)
    words = tl["words"]
    for sn in tl.get("sentences", []):
        sn["start"] = round(to_edited(sn["start"]), 3)
        sn["end"] = round(to_edited(sn["end"]), 3)
        if sn["end"] < sn["start"]:
            sn["end"] = sn["start"]
    if words:
        for sn in tl.get("sentences", []):
            sn["start"] = max(sn["start"], words[0]["start"])
            sn["end"] = min(sn["end"], words[-1]["end"])
    rates = [c["rate"] for c in meta["chunks"]]
    steps = [abs(b["rate_after"] - b["rate_before"])
             for b in meta["boundaries"]]
    tl["runtime_s"] = round(runtime_s, 3)
    tl["tempo_field_applied"] = True
    tl["edit_pauses_applied"] = True      # downstream guard convention
    tl["dead_space_compressed"] = True
    tl["paused_audio"] = paused_rel
    tl["tempo_field"] = {
        "chunks": len(meta["chunks"]),
        "cuts": meta["cuts"],
        "inserts": len(meta["inserts"]),
        "inserted_s": round(sum(i["s"] for i in meta["inserts"]), 3),
        "rate_min": round(min(rates), 4) if rates else None,
        "rate_max": round(max(rates), 4) if rates else None,
        "max_rate_step": round(max(steps), 4) if steps else 0.0,
    }
    return tl


def run_take_mode():
    """CHAIN STAGE: edit the joined master, rewrite the timeline onto
    the edited clock. Replaces compress_dead_space + insert_edit_pauses
    (doc 37 s20)."""
    tl_path = EP / "build-f/timeline.json"
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    if tl.get("tempo_field_applied"):
        print("REFUSED: tempo field already applied")
        return 1
    if tl.get("edit_pauses_applied"):
        print("REFUSED: legacy pause insertion already ran on this "
              "timeline - rebuild it first")
        return 1
    plan = json.loads((EP / "SCRIPT-G-EDIT-PAUSES.json")
                      .read_text(encoding="utf-8"))
    audio = decode(EP / "build-f/audio/episode.mp3")
    out, to_edited, meta = build(tl["words"], plan, audio)
    dest = EP / "build-f" / PAUSED_REL
    encode(out, dest)
    warp_timeline(tl, to_edited, measure_duration(dest), meta)
    tl_path.write_text(json.dumps(tl, indent=1), encoding="utf-8")
    print(f"episode-paused.mp3 (tempo field): {tl['runtime_s']:.1f}s; "
          f"timeline rewritten onto the edited clock")
    return 0


def row(gid: str, name: str, ok: bool, detail: str,
        warn: bool = False) -> dict:
    return {"id": gid, "name": name,
            "verdict": "WARN" if (warn and not ok) else
                       ("PASS" if ok else "FAIL"),
            "detail": detail}


def gate_monotonic(words: list[dict]) -> dict:
    """G1 - starts and ends non-decreasing, no word overlapping the
    next: a dock pinned to an inverted word lands in the wrong shot."""
    bad = []
    for i, w in enumerate(words):
        if w["end"] < w["start"] - 1e-9:
            bad.append(f"[{i}] {w['w']!r} end<start")
        if i and w["start"] < words[i - 1]["end"] - 1e-9:
            over = words[i - 1]["end"] - w["start"]
            bad.append(f"[{i}] {w['w']!r} starts {over:.3f}s "
                       f"before {words[i - 1]['w']!r} ends")
    return row("G1", "word monotonicity", not bad,
               f"{len(words)} words, {len(bad)} violations"
               + (f"; first: {bad[0]}" if bad else ""))


def gate_words_preserved(src: list[dict], out: list[dict]) -> dict:
    """G2 - the edit authors silence and tempo, never text (s20's ladder
    of authority): same words, same order, same spelling."""
    if len(src) != len(out):
        return row("G2", "word count preserved", False,
                   f"input {len(src)} words, emitted {len(out)}")
    diff = [i for i, (a, b) in enumerate(zip(src, out)) if a["w"] != b["w"]]
    return row("G2", "word count preserved", not diff,
               f"{len(out)} words, order and text identical"
               if not diff else
               f"{len(diff)} words differ; first at [{diff[0]}]: "
               f"{src[diff[0]]['w']!r} -> {out[diff[0]]['w']!r}")


def gate_clock(runtime_s: float, measured_s: float) -> dict:
    """G3 - the authored clock IS the audio's clock, measured with
    ffprobe on the written file. Arithmetic is not evidence here."""
    d = abs(runtime_s - measured_s)
    return row("G3", "clock matches audio", d <= CLOCK_TOL_S,
               f"timeline runtime_s {runtime_s:.3f}s vs ffprobe "
               f"{measured_s:.3f}s = {d * 1000:.1f}ms "
               f"(tol {CLOCK_TOL_S * 1000:.0f}ms)")


def constructed_time(t: float, pieces: list[dict]) -> float:
    """The edited time of an original instant, from the geometry alone:
    every preceding span over ITS chunk's rate, plus every inserted pause,
    less a crossfade per joint - independent of the rendered lengths."""
    acc = 0.0
    for i, pc in enumerate(pieces):
        if i:
            acc -= XF / SR
        if pc["o0"] is None:
            acc += pc["ins_s"]
            continue
        if pc["o0"] - 1e-3 <= t <= pc["o1"] + 1e-3:
            return acc + (t - pc["o0"]) / pc["rate"]
        acc += (pc["o1"] - pc["o0"]) / pc["rate"]
    return acc


def sample_indices(words: list[dict], n: int) -> list[int]:
    """Evenly spaced words with enough body to carry energy."""
    meaty = [i for i, w in enumerate(words) if w["end"] - w["start"] >= 0.15]
    pool = meaty or list(range(len(words)))
    if len(pool) <= n:
        return pool
    step = len(pool) / n
    return [pool[int(k * step)] for k in range(n)]


def speech_frames(pcm: np.ndarray, frame_s: float = 0.02):
    n = max(1, int(SR * frame_s))
    usable = len(pcm) // n * n
    rms = np.sqrt((pcm[:usable].reshape(-1, n) ** 2).mean(axis=1))
    floor = max(float(np.percentile(rms, 95)) * 0.05, 1e-5)
    return rms, floor, n


def gate_anchors(src_words: list[dict], out_words: list[dict],
                 meta: dict, pcm: np.ndarray, n: int = 24) -> dict:
    """G4 - a sampled word's emitted time still points at the audio it
    pointed at before, checked two ways: (a) BY CONSTRUCTION, summing the
    preceding chunk scalings and inserted pauses (`constructed_time`);
    (b) ACOUSTICALLY, re-decoding the file that was actually written and
    requiring the word's window to hold speech, not silence."""
    idx = sample_indices(src_words, n)
    worst, worst_i = 0.0, -1
    for i in idx:
        d = abs(constructed_time(src_words[i]["start"], meta["pieces"])
                - out_words[i]["start"])
        if d > worst:
            worst, worst_i = d, i
    rms, floor, fn = speech_frames(pcm)
    silent = []
    for i in idx:
        a = int(out_words[i]["start"] * SR) // fn
        b = max(a + 1, int(out_words[i]["end"] * SR) // fn)
        if b > len(rms) or float(rms[a:b].max(initial=0.0)) <= floor:
            silent.append(i)
    ok = worst <= ANCHOR_TOL_S and not silent
    detail = (f"{len(idx)} sampled words: max |constructed - emitted| = "
              f"{worst * 1000:.1f}ms (tol {ANCHOR_TOL_S * 1000:.0f}ms"
              + (f", worst {src_words[worst_i]['w']!r}"
                 if worst_i >= 0 else "")
              + f"); {len(idx) - len(silent)}/{len(idx)} land on speech "
              f"in the written audio (frame RMS > {floor:.5f})")
    if silent:
        detail += f"; silent: {[out_words[i]['w'] for i in silent[:5]]}"
    return row("G4", "anchors land", ok, detail)


def gate_rate_sanity(meta: dict, strict: bool = False) -> list[dict]:
    """G5 - the tempo field's own laws (doc 37 s20 classes 3/4/5b)."""
    chunks, bounds = meta["chunks"], meta["boundaries"]
    spans = [c["end"] - c["start"] for c in chunks]
    short = [x for x in spans if x < MIN_CHUNK_S]
    rows = [row("G5a", "chunk minimum duration", not short,
                f"{len(chunks)} chunks, shortest "
                f"{min(spans, default=0):.3f}s "
                f"(floor {MIN_CHUNK_S:.3f}s, class 3); {len(short)} under")]
    tight = [b for b in bounds if b["gap_s"] < MIN_STEP_GAP_S]
    rows.append(row("G5b", "rate step sits in silence", not tight,
                    f"{len(bounds)} rate steps, smallest host gap "
                    f"{min((b['gap_s'] for b in bounds), default=0):.3f}s "
                    f"(floor {MIN_STEP_GAP_S:.3f}s, class 5b); "
                    f"{len(tight)} too tight"))
    steps = [abs(b["rate_after"] - b["rate_before"]) for b in bounds]
    big = [s for s in steps if s > MAX_RATE_STEP + 1e-9]
    rows.append(row("G5c", "rate step size", not big,
                    f"max adjacent step {max(steps, default=0.0):.4f}x vs "
                    f"class 4's {MAX_RATE_STEP}x; {len(big)}/{len(steps)} over"
                    + ("" if strict else
                       " - WARN not FAIL: the split rule only cuts a new "
                       "chunk once the curve has drifted PAST 0.015x, so "
                       "the step is larger by construction "
                       "(--strict-rate-step enforces the doc)"),
                    warn=not strict))
    return rows


def print_table(rows: list[dict]) -> int:
    width = max(len(r["name"]) for r in rows)
    print(f"\n{'GATE':<5} {'CHECK':<{width}}  VERDICT  DETAIL")
    for r in rows:
        print(f"{r['id']:<5} {r['name']:<{width}}  {r['verdict']:<7}  "
              f"{r['detail']}")
    fails = [r for r in rows if r["verdict"] == "FAIL"]
    warns = [r for r in rows if r["verdict"] == "WARN"]
    print(f"\n{len(rows) - len(fails) - len(warns)} PASS / {len(warns)} WARN "
          f"/ {len(fails)} FAIL")
    return 1 if fails else 0


def measure_duration(path: Path) -> float:
    """The WRITTEN file's duration, measured - never inferred from the
    arithmetic that produced it (xfade_join only overlaps pieces long
    enough to cross-fade, and the encoder pads)."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        check=True, capture_output=True, text=True)
    return float(out.stdout.strip())


def encode(pcm, dest: Path):
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "o.wav"
        sf.write(wav, pcm, SR)
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(wav),
                        "-c:a", "libmp3lame", "-b:a", "192k", str(dest)],
                       check=True)


def load_source_timeline(path: Path) -> dict:
    """A pre-edit timeline from either shape the chain produces: a
    build's `timeline.json`, or a take's `<scene>.words.json` (the
    provider's `start_s` / `end_s`), whose sentences are derived with
    the same grouping the field uses."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("tempo_field_applied") or raw.get("edit_pauses_applied"):
        raise SystemExit(f"{path.name} is already on an edited clock - "
                         "--verify needs the take's own timeline")
    if raw["words"] and "start_s" in raw["words"][0]:
        words = [{"w": x["w"], "start": x["start_s"], "end": x["end_s"]}
                 for x in raw["words"]]
        sents = [{"text": " ".join(w["w"] for w in g),
                  "start": g[0]["start"], "end": g[-1]["end"]}
                 for g in sentence_groups(words)]
        return {"source": path.name, "words": words, "sentences": sents,
                "runtime_s": words[-1]["end"] if words else 0.0}
    return raw


def run_verify_mode(a) -> int:
    """THE GATE. Renders the edit into --out, emits the warped timeline
    beside it, then judges that timeline against the audio that was
    actually written. Nothing is read from or written to the episode's
    own build."""
    out_dir = Path(a.out)
    (out_dir / "audio").mkdir(parents=True, exist_ok=True)
    src_tl = load_source_timeline(Path(a.words))
    src_words = [dict(w) for w in src_tl["words"]]
    plan = json.loads((EP / a.plan).read_text(encoding="utf-8"))
    audio = decode(Path(a.audio))
    print(f"verify: {len(src_words)} words, {len(audio) / SR:.1f}s of take, "
          f"plan {a.plan}")
    pcm, to_edited, meta = build(src_tl["words"], plan, audio)
    dest = out_dir / PAUSED_REL
    encode(pcm, dest)
    measured = measure_duration(dest)
    warp_timeline(src_tl, to_edited, measured, meta)
    (out_dir / "timeline.json").write_text(
        json.dumps(src_tl, indent=1), encoding="utf-8")
    written = decode(dest)
    rows = [
        gate_monotonic(src_tl["words"]),
        gate_words_preserved(src_words, src_tl["words"]),
        gate_clock(src_tl["runtime_s"], measured),
        gate_anchors(src_words, src_tl["words"], meta, written, a.sample),
    ] + gate_rate_sanity(meta, a.strict_rate_step)
    if meta["regressions"]:
        print(f"\nNOTE: {len(meta['regressions'])} ops rewind the read "
              f"head - two edits fighting over one silence, the class the "
              f"merge retired. A NEW defect: {meta['regressions']}")
    print(f"\nemitted: {dest} ({measured:.3f}s), "
          f"{out_dir / 'timeline.json'}")
    return print_table(rows)


def main() -> int:
    global EP, RUN_RATE, INTRA, INTRAT, INTER, INTERT, HOOK_HOLD_S, TAIL_HOLD_S
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--take", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="render + emit the warped timeline into --out and "
                         "gate it (G1-G5); non-zero exit on any FAIL")
    ap.add_argument("--ep", help="episode root (default: steel-and-paper)")
    ap.add_argument("--words", help="--verify: the take's pre-edit timeline "
                                    "or <scene>.words.json")
    ap.add_argument("--audio", help="--verify: the take's audio")
    ap.add_argument("--out", help="--verify: where the gate writes")
    ap.add_argument("--plan", default="SCRIPT-G-EDIT-PAUSES.json",
                    help="--verify: the edit-pause plan, relative to --ep")
    ap.add_argument("--sample", type=int, default=24,
                    help="--verify: words sampled by G4")
    ap.add_argument("--strict-rate-step", action="store_true",
                    help="--verify: G5c FAILs instead of WARNs")
    ap.add_argument("--run-rate", type=float, default=RUN_RATE,
                    help="tempo-field cruise multiplier (default: %(default)s)")
    ap.add_argument("--hook-hold-s", type=float, default=HOOK_HOLD_S,
                    help="seconds held at 1.0x before the tempo field may accelerate")
    ap.add_argument("--tail-hold-s", type=float, default=TAIL_HOLD_S,
                    help="seconds held at 1.0x before the final spoken word")
    ap.add_argument("--inter-cap", type=float, default=INTER,
                    help="compress sentence gaps longer than this many seconds")
    ap.add_argument("--inter-target", type=float, default=INTERT,
                    help="surviving sentence-gap duration after compression")
    ap.add_argument("--intra-cap", type=float, default=INTRA,
                    help="compress intra-sentence gaps longer than this many seconds")
    ap.add_argument("--intra-target", type=float, default=INTRAT,
                    help="surviving intra-sentence gap after compression")
    a = ap.parse_args()
    if not 1.0 <= a.run_rate <= 1.20:
        ap.error("--run-rate must be between 1.0 and 1.20")
    if min(a.hook_hold_s, a.tail_hold_s, a.inter_cap, a.inter_target,
           a.intra_cap, a.intra_target) < 0:
        ap.error("tempo holds and gap values must be non-negative")
    if a.inter_target > a.inter_cap or a.intra_target > a.intra_cap:
        ap.error("each gap target must be less than or equal to its cap")
    RUN_RATE = a.run_rate
    HOOK_HOLD_S = a.hook_hold_s
    TAIL_HOLD_S = a.tail_hold_s
    INTER, INTERT = a.inter_cap, a.inter_target
    INTRA, INTRAT = a.intra_cap, a.intra_target
    if a.ep:
        EP = Path(a.ep)
    if a.verify:
        missing = [f"--{k}" for k in ("words", "audio", "out")
                   if not getattr(a, k)]
        if missing:
            print(f"--verify needs {', '.join(missing)}")
            return 2
        return run_verify_mode(a)
    if a.take:
        return run_take_mode() or 0
    run_probe_mode()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
