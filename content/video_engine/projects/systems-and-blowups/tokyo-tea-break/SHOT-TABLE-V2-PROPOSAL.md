# Tokyo short v2 — the shot table under E44 (proposal for the operator, 2026-09-06)

Same take (`SCRIPT-90S-VO.claude.txt`, the paused master, 88.82 s), same clips, same three ledger pages, same outro.
**No new asset, no new VO, no spend.** What changes is where the pages sit and how the clips arrive. The edit lands in
`build_short.shot_table` (the authored table; `SHOT-TABLE-SHORT.py` is generated from it).

## What v1 does and where it bleeds (`ANALYTICS-2026-09-06.md`, n = 51)

| v1 | span | world | curve |
|---|---|---|---|
| s01 clip a (the host enters the bar) | 0.00–5.09 | clip | 100 % |
| s02 clip b (dial and bill) | 5.09–8.99 | clip | **the cliff starts** |
| s03 clip c (blue-ties panel), `press 3` cue, hard cut | 8.99–17.17 | clip | **cliff to ~30 %** |
| s04 holdings page, spotlight + callout at 25.6 | 17.17–33.05 | ledger | flat |
| s05 clip g (two fingers) | 33.05–38.96 | clip | flat |
| s06 viewers-desk plate, suck transition, steam/trace/ticker | 38.96–44.88 | plate | step |
| s07 holdings page again (spiral), punch + callout | 44.88–54.52 | ledger | flat |
| s08 clip f (toll gate to fab) | 54.52–61.76 | clip | step |
| s09 Meta-yield bars, mount 2.43, callout + punch | 61.76–75.73 | ledger | flat, one late step |
| s10 clip a2 (counter, colder) | 75.73–82.62 | clip | flat |
| s11 outro card | 82.62–88.82 | clip | — |

Twelve seconds of clips before the first page; every step afterwards is a clip between pages.

## v2 — the page rolls out on the hook, the clips become mounts and docks

| v2 | span | on the words | world | how it arrives | what it proves |
|---|---|---|---|---|---|
| **s01** clip a, the host enters the bar | 0.00–3.0 | "Tokyo took a tea break." | clip | as v1 (this mount reads well) | the tea break, literally |
| **s02** the holdings page **rolls out** | 3.0–8.99 | "…an unfunded bar tab. The Fed hasn't moved, but your borrowing costs climbed anyway." | ledger | the six-beat roll-out (0.7 s) on "unfunded"; the line draws to the February peak under "bar tab"; the **coral drop draws** under "The Fed hasn't moved…"; the `−$122.6B` callout lands on "climbed anyway" (8.0) | the tab is the sell-off; the drop is why costs climbed |
| **s03** the panel over the page | 8.99–17.17 | "Three men in blue ties… sixty-three stick figures." | ledger + dock | the page **stays**; clip c mounts as a **dock** (inset, doc 29 docks) on "Three", dissolve on the word, no press cue; on "sixty-three stick figures" the dock swaps to the host (clip a2 or a still) | the archetype, without leaving the proof |
| **s04** the datum | 17.17–33.05 | "Here's what nobody on that panel is watching: our biggest lender. The Treasury's table shows… I ran risk at JPMorgan…" | ledger | the dock retracts on "watching"; **spotlight** on the June datum on "our biggest lender" (19.7), the callout on "over a trillion" (22.5) — the v1 spotlight at 25.6 moves up; the page unwinds from its point, never redraws (E40 §4) | the number, on the page it lives on |
| **s05** the opponent | 33.05–38.96 | "The opponent isn't the Fed; it's a Japanese balance sheet. Two numbers show where the money went:" | ledger + dock | clip g (two fingers) as a **dock** on "Two numbers", page stays | the map, on the proof |
| **s06** the desk | 38.96–44.88 | "a Treasury page, and your phone. By the end you'll read both numbers yourself." | plate | as v1 (the suck into the viewers' desk is the one transition that earns itself: it is the promise's image) — **but** the `suck 6` cue at 0.22 comes down with the press cue | the promise |
| **s07** the second pass on holdings | 44.88–54.52 | "Since February, Japan has sold… a tenth of the pile. The Treasury prints the new total monthly…" | ledger | as v1 (spiral return, punch on the February datum, callout) | the first number |
| **s08** the chips pledge | 54.52–61.76 | "Tokyo has pledged ten trillion yen to chips… the money went home, and the tab stayed here." | ledger + dock | **the page stays**; clip f (toll gate to fab) mounts as a dock on "pledged", retracts on "the tab stayed here" | the flow home, over the tab |
| **s09** Meta-yield bars | 61.76–75.73 | "So, the second number: it's on your phone. Pull up Meta…" | ledger | as v1 (mount 2.43, callout, punch) | the second number |
| **s10** the ring | 75.73–82.62 | "The Fed still hasn't moved. Tokyo is still on its tea break. And that unfunded bar tab is still ours." | ledger → clip | the holdings page **returns unwound** on "The Fed still hasn't moved" with the coral drop and the `−$122.6B` callout re-lit on "unfunded bar tab"; clip a2 (counter, colder) mounts on "still ours" as the last image | the ring on the mechanism, not the phrase (G15b) |
| **s11** outro | 82.62–88.82 | brand line, stitched | clip | as v1 | — |

Clip a2 moves from a 7 s scene to the closing mount; clip b (dial and bill) is **dropped** from the cut - its sentence is now
proved by the drop on the page. Nothing else is lost.

## The cues (`sound/SOUND-PLAN.json`)

| cue | v1 | v2 |
|---|---|---|
| `press 3` at 8.99 | 0.16 | **removed** (no cut there any more); if a dock mount wants a sound, a page-enter at 0.08 `[DERIVED: the 2026-09-05 metering, halved]` |
| `page enter 4` at 17.17 | 0.18 | moves to **3.0** (the roll-out) at 0.12 |
| `suck 6` at 38.96 | 0.22 | 0.12 |
| page enter / retract 7, retract 4 | 0.18–0.22 | 0.12 each - the pages are now the constant, the sound should not announce them |
| beds | 0.0226 | unchanged |

## What the curve should do if E44 is right

The cliff window (0:03–0:15) now holds a page from 3.0 s on. If the plateau starts near 0:05 instead of 0:17, the ruling
holds. If the cliff survives with the page on screen, the cause is upstream of the picture (the hook line, the voice, the
package) and the analytics file says so.

## Three decisions for the operator

1. **The dock or the cut for the blue-ties panel (s03).** The dock keeps the proof on screen for the whole tricolon; the cut
   keeps the panel full-frame for the joke. The data says dock; the joke says cut. Recommendation: dock, the joke lands on
   the caption.
2. **Whether clip b (dial and bill) is worth keeping anywhere.** It is the one image that shows *your* cost; under v2 the
   drop proves the sentence and the clip has no slot. Recommendation: drop it from this cut, keep it for the long form.
3. **The ring return (s10).** Returning the page under the ring is G15b in pictures; it also means the last thing seen before
   the card is the drop, not the host. Recommendation: page, then the host on "still ours".

## What running it costs

`build_short.py` shot-table edit, the cue edits, `python build_short.py`, the motion gate, `render_episode.py` with
`RENDER_ASPECT=9:16`. No new assets, no new VO. About an hour of lane time, no spend. The muted-caption judge (V-a) on the
render is still open from v1 and applies to v2.
