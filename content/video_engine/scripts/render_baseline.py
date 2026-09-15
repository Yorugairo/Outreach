"""Render one frame of the scene-evidence player from a committed source (P39).

The same mechanism `render_episode.py` ships with - headless Chromium seeks `#scrub` to t
and screenshots `#stage` - reduced to a single frame from a self-contained player, so a
regression can be caught by pixels without an episode build or the :8731 server.

    python render_baseline.py --list
    python render_baseline.py --surface chart-callout --out frame.png      # one frame at its judged t
    python render_baseline.py --update                                      # rewrite every golden frame
    python render_baseline.py --check                                       # compare, write diffs, exit 1 on any change

Golden frames live in content/video_engine/tests/golden/frames/; their sources in
.../golden/sources/ (written by build_golden_sources.py). Frames are captured at device
scale 1 (1920x1080 or 1080x1920) - the check is exact, so resolution only costs bytes.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import http.server
import io
import json
import shutil
import sys
import tempfile
import threading
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
ENGINE = REPO / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
ASSETS_NAME = "assets.json"        # the split form's fetched asset map
MANIFEST_NAME = "player.json"      # names the engine a served build is running, and its sha
GOLDEN = REPO / "content/video_engine/tests/golden"
SOURCES = GOLDEN / "sources"
FRAMES = GOLDEN / "frames"
DIFFS = GOLDEN / "diffs"
STAGE = {"16:9": (1920, 1080), "9:16": (1080, 1920)}
# P43 T6: one golden per capability with its flag ON, at a t where the change is on screen. Each is checked like the
# base frames; test_kinetics_flags proves each differs from the flag-off render at the same t (a flag golden that
# matched the base would prove nothing). The squash frame has its spring-only twin so the squash is what differs.
FLAG_FRAMES = {
    "chart-callout@curvature_stroke": ("chart-callout", {"curvature_stroke": True}, 10.3),
    "ledger-page-mid-build@curvature_stroke": ("ledger-page-mid-build", {"curvature_stroke": True}, 5.6),
    "ledger-soak-page@km_ink": ("ledger-soak-page", {"km_ink": True}, 2.7),
    "ledger-soak-page@analytic_spring": ("ledger-soak-page", {"analytic_spring": True}, 7.86),
    "ledger-soak-page@area_squash": ("ledger-soak-page", {"analytic_spring": True, "area_squash": True}, 7.86),
    "ledger-soak-page@idle": ("ledger-soak-page", {"idle": True}, 11.0),   # the page holding after its build: the breath is the only difference (E49)
}
# P52 T7 + T8, HUMAN GATE 3: THE PROOF FRAMES. A second dict with FLAG_FRAMES' own shape (surface, flags, t) and a
# different claim: not "this capability changes the frame" but "this INSTANT of this surface is the one to judge".
# The two are kept apart on purpose - `test_kinetics_flags` is right to insist that every FLAG golden differs from
# the flag-off render at its t (a flag frame that changed nothing would prove nothing), and a second instant of one
# surface owes nobody that. Both are checked as goldens, and both are reachable by name from render_surface.
#
# `species-proof` carries the last three Bravos species on ONE clock, one per scene, so the operator reads each at
# its own instant and then plays the single file end to end. The flags they carry are `idle` ON - E49's own switch:
# what it turns on is the WORLD's breath under the species (the ledger page in scene 1), while each species' own
# named idle runs either way. On the two bare-plate scenes the flag changes no pixel (a flat plate breathing is a
# flat plate), which is exactly why these are PROOF frames and not FLAG frames.
PROOF_FRAMES = {
    # P58 T3 - THE CAMERA OVER PLANES, at the two instants the landed frame cannot show. The card lands at 5.0 and
    # the eye follows it in over 6.0 -> 8.0 (E51: a push is tied to a landing; E59's module is ON, as on the base
    # frame). No flag makes the depth happen: a plate that ships in planes takes the authored move at four factors.
    "camera-layers@proof-start": ("camera-layers", {"camera": True}, 5.9),   # BEFORE the move: the camera is LOCKED, so every k has nothing to multiply and the four planes paint exactly the flat composite
    "camera-layers@proof-mid": ("camera-layers", {"camera": True}, 6.56),    # MID-ZOOM (u 0.28 of the clock, 0.50 of the servo's reach): the lamp (1.40) leading the desk (1.275), the containers (1.15) and the sky (1.0)
    # P58 T4 - THE PAGE AS A CARD AT A DEPTH, at the two instants the held frame cannot show. Same flag as
    # camera-layers (E59's module drives the move); the depth and the plane are AUTHORED on the page, not switched on.
    "page-depth@proof-build": ("page-depth", {"camera": True}, 9.8),    # MID-BUILD: the chart DRAWING on the tilted page - the page's own clock opens at 5.0 and this is its 4.8 s, the subtitle half written, two of the four series in, the nib at the front; the camera is still locked, so what turns the page is the plane alone
    "page-depth@proof-leave": ("page-depth", {"camera": True}, 28.5),   # THE LEAVING: half way down the retract's drain (the colours over the scene's last 2 s), the page still standing on its plane
    # P58 T6 (b) - THE MELT'S BALL AT A DEPTH, at the instant the ending cannot show: the ball formed, the weight
    # phase opening, the eye mid-move - the ball at 1.15 and the board it came off at 1.0, parted.
    "melt-depth@proof-ball": ("melt-depth", {"camera": True}, 15.88),
    # E98 s7 / R26-134 - THE EVIDENCE DOOR, at the two instants its landing cannot show: the flat chart swinging open on
    # its left edge onto the plate mounted beneath it (the min-jerk clock from the cut at 15.0 over 0.9 s). No flag: a
    # door is an authored exit, not a capability behind a switch.
    "door-open@proof-early": ("door-open", {}, 15.32),   # u 0.25: the page turned 27 deg, its far edge drawn in toward the vanishing point, a strip of the plate showing
    "door-open@proof-mid": ("door-open", {}, 15.45),     # u 0.50: 54 deg, the page a trapezoid on its hinge, most of the plate open behind it
    # P58 T6 (c) - THE SLIDE THROUGH THE DEPTH, mid-slide: the seam on the centre line, the eye moving, the outgoing
    # board read at 0.925 of the move and the incoming at 1.075 (the base frame is the landing, where both are flat).
    "slide-depth@proof-mid": ("slide-depth", {"camera": True}, 15.3),
    # P58 T6 (a) - THE DOCK AT A DEPTH, at the instant the landed frame cannot show: the same flag and the same
    # t as `camera-layers@proof-mid`, so the pair reads the card's plane and nothing else.
    "dock-depth@proof-move": ("dock-depth", {"camera": True}, 6.56),   # MID-ZOOM (u 0.28 of the clock): the card riding the containers' plane (1.15) between the sky (1.0) and the lamp (1.40), its own park untouched
    # P58 T5 - THE TWO CHART FORMS, at the instants the held frame cannot show: the prisms GROWING with their
    # faces / the line drawing ON the plane (6.0, the same t the flat line page's own golden is judged at), and
    # the page LEAVING (28.5). No flag: a form is authored on the row, not switched on.
    "form-extruded-bar@proof-build": ("form-extruded-bar", {}, 6.0),
    "form-extruded-bar@proof-leave": ("form-extruded-bar", {}, 28.5),
    "form-tilted-line@proof-build": ("form-tilted-line", {}, 6.0),
    "form-tilted-line@proof-leave": ("form-tilted-line", {}, 28.5),
    # P61 T4b / E99 s35 - THE CROSS-FADE PAGE LEAVING BY THE SOAK'S RECEDE, at the instant only phase two of the
    # drain can show (the colours are gone by 29.0; the charcoal's own second runs 29.0 -> 30.0). At 29.35 the
    # inked plate and the crisp rect have faded off the seeps beneath them and the seeps are receding down the
    # vortex - the leave the operator chose for BOTH fields: "the leave-soak is much better than the two plate leave".
    # 29.6 is uf 0.60: the ink is one lumpy island and the PLATE'S OWN cream paper is uncovered all round it. The
    # instant is chosen for what it proves - at 29.35 the recede has only bitten the corners, and the two-plate
    # leave this replaces was flat cream a full second earlier (the reference clip `formed-page-leave-twoplate.mp4`).
    "form-tilted-line@proof-recede": ("form-tilted-line", {}, 29.6),
    "species-proof@proof-ring": ("species-proof", {"idle": True}, 12.6),     # the dashed ellipse closed round the series' own peak, its flag chip landed, the page breathing under it
    "species-proof@proof-count": ("species-proof", {"idle": True}, 22.5),    # the isometric field: all six icons in reading order, the count written as the claim
    "species-proof@proof-agenda": ("species-proof", {"idle": True}, 28.5),   # the numbered agenda: three rows revealed one per word, holding
    # P52 T9 / R26-15, HUMAN GATE 2, reworked to E88 / R26-76: THE MELT (the THROW ending), one frame per phase of its
    # 1.6 s window from the cut at 15.0. They carry no flag (a melt is an authored EXIT, not a capability behind a switch),
    # which is what makes them proofs and not flag frames. The other two endings are their own surfaces:
    # `frames/melt-splash.png` (splash:chart) and `frames/melt-plate.png` (splash:plate). In every one the board stays.
    "melt-page@proof-015": ("melt-page", {}, 15.0 + 0.15 * 1.6),   # THE SAG: the chart's marks swelling and running down under the goo, the board whole behind them
    "melt-page@proof-045": ("melt-page", {}, 15.0 + 0.45 * 1.6),   # THE BALL, forming: the ink squeezed toward the centre on the stepped clock, the dense body coming up over it
    "melt-page@proof-075": ("melt-page", {}, 15.0 + 0.75 * 1.6),   # THE THROW: the heavy ball in flight off the bottom right, the next chart drawing on the same board
    "melt-page@proof-100": ("melt-page", {}, 15.0 + 1.00 * 1.6),   # GONE: the next chart on its board, drawing, nothing left of the ink that melted
    # R26-118 / E88 s6-s7: THE BALL WITH MASS, at the two instants its mid-roll golden cannot show. The same two pages
    # as `melt-page`, the exit `melt:weight` - so the window is 2.75 s from the cut at 15.0 and the weight phase runs
    # 15.88 - 17.03. No flag: weight is authored on the exit, not switched on.
    "melt-ball-roll@proof-land": ("melt-ball-roll", {}, 16.11),     # THE LANDING: the contact - the board dipped under it, the contact shadow tightened from FAR to NEAR, the surface re-excited by the hit
    "melt-ball-roll@proof-settle": ("melt-ball-roll", {}, 16.98),   # AT REST before the ending: rolled and nudged its whole way, the mark turned round, the drop still wriggling to contain itself (E49)
    # P55 T6: THE VERDICT STACK's last phase - the radial BURST at clear_at (20.0) + 0.25 s: with the 60 ms stagger the
    # first card is half way through its 0.5 s throw and the fifth just leaving, each along its own bearing, spinning
    "verdict-stack@proof-burst": ("verdict-stack", {}, 20.25),
    # P57 T12 / R26-70b, E76, re-goldened by T12b and again by T12c: THE COMPARE, at the instants its landed frame
    # cannot show. The row runs 12.0 -> 14.4 (the base golden `compare-morph` is judged at 14.9, held). No flag: the
    # verb is authored on the row, not switched on - and since T12b the FORM is too, so each form has its own surface
    # and its own proofs. The DEFAULT form is E76 s5's ball, on melt.mjs's own phase shares (MELT_END 0.30, BALL_END
    # 0.55), so its three instants are one per phase: the sag, the ball, and the morph's own half-way point - which is
    # u 0.775 of the WINDOW, because the morph is the last 0.45 of it and 0.50 of the window is still the ball.
    "compare-morph@proof-sag": ("compare-morph", {}, 12.0 + 0.15 * 2.4),   # MID-SAG (u 0.15, the sag at 0.50): the glyphs' own outlines hanging in seeded drips, the chart whole behind them
    "compare-morph@proof-ball": ("compare-morph", {}, 12.0 + 0.53 * 2.4),   # THE BALL (u 0.53, the ball phase at 0.92 - one hold before the ending takes it): the number compiled into one dense disc that holds its own ink
    "compare-morph@proof-050": ("compare-morph", {}, 12.0 + 0.775 * 2.4),   # THE MORPH AT 0.50 (u 0.775): the ball opening into "15 % dearer" - neither the ball nor the number
    # P57 T12b's TEXT melt, kept whole as `form: "streak"` by T12c: the three instants it shipped, byte-identical.
    "compare-streak@proof-quoted": ("compare-streak", {}, 11.9),   # THE QUOTED FIGURE: "24.8x" written at its datum by the hand, the page as it stands before the word
    "compare-streak@proof-melt": ("compare-streak", {}, 12.0 + 0.35 * 2.4),   # MID-MELT (u 0.35, take 0.64): the glyphs sagging and running down under melt's own streak, the chart whole behind them
    "compare-streak@proof-write": ("compare-streak", {}, 12.0 + 0.71 * 2.4),   # MID-WRITE (u 0.71, write 0.36): the hand part way through "15 % dearer" at the same datum, the ink of the metric gone
    "compare-count@proof-mid": ("compare-count", {}, 12.0 + 0.35 * 2.4),   # MID-COUNT (u 0.35): the number between the two, still in the metric's own clothes, the words beginning to cross - T12's own proof instant, byte-identical
    # P57 T19 / R26-96, E49 + E56: THE LIGHT'S OWN LIFE. The base golden `spotlight-hold` is judged at 8.0, held on
    # its first datum before the glide. These two are taken after the glide has landed on `target2` (9.0 + 0.6), so
    # the ONLY thing that differs between them is the `live` idle - the hole's radius breathing and its centre
    # drifting. They are 2.0 s apart, exactly half the breath's 4.0 s period (IDLE.BREATH_HZ 0.25), so whatever
    # phase the seeded hash hands this species they sit at opposite ends of one inhale. No flag: `idle: "live"` is
    # authored ON THE SPECIES and runs either way (E49's switch turns on the WORLD's breath, which is not this).
    "spotlight-hold@proof-idle-a": ("spotlight-hold", {}, 12.0),
    "spotlight-hold@proof-idle-b": ("spotlight-hold", {}, 14.0),
    # P57 T21 / R26-99: THE RECORD'S LANDING, the instant its base golden (7.62, mid-type) cannot show. The
    # quotation's `end` is 9.66, so at 10.26 the last word is whole (its slice clamped at 1), the cursor is
    # parked after it, and the two toggles the painter carries have both fired - the attribution at end + 0.15
    # and the source line at end + 0.45. No flag: a record types either way.
    "record-typewriter@proof-attr": ("record-typewriter", {}, 10.26),
    # P57 T22 / R26-101: THE RETRACT, the direction the base golden cannot show. `spiral-return` is judged
    # mid-RETURN (16.12), so these two take the other half of the same geometry off scene 1's own clock, which
    # runs over its last COLOURS + CHARCOAL (1.0 + 1.0 s) from 13.0: phase one the colours down the drain, phase
    # two the crisp charcoal fading to the stains as they follow. No flag: a page retracts unless its row says
    # `exit: "cut"`.
    "spiral-return@proof-retract": ("spiral-return", {}, 13.5),   # PHASE ONE at uc 0.5 - the twin of the base frame, run the other way: every colour at half its home radius, the series lines curling into the drain
    "spiral-return@proof-fade": ("spiral-return", {}, 14.5),      # PHASE TWO at uc 1, uf 0.5 - the colours gone, the charcoal fully faded to the field beneath it (uf past RECT_FADE 0.3) and the scribble strokes at half opacity, on their way down the same drain
    # P57 T23 / R26-100, E47 s1: THE RAMP, the half of the dip its black boundary frame cannot show. The base
    # golden `dip-boundary` is the boundary frame itself (15.0, dipA 1). This one is taken on the OUTGOING half,
    # where the fully drawn line page is still the picture: the scrub carries step="0.01", so the ramp's exact
    # midpoint (15.0 - DIP_S/4 = 14.8825) is not reachable and 14.88 is the frame beside it - dipA
    # 1 - 0.12/0.235 = 0.4894, the plate at just over half its light. LINEAR is what this pins: on any eased ramp
    # the same instant sits visibly off that value. No flag: a dip is an authored exit, not a capability.
    "dip-boundary@proof-ramp": ("dip-boundary", {}, 14.88),
    # P61 T2 / E99 s34: THE WHOLE-CHART REMAKE, at the two instants its 0.50 frame cannot show. The row runs
    # 12.0 -> 14.4 and the base golden of each surface IS its u = 0.50 (13.2), the instant a jump cannot fake -
    # so these two are the quarter and the three-quarter: the ink leaving its own form, and the ink arriving in
    # the other. No flag: the verb is authored on the row, not switched on.
    "remake-line-to-bars@proof-025": ("remake-line-to-bars", {}, 12.6),   # u 0.25: the line gone into its six columns, the data born, the rings just moving
    "remake-line-to-bars@proof-075": ("remake-line-to-bars", {}, 13.8),   # u 0.75: the columns nearly their bars, the data over their tops, the arriving labels writing
    "remake-bars-to-line@proof-025": ("remake-bars-to-line", {}, 12.6),   # u 0.25: the bars' own rectangles moving as rings, their numbers un-writing
    "remake-bars-to-line@proof-075": ("remake-bars-to-line", {}, 13.8),   # u 0.75: the rings landed as the area under the line, the line striking along their top edge
}
# P52 T18 / R26-55, HUMAN GATE 7: THE FACE OF A PULLED PHRASE. The phrase is live type now, so it has a face, and
# the face is the OPERATOR's to choose - never ours. The `press_face` DIAL names one of the three candidates
# species/press.mjs offers (all of them already on the page; the template downloads exactly one webfont and this
# adds none). Same card, same instant, same everything else, so the three frames differ in the FACE and nothing
# else. The HOUSE face - the default until the operator rules - is the base `press-stack` golden itself: a
# `press-stack@face-house` entry here would be a frame identical to it, and test_kinetics_flags rightly fails an
# entry in this map that changes nothing (measured 2026-09-12). Gate 7's three frames are therefore
# `frames/press-stack.png` (house), and these two.
FLAG_FRAMES["press-stack@face-serif"] = ("press-stack", {"press_face": "serif"}, 11.4)
FLAG_FRAMES["press-stack@face-condensed"] = ("press-stack", {"press_face": "condensed"}, 11.4)


# P51 T1 - THE TWO FORMS OF ONE PAGE. The engine is a module on disk (scene-evidence-engine.mjs);
# the template is a shell (style + DOM + the two data slots + {{ENGINE}}). One engine text serves both:
#   SINGLE  the engine inlined as a classic script, the data inlined in the slots - the goldens, every
#           test that instantiates a surface, and every player.html committed before the split;
#   SPLIT   the engine imported as a module beside the page, the data fetched from the slots' data-src -
#           what a build writes, so a build dir holds a ~45 KB page instead of a 32 MB one.
# The boot line is identical in both, and __mounted is what a renderer waits on (prepare_page).
BOOT = "window.__mounted = false; mount().then(() => { window.__mounted = true; });"


def engine_script(engine: Path = ENGINE) -> str:
    """The engine as ONE inline classic script: its module syntax stripped by the same code that
    inlines the kinetics modules into it, so there is exactly one stripper in the repo."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import sync_kinetics as SK  # noqa: E402 - a sibling script, not a package
    return "<script>\n" + SK.inline_text(engine.read_text(encoding="utf-8"), "") + "\n" + BOOT + "\n</script>"


# P51 T4 - THE WATCH CLIENT. It rides in the SPLIT form only (a golden's single-file page is the
# text it always was) and does nothing at all unless ?watch=1 is on the URL - so a served build
# without the flag is exactly today's page. With the flag it long-polls the review server's
# /reload, which holds the request until the build's generation moves, and hands the new timeline
# to the engine's reload(): no page load, the scrub position kept. The server's answer carries
# `reload` false for a generation that only reports a determinism result, so the check can land
# after the frame without re-mounting the page.
WATCH_CLIENT = """
if (/[?&]watch=1/.test(location.search)) {
  const W = window.__watch = { gen: 0, applied: 0, reloads: 0, last: null, error: null };
  (async () => {
    while (window.__mounted === false) await new Promise(r => setTimeout(r, 25));
    for (;;) {
      try {
        const m = await (await fetch("reload?since=" + W.gen, { cache: "no-store" })).json();
        W.last = m; W.error = null;
        if (m.gen > W.gen) {
          W.gen = m.gen;
          if (m.reload) {
            const tl = await (await fetch(m.timeline + "?gen=" + m.gen, { cache: "no-store" })).json();
            await reload(tl);
            W.reloads++;
          }
          W.applied = m.gen;
        }
      } catch (e) { W.error = String(e); await new Promise(r => setTimeout(r, 500)); }
    }
  })();
}
"""


def module_script(engine_src: str = None) -> str:
    """The engine as a module fetched beside the page, with the watch client behind ?watch=1.

    The namespace import is deliberate: a build dir written before P51 T4 carries an engine copy
    with no `reload` export, and a NAMED import of a missing binding is a link error that kills
    the whole page - `import * as` degrades to an undefined function instead."""
    return ('<script type="module">import * as ENGINE from "./' + (engine_src or ENGINE.name) + '";\n'
            'const mount = ENGINE.mount, reload = ENGINE.reload;\n'
            + BOOT + "\n" + WATCH_CLIENT + "</script>")


def player_text(template: Path = TEMPLATE, engine: Path = ENGINE) -> str:
    """The shell and the engine as ONE text - what a lint or a grep-style check means by "the
    player's source". It is not a page (nothing is substituted): use instantiate() for that."""
    return template.read_text(encoding="utf-8") + "\n" + engine.read_text(encoding="utf-8")


def single_file_shell(template: Path = TEMPLATE, engine: Path = ENGINE) -> str:
    """The shell with the engine inlined and the two DATA slots still open ({{TIMELINE}} / {{URIS}}).

    One caller needs this and not instantiate(): ep1's legacy F door patches the player's OWN JS
    (the caption loop, DUR, the title) before it substitutes its data - those anchors moved into
    the engine, so the door has to see the composed text."""
    html = template.read_text(encoding="utf-8")
    for slot in ("{{TIMELINE}}", "{{URIS}}", "{{ENGINE}}"):
        if slot not in html:
            raise RuntimeError(f"{template} is not the shell - it has no {slot} slot")
    return (html.replace("{{TIMELINE_SRC}}", "").replace("{{ASSETS_SRC}}", "")
                .replace("{{ENGINE}}", engine_script(engine)))


def instantiate(timeline: dict, uris: dict, template: Path = TEMPLATE, split: bool = False,
                engine: Path = ENGINE, timeline_src: str = "", assets_src: str = ASSETS_NAME) -> str:
    """The build step's exact substitution on the reviewed shell.

    split=False (the default, and what every golden and test takes): the single-file form.
    split=True: the shell with the two data slots EMPTY and their data-src filled - the engine
    fetches them. `timeline_src` is the compiled timeline's file name in the build dir."""
    html = template.read_text(encoding="utf-8")
    for slot in ("{{TIMELINE}}", "{{URIS}}", "{{ENGINE}}"):
        if slot not in html:
            raise RuntimeError(f"{template} is not the shell - it has no {slot} slot")
    if split and not timeline_src:
        raise ValueError("the split form needs the compiled timeline's file name (timeline_src)")
    return (html.replace("{{TIMELINE}}", "" if split else json.dumps(timeline, separators=(",", ":")))
                .replace("{{URIS}}", "" if split else json.dumps(uris, separators=(",", ":")))
                .replace("{{TIMELINE_SRC}}", timeline_src if split else "")
                .replace("{{ASSETS_SRC}}", assets_src if split else "")
                .replace("{{ENGINE}}", module_script(engine.name) if split else engine_script(engine)))


def write_split(build_dir: Path, timeline: dict, uris: dict, timeline_name: str,
                template: Path = TEMPLATE, engine: Path = ENGINE) -> Path:
    """Write a SELF-CONTAINED split build: the page, the compiled timeline, the asset map, and a COPY
    of the engine beside them (a served build never reaches back into docs/). player.json names the
    engine and its sha - the compiled timeline stays byte-identical to what the build always wrote."""
    build_dir = Path(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    (build_dir / timeline_name).write_text(json.dumps(timeline, indent=1), encoding="utf-8")
    (build_dir / ASSETS_NAME).write_text(json.dumps(uris, separators=(",", ":")), encoding="utf-8")
    shutil.copyfile(engine, build_dir / engine.name)
    out = build_dir / "player.html"
    out.write_text(instantiate(timeline, uris, template, split=True, engine=engine,
                               timeline_src=timeline_name), encoding="utf-8")
    (build_dir / MANIFEST_NAME).write_text(json.dumps({
        "form": "split",
        "engine": engine.name,
        "engine_sha256": hashlib.sha256(engine.read_bytes()).hexdigest(),
        "timeline": timeline_name,
        "assets": ASSETS_NAME,
    }, indent=1), encoding="utf-8")
    return out


class _Quiet(http.server.SimpleHTTPRequestHandler):
    # .mjs is NOT in Python's mimetypes table on Windows, and a module served as
    # application/octet-stream is refused by the browser's strict MIME check - the split page
    # would load its shell and mount nothing. no-store so a rebuilt engine is never the cached one.
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".mjs": "text/javascript"}

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *_):  # noqa: D401 - silence per-request logging
        pass


def serve(directory: Path):
    handler = functools.partial(_Quiet, directory=str(directory))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def frame_png(page, t: float, size: tuple[int, int]) -> bytes:
    page.evaluate(
        "t => { const s = document.getElementById('scrub');"
        " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
    # a CLIP world seeks a <video> to the scene clock; the frame is not a function of t until
    # the seek has landed (the template resolves __clipsSeeked once every pending seek fires)
    page.evaluate("() => window.__clipsSeeked ? window.__clipsSeeked() : null")
    # a clipped page shot at the stage's exact rectangle: an element screenshot inherits the
    # container's fractional offset and comes back a pixel wide (1081x1920 on 9:16)
    r = page.evaluate("(() => { const b = document.getElementById('stage').getBoundingClientRect(); return [b.x, b.y]; })()")
    return page.screenshot(type="png", clip={"x": round(r[0]), "y": round(r[1]), "width": size[0], "height": size[1]})


def prepare_page(page, w: int, h: int) -> None:
    """Make the loaded player a pure function of t, at the stage's native size.

    The four wall-clock / geometry dependencies P39 T2 found, neutralised in one place so
    the golden harness and the shipped renderer capture identically:
      - CSS transitions (.dock opacity .75s, pills .34s, captions .12s) run on the WALL CLOCK,
        so a seek-and-screenshot can land mid-transition (caught: run 2 of 3 differed on 9:16)
      - fitStage() scales #stage to the #fit container (~0.73x at 1920x1080), so an element
        screenshot is a downscaled stage that render_episode used to LANCZOS-upscale
      - document.fonts.ready.then(()=>1) is not awaited by page.evaluate; the bare promise is
      - an element screenshot inherits the container's fractional offset (1081x1920)
    """
    page.wait_for_selector("#stage", timeout=60000)
    # P51 T1: the split page mounts after two fetches, so the DOM can exist before the engine has
    # run. __mounted is undefined on a single-file page and on every player committed before the
    # split, where the engine has already run by load - those pass this line without waiting.
    page.wait_for_function("window.__mounted !== false", timeout=300000)
    page.evaluate("document.fonts.ready")
    page.evaluate("document.getElementById('vo').muted = true")
    page.evaluate("for (const id of ['sndbar']) { const e=document.getElementById(id); if (e) e.style.display='none'; }")
    page.add_style_tag(content=(
        "*, *::before, *::after { transition: none !important; animation: none !important; }"
        f" #shell {{ width: auto !important; max-width: none !important; }}"
        f" #fit {{ width: {w}px !important; height: {h}px !important; max-width: none !important; overflow: visible !important; }}"
        " #stage { transform: none !important; }"))
    page.set_viewport_size({"width": w + 64, "height": h + 64})
    # the handwriting face loads on first use: fetch it explicitly so a portrait page never measures its ink
    # in the fallback face (P41) - the template rebuilds its pages when the load lands
    page.evaluate("() => document.fonts.load('700 68px Kalam').then(() => document.fonts.load('400 40px Kalam')).then(() => 1)")
    page.wait_for_function("document.fonts.status === 'loaded'")
    page.wait_for_timeout(250)


def render_frame(html_path: Path, t: float, aspect: str = "16:9", device_scale_factor: float = 1.0) -> bytes:
    """One PNG of #stage at time t, from a fresh browser, served over a throwaway local server."""
    from playwright.sync_api import sync_playwright
    w, h = STAGE[aspect]
    srv, port = serve(html_path.parent)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=device_scale_factor).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html_path.name}", wait_until="networkidle", timeout=120000)
            prepare_page(page, w, h)
            png = frame_png(page, t, (w, h))
            size = rgb_bytes(png)[0]
            expect = (round(w * device_scale_factor), round(h * device_scale_factor))
            if size != expect:
                raise RuntimeError(f"stage captured at {size}, expected {expect} - fitStage is still scaling")
            browser.close()
    finally:
        srv.shutdown()
    return png


def rgb_bytes(png: bytes) -> tuple[tuple[int, int], bytes]:
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGB")
    return im.size, im.tobytes()


def load_surface(name: str) -> tuple[dict, dict, float, str]:
    sys.path.insert(0, str(GOLDEN))
    from build_golden_sources import FRAME_T  # noqa: E402
    tl = json.loads((SOURCES / f"{name}.timeline.json").read_text(encoding="utf-8"))
    uris = json.loads((SOURCES / f"{name}.uris.json").read_text(encoding="utf-8"))
    return tl, uris, FRAME_T[name], str(tl.get("aspect") or "16:9")


def render_surface(name: str, t: float | None = None, template: Path = TEMPLATE, kinetics: dict | None = None) -> bytes:
    """A frame of a golden surface; `name` may be a FLAG_FRAMES or PROOF_FRAMES key (surface@name), which fixes the flags and the t."""
    if name in FLAG_FRAMES or name in PROOF_FRAMES:   # P52 T7/T8: a proof frame is named and reached the same way
        surface, flags, t_flag = FLAG_FRAMES[name] if name in FLAG_FRAMES else PROOF_FRAMES[name]
        return render_surface(surface, t if t is not None else t_flag, template, dict(flags, **(kinetics or {})))
    tl, uris, t_default, aspect = load_surface(name)
    if kinetics is not None:
        tl = dict(tl, kinetics=kinetics)
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / f"{name.replace('@', '-')}.html"
        html.write_text(instantiate(tl, uris, template), encoding="utf-8")
        return render_frame(html, t if t is not None else t_default, aspect)


def write_diff(name: str, golden_png: bytes, actual_png: bytes) -> Path:
    """golden | actual | amplified difference, side by side - legible without reading code."""
    from PIL import Image, ImageChops, ImageDraw
    g = Image.open(io.BytesIO(golden_png)).convert("RGB")
    a = Image.open(io.BytesIO(actual_png)).convert("RGB")
    if a.size != g.size:
        a = a.resize(g.size)
    d = ImageChops.difference(g, a).point(lambda v: min(255, v * 8))
    w, h = g.size
    out = Image.new("RGB", (w * 3, h + 40), (8, 12, 16))
    for i, (im, label) in enumerate(((g, "GOLDEN"), (a, "ACTUAL"), (d, "DIFF x8"))):
        out.paste(im, (i * w, 40))
        ImageDraw.Draw(out).text((i * w + 12, 12), f"{label}  {name}", fill=(244, 230, 199))
    DIFFS.mkdir(parents=True, exist_ok=True)
    p = DIFFS / f"{name}.diff.png"
    out.save(p, "PNG")
    return p


def check(names: list[str]) -> list[str]:
    """Return one line per changed frame (empty = all identical)."""
    failures = []
    for name in names:
        golden = FRAMES / f"{name}.png"
        if not golden.exists():
            failures.append(f"{name}: no golden frame at {golden} (run --update)")
            continue
        actual = render_surface(name)
        if rgb_bytes(golden.read_bytes())[1] != rgb_bytes(actual)[1]:
            diff = write_diff(name, golden.read_bytes(), actual)
            failures.append(f"{name}: pixels changed - see {diff.relative_to(REPO)}")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--surface")
    ap.add_argument("--t", type=float)
    ap.add_argument("--flags", help="comma-separated kinetics flags to turn ON for --surface")
    ap.add_argument("--out")
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    names = sorted(p.name[: -len(".timeline.json")] for p in SOURCES.glob("*.timeline.json")) + sorted(FLAG_FRAMES) + sorted(PROOF_FRAMES)
    if args.list:
        print("\n".join(names)); return 0
    if args.surface:
        png = render_surface(args.surface, args.t, kinetics={f: True for f in args.flags.split(",")} if args.flags else None)
        Path(args.out or f"{args.surface}.png").write_bytes(png)
        print(args.out or f"{args.surface}.png"); return 0
    if args.update:
        FRAMES.mkdir(parents=True, exist_ok=True)
        for name in names:
            (FRAMES / f"{name}.png").write_bytes(render_surface(name)); print("golden", name)
        return 0
    if args.check:
        failures = check(names)
        print("\n".join(failures) if failures else f"PASS {len(names)} golden frames identical")
        return 1 if failures else 0
    ap.print_help(); return 2


if __name__ == "__main__":
    raise SystemExit(main())
