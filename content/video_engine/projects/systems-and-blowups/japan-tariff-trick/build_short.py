"""Japan tariff trick - the short, built from the take like the other short (both now write through
`scripts/authoring/`, the kit P51 T0 pulled out of the two copies).

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
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))
SIBLING = HERE.parent / "tokyo-tea-break"   # the channel assets the other short documents: the outro card, the host's clips

from authoring import Project                                             # noqa: E402
from authoring import audio as A, docks as D, table as T, words as W      # noqa: E402

SCRIPT = HERE / "SCRIPT-SHORT-VO.txt"
TAKE = HERE / "vo-short/audio"
BUILD = HERE / os.environ.get("TARIFF_BUILD_DIR", "build-short")   # P49 T5: a cut under review builds beside the approved one (TARIFF_BUILD_DIR=build-short-p49 -> :8741), never over it
CHART_ARRIVAL = os.environ.get("TARIFF_CHART_ARRIVAL", "snap")   # snap (approved, 2026-09-09) | camera (P49 T5, opt-in until HG2: the eye goes to the card)
STILLS = HERE / "omni-video/stills"
SERIES = ("ev-japan-holdings-v1", "ev-parts-cascade-v1", "ev-tariff-receipt-v1", "ev-japan-selling-v1", "ev-customs-duties-v1")
CUSTOMS_PEAK_IDX, CUSTOMS_LAST_IDX = 43, 45   # 2025 Q4 $364bn/yr, 2026 Q2 (the latest) in ev-customs-duties-v1 (asserted in build)
PEAK_IDX, LAST_IDX = 311, 315        # Feb 2026 $1,239.3B, Jun 2026 $1,116.7B in ev-japan-holdings-v1 (asserted in build)
ARM = sys.argv[sys.argv.index("--arm") + 1] if "--arm" in sys.argv else "sig"   # THE APPROVED ARM is the default (2026-09-10: another lane's plain rebuild produced the charcoal `still` arm and the watched player served it)
TAKE_STEM = sys.argv[sys.argv.index("--take") + 1] if "--take" in sys.argv else "scene_1-tight"   # THE APPROVED CLOCK (operator, 2026-09-09: "tight sounds right, approved, render it") - the Chirp take with doc 37 s14's dead space killed (retime_take.py scene_1.mp3 --gaps --out scene_1-tight, 79.18 s); --take <stem> builds another candidate   # still (charcoal on cream) | sig (the signature line)
EP = Project(here=HERE, build=BUILD, take=TAKE, take_stem=TAKE_STEM, script_name=SCRIPT.name, episode_id="japan-tariff-trick")

# the outro and the brand line are channel assets (the other short's build documents both); reused by path, not copied
OUTRO = SIBLING / "outro/outro-v2.mov"                     # 6.2 s, the dark card: "It's not magic. It's mechanics."
BRAND_LINE = HERE.parents[2] / "channel-assets/money-physics/outro/vo/audio/brand-line-paced.mp3"
BRAND_GAP, BRAND_TAIL = 0.7, 1.0
OUTRO_S, OUTRO_LEAD = 6.2, 0.1

# the beds (the channel's, sound/SOURCES.md) at the youtube level; the VO is the Chirp take, measured 2026-09-07 (ebur128)
BED_LU = {"youtube": -20.0, "facebook": -20.0}   # a SHORT sits at -20 (operator, 2026-09-08, second pass on the strip: "i like it at +6db" against the -26 plan; "sub-threshold is basically useless, we want to be just above sub-threshold... competitors play music even louder"); -28 is the long-form calibration (Steel and Paper, the research blueprint)
BED_SWELL_DB = 4.0   # the bed BREATHES with the structure (the blueprint, rule 3: it rises under scene transitions): +4 dB from a card's throw through its snap - the operator heard the landing "sound much better" with the bed up; the rest of the bed stays at BED_LU
PLATFORM = "youtube"
VO_LUFS = -21.5
BEDS = {"suno-hook-A.mp3": -13.2, "suno-hook-B.mp3": -13.0, "suno-pivot-A.mp3": -13.0, "suno-pivot-B.mp3": -13.0}
bed_gain = lambda f: A.bed_gain(VO_LUFS, BED_LU[PLATFORM], BEDS[f])

# the ledger page's own clock (mirrored from the player's LP block, as the other short mirrors it): the chart LANDS 7.4 s after
# the page's clock starts; a mount replaces the 0.7 s roll and ends where the roll would have (E45)
PAGE_BUILD_END_S, PAGE_BUILD_START_S, PAGE_BUILD_S, LP_ROLL_S = 7.4, 4.4, 3.0, 0.7
# the pledge card's box on the portrait stage, MEASURED against the Japan-selling page's ink (2026-09-09, stage px): the subtitle
# ends at y 413, the source line sits at 1077-1108 and the badge at 1159-1301 from x 76 - so the card's box spans x 76-846, y 430-1120:
# it covers the proved plot and the source line whole (no peeking fragments) and leaves the -$122.6B badge and the caption clear
PLEDGE_CY, PLEDGE_CX, PLEDGE_CW = 0.4021, 0.4407, 0.7407   # box x 76-876, y 428-1116 (crop 0.48 of the still): covers every label of the plot (the -$26.4 tag ends at x 872), the frame and shadow stop short of the badge at 1159
PLEDGE_WAFER = (0.645, 0.477)   # the wafer's centre as a fraction of the fab card (measured: the warm disc's centroid in the crop)
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
DOCK_FILES = {                       # still id per arm, and the card crop (top, height) as fractions of the still - a card the way the other short cropped its clips
    "dock-c-two-lanes": ({"still": "still-c-two-lanes-v2", "sig": "sig-c-two-lanes"}, (0.26, 0.44)),      # the two lanes, docked on the archetype
    "dock-a-podium": ({"still": "still-a-podium-victory", "sig": "sig-a-podium-victory"}, (0.14, 0.52)),   # the podium, docked on "Washington signed" (E48 callback)
    "dock-e-vault": ({"still": "still-e-vault", "sig": "sig-e-vault"}, (0.18, 0.52)),                     # the vault, docked on "Tokyo checked the Treasury vault"
    # the PLEDGE dock (operator, 2026-09-09: the other short's toll-gate clip "was already weak because it was supposed to be a toll
    # gate, without the manufacturing plant it's just useless") - the operator's own Flow images: the fab (Mike at the wafer chamber,
    # the E39 atom) by default; DOCK_H=trap swaps in the $122B-trap panel (the vault emptying into the wafer, the package composition)
    "dock-h-pledge": ({"still": "sig-i-fab-wafer", "sig": "sig-i-fab-wafer"}, (0.19, 0.48)) if os.environ.get("DOCK_H", "fab") == "fab"
                     else ({"still": "sig-j-vault-to-chips", "sig": "sig-j-vault-to-chips"}, (0.152, 0.55)),
}
CLIPS = {
}
WORLD_CLIPS = {
    "clip-g-two-fingers-v2.mp4": SIBLING / "omni-video/stills/clip-g-two-fingers-v2.mp4",     # StickMike to camera, two fingers up (10.0 s)
}
DOCK_META = [
    {"asset": "dock-h-pledge", "title": "Ten trillion yen for chips", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-c-two-lanes", "title": "The left lane and the right lane", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-a-podium", "title": "Washington signed a tariff", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-e-vault", "title": "Tokyo checked the vault", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-b-holdings", "title": "Japan is selling America's debt", "source": "US Treasury TIC · Sep 2026", "species": "chart", "badges": []},   # the hook page as a thrown card
    {"asset": "dock-g-receipt", "title": "The tariff bill on a $30,000 car", "source": "DERIVED · USTR + USITC HTS 8708 · Sep 2026", "species": "chart", "badges": []},   # the receipt page as a thrown card
]


def chart_dock_card(aid: str, series: str, variant: str = "line", aspect: str = "9:16") -> str:
    """A CHART CARD (R26-19 / the third watch): the series object's ledger page rendered once at its landing as a PORTRAIT
    card - the page it will become. The card is THROWN onto the previous scene on the dock's stop-action kinetics and the
    page then enters with snap=<this card>: it grows from the landed card's rectangle to the stage (operator, 2026-09-08)."""
    return D.chart_card(aid, HERE / "evidence/objects" / f"{series}.series.json", BUILD, variant, aspect)


def card_aspect(aid: str) -> float:
    """The rendered card's h / w, for a centred placement sized to the card (chart_dock_card must have run)."""
    return D.card_aspect(aid, BUILD)


def still_card_aspect(aid: str) -> float:
    """h / w of a DOCK_FILES still's card crop, from the still's own size (before the card has been cut)."""
    arms, crop = DOCK_FILES[aid]
    return D.still_card_aspect(STILLS / f"{arms[ARM]}.png", crop)


def register_assets() -> None:
    """The resolver checks STAMPED first (build_render_f.find_asset): the stills, the dock cards and the dock clips land there by id."""
    for aid, arms in PLATE_FILES.items():
        p = STILLS / f"{arms[ARM]}.png"
        assert p.exists(), f"missing still {aid}: {p}"
        D.register(aid, p)
    for aid, (arms, crop) in DOCK_FILES.items():
        p = STILLS / f"{arms[ARM]}.png"
        assert p.exists(), f"missing still {aid}: {p}"
        D.register(aid, D.still_card(aid, p, crop, BUILD))
    for aid, p in CLIPS.items():
        assert p.exists(), f"missing clip {aid}: {p}"
        D.register(aid, p)


MAP_PLANTS = {"D": (0.215, 0.425), "O": (0.65, 0.34), "M": (0.455, 0.87)}   # plant chip centres on the crossings map, stage fractions
MAP_ROUTE = "DO OD DM MD DO OD".split()                                        # six crossings; each hop crosses a drawn line


def crossings_species(t0: float, t_truck: float, t_six: float, t_end: float) -> list[dict]:
    """The six hops and six stamps over the crossings map. The first hop leaves as the truck is named and the sixth STAMP
    lands on "six"; the hops between are evenly spaced. Every hop is a held `trace` (hop mode) and every landing a `callout`
    ring with the 25% label, both held to the cut so the picture accumulates into the count (M16: an event every ~0.9 s)."""
    n = len(MAP_ROUTE)
    draw_s = 0.55
    first = round(t_truck - 0.2, 2)                          # t_truck is now "compounded" (9.98): six hops from 9.8 to the sixth stamp on "six" (16.79)
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
    """The authored rows. E44/E45/E50, the v3 grammar: the REAL chart (Japan's Treasury holdings) mounts over the podium
    on the hook line and carries the -$122.6B bracket on "what nobody explained"; the six gates take the frame on "six separate
    times"; the parts page mounts over them on "An engine block" with the two lanes docked on the archetype; the ship carries
    "Toyota crosses once"; the receipt page mounts over it on "the math breaks Detroit"; the vault on "the second lever"; the
    holdings page RETURNS by the spiral with the gate-to-the-fab docked on "pledging"; two fingers for the double squeeze, the
    blank cheque on "we wrote them a blank check"; the ring is the podium, the vault and the page with the bracket standing."""
    at = lambda phrase: W.at(ws, phrase)
    cut = lambda phrase: W.cut_before(ws, phrase, rule="gap")   # P52 T11 PIN: the approved cut keeps M13's 0.8-of-the-gap placement;
                                                                #   TR-13's onset rule is words.py's default for every later build
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
    # 2026-09-08, the first watch: "by our own logic the cut should come after 'dollars' - there's a big empty gap where we're
    # lingering on the chart when we should transition". E25: the chart proves one sentence and leaves. cut_before("Auto parts")
    # refuses because Whisper stretched "dollars." to 8.88 and swallowed the ~1 s of silence; the boundary is the ONSET of "Auto"
    # (E47 / TR-2: the reference's dips are centred on the next word's onset), so the light fades out into the dip and the map
    # arrives on its own sentence, "Auto parts taxes compounded against Detroit"
    t_gates = at("Auto parts")
    t_compound = at("compounded")                                     # the hops ARE the compounding: the first one leaves here
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
            # THE CARD, THROWN (the third watch, the other short's way): the holdings page as a portrait card flies onto the podium on
            # the dock's stop-action throw and lands with weight; the next row's page SNAPS up from where it landed and IS the world
            # it lands CENTRED over the imagery (operator: the other cut adapted the spot because its dock stayed; here the card lands
            # and zooms fast, so the middle is fine) on the dock's own stop-action throw
            (chart_dock_card("dock-b-holdings", "ev-japan-holdings-v1", "line"), 0, t_card, t_mount, {"arrive": "throw", "mass": "paper", "centre": True, "card_aspect": card_aspect("dock-b-holdings")}),
        ], None, None),
        # 2 THE PAGE ON THE HOOK: Japan's holdings ARRIVE DRAWN over the podium (enter=built, operator 2026-09-08: "chart 1
        #   doesn't actually need a build... we have plenty of builds in the short"). The build was never what starved this
        #   page - the BRACKET was, scheduled at 11.9-13.70 against a cut at 13.73, which also wrote -$122.6B six and a half
        #   seconds after the voice says it. The bracket is cut outright: operator, "a cheap, relatively bad way we use just
        #   to add some motion", and the figure is not lost - the selling page pays it off properly at 0:50. Deployed life
        #   goes 0.03s -> the whole span. exit=cut: the gates dip in.
        (t_mount, t_gates, hold + f":{CHART_ARRIVAL}=dock-b-holdings:cut" + ";idle=live", ken, [], "cut", [
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
        (t_gates, t_engine, "plate-gates;idle=drift", ken, [], "dip", crossings_species(t_gates, t_compound, t_six_times, t_engine)),
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
        (t_math, t_lever, f"ledger:ev-tariff-receipt-v1:bars:1:right:{CHART_ARRIVAL}=dock-g-receipt:cut" + ";idle=live", ken, [], "cut", [
            {"kind": "spotlight", "at": t_six, "dur": "hold", "target": datum(1)},
        ]),
        # 7 the second lever: the vault, shelves emptying (it returns on "Tokyo checked the Treasury vault" - E48, the callback is the thread)
        (t_lever, t_return, "plate-vault;idle=drift", ken, [], "dip", None),
        # 8 THE SECOND LEVER as its own chart: Japan's month-by-month selling (four bars, REAL, TIC table 5) mounts over the vault on
        #   "Instead of reinvesting"; the bars land under "of Washington's debt" and May, the biggest month, is called out; the
        #   the pledge dock (the fab) lands on "pledging" and leaves with the page (E40 #5: exit=cut). The holdings line stays at the hook only.
        (t_return, t_finance, f"ledger:ev-japan-selling-v1:bars:2:right:mount={round(t_page4 + LP_ROLL_S - t_return, 2)}:cut" + ";idle=live", ken, [
            # the pledge card sits CENTRED over the proved chart from its first frame (the park spot at the top-right sat on the
            # chart's title and the April label); the light lands on the wafer at "semiconductors" - the sentence's object, and
            # the visual event M16 asks for inside the card's 3.3 s
            ("dock-h-pledge", 0, t_pledge, t_finance, {"centre": True, "card_aspect": still_card_aspect("dock-h-pledge"), "centre_y": PLEDGE_CY, "centre_x": PLEDGE_CX, "centre_w": PLEDGE_CW}),
        ], "cut", [
            {"kind": "spotlight", "at": t_sell_land, "dur": "hold", "target": datum(2)},   # May, the biggest month (a callout ring sat on the pill)
            # the LIGHT on the wafer (E56, operator 2026-09-09: "drawing the ring on the wafer is dumb ... give it a light shimmer or a
            # spotlight"): the focus light lands on the wafer at "semiconductors", holds to the cut, and breathes (idle live)
            {"kind": "spotlight", "at": at("semiconductors"), "dur": "hold", "idle": "live",
             "target": D.centred_card_point(still_card_aspect("dock-h-pledge"), PLEDGE_CY, *PLEDGE_WAFER, centre_w=PLEDGE_CW, centre_x=PLEDGE_CX)},
        ]),
        # 9 the reflection: two fingers to camera - "In finance, we call this the double squeeze"
        (t_finance, t_wrote, "clip:" + D.seekable_clip("clip-g-two-fingers-v2.mp4", WORLD_CLIPS["clip-g-two-fingers-v2.mp4"], BUILD).as_posix(), ken, [], "dip", None),
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
        (t_outro, runtime_s, "clip:" + D.seekable_clip("outro-v2.mp4", OUTRO, BUILD).as_posix(), ken, [], "dip", [
            {"kind": "life", "at": t_outro, "dur": round(runtime_s - t_outro, 2)},
        ]),
    ]


# the sound map (the other short's, verbatim): a spiral entry is the warped whoosh at 0.12; mounts are silent; every page exits by cut
ACCENT = 0.12
SPIRAL_IN = {"A": "fs-whoosh-3-spiral-in.mp3", "B": "fs-whoosh-3-648729.mp3", "C": "fs-swirl-in-478722.mp3"}
SNAP_IN = {"A": "fs-whoosh-3-648729.mp3", "B": "fs-riserhit-754771.mp3", "C": "fs-whoosh-1-706679.mp3"}   # the SNAP's (or the camera arrival's) whoosh (operator, 2026-09-08: "fast with a woosh to full size") - the card becomes the world
TURN_PLATE = "plate-vault"   # the second lever: the turn bed fades in under it


def sound_cues(rows: list[tuple]) -> list[dict]:
    """This episode's cue map over the kit's transition and arrival readings."""
    cues: list[dict] = []
    for i, r in enumerate(rows):
        page = A.page_transitions(r[2])
        if page["ledger"] and page["spiral"]:
            cues.append({"slot": f"page enter {i + 1} (spiral)", "at": round(r[0], 2), "gain": ACCENT, "fade_in": 0.0,
                         "variants": dict(SPIRAL_IN)})
        if page["ledger"] and (page["snap"] or page["camera"]):
            cues.append({"slot": f"page enter {i + 1} (snap)", "at": round(r[0], 2), "gain": ACCENT, "fade_in": 0.0,
                         "variants": dict(SNAP_IN)})
    t_turn = next(r[0] for r in rows if r[2].startswith(TURN_PLATE))
    # the bed's ENVELOPE, in dB against its own gain, keyed to every thrown card: up over the 0.3 s before the throw, held
    # through the landing and the snap, down over 0.8 s after the page is the world (a pure function of t in the player)
    env = A.bed_envelope(rows, BED_SWELL_DB, SNAP_S, fallback_end=lambda d: float(d[3]) + SNAP_S)
    cues.append({"slot": "hook bed", "at": 0.0, "gain": bed_gain("suno-hook-B.mp3"), "fade_in": 1.5, "env": env,
                 "variants": {"A": "suno-hook-B.mp3", "B": "suno-hook-A.mp3"},
                 "note": f"{PLATFORM} {BED_LU[PLATFORM]:+.0f} LU under the VO ({VO_LUFS} LUFS)"})
    cues.append({"slot": "turn bed", "at": round(t_turn, 2), "gain": bed_gain("suno-pivot-A.mp3"), "fade_in": 3.0,
                 "variants": {"A": "suno-pivot-A.mp3", "B": "suno-pivot-B.mp3"},
                 "note": f"{PLATFORM} {BED_LU[PLATFORM]:+.0f} LU under the VO; fades in under the second lever"})
    return cues


def main() -> int:
    ws = W.take_words(EP)
    EP.mkdirs()
    shutil.copy2(TAKE / f"{TAKE_STEM}.mp3", EP.audio_master)
    t_vo_end = round(A.probe_duration(EP.audio_master), 3)
    line_s = A.probe_duration(BRAND_LINE)
    t_outro, t_line, runtime_s = A.outro_clock(t_vo_end, line_s, outro_lead=OUTRO_LEAD, outro_s=OUTRO_S, brand_gap=BRAND_GAP, brand_tail=BRAND_TAIL)
    A.stitch_brand_line(EP.audio_master, BRAND_LINE, BRAND_GAP, runtime_s)
    W.write_timeline(EP, ws, runtime_s)
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

    T.caption_pages(BUILD, char_budget=28, max_words=6)

    rows = shot_table(ws, runtime_s, t_outro)
    T.hold_until(rows, ws)   # E25: a held light follows its sentence
    plan_path = HERE / "sound/SOUND-PLAN.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["cues"] = sound_cues(rows)
    plan_path.write_text(json.dumps(plan, indent=1), encoding="utf-8")
    T.write_shot_table(HERE / "SHOT-TABLE-SHORT.py", rows,
                       '"""Japan tariff trick short - AUTHORED shot table, timed from the take by build_short.py. Do not hand-edit; edit build_short.shot_table."""\n'
                       f"# arm: {ARM}\n")
    T.print_rows(rows, show_docks=True)

    rc = T.compile_timeline(
        HERE, BUILD,
        timeline_name="japan-short.timeline.json",
        shot_table_file="SHOT-TABLE-SHORT.py",
        title="How Japan Tricked Trump", subtitle="Money Physics - short", episode_id="japan-tariff-trick",
        aspect="9:16",
        caption_style="phrase",
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False, "curvature_stroke": True},
        render=True)
    if os.environ.get("SELF_WATCH", "1") == "1":   # P51 T3: the one-shot bar runs LAST - the probe (M25's input), the gate, the lint, the verdicts, the opening's sheets -> SELF-WATCH.md; SELF_WATCH=0 skips it
        import self_watch as SW
        rc = rc or SW.main([str(BUILD), "--project", str(HERE), "--script", "SCRIPT-SHORT"])
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
