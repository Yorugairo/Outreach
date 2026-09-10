"""The Bravos ledger and report, from the measured events (cuts.json), the frames read by hand (SPECIES below) and the
deduped captions (transcript.json). House format: the WL reference's SHOT_LEDGER / REPORT, plus doc 46's distribution.

    python build_ledger.py            -> ../SHOT_LEDGER.claude.md, ../REPORT.claude.md
"""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOSSIER = HERE.parent
RUNTIME = 1196.55
TITLE = "China Just Triggered A New World Order"
URL = "https://youtu.be/1ZS5_txbOsc"

# species per shot number (1-based, inclusive ranges) - read from the 120 frames on 2026-09-10; COMP marks a NEW composition
# (a cut), everything else is a BUILD inside the held composition (a card lands, a line draws, a country lights, a node swaps)
SPECIES = [
    ((1, 3), "headline-card (press headline as a full plate, key word in the accent)", "external"),
    ((4, 4), "tv-embed: an article on a TV in a dark room", "external"),
    ((5, 10), "tv-embed: press cards STACK inside the TV, the newest lit, key phrase underlined", "external"),
    ((11, 11), "tv-embed: the collage dissolves to question marks", "external"),
    ((12, 12), "headline-card (The Atlantic, 'The Great Chinese Oil Mystery')", "external"),
    ((13, 13), "tv-embed: a lone '?'", "external"),
    ((14, 14), "tv-embed: metaphor icon (a pink chess knight on a board)", "external"),
    ((15, 15), "tv-embed: icon pair (US puck | China puck)", "external"),
    ((16, 19), "tv-embed: press cards (one at a time, then a grid)", "external"),
    ((20, 22), "tv-embed: news clip (CBC anchor), the room darkens at the end", "external"),
    ((23, 25), "tv-embed: news clip + an ICON RAIL of the predictions building beside the TV", "external"),
    ((26, 28), "icon board on black: the predictions, crossed out one by one ('6 Months Later')", "own"),
    ((29, 30), "line chart, DRAWN: Global Oil Supply and Demand (production first, then consumption)", "own"),
    ((31, 31), "map: the Gulf, dark, labelled", "own"),
    ((32, 34), "icon triad + title lands: Strategic Petroleum Reserves (barrels), then the subtitle band", "own"),
    ((35, 36), "small multiples: Japan SPR | US SPR, two panels drawing, the drop as a pink bar", "own"),
    ((37, 37), "line chart, DRAWN: Global SPR", "own"),
    ((38, 41), "line chart + DATUM RING: China daily crude imports drawing, then a dashed ellipse on the final drop + a flag chip", "own"),
    ((42, 42), "sponsor: strategy-session icon (maroon gradient ground begins)", "sponsor"),
    ((43, 44), "sponsor: stock line with event tags + a portfolio donut", "sponsor"),
    ((45, 48), "sponsor: icon diagrams (person, chart, a grid of people)", "sponsor"),
    ((49, 49), "icon chip: China", "own"),
    ((50, 50), "bar chart, RANKED, racing: SPR by country, China's bar runs out", "own"),
    ((51, 51), "isometric icon array: a field of oil silos", "own"),
    ((52, 52), "bar chart racing (a pendulum '?' icon at the left)", "own"),
    ((53, 53), "isometric array + 'Underground Oil Reserves' card", "own"),
    ((54, 55), "bar chart complete: 1,405 stamped, a dotted rule; the two cards beside", "own"),
    ((56, 56), "flow diagram over the map (dashed box, three icon chips)", "own"),
    ((57, 60), "map + YEAR STAMP (1996 -> 2022) + a B/W figure cutout (Clinton); Iran lit, a '$' chip crossed", "own"),
    ((61, 61), "map: Russia lit", "own"),
    ((62, 62), "map + title 'Petrodollar' + dashed ARCS from the Gulf, pink X's", "own"),
    ((63, 67), "map: Saudi lit; the world in white with the US pink; '$' chip; a chip flow beside the US", "own"),
    ((68, 73), "map: bare; Russia+Iran lit; arcs to the US crossed; China lit; an Atlantic Council press card beside China; '$' chip", "own"),
    ((74, 77), "map: Russia white, China pink, Iran; a yen chip; a dashed rectangle joins the chips to China", "own"),
    ((78, 80), "map + FIGURE STAMP on China ('1.4 Billion Barrels') + the silo/underground cards", "own"),
    ((81, 81), "numbered agenda: 'China's Gameplan' 1 | 2", "own"),
    ((82, 86), "flow diagram (Arab Oil States -> Control Oil Supply -> Geopolitical Leverage, 1973 tag, NYT card) - then the SAME diagram with China swapped in (the rhyme) + a 'Fall of the Petrodollar' card", "own"),
    ((87, 87), "numbered agenda: tile 2 revealed ('New Geopolitical Weapon')", "own"),
    ((88, 88), "line chart: Share of Global Manufacturing (China)", "own"),
    ((89, 91), "TREEMAP: China's exports by partner; partners X'd out in pink; the treemap shrinks, two chips flow", "own"),
    ((92, 93), "icon diagram: China <-> US -> Trade Partners; an icon with a green up-arrow", "own"),
    ((94, 98), "press collage stacking (WaPo, Gadgets360, FT, Politico) + the two thesis icons + a 'Trust' handshake", "external"),
    ((99, 104), "MULTI-LINE chart drawing (US/Germany/UK/Japan), TERMINAL TAGS name each line at its end; China added at the bottom; value bars at the ends (4.68% / 1.69%)", "own"),
    ((105, 106), "bar chart, horizontal: current 10-year yields with values", "own"),
    ((107, 110), "flow diagram: safe-haven chip -> Global Economic Order, a SPAN BRACKET ('Decades')", "own"),
    ((111, 111), "press collage (The Times, Inquirer, The Economist)", "external"),
    ((112, 112), "diagram skeleton: 'Global Economic Order' dashed box, empty tiles", "own"),
    ((113, 114), "scale metaphor: Threat vs Opportunity tipping ('Portfolio Positioning')", "own"),
    ((115, 120), "CTA: a check icon, a person in a pink frame, person <-> bull, a grid of people, 'Investment Strategy Call', 'Book a Call'", "cta"),
]
COMP = {1, 4, 5, 11, 12, 13, 14, 15, 16, 20, 23, 26, 29, 31, 32, 35, 37, 38, 42, 43, 45, 49, 50, 51, 52, 53, 54, 56, 57, 61, 62, 63, 68, 74, 78, 81, 82, 87, 88, 89, 92, 94, 99, 105, 107, 111, 112, 113, 115, 119}
SPONSOR = (393.0, 428.0)   # 6:33 - 7:08, the strategy-session pitch (its own maroon ground)


def species_of(n: int) -> tuple[str, str]:
    for (a, b), s, lane in SPECIES:
        if a <= n <= b:
            return s, lane
    return "unclassified", "?"


def mmss(t: float) -> str:
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:04.1f}"


def main() -> None:
    cuts = json.load(open(HERE / "cuts.json"))
    tr = json.load(open(HERE / "transcript.json"))
    ends = cuts[1:] + [RUNTIME]
    shots = [(i + 1, a, b, b - a) for i, (a, b) in enumerate(zip(cuts, ends))]
    frames = sorted((HERE / "shots").glob("shot_*.jpg"))

    def line_for(a: float, b: float) -> str:
        text = " ".join(s["text"] for s in tr if s["t0"] < b and s["t1"] > a and s["text"] != "[music]")
        return (text[:96] + "...") if len(text) > 96 else text

    rows = ["# SHOT LEDGER (Claude, 2026-09-10): the measured events, the species read from the frames, the spoken line",
            "",
            f"Source `{URL}` - {TITLE}, Bravos Research, {mmss(RUNTIME)}. Events measured as local maxima of the frame-to-frame",
            "difference (96x54 grey, 4 fps, mean |delta| >= 6/255, 1 s refractory) - a cut OR a build inside a composition; `COMP`",
            "marks a new composition (a true cut), the rest are builds. The frame is 0.5 s after the event. Gemini's ledger in this",
            "folder was a fixed 5.7 s sampler (every duration a multiple of 5.7) with every species `unclassified`; this one is the read.",
            "",
            "| # | Start | End | Dur | Kind | Frame | Species (read) | Lane | Spoken line |",
            "| :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :--- |"]
    for n, a, b, d in shots:
        s, lane = species_of(n)
        f = frames[n - 1].name if n - 1 < len(frames) else ""
        rows.append(f"| {n} | {mmss(a)} | {mmss(b)} | {d:.1f}s | {'COMP' if n in COMP else 'build'} | [{f}](claude-watch/shots/{f}) | {s} | {lane} | {line_for(a, b)} |")
    (DOSSIER / "SHOT_LEDGER.claude.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

    def dist(durs):
        q = st.quantiles(durs, n=4)
        return dict(n=len(durs), cpm=len(durs) / (RUNTIME / 60), mean=st.mean(durs), median=st.median(durs), q1=q[0], q3=q[2], iqr=q[2] - q[0],
                    longest=max(durs), shortest=min(durs), ge6=sum(1 for d in durs if d >= 6) / len(durs))
    ev = dist([d for *_, d in shots])
    comp_starts = sorted(a for n, a, *_ in shots if n in COMP)
    comp_durs = [b - a for a, b in zip(comp_starts, comp_starts[1:] + [RUNTIME])]
    cp = dist(comp_durs)
    words = sum(len(s["text"].split()) for s in tr if s["text"] != "[music]")
    bounds = [0, 90, 0.17 * RUNTIME, 0.45 * RUNTIME, 0.55 * RUNTIME, 0.85 * RUNTIME, RUNTIME]
    names = ["P1 The Open", "P2 The Engine", "P3 The Gap", "P4 The Pivot", "P5 The Payoff", "P6 The Close"]
    ph = []
    for name, a, b in zip(names, bounds, bounds[1:]):
        w = sum(len(s["text"].split()) for s in tr if a <= s["t0"] < b and s["text"] != "[music]")
        n_ev = sum(1 for _, x, *_ in shots if a <= x < b); n_c = sum(1 for x in comp_starts if a <= x < b)
        ph.append((name, a, b, n_ev, n_c, w, w / ((b - a) / 60)))
    lanes = {}
    for n, a, b, d in shots:
        _, lane = species_of(n); lanes[lane] = lanes.get(lane, 0) + d

    R = [f"# PRODUCTION REFERENCE REPORT (Claude, 2026-09-10): {TITLE}", "",
         f"- **Source:** `{URL}` - Bravos Research, {mmss(RUNTIME)} ({RUNTIME:.1f} s), 1280x720 av1, 29.97 fps",
         f"- **Transcript:** native captions, deduped (YouTube's rolling windows repeat lines): **{words} words, {words / (RUNTIME / 60):.1f} WPM** over the runtime",
         f"- **Visual events:** {ev['n']} ({ev['cpm']:.1f}/min) - of which **{cp['n']} new compositions ({cp['cpm']:.1f}/min)** and {ev['n'] - cp['n']} builds inside a held composition",
         f"- **Sponsor:** {mmss(SPONSOR[0])}-{mmss(SPONSOR[1])} ({SPONSOR[1] - SPONSOR[0]:.0f} s) inside P3, on its own maroon ground; the CTA is the last {RUNTIME - shots[114][1]:.0f} s",
         "", "## The distribution (doc 46's table, recomputed here)", "",
         "| | events (cuts + builds) | compositions (cuts only) | WL reference (doc 46) |", "|---|---|---|---|",
         f"| per minute | {ev['cpm']:.1f} | {cp['cpm']:.1f} | 5.9 |",
         f"| mean | {ev['mean']:.1f} s | {cp['mean']:.1f} s | 10.1 s |",
         f"| median | {ev['median']:.1f} s | {cp['median']:.1f} s | 9.6 s |",
         f"| Q1 / Q3 | {ev['q1']:.1f} / {ev['q3']:.1f} s | {cp['q1']:.1f} / {cp['q3']:.1f} s | 6.3 / 13.2 s |",
         f"| IQR | {ev['iqr']:.1f} s | {cp['iqr']:.1f} s | 6.9 s |",
         f"| longest | {ev['longest']:.1f} s | {cp['longest']:.1f} s | 26.0 s |",
         f"| shortest | {ev['shortest']:.1f} s | {cp['shortest']:.1f} s | 1.6 s |",
         f"| >= 6 s | {ev['ge6'] * 100:.0f} % | {cp['ge6'] * 100:.0f} % | 80 % |",
         "", "**The finding:** the picture changes six times a minute, the composition only two and a half. The 'clean' feel is",
         "builds inside a held frame - a card lands, a line draws, a country lights, one node swaps - not cutting. Their cut",
         "rate is well under the WL reference's; their event rate matches it. This is E21 (never still) answered by BUILDS, and",
         "E50's deployed clock answered by a composition that keeps earning its hold.", "",
         "## Screen time by lane", "",
         "| lane | seconds | share |", "|---|---|---|"] + [f"| {k} | {v:.0f} | {v / RUNTIME * 100:.0f} % |" for k, v in sorted(lanes.items(), key=lambda kv: -kv[1])] + [
         "", "external = other people's claims (press cards, news clips) - always framed on the TV or as a stacked card; own = Bravos' analysis on the bare black stage.", "",
         "## The six phases (the house grid; words from the deduped captions)", "",
         "| phase | window | events | compositions | words | WPM |", "|---|---|---|---|---|---|"] + [
         f"| {n} | {mmss(a)}-{mmss(b)} | {e} | {c} | {w} | {wpm:.0f} |" for n, a, b, e, c, w, wpm in ph] + [
         "", "Gemini's report gave 214-249 WPM per phase against a 177.7 total - the rolling caption windows counted twice (4,530 words for a 3,543-word take). The honest phases run near the mean.", "",
         "## The grammar (what the frames say; what it maps to in our engine)", "",
         "1. **One stage, one accent.** Near-black charcoal, one pink, white type; green only for 'up' and the CTA. Titles top-centre in the accent; a small source line bottom-left (`Data: ... Source: ..., Bravos Research`). -> our brand tokens already say this (charcoal 60 / chalk 30 / coral+sunflower 10); we use two accents, they use one.",
         "2. **Other people's claims are framed; their own analysis is bare.** The first 1:40 plays entirely on a TV in a dark room (articles, news clips); the moment the argument is theirs the TV is gone and the stage is black. -> a WORLD plate for the external lane (`tv-embed`) we do not have; our docks could carry it.",
         "3. **The press card is their proof species.** A real screenshot cropped to the headline, the key phrase underlined in the accent, cards stacking one at a time with the newest lit (shots 5-10, 16-19, 94-98, 111). -> our `record document` species is the typewriter; a `press-card` dock (still + underline callout) is the missing sibling.",
         "4. **Charts draw and name themselves at the end.** Lines draw left-to-right, the subject series in pink, context grey; TERMINAL TAGS (pill labels at the line ends, 99-104) - exactly E53's 'named at its end'; the value bars at the line ends (104) then become the next chart (105). -> we have the terminal tag; the line-end-to-bar handoff is a morph we have (P47 T3).",
         "5. **The ring is a dashed ellipse on the datum** (38-41: the final drop of China's imports, with a flag chip beside) - E56's one allowed use, done as a dashed oval, not a circle. -> our callout ring; consider the dashed ellipse form.",
         "6. **Ranked bars race and stamp** (50-55: SPR by country; China's bar runs out, `1,405` in a pink capsule, a dotted rule). -> our story bars + the E53 reference rule.",
         "7. **The map is a live vector stage** (31, 57-80): countries light in pink/white as named, dashed arcs with X's for blocked flows, year stamps as pink tags, a B/W figure cutout (Clinton), a figure stamp on a country ('1.4 Billion Barrels'). -> our crossings map is a painted plate with hop traces; a `vector map` species (SVG world, lit countries, arcs) is the gap.",
         "8. **Diagrams are dashed boxes of icon chips joined by arrows**, and the SAME diagram is reused with one node swapped (82-86: Arab Oil States -> China) - the rhyme as a visual. Span brackets ('Decades', 107-110). -> our `bracket` exists; a `flow-diagram` species (chips + arrows + a swap) is the gap.",
         "9. **A numbered agenda** ('China's Gameplan' 1 | 2, revealed in turn, 81/87) sets the second half. -> a stage caption device we could do with figures.",
         "10. **The treemap with X marks** (89-91: exports by partner, partners crossed out) is a part-to-whole we have not built (E53 s7 has the donut exception; the treemap is a second one worth a ruling).",
         "11. **Motion is restrained:** slow pushes on the map between countries, a drift on the TV mock, chart draws; no host, no camera shake, no particles. Nothing is ever still and nothing ever spins.",
         "12. **Sound:** a continuous narration at 178 WPM with no pauses for effect; the sponsor block is the only tonal break.",
         "", "## Artifacts", "",
         "- `SHOT_LEDGER.claude.md` - every event with its species and line; `claude-watch/shots/` - one frame per event (0.5 s after) and ten contact sheets",
         "- `claude-watch/cuts.json` (event times), `claude-watch/d1.npy` (the per-sample difference), `claude-watch/transcript.json` (deduped captions)",
         "- Gemini's `REPORT.md` / `SHOT_LEDGER.md` / `frames/` are kept as its own artifact; its shot times are a 5.7 s sampler, its species empty, its phase word counts doubled."]
    (DOSSIER / "REPORT.claude.md").write_text("\n".join(R) + "\n", encoding="utf-8")
    print(f"events {ev['n']} ({ev['cpm']:.1f}/min), compositions {cp['n']} ({cp['cpm']:.1f}/min); words {words}; median event {ev['median']:.1f}s, median composition {cp['median']:.1f}s")


if __name__ == "__main__":
    main()
