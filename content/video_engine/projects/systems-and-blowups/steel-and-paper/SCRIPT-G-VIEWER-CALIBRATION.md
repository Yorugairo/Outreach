# SCRIPT G — the viewer, calibrated against the one retention curve we hold

Run 2026-09-03. 54 windows of 15s on the take's own word timings, plus the
package window, Codex headless at high reasoning effort, 0 errored. The reader
saw the title, the FINAL thumbnail, and the script one window at a time with a
two-window memory. It saw no tags, no doctrine, no ledger, and was never told a
test was happening. Artifacts: `SCRIPT-G-VIEWER-REPORTS.json`, `SCRIPT-G-VIEWER.md`.

**Verdict: PARTIAL. Two of the three measures agree with the analytics. One
does not, and it is the one the plan proposed to promote to WARN.**

---

## 1. The package — the reader was promised something else

Before a word of script, shown only the title and the thumbnail:

> *"The video promises to explain why the current AI boom may be a bubble and
> which tangible industries or assets — represented by steel — could endure
> after it deflates."*

Fifteen seconds in, the reader is holding *"What does the iron spike and the
repeated chart have to do with the video's promised explanation?"*, lists
*"what 'the safest thing you own' refers to"* as something it could not
follow, and answers the promise question: **not yet**.

The mechanical gate says the same thing by word match (G45), and the judge says
it by reading (J12). This is a third instrument, with no knowledge of either,
reaching the same verdict from the outside. **The package finding is
corroborated three ways.**

## 2. Beat recall — 25 of 37, and the misses cluster where the gate said

12 declared beats were never felt. Four of them sit in the first seven windows:

| beat | window | the sentence |
|---|---|---|
| `[payoff]` | w2 (0:30–0:45) | "So here's the original." |
| `[reflect]` | w4 (1:00–1:15) | "The chart is right." |
| `[opponent]` | w5 (1:15–1:30) | "And the opponent here isn't Bravos, and it isn't Nvidia." |
| `[rehook]` | w6 (1:30–1:45) | "But a machine you can test." |

These are the same beats the annotated opening gate flagged as landing outside
their windows, and `[opponent]` is the line the judge failed on J04 for stacking
three uncashed abstractions. Three instruments, one conclusion, reached
independently. **Recall agrees with the diagnosis.**

The other eight misses are the ring token (`[ring]` w29 and w46, both spike
recalls), the anaphora arc (`[anaphora]` w25 and w51 — including the final
triad), `[concede]` w12, `[loop]` w16, `[loop-close]` w17, and one `[new]`.
The ring and the anaphora are the two constructions doctrine most relies on to
carry a video's shape, and the blind reader felt neither.

## 3. Information gain — **the measure does not track the drop**

This is the negative result, and it decides the promotion.

| window | span | gain | note |
|---|---|---|---|
| w0 | 0:00–0:15 | 5 | |
| w1 | 0:15–0:30 | 6 | |
| w2 | 0:30–0:45 | 3 | |
| **w3** | **0:45–1:00** | **5** | **the analytics drop lands here** |
| w4 | 1:00–1:15 | 4 | |

Median gain across the episode is 3. The window where viewers actually leave
scores **above** it. So do all six dock-held stills the motion gate flagged
(gains 3, 5, 4, 3, 4, 4 at 0:33, 0:57, 2:24, 6:53, 8:14, 12:24). There is not a
single dead window in 13½ minutes, and no dead-run anywhere.

The script is information-dense everywhere, including exactly where it loses
people. **Density is not the problem, so a density measure cannot find it.**
Promoting gain to WARN would add a row that stays green on the one episode we
know failed.

## 4. Confusion — the measure that does track

22 real comprehension misses across the run, after excluding 20 items that were
the 15-second cut itself rather than the script (that filter is now in the
scorer; it was inflating the count by nearly half).

Ten are **unresolved referents** — "who exactly 'they' refers to" (6:15), "what
'the one from the top' refers to" (8:00), "what 'the board' refers to" (10:15),
"what the spike staying on the desk means" (13:15). That is the X1 antecedent
class, caught from the outside.

And one finding no other instrument produced: **the counterparty evaporates.**
"Bravos" is listed as unfollowable at 6:45, 9:00, 12:00 and 13:00. The script
introduces Bravos in window 2 and never re-establishes who they are, so by the
middle of the episode the reader has lost the argument's opponent entirely
while the script keeps arguing against them. No gate can see this. The judge
did not catch it. The blind reader did, four times.

---

## Recommendation for Human Gate 1 (the operator rules)

**Promote beat recall to FAIL.** It agreed with the analytics, it agreed with
the gate, and it caught the ring and the anaphora going unfelt, which nothing
else measures. An unperceived declared beat is laundering, and it should block
a recording.

**Do not promote information gain.** It is green on the episode that failed.
Keep it as an INFO row, because gain per window is still worth reading, but it
earns no authority.

**Promote confusion (V04) to WARN in gain's place.** It found the drop's
neighbourhood, it found the referent failures, and it found the counterparty
evaporating. It is the measure that carries signal on this episode.

**One instrument change already made:** window-cut artifacts are filtered out of
confusion. They were our own measurement noise, not the script's defect.

Until you rule, the VIEWER block stays advisory: every row is shown at INFO and
the verdict is unchanged. `run_script_gates.py --viewer-gate` is the switch.
