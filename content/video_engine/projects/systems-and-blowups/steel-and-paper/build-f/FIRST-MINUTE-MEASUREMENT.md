# The first minute, measured — Steel and Paper (P40 T3, 2026-09-04)

**Every number here is a hypothesis from n = 1.** One episode, one retention curve
(1:05 cold drop, 4:39 overall, 75 % mobile). It proposes; a second episode's curve promotes.

## What was measured

The rebuilt player (P39's capture — native size, no wall-clock effects) stepped through
the first two minutes at 2 fps, 241 frames. Two E1 metrics in numpy
(`scripts/metrics/frame_metrics.py`): **motion energy** (mean absolute luminance change
between consecutive frames, 0–255) and the **centroid of change** (where on the frame the
change happened). Saliency and optical flow are deferred — they need OpenCV, which is not
installed. Windows are the viewer's 15 s windows (`viewer_windows.py`).

| window | span | motion energy, mean | max | centroid drift | on screen (`steel-and-paper.timeline.json`) |
|---|---|---|---|---|---|
| w0 | 0:00–0:15 | 6.56 | 58.2 | 0.082 | s01–s02, cuts at 7.8 s and 16.7 s |
| w1 | 0:15–0:30 | 5.36 | 34.3 | 0.079 | s03 share-office, cut at 29.1 |
| **w2** | **0:30–0:45** | **1.94** | **6.5** | **0.038** | **s04 gpu-crate-dock: a bare plate, Ken Burns 0.04, no dock, no species — held 29.1 → 50.4 (21.3 s)** |
| **w3** | **0:45–1:00** | 10.23 | 88.9 | 0.076 | the tail of that hold, then s05 at 50.4 with the **first dock** (`ev-divergence-v1`, four badges 52.5–56.4), cut at 57.3 — **the analytics drop lands here** |
| w4 | 1:00–1:15 | 5.89 | 101.0 | 0.049 | s06 three-notch-slate, dock exits at 70.9 |
| w5 | 1:15–1:30 | 7.98 | 71.6 | 0.076 | s07 signature-nib, s08 with a stamped dock at 86.8 |
| w6 | 1:30–1:45 | 14.26 | 60.8 | 0.102 | s09, s10, s11 with the railway pair |
| w7 | 1:45–2:00 | 8.16 | 52.8 | 0.068 | s11 → s12 dotcom |

## Does anything separate w3?

**Not w3 itself — the window before it.** w2 is the stillest window in the first two
minutes by a factor of three (energy 1.94 against a next-lowest 5.36; max 6.5 against
34–101 everywhere else; centroid drift half of any neighbour). Its energy is the Ken Burns
drift and nothing else — a plate held bare for 21 seconds across the 0:30–0:50 span. Then w3
is the *loudest* window of the first minute: the first evidence card arrives at 0:50 and
lands four badges in four seconds.

So the metric does not say "the drop window is still." It says **the drop follows the
stillest window, and it lands on the moment the first chart finally arrives — late and
dense.** Two readings, both consistent with what the gates already flag:

- **M10 / M01**: a 21 s bare hold inside the opening minute (ceiling 6 s in the first
  minute, 12 s anywhere).
- **M11**: the first chart enters at 0:50; the rule is 0:08–0:20, annotated, with a cue.

## Cross-read against the viewer (P36)

P36 found that **information gain does not track the drop** (w3 scores 5 against a
median of 3 — the script is dense exactly where it loses people) and that **confusion
does** (the unresolved-referent class, the counterparty evaporating). The frame metrics
add the third leg: the *picture* was empty for the 20 seconds before the drop, and then
delivered its first proof as a four-badge card at the moment the viewer's patience ran out.
Dense script + empty screen + late, crowded proof — that is the shape of 0:30–1:00.

Nothing here contradicts P36; it locates the visual half of the same failure.

## With OpenCV (added the same evening, under the operator's install permission)

The two deferred metrics, over the same 241 frames:

| window | span | optical flow (px/frame, downsampled) | saliency concentration (top 5 % share) |
|---|---|---|---|
| w0 | 0:00–0:15 | 1.20 | **0.276** — one clear focus at the open |
| w1 | 0:15–0:30 | 0.83 | 0.209 |
| **w2** | **0:30–0:45** | **0.15** — 5–10× less real motion than any other window; the Ken Burns drift is the only thing moving | 0.171 |
| **w3** | **0:45–1:00** | 1.47 | **0.168** — the four-badge card raises energy but *not* focus: a crowded card is diffuse, not a target |
| w4 | 1:00–1:15 | 0.88 | 0.200 |
| w5 | 1:15–1:30 | 1.07 | 0.193 |
| w6 | 1:30–1:45 | 1.66 | 0.170 |
| w7 | 1:45–2:00 | 1.02 | 0.148 |

Flow confirms the luminance read and removes the doubt that w2's stillness was a fade or a
colour shift: it is real stillness, the plate drifting and nothing else. Saliency adds the
piece motion energy could not: **focus decays monotonically from the open through the drop**
(0.276 → 0.209 → 0.171 → 0.168) — the frame gives the eye less and less to hold from 0:00 to
1:00 — and the first proof card does not restore it, because a card carrying four badges at
once is a field, not a point. (w7's 0.148 says the rest of the episode has the same habit;
the opening is where it costs the most.)

So the visual shape of the drop, in three instruments: **still (flow), diffuse (saliency),
then loud but still diffuse (energy without concentration).** The rewrite's first-minute
rule gains a clause: the first proof should be *one* thing the eye lands on, annotated —
which is what M11's "annotated on its divergence" already asks for.

## What this does not settle

- Whether the still window *causes* the exit or merely precedes it. n = 1 cannot say.
  A second episode with the first chart inside 0:08–0:20 and no bare hold over 6 s is the
  test, and its curve is the promotion gate for any threshold.
- The `still_share` column (frames under 0.5 energy) reads 0.0 everywhere because Ken
  Burns alone produces ~1–2 units of energy. If a "still" threshold is ever set, it sits
  around **2.0** on this scale — and that number is a hypothesis from this one render.

## For the rewrite

The first minute's fix is already written in the gates: break the 0:29–0:50 hold, bring
the first chart into 0:08–0:20 with its annotation and cue, and give the viewer something
to read on the screen while the script is at its densest. The measurement says the drop
sits precisely where those three rules are broken together.

Data: `FIRST-MINUTE-MEASUREMENT.json` beside this file (per-frame rows, windows), frames
rendered from `player.html` at 2 fps through `render_baseline.prepare_page`.
