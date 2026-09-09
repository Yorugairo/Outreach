"""Japan tariff trick - the short, built from the take like the Tokyo short (tokyo-tea-break/build_short.py, the template).

One take, one part (`vo-short/audio/scene_1.words.json` is the clock - today the Chirp scratch take, word-timed locally by
align_take_whisper.py; an ElevenLabs master drops in at the same path and every row re-times itself). The shot table is
AUTHORED in `shot_table()` from the words: `ledger:<series>:<variant>:<emphasize>:<quiet_zone>[:mount=<s>|:spiral][:cut]`
places a LEDGER PAGE from `evidence/objects/<series>.series.json`; a plain id is a plate (this story's own stills, generated
2026-09-07 on the bound HollowStickMike - omni-video/stills/, two arms: `still-*` charcoal on cream, `sig-*` the signature
line); `clip:<path>` a clip. Cuts land at 0.8 of the >= 0.30 s gap before the next phrase (M13); mounts and docks land ON a word.

    python build_short.py            # -> build-short/player.html + japan-short.timeline.json + GATES-MOTION.md
    python build_short.py --arm sig  # the signature-line stills instead of the charcoal ones (same rows)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))
TOKYO = HERE.parent / "tokyo-tea-break"

SCRIPT = HERE / "SCRIPT-SHORT-VO.txt"
TAKE = HERE / "vo-short/audio"
BUILD = HERE / "build-short"
STILLS = HERE / "omni-video/stills"
SERIES = ("ev-japan-holdings-v1", "ev-parts-cascade-v1", "ev-tariff-receipt-v1", "ev-japan-selling-v1", "ev-customs-duties-v1")
CUSTOMS_PEAK_IDX, CUSTOMS_LAST_IDX = 43, 45   # 2025 Q4 $364bn/yr, 2026 Q2 (the latest) in ev-customs-duties-v1 (asserted in build)
CUT_AT, MIN_GAP = 0.8, 0.30          # M13
PEAK_IDX, LAST_IDX = 311, 315        # Feb 2026 $1,239.3B, Jun 2026 $1,116.7B in ev-japan-holdings-v1 (asserted in build)
KEYFRAME_EVERY = 12
ARM = sys.argv[sys.argv.index("--arm") + 1] if "--arm" in sys.argv else "still"   # still (charcoal on cream) | sig (the signature line)

# the outro and the brand line are channel assets (the Tokyo build documents both); reused by path, not copied
OUTRO = TOKYO / "outro/outro-v2.mov"                       # 6.2 s, the dark card: "It's not magic. It's mechanics."
BRAND_LINE = HERE.parents[2] / "channel-assets/money-physics/outro/vo/audio/brand-line-paced.mp3"
BRAND_GAP, BRAND_TAIL = 0.7, 1.0
OUTRO_S, OUTRO_LEAD = 6.2, 0.1

# the beds (Tokyo's, sound/SOURCES.md) at the youtube level; the VO is the Chirp take, measured 2026-09-07 (ebur128)
BED_LU = {"youtube": -28.0, "facebook": -26.0}
PLATFORM = "youtube"
VO_LUFS = -21.5
BEDS = {"suno-hook-A.mp3": -13.2, "suno-hook-B.mp3": -13.0, "suno-pivot-A.mp3": -13.0, "suno-pivot-B.mp3": -13.0}
bed_gain = lambda f: round(10 ** ((VO_LUFS + BED_LU[PLATFORM] - BEDS[f]) / 20), 4)

# the ledger page's own clock (mirrored from the player's LP block, as Tokyo mirrors it): the chart LANDS 7.4 s after the
# page's clock starts; a mount replaces the 0.7 s roll and ends where the roll would have (E45)
PAGE_BUILD_END_S, PAGE_BUILD_START_S, PAGE_BUILD_S, LP_ROLL_S = 7.4, 4.4, 3.0, 0.7
SNAP_S = 0.45        # the player's SNAP_S: a landed card grows to the stage in this long (the third watch)
CARD_LEAD_S = 1.0    # a chart card is thrown onto the previous scene this long before its page snaps up from it (the dock's 0.45 s flight + a beat on the ground)

# THE WORLDS - this story's stills (omni-video/stills/<arm>-<id>.png, 768x1376, Nano Banana Pro on HollowStickMike). The
# `-v2` retries replaced a first pass that lost or drifted the character in a busy frame (the operator picks; these are the picks).
PLATE_FILES = {
    "plate-podium": {"still": "still-a-podium-victory", "sig": "sig-a-podium-victory"},     # the victory lap at the podium
    "plate-gates": {"still": "sig-b-crossings-map-v9-operator-edit", "sig": "sig-b-crossings-map-v9-operator-edit"},   # THE CROSSINGS MAP (2026-09-08): Detroit, Ontario across the water, Mexico below the border - the six hops are drawn over it (PLATE-ORDER-MAP-BEAT.md); the six-gates drawing it replaced was a metaphor for information. One frame for both arms: the operator's own edit of the v2 HollowStickMike ground
    "plate-ship": {"still": "still-d-ship-once", "sig": "sig-d-ship-once"},                # the car carrier, one ramp, one stamp (the v2 retry lost the character)
    "plate-vault": {"still": "still-e-vault", "sig": "sig-e-vault"},                       # the Treasury vault, shelves emptying
    "plate-check": {"still": "still-h-blank-check", "sig": "sig-h-blank-check"},           # the blank cheque pushed across the desk
}
DOCK_FILES = {                       # still id per arm, and the card crop (top, height) as fractions of the still - a card the way Tokyo cropped its clips
    "dock-c-two-lanes": ({"still": "still-c-two-lanes-v2", "sig": "sig-c-two-lanes"}, (0.26, 0.44)),      # the two lanes, docked on the archetype
    "dock-a-podium": ({"still": "still-a-podium-victory", "sig": "sig-a-podium-victory"}, (0.14, 0.52)),   # the podium, docked on "Washington signed" (E48 callback)
    "dock-e-vault": ({"still": "still-e-vault", "sig": "sig-e-vault"}, (0.18, 0.52)),                     # the vault, docked on "Tokyo checked the Treasury vault"
}
CLIPS = {
    "dock-f-toll-gate-to-fab": TOKYO / "omni-video/stills/clip-f-toll-gate-to-fab-v2.mp4",   # the open gate, the road to the fab (10.0 s)
}
WORLD_CLIPS = {
    "clip-g-two-fingers-v2.mp4": TOKYO / "omni-video/stills/clip-g-two-fingers-v2.mp4",     # StickMike to camera, two fingers up (10.0 s)
}
DOCK_META = [
    {"asset": "dock-f-toll-gate-to-fab", "title": "The gate to the fab", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-c-two-lanes", "title": "The left lane and the right lane", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-a-podium", "title": "Washington signed a tariff", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-e-vault", "title": "Tokyo checked the vault", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-b-holdings", "title": "Japan is selling America's debt", "source": "US Treasury TIC · Sep 2026", "species": "chart", "badges": []},   # the hook page as a thrown card
    {"asset": "dock-g-receipt", "title": "The tariff bill on a $30,000 car", "source": "DERIVED · USTR + USITC HTS 8708 · Sep 2026", "species": "chart", "badges": []},   # the receipt page as a thrown card
]


def words() -> list[dict]:
    d = json.loads((TAKE / "scene_1.words.json").read_text(encoding="utf-8"))
    return d["words"] if isinstance(d, dict) else d


def phrase_start(ws: list[dict], phrase: str) -> tuple[int, float]:
    norm = lambda s: s.strip(".,:;!?\"'").lower()
    toks = [norm(x) for x in phrase.split()]
    for i in range(len(ws) - len(toks) + 1):
        if [norm(x["w"]) for x in ws[i:i + len(toks)]] == toks:
            return i, ws[i]["start_s"]
    raise SystemExit(f"phrase not in the take: {phrase!r}")


def cut_before(ws: list[dict], phrase: str) -> float:
    i, start = phrase_start(ws, phrase)
    if i == 0:
        return 0.0
    gap = start - ws[i - 1]["end_s"]
    if gap < MIN_GAP:
        raise SystemExit(f"no cut point before {phrase!r}: gap {gap:.2f}s < {MIN_GAP}s (M13)")
    return round(ws[i - 1]["end_s"] + CUT_AT * gap, 2)


def next_sentence_start(ws: list[dict], t: float) -> float | None:
    """The start of the first word of the NEXT sentence after t - the take's own punctuation is the boundary (24 of 247 words
    end in . ? !). E25 (2026-09-08): "the light should unzoom when it says 'Auto parts taxes' - that's the real beginning of the
    scene transition": the chart proves one sentence, so its light releases on the first word of the next one. None = no
    sentence ends after t."""
    seen_end = False
    for w in ws:
        if w["start_s"] < t:
            continue
        if seen_end:
            return round(w["start_s"], 2)
        if w["w"].rstrip()[-1:] in ".?!":
            seen_end = True
    return None


def word_time(ws: list[dict], phrase: str) -> float:
    return phrase_start(ws, phrase)[1]


def write_timeline(ws: list[dict], runtime_s: float) -> dict:
    out_words = [{"w": w["w"], "start": round(w["start_s"], 3), "end": round(w["end_s"], 3), "part": 1} for w in ws]
    sents, cur = [], []
    for w in out_words:
        cur.append(w)
        if w["w"].rstrip("\"”").endswith((".", "!", "?", ":")):
            sents.append({"text": " ".join(x["w"] for x in cur), "start": cur[0]["start"], "end": cur[-1]["end"], "part": 1})
            cur = []
    if cur:
        sents.append({"text": " ".join(x["w"] for x in cur), "start": cur[0]["start"], "end": cur[-1]["end"], "part": 1})
    tl = {"episode": "japan-tariff-trick", "script": SCRIPT.name, "take": "vo-short", "runtime_s": runtime_s,
          "words": out_words, "sentences": sents, "edit_pauses_applied": False}
    (BUILD / "timeline.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")
    return tl


def seekable_clip(name: str, src: Path) -> Path:
    """A keyframe every KEYFRAME_EVERY frames so a seek never decodes from frame 0 (Tokyo, 2026-09-05)."""
    out = BUILD / "clips" / name
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-an", "-c:v", "libx264", "-profile:v", "high", "-crf", "17", "-preset", "slow",
                        "-g", str(KEYFRAME_EVERY), "-keyint_min", str(KEYFRAME_EVERY), "-sc_threshold", "0", "-bf", "0", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(out)], check=True)
    return out


def dock_card(aid: str, src: Path, crop: tuple[float, float]) -> Path:
    """The still cropped to a card the way Tokyo cropped its clips for the still fallback; written once."""
    out = BUILD / "docks" / f"{aid}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        top, h = crop
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", f"crop=iw:ih*{h}:0:ih*{top}", str(out)], check=True)
    return out


def chart_dock_card(aid: str, series: str, variant: str = "line", aspect: str = "9:16") -> str:
    """A CHART CARD (Tokyo R26-19 / the third watch): the series object's ledger page rendered once at its landing by
    scripts/chart_card.py as a PORTRAIT card - the page it will become - and registered as a dock still. The card is THROWN onto
    the previous scene on the dock's stop-action kinetics (the landing with weight Tokyo got right) and the page then enters with
    snap=<this card>: it grows from the landed card's rectangle to the stage (the part Tokyo never did; operator, 2026-09-08)."""
    import build_render_f as R
    import chart_card as CC
    src = HERE / "evidence/objects" / f"{series}.series.json"
    out = BUILD / "docks" / f"{aid}.png"
    if not out.exists() or out.stat().st_mtime < max(src.stat().st_mtime, Path(CC.__file__).stat().st_mtime):
        CC.render_card(src, out, variant, aspect=aspect)
    R.STAMPED[aid] = str(out)
    return aid


def card_aspect(aid: str) -> float:
    """The rendered card's h / w, for a centred placement sized to the card (chart_dock_card must have run) - Tokyo's."""
    from PIL import Image
    w, h = Image.open(BUILD / "docks" / f"{aid}.png").size
    return round(h / w, 4)


def register_assets() -> None:
    """The resolver checks STAMPED first (build_render_f.find_asset): the stills, the dock cards and the dock clips land there by id."""
    import build_render_f as R
    for aid, arms in PLATE_FILES.items():
        p = STILLS / f"{arms[ARM]}.png"
        assert p.exists(), f"missing still {aid}: {p}"
        R.STAMPED[aid] = str(p)
    for aid, (arms, crop) in DOCK_FILES.items():
        p = STILLS / f"{arms[ARM]}.png"
        assert p.exists(), f"missing still {aid}: {p}"
        R.STAMPED[aid] = str(dock_card(aid, p, crop))
    for aid, p in CLIPS.items():
        assert p.exists(), f"missing clip {aid}: {p}"
        R.STAMPED[aid] = str(p)


MAP_PLANTS = {"D": (0.215, 0.425), "O": (0.65, 0.34), "M": (0.455, 0.87)}   # plant chip centres on the crossings map, stage fractions
MAP_ROUTE = "DO OD DM MD DO OD".split()                                        # six crossings; each hop crosses a drawn line


def crossings_species(t0: float, t_truck: float, t_six: float, t_end: float) -> list[dict]:
    """The six hops and six stamps over the crossings map. The first hop leaves as the truck is named and the sixth STAMP
    lands on "six"; the hops between are evenly spaced. Every hop is a held `trace` (hop mode) and every landing a `callout`
    ring with the 25% label, both held to the cut so the picture accumulates into the count (M16: an event every ~0.9 s)."""
    n = len(MAP_ROUTE)
    draw_s = 0.55
    first = round(t_truck - 0.2, 2)
    last_land = round(t_six + 0.05, 2)                       # the sixth stamp ON "six"
    step = (last_land - draw_s - first) / (n - 1)
    out = []
    landed: dict[str, int] = {}
    for i, (a, b) in enumerate(MAP_ROUTE):
        t = round(first + i * step, 2)
        land = round(t + draw_s, 2)
        (x0, y0), (x1, y1) = MAP_PLANTS[a], MAP_PLANTS[b]
        # one bow sign for every hop: the bow is perpendicular to the DIRECTION, so the return already bows to the other side
        # (an alternating sign cancels that and the return retraces the outbound - the first render showed three lines for six)
        out.append({"kind": "trace", "at": t, "dur": round(t_end - t, 2), "color": "#B0201F",
                    "target": {"kind": "region", "x0": min(x0, x1), "y0": min(y0, y1), "x1": max(x0, x1), "y1": max(y0, y1)},
                    "hop": {"from": [x0, y0], "to": [x1, y1], "bow": 0.16, "draw_s": draw_s, "width": 9}})
        # the stamps accumulate like passport stamps: a plant's second and third landings sit offset from the first, so Detroit
        # shows three, Ontario two, Mexico one - six on the page, which IS the count (no counter)
        k = landed.get(b, 0); landed[b] = k + 1
        ddx = -0.05 if b == "D" else 0.055                  # Detroit stacks up-LEFT (clear of its smoke and the outbound arc), the others up-right
        sx, sy = x1 + ddx * k, y1 - 0.045 * k
        out.append({"kind": "callout", "at": land, "dur": round(t_end - land, 2), "label": "25%", "pad": 22, "label_scale": 2.2,
                    "target": {"kind": "point", "x": round(sx, 4), "y": round(sy, 4)}})
    return out


def shot_table(ws: list[dict], runtime_s: float, t_outro: float) -> list[tuple]:
    """The authored rows. E44/E45/E50, the Tokyo v3 grammar: the REAL chart (Japan's Treasury holdings) mounts over the podium
    on the hook line and carries the -$122.6B bracket on "what nobody explained"; the six gates take the frame on "six separate
    times"; the parts page mounts over them on "An engine block" with the two lanes docked on the archetype; the ship carries
    "Toyota crosses once"; the receipt page mounts over it on "the math breaks Detroit"; the vault on "the second lever"; the
    holdings page RETURNS by the spiral with the gate-to-the-fab docked on "pledging"; two fingers for the double squeeze, the
    blank cheque on "we wrote them a blank check"; the ring is the podium, the vault and the page with the bracket standing."""
    at = lambda phrase: round(word_time(ws, phrase), 2)
    cut = lambda phrase: cut_before(ws, phrase)
    datum = lambda i: {"kind": "datum", "index": i}
    hold = f"ledger:ev-japan-holdings-v1:line:{LAST_IDX}:right"
    BRACKET = {"kind": "bracket", "from": PEAK_IDX, "to": LAST_IDX, "label": "−$122.6B", "sub": "Feb to Jun 2026", "color": "neg"}
    # 1-2 the hook and THE PAGE ON THE HOOK (E44): the mount begins on the hook's last word and ends where the roll-out would
    t_mount = at("tariffs")
    t_card = round(max(0.05, t_mount - CARD_LEAD_S), 2)             # the holdings card is thrown onto the podium a second before it snaps up
    t_page = at("Instead")
    mount_hook = round(t_page + LP_ROLL_S - t_mount, 2)
    t_build = round(t_page + PAGE_BUILD_START_S, 2)                 # the line draws to the February peak
    t_land = round(t_page + PAGE_BUILD_END_S, 2)                     # ... and the June stroke follows the landing (no highlight over the charcoal build)
    t_but = at("But look")                                           # the bracket: WHAT NOBODY EXPLAINED is the drop
    # 3 THE CROSSINGS MAP takes the frame on "But look at what nobody explained" and carries "When you buy an American truck, its
    #   parts cross the border six separate times" - six hops drawn plant to plant, a 25% stamp on every landing, the sixth stamp
    #   landing on "six". cut("Auto parts") at 8.88 was the plan (PLATE-ORDER-MAP-BEAT.md) and is not a legal cut: the voice runs
    #   straight from "Toyota." into "Auto parts" with no M13 gap, so the boundary is the next breath, 11.78 (a 6.5 s beat).
    t_gates = cut("But look")
    t_truck = at("When you buy")
    t_six_times = at("six separate times")                          # (t_six is the receipt row's "six thousand dollars", below)
    # 4 the parts page mounts over the gates on "An engine block"; its bars land as the harness sentence ends; the two lanes dock on the archetype
    t_engine = cut("An engine block")
    t_page2 = at("An engine block")
    t_parts_land = round(t_page2 + PAGE_BUILD_END_S + 0.05, 2)
    t_lanes = at("In the left lane")
    t_right = at("In the right")                                     # the title rewrites to the right lane (M16: the page was still here after the dock parked)
    # 5-6 the ship on "Toyota crosses once"; the receipt page mounts over it on "But here's where the math breaks Detroit"
    t_ship = cut("Toyota crosses once")
    t_math = cut("But here's where")
    t_receipt_card = round(t_math - CARD_LEAD_S, 2)                  # the receipt card is thrown onto the ship a second before it snaps up
    t_page3 = at("But here's where")
    t_six = max(at("six thousand dollars"), round(t_page3 + PAGE_BUILD_END_S + 0.05, 2))
    # 7-8 the vault on "the second lever"; the holdings page RETURNS by the spiral on "Instead of reinvesting"
    t_lever = cut("And that's where Tokyo")
    t_return = cut("Instead of reinvesting")
    t_page4 = at("Instead of reinvesting")
    t_sell_land = round(t_page4 + PAGE_BUILD_END_S + 0.05, 2)     # the four bars land under "of Washington's debt"
    t_pledge = at("pledging")
    # 9-10 two fingers on "In finance ... the double squeeze"; the blank cheque on "And then we wrote them a blank check"
    t_finance = cut("In finance")
    t_wrote = cut("And then we wrote")
    # 11-13 the ring: the podium, the vault, the page with the bracket standing
    t_backfire = cut("And this is where")
    t_page5 = at("And this is where")
    t_signed = at("Washington signed")
    t_checked = at("Then Tokyo checked")
    t_used = at("America used the tariff")
    t_customs_build = round(t_page5 + PAGE_BUILD_START_S, 2)
    t_customs_land = round(t_page5 + PAGE_BUILD_END_S + 0.05, 2)
    t_funded = at("while Tokyo funded")
    ken = (0, 0, 0)
    # THE TRANSITION VOCABULARY (E48: declared, not improvised). PRIMARY for a plate-to-plate world change = the DIP through
    # black, the reference's 0.47 s `[DERIVED: measured on all 35]` (E47 s1). A page that ARRIVES BUILT is THROWN onto the world
    # (enter=throw; operator, 2026-09-08: "the transition is literally the plate entering the world" - the row's boundary is a
    # cut, the world stays beneath, the page flies in on the pills' own kinetics and lands with its chart standing): the ACCENT,
    # spent on the two chart arrivals. The MOUNT stays the signature for a page that draws (the cream rises under the outgoing
    # world, then the ink). The HERO is the spiral, unspent here (the holdings page's return is the candidate). The wipe appears
    # nowhere: a `cut` row is a cut since 2026-09-08 (it used to fall through to the wipe, E47 s3).
    return [
        # 1 the hook: the victory lap at the podium - "Trump announced he beat Japan on tariffs"
        (0.0, t_mount, "plate-podium;idle=drift", ken, [
            # THE CARD, THROWN (the third watch, the Tokyo way): the holdings page as a portrait card flies onto the podium on the dock's
            # stop-action throw and lands with weight; the next row's page SNAPS up from where it landed and IS the world
            # it lands CENTRED over the imagery (operator: Tokyo adapted the spot because its dock stayed; here the card lands and
            # zooms fast, so the middle is fine) on the dock's own stop-action throw
            (chart_dock_card("dock-b-holdings", "ev-japan-holdings-v1", "line"), 0, t_card, t_mount, {"arrive": "throw", "mass": "paper", "centre": True, "card_aspect": card_aspect("dock-b-holdings")}),
        ], None, None),
        # 2 THE PAGE ON THE HOOK: Japan's holdings ARRIVE DRAWN over the podium (enter=built, operator 2026-09-08: "chart 1
        #   doesn't actually need a build... we have plenty of builds in the short"). The build was never what starved this
        #   page - the BRACKET was, scheduled at 11.9-13.70 against a cut at 13.73, which also wrote -$122.6B six and a half
        #   seconds after the voice says it. The bracket is cut outright: operator, "a cheap, relatively bad way we use just
        #   to add some motion", and the figure is not lost - the selling page pays it off properly at 0:50. Deployed life
        #   goes 0.03s -> the whole span. exit=cut: the gates dip in.
        (t_mount, t_gates, hold + ":snap=dock-b-holdings:cut" + ";idle=live", ken, [], "cut", [
            # M11: a page that ARRIVES full must be pointed at, or it is homework (E25). The spotlight lands on the June
            # low as the page appears - the divergence IS the mechanism, and pointing at it beats the bracket that used
            # to write the figure six and a half seconds after the voice said it.
            {"kind": "spotlight", "at": round(t_mount + SNAP_S + 0.4, 2), "dur": "hold", "target": datum(LAST_IDX)},   # after the SNAP has finished, never mid-snap
        ]),
        # 3 the crossings map: six hops, six stamps. Plant centres as stage fractions on sig-b-crossings-map-v9 (768x1376 -> 9:16):
        #   Detroit (0.215, 0.425), Ontario (0.65, 0.34) across the water, Mexico (0.455, 0.87) below the border. The route is
        #   D->O, O->D, D->M, M->D, D->O, O->D - every hop crosses a drawn line, and the sixth stamp lands on "six" (the count is
        #   the stamps, no counter). Hops are held to the cut so the picture accumulates; the arcs alternate sides so the
        #   return never retraces the outbound.
        (t_gates, t_engine, "plate-gates;idle=drift", ken, [], "dip", crossings_species(t_gates, t_truck, t_six_times, t_engine)),
        # 4 the parts page mounts over the gates on "An engine block"; the engine bar is spotlit as the bars land, the harness
        #   called out after it (both after the landing - no highlight over the charcoal build); the two lanes DOCK on the
        #   archetype (E45: springs to reading size, then parks in the quiet zone) and leave with the page (E40 #5: exit=cut)
        (t_engine, t_ship, f"ledger:ev-parts-cascade-v1:bars:0:right:mount={round(t_page2 + LP_ROLL_S - t_engine, 2)}:cut" + ";idle=live", ken, [
            ("dock-c-two-lanes", 0, t_lanes, t_ship),
        ], "cut", [
            {"kind": "spotlight", "at": t_parts_land, "dur": "hold", "target": datum(0)},   # holds until the two-lanes card lands (a card arriving is a reason not to)
            # the harness callout is GONE (operator, 2026-09-08: "we don't even need it here. The evidence layer we're throwing in is the
            # better story") - the two-lanes card parks over that bar, and a ring beneath a card is not a circle
            {"kind": "retitle", "at": t_right, "dur": 2.4, "text": "The right lane: Detroit's parts bill"},
        ]),
        # 5 the catalyst: the car carrier at one pier, one stamp - "Toyota crosses once. Tokyo pays a flat fifteen percent"
        (t_ship, t_math, "plate-ship;idle=drift", ken, [
            (chart_dock_card("dock-g-receipt", "ev-tariff-receipt-v1", "bars"), 0, t_receipt_card, t_math, {"arrive": "throw", "mass": "paper", "centre": True, "card_aspect": card_aspect("dock-g-receipt")}),
        ], "dip", None),
        # 6 the receipt page mounts over the ship on "the math breaks Detroit"; Detroit's bar is spotlit as the number is spoken;
        #   the +$1,740 is the page's own badge (B3: the numeral is in the sub behind it)
        (t_math, t_lever, "ledger:ev-tariff-receipt-v1:bars:1:right:snap=dock-g-receipt:cut" + ";idle=live", ken, [], "cut", [
            {"kind": "spotlight", "at": t_six, "dur": "hold", "target": datum(1)},
        ]),
        # 7 the second lever: the vault, shelves emptying (it returns on "Tokyo checked the Treasury vault" - E48, the callback is the thread)
        (t_lever, t_return, "plate-vault;idle=drift", ken, [], "dip", None),
        # 8 THE SECOND LEVER as its own chart: Japan's month-by-month selling (four bars, REAL, TIC table 5) mounts over the vault on
        #   "Instead of reinvesting"; the bars land under "of Washington's debt" and May, the biggest month, is called out; the
        #   gate to the fab docks on "pledging" and leaves with the page (E40 #5: exit=cut). The holdings line stays at the hook only.
        (t_return, t_finance, f"ledger:ev-japan-selling-v1:bars:2:right:mount={round(t_page4 + LP_ROLL_S - t_return, 2)}:cut" + ";idle=live", ken, [
            ("dock-f-toll-gate-to-fab", 0, t_pledge, t_finance),
        ], "cut", [
            {"kind": "spotlight", "at": t_sell_land, "dur": "hold", "target": datum(2)},   # May, the biggest month (a callout ring sat on the pill)
        ]),
        # 9 the reflection: two fingers to camera - "In finance, we call this the double squeeze"
        (t_finance, t_wrote, "clip:" + seekable_clip("clip-g-two-fingers-v2.mp4", WORLD_CLIPS["clip-g-two-fingers-v2.mp4"]).as_posix(), ken, [], "dip", None),
        # 10 the blank cheque pushed across the desk - "And then we wrote them a blank check anyway"
        (t_wrote, t_backfire, "plate-check;idle=drift", ken, [], "dip", None),
        # 11 THE RING on the mechanism, a NEW chart: customs duties - the tariff America paid at its own border - mounts over the
        #   cheque on "And this is where the policy backfired"; the line draws to the latest quarter and lands under "America used
        #   the tariff"; the peak is spotlit on "to tax its own cars" and its figure written on "while Tokyo funded". The two
        #   callbacks ride it as DOCKS: the podium on "Washington signed", the vault on "Then Tokyo checked the Treasury vault".
        (t_backfire, t_outro, f"ledger:ev-customs-duties-v1:line:{CUSTOMS_LAST_IDX}:right:mount={round(t_page5 + LP_ROLL_S - t_backfire, 2)}:cut" + ";idle=live", ken, [
            ("dock-a-podium", 0, t_signed, t_checked),
            ("dock-e-vault", 0, t_checked, t_used),
        ], "cut", [
            {"kind": "build_to", "at": t_customs_build, "dur": PAGE_BUILD_S, "target": datum(CUSTOMS_LAST_IDX)},
            {"kind": "spotlight", "at": max(t_customs_land, at("tax its own cars")), "dur": "hold", "target": datum(CUSTOMS_PEAK_IDX)},
            {"kind": "figure", "at": t_funded, "dur": 1.4, "target": datum(CUSTOMS_PEAK_IDX), "text": "$364bn a year", "sub": "customs duties, late 2025", "color": "neg", "dy": -0.9},
        ]),
        # 12 the outro card, dissolving in over the ring page
        (t_outro, runtime_s, "clip:" + seekable_clip("outro-v2.mp4", OUTRO).as_posix(), ken, [], "dip", [
            {"kind": "life", "at": t_outro, "dur": round(runtime_s - t_outro, 2)},
        ]),
    ]


def main() -> int:
    ws = words()
    BUILD.mkdir(exist_ok=True)
    (BUILD / "audio").mkdir(exist_ok=True)
    shutil.copy2(TAKE / "scene_1.mp3", BUILD / "audio/episode.mp3")
    probe = lambda p: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                           capture_output=True, text=True).stdout or 0)
    t_vo_end = round(probe(BUILD / "audio/episode.mp3"), 3)
    t_outro = round(t_vo_end - OUTRO_LEAD, 3)
    line_s = probe(BRAND_LINE)
    t_line = round(t_vo_end + BRAND_GAP, 3)
    runtime_s = round(max(t_outro + OUTRO_S, t_line + line_s + BRAND_TAIL), 3)
    audio = BUILD / "audio/episode.mp3"
    stitched = audio.with_name("episode-stitched.mp3")
    fc = ("[0:a]aresample=44100,aformat=channel_layouts=mono[a];[1:a]aresample=44100,aformat=channel_layouts=mono[g];"
          "[2:a]aresample=44100,aformat=channel_layouts=mono[l];[a][g][l]concat=n=3:v=0:a=1,apad=whole_dur=" + str(runtime_s) + "[out]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(audio), "-f", "lavfi", "-t", str(BRAND_GAP), "-i", "anullsrc=r=44100:cl=mono", "-i", str(BRAND_LINE),
                    "-filter_complex", fc, "-map", "[out]", "-c:a", "libmp3lame", "-q:a", "2", str(stitched)], check=True)
    stitched.replace(audio)
    write_timeline(ws, runtime_s)
    print(f"  arm {ARM}; take {t_vo_end:.2f}s; brand line {line_s:.2f}s at {t_line:.2f}s; card at {t_outro:.2f}s; runtime {runtime_s:.2f}s")

    (BUILD / "evidence-dock.json").write_text(json.dumps(DOCK_META, indent=1), encoding="utf-8")
    (HERE / "evidence/objects").mkdir(exist_ok=True)
    for s in SERIES:
        shutil.copy2(HERE / "evidence" / f"{s}.series.json", HERE / "evidence/objects" / f"{s}.series.json")
    h = json.loads((HERE / "evidence/objects/ev-japan-holdings-v1.series.json").read_text(encoding="utf-8"))["series"][0]["pts"]
    assert h[PEAK_IDX][1] == 1239.3 and h[LAST_IDX][1] == 1116.7, "the holdings object moved under the shot table"
    c = json.loads((HERE / "evidence/objects/ev-customs-duties-v1.series.json").read_text(encoding="utf-8"))["series"][0]["pts"]
    assert c[CUSTOMS_PEAK_IDX][1] == 364.324 and len(c) == CUSTOMS_LAST_IDX + 1, "the customs object moved under the shot table"
    register_assets()

    import build_caption_pages as CP
    CP.BUILD = BUILD
    CP.CHAR_BUDGET, CP.MAX_WORDS = 28, 6
    CP.main()

    rows = shot_table(ws, runtime_s, t_outro)
    # E25: a held light follows its SENTENCE - every `dur: "hold"` species gets `until` = the first word of the next sentence
    # (from the take's punctuation), unless the row already names one; the compiler takes the earliest of that, the next event
    # on the row, a card arriving, and the cut
    for r in rows:
        for e in (r[6] or []) if len(r) > 6 else []:
            if isinstance(e, dict) and e.get("dur") == "hold" and "until" not in e:
                u = next_sentence_start(ws, float(e["at"]))
                if u is not None:
                    e["until"] = u
    # the sound map (Tokyo's, verbatim): a spiral entry is the warped whoosh at 0.12; mounts are silent; every page exits by cut
    plan_path = HERE / "sound/SOUND-PLAN.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    ACCENT = 0.12
    cues = []
    for i, r in enumerate(rows):
        if r[2].startswith("ledger:") and ":spiral" in r[2]:
            cues.append({"slot": f"page enter {i + 1} (spiral)", "at": round(r[0], 2), "gain": ACCENT, "fade_in": 0.0,
                         "variants": {"A": "fs-whoosh-3-spiral-in.mp3", "B": "fs-whoosh-3-648729.mp3", "C": "fs-swirl-in-478722.mp3"}})
        if r[2].startswith("ledger:") and ":snap=" in r[2]:   # the SNAP's whoosh (operator, 2026-09-08: "fast with a woosh to full size") - the card becomes the world
            cues.append({"slot": f"page enter {i + 1} (snap)", "at": round(r[0], 2), "gain": ACCENT, "fade_in": 0.0,
                         "variants": {"A": "fs-whoosh-3-648729.mp3", "B": "fs-riserhit-754771.mp3", "C": "fs-whoosh-1-706679.mp3"}})
    t_turn = next(r[0] for r in rows if r[2].startswith("plate-vault"))   # the second lever
    cues.append({"slot": "hook bed", "at": 0.0, "gain": bed_gain("suno-hook-B.mp3"), "fade_in": 1.5,
                 "variants": {"A": "suno-hook-B.mp3", "B": "suno-hook-A.mp3"},
                 "note": f"{PLATFORM} {BED_LU[PLATFORM]:+.0f} LU under the VO ({VO_LUFS} LUFS)"})
    cues.append({"slot": "turn bed", "at": round(t_turn, 2), "gain": bed_gain("suno-pivot-A.mp3"), "fade_in": 3.0,
                 "variants": {"A": "suno-pivot-A.mp3", "B": "suno-pivot-B.mp3"},
                 "note": f"{PLATFORM} {BED_LU[PLATFORM]:+.0f} LU under the VO; fades in under the second lever"})
    plan["cues"] = cues
    plan_path.write_text(json.dumps(plan, indent=1), encoding="utf-8")
    (HERE / "SHOT-TABLE-SHORT.py").write_text(
        '"""Japan tariff trick short - AUTHORED shot table, timed from the take by build_short.py. Do not hand-edit; edit build_short.shot_table."""\n'
        f"# arm: {ARM}\n"
        "W = " + repr(rows).replace("), (", "),\n     (") + "\n", encoding="utf-8")
    for r in rows:
        name = r[2].split("/")[-1] if r[2].startswith("clip:") else r[2]
        extra = (f"  docks {[d[0] for d in r[4]]}" if r[4] else "") + (f"  species {[s['kind'] for s in r[6]]}" if r[6] else "")
        print(f"  {r[0]:6.2f}-{r[1]:6.2f}  {name}{extra}")

    import build_render_f as R
    import build_scene_timeline_f as C
    R.EP, R.BUILD = HERE, BUILD
    C.EP, C.BUILD = HERE, BUILD
    C.TIMELINE_NAME = "japan-short.timeline.json"
    C.SHOT_TABLE_FILE = "SHOT-TABLE-SHORT.py"
    C.TITLE, C.SUBTITLE, C.EPISODE_ID = "How Japan Tricked Trump", "Money Physics - short", "japan-tariff-trick"
    C.ASPECT = "9:16"
    C.CAPTION_STYLE = "phrase"
    C.KINETICS = {"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False, "curvature_stroke": True}
    return C.main()


if __name__ == "__main__":
    raise SystemExit(main())
