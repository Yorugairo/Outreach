"""Build the hosted review-pass page (Money Physics register: cream ground, charcoal ink, sunflower accent)."""
import json
from pathlib import Path

S = Path(__file__).parent
IMG = json.loads((S / "review-images.json").read_text(encoding="utf-8"))
PROOF = "https://claude.ai/code/artifact/d4bf959c-4fbe-4526-970b-64ec8070b196"
BUILDERS = "https://claude.ai/code/artifact/7563abf9-a673-4d9d-b19b-e756acd1ac90"
RACK = "https://claude.ai/code/artifact/fcbdced9-8d1c-4926-8b17-2f85c9edde11"

decisions = [
    ("Caption STAGE mode", "P34 · HG2 · DECIDED", "The only question was whether stage captions ship as the default when no dock is up (a change to a reviewed shot is a proposal until you rule). You ruled: “the captions on the ledger proof are awesome.” Stage is the default; recorded in doc 29 §9.25.", "stage", "doc 29 §9.25 (PICK: STAGE)"),
    ("The field: the deckle is the feature", "P35 · HG1 · DECIDED", "Settled in two rounds today. The page sits on the cream ground (the white beyond the deckle read as broken); the charcoal fills the paper to its deckle, so the edge only appears as the ink arrives; the line is pushed out to the deckle’s innermost boundary and just touches the cream at the deepest points; the chart builds inside it. E22 addenda 4–5.", "deckle", "doc 29 §9.26 E22 addenda 4–5"),
    ("The plates", "claim · DECIDED", "The delivered blank page is the ground; its deckle is the feature. The inked page is now made procedurally from it (charcoal to the deckle), so the generated rounded-board plate is retired. Both stay in the claim delivery for the record.", "plates", "claim approvals.json"),
    ("Roadmap by 0:45 (E24)", "doctrine · DECISION", "The analyst’s blueprint puts the roadmap by 0:45; doc 38 puts the promise 0:30–0:60 after the mini-payoff. The gate now WARNs past 0:45 and FAILs past 0:60 until you rule. Recommendation: tighten to 0:45, because the analytics agree with the analyst. The rest of that review is now gated and red on ep1: G45 (the first sentence, “The safest thing you own looks like this,” answers none of ai / bubble / real / survives / steel / paper — the thumbnail’s words), M10 (three stills over 6s in the first minute), M11 (the first chart at 0:09.5, full and unannotated, no sound hit), and E25’s M12 (25 chart docks held as homework, Bravos’ 0:09–0:50 across four plates first among them). Ep1 now: opening gate 28 FAIL, motion gate 8 FAIL.", None, "doc 29 §9.29–9.30 · OPERATOR-RULINGS E24–E25"),
    ("The chart is the proof, not the homework", "doctrine · E25 · DECIDED", "Your diagnosis: the drop-off is the static chart held across plates. Now a ruling and a gate (M12): a chart enters to prove the sentence being spoken and leaves when it has (hold ceiling 10s, 6s in the first minute); it never survives a plate change; when the narrative returns to it, it re-enters spotlit on the new datum. The shot table’s topic-governed exits are retired. Ep1 baseline red: Bravos’ chart 0:09–0:50 across four plates, ours 0:50–1:11 across three.", None, "doc 29 §9.30 · OPERATOR-RULINGS E25"),
    ("The host at the board", "C5 addendum · contact sheet", "Your call from the banner and avatar: the host belongs on the developed board. Three generated poses are in review quarantine (presenting, pointing, turned); the pointing pose already runs scene 1 of the proof: blank state derived with his arm intact, ink to the deckle, the chart built in the board he points at, the callout on the datum under his fingertip, captions pinned to the anchor. Approve the plates and choose which first-person beats carry him.", "host_sheet", "claim steel-and-paper-host-board-v1 · doc 29 §9.26 C5 addendum"),
    ("The handwriting face", "P35 · HG2", "The ink writes use Inter until a licensed handwriting face is picked. No generic cursive (it resolves per machine).", None, "brand sheet, type table"),
    ("Race on a page", "P35 · HG3 · READY FOR YOUR READ", "Re-timed after your note: values ease across the whole period, rows cross exactly where the values cross, the accent hands over there, the axis glides. Chart hygiene is back on all three builders (ticks with units, readable dates, inline names, basis label). Race at about 5–10s, decline 20–24s, combo 32–38s in the builders proof. The memory-share race itself is SOURCES-TO-VERIFY and refuses to render until quarterly vendor share is cited.", "builders", "doc 29 §9.26"),
    ("The targeted species", "P35 · T6/T7 · APPROVED", "“All worked really well, so that’s finally a real capability.” Callout, squiggle, spotlight glide, plate life, camera punch, each from a declared target.", "menu", "doc 29 §9.27 “Shipped”"),
    ("Focus rack", "P35 · T8 · DECIDED", "“Wash beats the focus rack.” The current wash/spot stays; the rack is retired as a proposal.", None, "doc 29 §9.27"),
]

reading = [
    ("docs/content-video-engine/41-LEDGER-PAGE-SPECIES.md", "The component doc: five beats, the page spec, the shot row, plates, sound, gates, open picks."),
    ("docs/content-video-engine/CAPABILITIES.md", "Ten new rows: opening gate, script-gate runner + recording refusal, declared-beat enumeration, motion gate wired, caption STAGE mode, ledger page, surface grammar + census, page sound cues, motion-menu species."),
    ("docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md", "§9.25 Shipped · §9.26 E22 addenda 2–3 (today’s corrections, in order) · §9.27 Shipped · §9.28 surface grammar."),
    ("docs/portable/OPERATOR-RULINGS.md", "E22 addenda 2–3; E23 (A3 = 10% of runtime)."),
    ("docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md", "§2 runner and gate rows · §3g surface choice · §4 the runner is step 1."),
    ("docs/content-video-engine/PIPELINE.md", "Stages 3–4 runner · 5 refusal · 7 page and species rows · 7c gate · 8 render refusal."),
    ("content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/SURFACE-CENSUS.md", "75 rows classified; six page candidates; four defect rows."),
    ("content/video_engine/projects/systems-and-blowups/steel-and-paper/REWRITE-ORDER-G.md", "Acceptance for the re-script = the two gate reports."),
]

p34 = [
    ("T1", "run_script_gates.py writes the gates report; both recorders refuse a missing, stale or failing one (--force logs the reason). Ep1 opening gate 26 → 27 FAIL."),
    ("T2", "A3 = 10% of runtime (E23); the retention cycle gated over the whole video (G36); one rehook per unit (G44)."),
    ("T3", "The screens file gains the DECLARED section; ep1 declares zero beats."),
    ("T4", "The build writes GATES-MOTION.md; render_episode.py refuses a full render on FAIL."),
    ("T5", "Caption STAGE mode in the player, declared per page, M08 enforced. Ep1 rebuilt: 5 FAIL — the six remaining still stretches are dock-held or silent."),
    ("T6", "The audit defers doc-38 beats 1–4 to the gate when the report exists. One row, one verdict."),
    ("E24/25", "Post-plan, from your analytics read: G45 + J12 (answer the thumbnail), M10 (6s stillness in the first minute), M11 (first chart 8–20s, spotlit, sound hit), M12 (the chart is the proof, not the homework). Baselines: opening gate 28 FAIL, motion gate 8 FAIL."),
]
p35 = [
    ("T0", "Surface grammar §9.28 and the census. Finding: the gate read a stale dock file — fixed in T4 (ep1 M01 23% → 15% still, M03 197s → 54s)."),
    ("T1", "The hyperframes stitch, three candidates. The first “bleed” was the wrong mechanism and is recorded as such."),
    ("T2", "ledger_page.py: series.json → page spec, builder by data shape, values verbatim; placeholders refused."),
    ("T3", "The species in the player, settled after four corrections: plain cream → field → tight line; page.plate / page.field_plate / page.board for the generated plates."),
    ("T4", "Shot rows ledger:<series>:<variant>…, timeline species, page beats as gate events, the gate on the timeline’s own clock."),
    ("T5", "Race, decline and combo builders on the page, each from its own component."),
    ("T6/T7", "Declared targets on species rows (build + gate M09); plate life, punch / focus zoom / pull-back, callout, spotlight, squiggle in the player. Not built: beat-freeze exit, radial reveal, push hand-off, weight-shift captions."),
    ("T8", "Focus rack vs wash/spot, side by side (proposal)."),
    ("T9", "Three CC0 page cues at −14 LUFS. No CC0 ink sound under 4s exists; the bleed cue is a water drop."),
]
edges = [
    "The ink writes read as a wipe of Inter until the handwriting face is picked.",
    "render_episode.py treats --t0 30 alone as a slice (never blocks) — consistent with its own tag logic.",
    "The audit’s break ration counts silent beat tags as marks (latent).",
    "Pre-existing dirty build outputs (timeline, caption pages) were regenerated by the rebuild; a backup of the pre-session versions sits in the session scratchpad.",
    "56 pre-existing test failures elsewhere in the engine (audio_synth, finance, console, remotion suites); none import the files this sprint touched.",
]


def esc(s: str) -> str:
    return s


def figure(key: str, cap: str) -> str:
    if not key or key not in IMG:
        return ""
    return f'<figure class="plate"><img src="{IMG[key]}" alt="{cap}"><figcaption>{cap}</figcaption></figure>'


rows = []
for i, (name, ref, body, img, where) in enumerate(decisions, 1):
    fig = ""
    if img == "plates":
        fig = f'<div class="pair"><figure class="plate"><img src="{IMG["blank"]}" alt="blank page plate"><figcaption>world-ledger-blank-page-v1</figcaption></figure><figure class="plate"><img src="{IMG["inked"]}" alt="inked board plate"><figcaption>world-ledger-inked-board-v1</figcaption></figure></div>'
    else:
        fig = figure(img, {"stage": "3:11–3:31 · top STAGE, bottom ANCHOR", "two_plate": "two-plate path", "deckle": "cream ground → charcoal fills to the deckle → the line at the deckle’s innermost boundary → ink → build", "menu": "callout · squiggle · spotlight glide · plate life · camera punch", "builders": "race re-timed; ticks, dates, inline names on race / decline / combo", "host_sheet": "presenting · pointing · turned (review quarantine)"}.get(img, ""))
    rows.append(f'''<article class="decision">
  <div class="dhead"><span class="chip {"done" if ("DECIDED" in ref or "APPROVED" in ref) else "open"}">{"decided" if "DECIDED" in ref else "approved" if "APPROVED" in ref else "open"}</span><h3>{name}</h3><span class="ref">{ref}</span></div>
  <p>{body}</p>
  {fig}
  <p class="where">Record the pick in <span class="path">{where}</span></p>
</article>''')

read_rows = "".join(f'<li><span class="path">{p}</span><span>{d}</span></li>' for p, d in reading)
p34_rows = "".join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in p34)
p35_rows = "".join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in p35)
edge_rows = "".join(f"<li>{e}</li>" for e in edges)

html = f'''<title>Money Physics Review Pass</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Roboto+Mono:wght@400;500&display=swap">
<style>
  :root {{
    --ground: #F4E6C7; --ink: #25313C; --ink-soft: #55606a; --rule: #d9c9a4; --paper-deep: #e9d9b2;
    --accent: #F5B72E; --open: #ED6A4A; --done: #178C83; --frame: #1B1E23; --frame-ink: #F2F2F2; --cobalt: #1769C2;
  }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
    --ground: #1B1E23; --ink: #F2F2F2; --ink-soft: #b8c0c8; --rule: #3a4048; --paper-deep: #242930; --frame: #0f1114; --frame-ink: #F2F2F2;
  }} }}
  :root[data-theme="dark"] {{
    --ground: #1B1E23; --ink: #F2F2F2; --ink-soft: #b8c0c8; --rule: #3a4048; --paper-deep: #242930; --frame: #0f1114; --frame-ink: #F2F2F2;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--ground); color: var(--ink); font-family: Inter, Arial, sans-serif; font-size: 17px; line-height: 1.55; }}
  main {{ max-width: 76ch; margin: 0 auto; padding: 48px 24px 96px; }}
  header {{ border-bottom: 3px solid var(--ink); padding-bottom: 20px; margin-bottom: 36px; }}
  .eyebrow {{ font-size: 12px; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-soft); font-weight: 600; margin: 0 0 8px; }}
  h1 {{ font-size: 40px; font-weight: 900; letter-spacing: -.02em; line-height: 1.05; margin: 0 0 12px; text-wrap: balance; }}
  header p {{ margin: 0; max-width: 62ch; color: var(--ink-soft); }}
  h2 {{ font-size: 13px; letter-spacing: .14em; text-transform: uppercase; font-weight: 700; margin: 48px 0 16px; padding-top: 12px; border-top: 1px solid var(--rule); color: var(--ink); }}
  h3 {{ font-size: 21px; font-weight: 700; margin: 0; letter-spacing: -.01em; }}
  .links {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 18px 0 0; }}
  .links a {{ display: inline-block; padding: 8px 14px; border: 2px solid var(--ink); border-radius: 999px; color: var(--ink); text-decoration: none; font-weight: 600; font-size: 14px; }}
  .links a:hover, .links a:focus-visible {{ background: var(--accent); border-color: var(--accent); color: #25313C; outline: none; }}
  .decision {{ padding: 20px 0 22px; border-bottom: 1px solid var(--rule); }}
  .decision:last-child {{ border-bottom: 0; }}
  .dhead {{ display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }}
  .ref {{ font-family: "Roboto Mono", monospace; font-size: 12px; color: var(--ink-soft); }}
  .chip {{ font-size: 11px; letter-spacing: .12em; text-transform: uppercase; font-weight: 700; padding: 3px 9px; border-radius: 999px; }}
  .chip.open {{ background: var(--open); color: #fff; }}
  .chip.done {{ background: var(--done); color: #fff; }}
  .decision p {{ margin: 0 0 12px; max-width: 68ch; }}
  .where {{ font-size: 14px; color: var(--ink-soft); }}
  .path, code {{ font-family: "Roboto Mono", monospace; font-size: 13px; background: var(--paper-deep); padding: 1px 6px; border-radius: 4px; color: var(--ink); word-break: break-all; }}
  .plate {{ margin: 12px 0 14px; background: var(--frame); border-radius: 6px; padding: 8px; }}
  .plate img {{ display: block; width: 100%; height: auto; border-radius: 3px; }}
  .plate figcaption {{ color: var(--frame-ink); font-size: 12px; letter-spacing: .04em; padding: 8px 4px 2px; opacity: .85; }}
  .pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  @media (max-width: 640px) {{ .pair {{ grid-template-columns: 1fr; }} h1 {{ font-size: 32px; }} }}
  ol.read, ul.log, ul.edges {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }}
  ol.read li, ul.log li {{ display: grid; grid-template-columns: minmax(0, 1fr); gap: 4px; padding: 10px 0; border-bottom: 1px solid var(--rule); }}
  ul.log li {{ grid-template-columns: 64px minmax(0, 1fr); }}
  ul.log b {{ font-family: "Roboto Mono", monospace; font-weight: 500; color: var(--done); }}
  ul.edges li {{ padding-left: 18px; position: relative; }}
  ul.edges li::before {{ content: ""; position: absolute; left: 0; top: .6em; width: 8px; height: 8px; background: var(--accent); border-radius: 50%; }}
  .cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }}
  @media (max-width: 760px) {{ .cols {{ grid-template-columns: 1fr; }} }}
  .note {{ font-size: 14px; color: var(--ink-soft); margin-top: 8px; }}
  a {{ color: var(--cobalt); }}
</style>
<main>
<header>
  <p class="eyebrow">Money Physics · Steel and Paper · 2026-09-03</p>
  <h1>Money Physics Review Pass</h1>
  <p>P34 gate improvements and P35 the ledger page are built to their human gates and sit in review. Decisions first, then what to read, then what changed. Everything is on <code>main</code>.</p>
  <div class="links">
    <a href="{PROOF}">Ledger species proof</a>
    <a href="{BUILDERS}">Builders proof (race · decline · combo)</a>
    <a href="{RACK}">Focus rack vs wash</a>
    <a href="http://localhost:8731/ledger-species-proof.html">Proof on localhost</a>
  </div>
  <p class="note">The proofs are scrubbable players: drag the bar, or seek with the clock. The hosted copies are the same files served from build-f.</p>
</header>

<h2>1 · Decisions waiting on you</h2>
{"".join(rows)}

<h2>2 · What to read, in order</h2>
<ol class="read">{read_rows}</ol>

<h2>3 · What changed</h2>
<div class="cols">
  <div><h3 style="margin-bottom:10px">P34 · gates as a pipeline</h3><ul class="log">{p34_rows}</ul></div>
  <div><h3 style="margin-bottom:10px">P35 · the ledger page</h3><ul class="log">{p35_rows}</ul></div>
</div>
<p class="note">Reversed by you today: “no generated paper imagery” → the ground and the board are generated plates (claim <span class="path">steel-and-paper-ledger-page-v1</span>, delivered).</p>

{figure("host", "the host at the board: blank → ink to the deckle → line inside → the chart in the board he points at → the callout on the datum")}
{figure("species_settled", "the species as first settled: plain cream → half savor → soak (scene 1) or scribble (scene 2) → tight outline → exact-value build")}

<h2>4 · Known rough edges</h2>
<ul class="edges">{edge_rows}</ul>
</main>
'''
out = S / "review-pass.html"
out.write_text(html, encoding="utf-8")
print("wrote", out, out.stat().st_size // 1024, "KB")
