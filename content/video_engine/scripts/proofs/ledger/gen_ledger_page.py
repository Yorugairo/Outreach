"""Generate the three ledger-page candidates (P35 T1) into the hyperframes lane."""
from pathlib import Path
import sys

HF = Path(sys.argv[1])
# Divergence end values, verbatim from ev-divergence-v1.series.json (last point of each series)
DATA = "712.52, 204.62, 120.75, 121.49"
LABELS = "Mega-cap tech, S&P 500, Semis, Memory"
SRC = "Yahoo Finance - pairing after Bravos Research - index, 100 = Aug 2025"
TITLE = "The sharpest chart on YouTube - plus the layer it needed"
CHART_IN = 5.0                    # chart-story intrinsic duration: the composition ends before any sub-comp outlives its own clock
ROLL = 0.6                        # s9.26 beat 1: roll-out 0-0.6s
FIELD_AT = ROLL                   # the field begins as the roll settles
IN_BLEED, IN_STROKES = 2.8, 3.55  # component IN_BASE: ink-bleed-reveal / whiteboard-ink
OUTLINE_IN = 0.8                  # outline-draw IN_BASE (draw-complete sync point)


def build(variant: str) -> str:
    field_in = {"A": 0.0, "B": IN_STROKES, "C": IN_BLEED}[variant]
    outline_at = round(FIELD_AT + field_in, 2)
    chart_at = round(outline_at + OUTLINE_IN, 2)
    src_at = round(chart_at + 2.6, 2)
    DUR = round(chart_at + CHART_IN - 0.2, 2)
    board = variant != "A"
    ink = "#F2F2F2" if board else "#25313C"   # chalk-light on charcoal; charcoal on plain cream
    surface = "#25313C" if board else "#F4E6C7"
    border = "#8a94a0" if board else "#7a6f5a"
    muted = "#c9ced4" if board else "#7a6f5a"
    field = ""
    if variant == "C":
        field = f'''
      <!-- C: the charcoal field BLEEDS in (ink-bleed-reveal; its mark slot is the field) -->
      <div class="clip layer field-host" data-composition-id="bleed" data-composition-src="compositions/components/ink-bleed-reveal-ledger.html"
           data-variable-values='{{"blobs": 6, "accent": "green", "exit": "none"}}'
           data-start="{FIELD_AT}" data-duration="{DUR - FIELD_AT}" data-track-index="2"></div>'''
    if variant == "B":
        field = f'''
      <!-- B: the charcoal field is SCRIBBLED (whiteboard-ink; strokes slot = 14 seeded field strokes) -->
      <div class="clip layer field-host strokes" data-composition-id="scribble" data-composition-src="compositions/components/whiteboard-ink-field.html"
           data-variable-values='{{"caption": "", "pen": "show", "accent": "green", "exit": "none"}}'
           data-start="{FIELD_AT}" data-duration="{DUR - FIELD_AT}" data-track-index="2"></div>'''
    slot = ""
    if variant == "C":
        slot = '''
    <!-- ink-bleed-reveal reads this inert template from the HOST document: the mark is the charcoal field -->
    <template data-slot="ink-bleed-reveal-mark">
      <div class="charcoal-field"></div>
    </template>'''
    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      /* LEDGER PAGE v1 - candidate {variant}. P35 T1: the stitch, doc 29 s9.26.
         A = plain cream page (comparison only)  B = scribbled field  C = bled field.
         Register: cream #F4E6C7, charcoal #25313C, accent sunflower; docks stay near-black elsewhere.
         Beats: roll-out 0-{ROLL}s -> field ({variant}: {field_in}s) -> outline draws ({outline_at}s, draw-complete +{OUTLINE_IN}s)
                -> chart builds ({chart_at}s) -> source line ({src_at}s). Everything derives from the paused timeline. */
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #1B1E23; }}
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}
      /* the page rolls out inside an overflow-hidden frame: a TRANSFORM, never an animated clip-path (determinism allowlist) */
      .page-frame {{ position: absolute; inset: 0; overflow: hidden; }}
      .page {{ position: absolute; inset: 0; background: #F4E6C7; will-change: transform; }}
      .grain {{ position: absolute; inset: 0; opacity: .18; mix-blend-mode: multiply; pointer-events: none; }}
      .roll-edge {{ position: absolute; top: 0; bottom: 0; right: -6px; width: 42px; will-change: opacity;
        background: linear-gradient(90deg, rgba(37,49,60,0) 0%, rgba(37,49,60,.28) 35%, rgba(255,255,255,.55) 60%, rgba(37,49,60,.35) 100%); }}
      /* the charcoal field: the full page minus a cream-stained margin (s9.26 geometry: a stained page, not a framed board) */
      .layer {{ position: absolute; inset: 0; }}
      .field-host {{ --brand: #25313C; --accent: #25313C; --accent-2: #25313C; --fg: #25313C; --bg: transparent; --surface: #F4E6C7; --muted: #7a6f5a;
        --font-body: Inter, sans-serif; --font-display: Inter, sans-serif; }}
      .charcoal-field {{ width: 88cqw; height: 84cqh; background: #25313C;
        border-radius: 3cqmin 5cqmin 4cqmin 6cqmin / 5cqmin 3cqmin 6cqmin 4cqmin; }}
      .outline-host {{ --accent: {ink}; --fg: {ink}; --space-8: 7cqmin; }}
      .chart-host {{ position: absolute; left: 6%; top: 8%; width: 88%; height: 84%;
        --fg: {ink}; --bg: #25313C; --surface: {surface}; --border: {border}; --muted: {muted};
        --brand: #1769C2; --accent: #F5B72E; --accent-2: #178C83;
        --font-body: Inter, sans-serif; --font-display: Inter, sans-serif; --font-mono: "Roboto Mono", monospace; }}
      .title {{ position: absolute; left: 8%; top: 9.5%; font: 700 34px/1.2 Inter, sans-serif; color: {ink}; letter-spacing: -.01em; opacity: 0; }}
      .source {{ position: absolute; left: 6%; bottom: 2.2%; font: 500 22px/1.2 Inter, sans-serif; color: #25313C; opacity: 0; }}
    </style>
  </head>
  <body>{slot}
    <div id="root" data-composition-id="ledger-page-v1-{variant}" data-start="0" data-duration="{DUR}" data-width="1920" data-height="1080" data-fps="30">
      <div class="clip page-frame" data-start="0" data-duration="{DUR}" data-track-index="1">
        <div class="page" id="page">
          <svg class="grain" width="100%" height="100%" aria-hidden="true">
            <filter id="paper"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 0.15  0 0 0 0 0.13  0 0 0 0 0.10  0 0 0 0.35 0"/></filter>
            <rect width="100%" height="100%" filter="url(#paper)"/>
          </svg>
          <div class="roll-edge" id="roll-edge"></div>
        </div>
      </div>{field}
      <!-- the clean edge: outline-draw over the field (draw-complete at +{OUTLINE_IN}s) -->
      <div class="clip layer outline-host" data-composition-id="outline" data-composition-src="compositions/components/outline-draw-ledger-{variant}.html"
           data-variable-values='{{"progress": 100, "thickness": 5, "radius": 30}}'
           data-start="{outline_at}" data-duration="{DUR - outline_at}" data-track-index="3"></div>
      <!-- the chart builds: chart-story bars landing on the exact series end values -->
      <div class="clip chart-host" data-composition-id="chart" data-composition-src="compositions/components/chart-story-ledger-{variant}.html"
           data-variable-values='{{"type": "bars", "data": "{DATA}", "labels": "{LABELS}", "emphasize": 0, "unit": "", "accent": "blue", "exit": "none"}}'
           data-start="{chart_at}" data-duration="{DUR - chart_at}" data-track-index="4"></div>
      <div class="clip title" id="title" data-start="{chart_at}" data-duration="{DUR - chart_at}" data-track-index="5">{TITLE}</div>
      <div class="clip source" id="source" data-start="{src_at}" data-duration="{DUR - src_at}" data-track-index="5">{SRC}</div>
    </div>
    <script>
      (function () {{
        "use strict";
        var tl = gsap.timeline({{ paused: true }});
        var page = document.getElementById("page");
        var edge = document.getElementById("roll-edge");
        // beat 1: roll-out - the page unrolls from the left; the rolled-edge light rides the front, then dies
        gsap.set(page, {{ xPercent: -100 }});
        gsap.set(edge, {{ opacity: 1 }});
        tl.to(page, {{ xPercent: 0, duration: {ROLL}, ease: "power3.out" }}, 0);
        tl.to(edge, {{ opacity: 0, duration: 0.25, ease: "power2.out" }}, {ROLL});
        // title and source: written by hand in the player species (T3); a plain settle here so the pick judges the stitch, not a font
        gsap.set("#title", {{ opacity: 0, y: 8 }});
        gsap.set("#source", {{ opacity: 0, y: 6 }});
        tl.to("#title", {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, {chart_at});
        tl.to("#source", {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, {src_at});
        tl.seek(0);
        window.__timelines = window.__timelines || {{}};
        window.__timelines["ledger-page-v1-{variant}"] = tl;
      }})();
    </script>
  </body>
</html>
'''


TOKENS = {
    "board": "--fg:#F2F2F2;--bg:#25313C;--surface:#25313C;--border:#8a94a0;--muted:#c9ced4;--brand:#1769C2;--accent:#F5B72E;--accent-2:#178C83;--font-body:Inter,sans-serif;--font-display:Inter,sans-serif;--font-mono:'Roboto Mono',monospace;",
    "plain": "--fg:#25313C;--bg:#F4E6C7;--surface:#F4E6C7;--border:#7a6f5a;--muted:#7a6f5a;--brand:#1769C2;--accent:#F5B72E;--accent-2:#178C83;--font-body:Inter,sans-serif;--font-display:Inter,sans-serif;--font-mono:'Roboto Mono',monospace;",
    "ink":   "--fg:#25313C;--bg:transparent;--surface:#F4E6C7;--brand:#25313C;--accent:#25313C;--accent-2:#25313C;--muted:#7a6f5a;--font-body:Inter,sans-serif;--font-display:Inter,sans-serif;",
}
def tokened(src_name: str, dst_name: str, tokens: str, comp_id: str) -> None:
    """A lane copy of a verbatim registry component: our six tokens on #root
    (the host's CSS variables do not reach a mounted sub-composition), the
    composition id renamed so the runtime keys a distinct timeline."""
    src = (HF / "compositions/components" / src_name).read_text(encoding="utf-8")
    old_id = src.split('data-composition-id="', 1)[1].split('"', 1)[0]
    out = src.replace("<style>", "<style>\n          #root { " + tokens + " }  /* Money Physics ledger tokens (P35 T1) */", 1)
    out = out.replace('data-composition-id="' + old_id + '"', 'data-composition-id="' + comp_id + '"')
    out = out.replace('window.__timelines["' + old_id + '"]', 'window.__timelines["' + comp_id + '"]')
    (HF / "compositions/components" / dst_name).write_text(out, encoding="utf-8")

tokened("ink-bleed-reveal.html", "ink-bleed-reveal-ledger.html", TOKENS["ink"], "ink-bleed-reveal-ledger")
for v in "ABC":
    reg = "plain" if v == "A" else "board"
    tokened("outline-draw.html", f"outline-draw-ledger-{v}.html", TOKENS[reg], f"outline-draw-ledger-{v}")
    tokened("chart-story.html", f"chart-story-ledger-{v}.html", TOKENS[reg], f"chart-story-ledger-{v}")
for v in "ABC":
    (HF / f"compositions/ledger-page-v1-{v}.html").write_text(build(v), encoding="utf-8")
(HF / "compositions/ledger-page-v1.html").write_text(build("C"), encoding="utf-8")  # the reference stitch = C
print("written A B C + reference")
