# The long-form capability audit - the either-format proof (2026-09-18)

**P68 T3.** The operator's correction this file discharges: *"i had told you to build to be
able to run either long form or short form. sounds like that didn't happen."* (E99 s81,
`docs/portable/OPERATOR-RULINGS.md:3280`).

**The verdict in one paragraph.** The engine is not portrait. Its stage constants read
16:9 FIRST and branch to 9:16 (`build_scene_timeline_f.py:148` `ASPECT = None`;
`render_baseline.py:39` `STAGE = {"16:9": (1920, 1080), "9:16": (1080, 1920)}`;
`scene-evidence-engine.mjs:112-114` reads `--stage-w` / `--stage-h` from CSS and derives
`PORTRAIT = STAGE_H > STAGE_W`), 63 of the 69 distinct goldens render on the 1920x1080
default, and the long-form render door is the 1440p tool the operator just confirmed
(`render_episode.py:94` - `#stage` at device scale 4/3 = **2560x1440**, `:38` `FPS = 24`).
So the format switch is real and it is built. What is NOT built is any *use* of it: the
only 16:9 cut on disk is `build-f` (ep1, August), and its compiled timeline carries **0
ledger pages, 0 species, 0 chart_to transforms, 0 camera rows, 0 idle declarations, 43
docks all on the default arrival, and exactly two exit tokens (`cut` 43, `wipe_right`
32)**. Every mechanism built since 2026-09-05 has a 16:9 GOLDEN and no 16:9 SCENE. That is
the whole gap, and E99 s60 already names why it matters: a golden fixture is not a scene.

**The three answers in the table's "16:9" column, and what each is worth:**

| Answer | Means | Worth |
|---|---|---|
| **CUT** | it ran in a 16:9 cut - `build-f`, August 2026 | the only real evidence |
| **GOLDEN** | a 1920x1080 golden frame locks its pixels; no cut has used it | the mechanism renders at 16:9; its *choreography at 16:9* is unproven |
| **NONE** | neither | it has never drawn a landscape pixel outside a unit test |

## How every number here was measured (re-runnable)

```bash
# the two validation commands this slice owes
python content/video_engine/scripts/docs_find.py "caption strip 16:9"
python content/video_engine/scripts/lint_species_choice.py \
  content/video_engine/projects/systems-and-blowups/steel-and-paper --build build-f \
  --table content/video_engine/projects/systems-and-blowups/steel-and-paper/SHOT-TABLE-F.py --long

# what ep1's only long-form timeline actually contains
python -c "import json,collections;tl=json.load(open('content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/steel-and-paper.timeline.json',encoding='utf-8'));sc=tl['scenes'];print(len(sc),collections.Counter(s.get('exit') for s in sc),sum(len(s.get('species') or []) for s in sc),sum(len(s.get('chart_to') or []) for s in sc),sum(1 for s in sc if s.get('camera')),tl.get('aspect'),tl.get('caption_style'),tl.get('kinetics'))"

# the proven recipes, by the format they were proven in
python -c "import json,collections;r=[json.loads(l) for l in open('docs/EFFECTS-CATALOG.jsonl',encoding='utf-8')];p=[x for x in r if x['axis']=='recipe' and x['status']=='proven'];print(len(p),collections.Counter(x['proof']['project'] for x in p))"

# the goldens, by stage
ls content/video_engine/tests/golden/frames/ | sed 's/@.*//;s/\.png//' | sort -u | wc -l
grep -c '_timeline(.*"9:16"' content/video_engine/tests/golden/build_golden_sources.py   # -> 3, declared inline
# the other three portrait goldens pass the aspect through a helper - the full 9:16 set is six:
#   vecmap-arc (:726), art-embed (:1167), dock-pair-9x16 (_dock_pair, :1246),
#   newsreel-strip-9x16 (:1413), newsreel-strip-above (:1419), verdict-stack-9x16 (:1633)

# the plate drift dial, as actually authored anywhere on disk
grep -rhoE "drift=[0-9]+" content/video_engine/projects/ | sort | uniq -c
```

**Verbatim output of the first validation command:**

```
0 hit(s) in capabilities, assets, effects, manifest, index, topics, gates, animation, craft
```

**Verbatim head and E61 block of the second** (it exits 2 on the plan's own form of the
command - see gap G-11):

```
species by sentence - steel-and-paper - SHOT-TABLE-F.py + build-f/timeline.json - 240 sentences - 75 rows - 806.5 s
INFO 240 sentences - 81 carry an act - 58 have a row firing - 76 have an available species and no row
INFO long form (806 s): E61 - every plate names its use (;use=landing|bridge|reset)
WARN   0.00-  7.70 - plate world-spike-desk-v1 - no named use (E61: a plate is a landing surface, a bridge or a reset, and says which)
...
WARN 805.00-806.50 - plate world-spike-rest-v2 - no named use (E61: a plate is a landing surface, a bridge or a reset, and says which)
```

**75 WARN rows, one per plate window: not one plate in the only long form we have names its
use.** `--long` exists and does exactly what E61 asks -
`lint_species_choice.py --help`: `--long   apply E61's plate-use check regardless of runtime`.

## Recall (docs_find, run 2026-09-18 before any mechanism below was named)

- `Recall: docs_find "caption strip 16:9" -> 0 hits` across capabilities, assets, effects,
  manifest, index, topics, gates, animation, craft. There is no 16:9 caption-strip
  capability row. What exists is the constant: `ledger_page.py:1159`
  `CAPTION_ANCHOR = {"9:16": (80, 1290, 800, 150), "16:9": (145, 878, 1630, 82)}`.
- `Recall: docs_find "PHRASE captions" -> docs/content-video-engine/CAPABILITIES.md:66` -
  titled **"(shorts)"**; the engine's test is `TL.caption_style === "phrase"`
  (`scene-evidence-engine.mjs:7532`), a timeline field with no aspect condition anywhere.
- `Recall: docs_find "caption STAGE mode" -> CAPABILITIES.md:23`; the 16:9 rule is
  `scene-evidence-player.template.html:524`, the 9:16 override `:234`.
- `Recall: docs_find "the idle" -> CAPABILITIES.md:71` - 20 px long form, 30-40 shorts.
- `Recall: docs_find "the camera arrival" -> CAPABILITIES.md:84`;
  `"the camera over layers" -> :149`; the persistent similarity `:85`; the targeting law `:124`.
- `Recall: docs_find "remotion kit outro" -> CAPABILITIES.md:63`.
- `Recall: docs_find "authoring kit" -> CAPABILITIES.md:90` - "one door for both formats", WIRED.
- `Recall: docs_find "one-shot floor" -> CAPABILITIES.md:327`;
  `"vertical safe-box gate" -> :269`; `"portrait parity gate" -> :273`; `"G2 short mode" -> :201`.
- `Recall: docs_find "Mike" -> CAPABILITIES.md:159` (the Flow stdio dispatcher, `create_flow_image`)
  and `:181` (the Flow character pack, `@Mike` entity `dab5d902`), plus
  `docs/agent-memory/operator/mp-host-identity.md`.
- `Recall: docs_find "16:9" -> docs/content-video-engine/03-SYSTEM-ARCHITECTURE.md:275` -
  "Dual-format rendering (9:16 is a layout, not a crop)". The doctrine was written down at
  the start; the engine kept it; no long form ever exercised it.
- Every other mechanism below carries its own `docs_find` hit in the table's last column;
  each was run before the row was written.

**Path correction** (found while verifying, same class as the plan's own outro correction):
`CAPABILITIES.md:75` cites the head cutouts as `assets/heads/manifest.json`. There is no
such path - `git ls-files | grep assets/heads` returns exactly one file,
`content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/assets/heads/manifest.json`
(5 heads, `review_state: approved`, `render_eligible: true`, E68).

---

## The table - one row per mechanism the shorts proved

**Dial column.** Read it literally: the engine has exactly **one** per-format amplitude dial,
the plate drift (E99 s55 `OPERATOR-RULINGS.md:3228`, s64 `:3246`, s65 `:3248` - **20 px long
form, 30-40 shorts**). Every other "-" means the mechanism takes the same numbers in both
formats and the only thing that changes is the stage it is measured against. Where a real
second dial exists (caption sizes, safe boxes, gate windows, the render stage) it is named.

| # | Mechanism | Built at (path:line) | 16:9 | Evidence at 16:9 | Dial per format (ruling) | Recall (docs_find) |
|---|---|---|---|---|---|---|
| 1 | Word-level caption pages (kinetic + quiet) | `build_caption_pages.py:15-22`; `CAPABILITIES.md:22` | **CUT** | build-f: 464 pages, 5.3 words/page, **34.5 pages/min** over 806.5 s (M06 PASS, `build-f/GATES-MOTION.md`) | `CHAR_BUDGET` 34 / `MAX_WORDS` 6 is the long default; the Tokyo short overrides to 28 / 6 (`build_caption_pages.py:20`) | `CAPABILITIES.md:22` |
| 2 | Caption STAGE mode | `scene-evidence-player.template.html:524`; `CAPABILITIES.md:23` | **CUT** | build-f `caption_modes: ["stage","anchor"]`; 110 stage / 354 anchor pages | 64 px / 800 both ways; the 9:16 rule only re-places it (`template:234`) | `CAPABILITIES.md:23` |
| 3 | Anchor caption strip | `ledger_page.py:1159` `CAPTION_ANCHOR["16:9"] = (145, 878, 1630, 82)` | **CUT** | build-f, the 82 px strip = two lines at 33 px / 1.24 | **33 px / 600 landscape** vs **48 px / 800 portrait** (E62, `template:305-317`) | `CAPABILITIES.md:22` |
| 4 | PHRASE captions | `scene-evidence-engine.mjs:7532`; `template:537`; `CAPABILITIES.md:66` | **NONE** | none - build-f `caption_style: null`. Titled "(shorts)" by ruling, **not by code**: `TL.caption_style === "phrase"` has no aspect condition | a shorts style by ruling only | `CAPABILITIES.md:66` |
| 5 | The caption moves under a card (E62 band) | `build_scene_timeline_f.py` `caption_band` / `stamp_caption_bands`; `CAPABILITIES.md:24` | **NONE** | none - build-f has 43 docks and no band; the band is computed from dock boxes, so it is aspect-free | - | `CAPABILITIES.md:24` |
| 6 | Caption arrival stagger / the living caption | `kinetics/stagger.mjs`; `CAPABILITIES.md:46`, `:47` | **NONE** | none | - | `CAPABILITIES.md:46` |
| 7 | Plate world + Ken Burns | `build_scene_timeline_f.py:3632`; `CAPABILITIES.md:18` | **CUT** | build-f: **75 of 75** scenes carry a non-zero `ken_burns`; 73 distinct plates (M04 PASS) | - | `CAPABILITIES.md:18` |
| 8 | The idle (breath / drift / pulse / figure / live) | `kinetics/idle.mjs:16-60`, `:138` `idleDriftPx`; `CAPABILITIES.md:71` | **NONE** | none - build-f declares an idle on **0 of 75** scenes and `kinetics: null` | **20 px long / 30-40 shorts** (E99 s55 `:3228`, s64 `:3246`, s65 `:3248`). On disk: `drift=35` x157, `drift=20` x19 - and all 19 are the R26-133 alive PROBE (`tokyo-tea-break/build-p61-alive/`), never a cut | `CAPABILITIES.md:71` |
| 9 | The alive plate (background wall is a clip) | `build_plate_library.py` `_layer_life`; `CAPABILITIES.md:150` | **NONE** | none | the drift, as above | `CAPABILITIES.md:150` |
| 10 | The layered plate (2.5D) | `comfy_depth_split.py`; `CAPABILITIES.md:147` | **NONE** | none | E99 s65 `:3248`: Ken Burns + 20 px drift IS the long-form plate life; parallax under a free drift reads as random | `CAPABILITIES.md:147` |
| 11 | Plate-life cutouts (stop-action on a bare plate) | `scene-evidence-engine.mjs:15077`; `kinetics/stopaction.mjs` | **NONE** | none - positions are stage fractions (`c.x * STAGE_W`), so it is aspect-free by construction | 12 fps stepped, render at 24 (E99 s36 `:3172`) | `CAPABILITIES.md:75` |
| 12 | The plate library (330 plates, layer sidecars) | `build_plate_library.py`; `sources/PLATE-LIBRARY.json`; `CAPABILITIES.md:148`, `:183` | **CUT** | build-f drew 73 of them | - | `CAPABILITIES.md:148` |
| 13 | The vector-map world | `species/vecmap.mjs`; `CAPABILITIES.md:101` | **NONE** | its golden is declared 9:16 (`build_golden_sources.py:751`) | - | `CAPABILITIES.md:101` |
| 14 | LEDGER PAGE species (the channel signature) | `scene-evidence-engine.mjs` `buildLedger`; `ledger_page.py:1154` `STAGE_PX["16:9"]=(1920,1080)`; `CAPABILITIES.md:56` | **GOLDEN** | **`build-f/GATES-MOTION.md:9` reads `ledger_pages: 0`** - the signature form has never run in a long form | - | `CAPABILITIES.md:56` |
| 15 | Page MOUNT entry | `CAPABILITIES.md:64` | **GOLDEN** | none in a cut | - | `CAPABILITIES.md:64` |
| 16 | The page VORTEX / spiral return | `species/spiral.mjs`; `CAPABILITIES.md:57` | **GOLDEN** (`spiral-return`) | none in a cut | - | `CAPABILITIES.md:57` |
| 17 | `page_enter`: axes / built / throw / snap | `scene-evidence-engine.mjs` (`SNAP_S`, `THROW_S`); `CAPABILITIES.md:76` | **GOLDEN** | none in a cut | - | `CAPABILITIES.md:76` |
| 18 | `chart_to: rescale` | `scene-evidence-engine.mjs` `lpPaintRescale`; `CAPABILITIES.md:115` | **GOLDEN** | none - build-f has **0** `chart_to` | - | `CAPABILITIES.md:115` |
| 19 | `chart_to: extend` | `lpPaintExtend`; `CAPABILITIES.md:116` | **GOLDEN** (`ledger-extend`) | none | - | `CAPABILITIES.md:116` |
| 20 | `chart_to: recast` (keyed) | `lpPaintRecastKeyed`; `CAPABILITIES.md:117` | **GOLDEN** (`ledger-keyed`) | none | - | `CAPABILITIES.md:117` |
| 21 | `chart_to: morph` (ARAP, mid-page) | `kinetics/arap.mjs`; `CAPABILITIES.md:118` | **GOLDEN** (`morph-planted`) | none | - | `CAPABILITIES.md:118` |
| 22 | `chart_to: remake` (whole-chart) | `kinetics/chartxf.mjs`; `CAPABILITIES.md:119` | **GOLDEN** (`remake-bars-to-line`, `remake-line-to-bars`) | none | - | `CAPABILITIES.md:119` |
| 23 | `chart_to: compare` (the felt number) | `species/compare.mjs`; `CAPABILITIES.md:28` | **GOLDEN** (`compare-morph`) | none - never used on a shipped cut in either format | - | `CAPABILITIES.md:28` |
| 24 | `chart_to: park` / un-park | `lpPaintPark`; `CAPABILITIES.md:120` | **GOLDEN** | none | - | `CAPABILITIES.md:120` |
| 25 | Breakthrough bars (re-scale, burst) | `species/breakthrough.mjs`; `CAPABILITIES.md:86` | **GOLDEN** | none; E60 ruled "the re-scale is the way" | - | `CAPABILITIES.md:86` |
| 26 | N-TIER pages (small multiples, one x) | `species/tiers.mjs`; `ledger_page.py` `tiers`; `CAPABILITIES.md:102` | **GOLDEN** (`tiers-two`) | none. Note: the band floor (~250 px) was sized for a **9:16** plot | band heights are a 9:16 measurement; a 1080-tall stage gives fewer, wider bands | `CAPABILITIES.md:102` |
| 27 | TREEMAP page (the census exception) | `species/treemap.mjs`; `CAPABILITIES.md:103` | **GOLDEN** (`treemap-cross`) | none. `TREEMAP_VALUE_FONT = 18` is "the absolute legible floor on a **1080x1920** stage" (`ledger_page.py:605`) | the legibility floor was measured on the portrait stage | `CAPABILITIES.md:103` |
| 28 | Line-end tags become bars; the tip-riding pill | `species/tippill.mjs`; `CAPABILITIES.md:106` | **GOLDEN** (`tags-to-bars`) | none | - | `CAPABILITIES.md:106` |
| 29 | Video dock | `scene-evidence-engine.mjs` `paintDockClip`; `CAPABILITIES.md:67` | **NONE** | none - build-f's 38 evidence entries are **all** `kind: doc` | - | `CAPABILITIES.md:67` |
| 30 | Dock placement on a page | `ledger_page.py` `page_boxes`; `CAPABILITIES.md:68` | **GOLDEN** (`dock-pair-16x9`) | none in a cut; `PORTRAIT_LAYOUT` (`ledger_page.py:1160`) is the 9:16 branch | the layout constants are per-aspect by design | `CAPABILITIES.md:68` |
| 31 | Dock choreography (enter, read, park) | `scene-evidence-engine.mjs` `dockGeom`; `DOCK_OPTS`; `CAPABILITIES.md:69`, `:87` | **NONE** | none - build-f's 43 docks carry **no** `arrive` at all (default), only `enter` / `exit` / `badge_at` | - | `CAPABILITIES.md:69` |
| 32 | Chart card (a page rendered once as a dock) | `chart_card.py`; `authoring/docks.py:107` (`aspect` is a parameter) | **NONE** | none | `render_card(..., aspect=...)` - the short passes `"9:16"` explicitly (`tokyo build_short.py:403`) | `CAPABILITIES.md:73` |
| 33 | Card-then-snap (thrown, then snaps to the world) | `scene-evidence-engine.mjs` `SNAP_S`, `THROW_S`; `CAPABILITIES.md:76` | **GOLDEN** | none | - | `CAPABILITIES.md:76` |
| 34 | The art-embed surface | `kinetics/homography.mjs`; `CAPABILITIES.md:32`, `:33` | **NONE** | its golden is declared 9:16 (`build_golden_sources.py:1227`) | - | `CAPABILITIES.md:32` |
| 35 | Press card + the STACK hand-off | `species/press.mjs`; `press_card.py`; `CAPABILITIES.md:97` | **GOLDEN** (`press-stack`) | none | - | `CAPABILITIES.md:97` |
| 36 | The badge ladder (pills stamp one per clause) | `scene-evidence-engine.mjs` `LP_BADGE0`/`LP_BADGE_STEP`; `EFFECTS-CATALOG.jsonl` `recipe:badge-ladder` | **CUT** | **build-f s05 @ 50.4 s**, members at 50.4 / 52.45 / 53.75 / 55.05 / 56.35 | E99 s72 `:3262`: prefer landing on **even** pills (2 or 4) | `CAPABILITIES.md:267` |
| 37 | Cross-reveal wipe with carried light | `scene-evidence-engine.mjs`; `CAPABILITIES.md:18` | **CUT** | build-f: **32** `wipe_right` | - | `CAPABILITIES.md:18` |
| 38 | The cut | compiler default | **CUT** | build-f: **43** | E99 s74 `:3266`: a cut is the last resort and names the transform it refused | `CAPABILITIES.md:18` |
| 39 | Dip + blur-zoom exits | `scene-evidence-engine.mjs` `DIP_S`, `BLURZOOM_*`; `CAPABILITIES.md:70` | **GOLDEN** (`dip-boundary`) | none in a 16:9 cut | the dip is the one transition licensed to empty the stage (M31) | `CAPABILITIES.md:70` |
| 40 | The slide transition | `SCENE_EXITS`; `CAPABILITIES.md:39` | **GOLDEN** (`slide-mid`, `slide-landed`) | none; awaits an operator watch in motion in **either** format | - | `CAPABILITIES.md:39` |
| 41 | The evidence door | `kinetics/transitions.mjs` `doorOn`; `CAPABILITIES.md:38` | **GOLDEN** (`door-open`) | none | - | `CAPABILITIES.md:38` |
| 42 | The melt exit (gather / throw / splash) | `species/melt.mjs`; `CAPABILITIES.md:37` | **GOLDEN** (9 `melt-*` goldens) | none | E99 s51: the splash must be a THROW | `CAPABILITIES.md:37` |
| 43 | The suck | `approved-mix.json` signature `suck` | **NONE** | Tokyo s03 only | - | `CAPABILITIES.md:70` |
| 44 | Spotlight, held past its boundary | `species/spotlight.mjs`; `CAPABILITIES.md:77` | **GOLDEN** (`spotlight-hold`) | none | E99 s76 `:3270`: a light only where there is a specific callout; `R_PORTRAIT: 960` is an explicit portrait branch | `EFFECTS-CATALOG` `recipe:spotlight-held-past-the-cut` |
| 45 | The ring (dashed ellipse + flag chip) | `species/ring.mjs`; `CAPABILITIES.md:44` | **GOLDEN** (`ring-dashed-chip`) | none | E56: a ring circles a number or a point on a CHART only | `CAPABILITIES.md:44` |
| 46 | Callout / scribble | `species/callout.mjs`; `CAPABILITIES.md:124` | **GOLDEN** (`chart-callout`) | none | - | `CAPABILITIES.md:124` |
| 47 | Trace hops + stacked stamps + the UNDER layer | `species/trace.mjs`; `CAPABILITIES.md:78` | **GOLDEN** (`trace-hop`) | none | `#species-under` shares the stage frame - fixed 2026-09-08 after a portrait bug | `CAPABILITIES.md:78` |
| 48 | Record document (typewriter + highlighter) | `species/record.mjs`; `CAPABILITIES.md:19` | **CUT as a DOCUMENT DOCK** | build-f "3:10 in build F" is a rendered `kind: doc` dock, not the species - the timeline has 0 species. The species has a 16:9 golden (`record-typewriter`) | - | `CAPABILITIES.md:19` |
| 49 | Newsreel band | `species/newsreel.mjs`; `CAPABILITIES.md:45` | **GOLDEN** (`newsreel-band`, 16:9) | none in a cut; the 9:16 variants are the ones with a ruling behind them | `newsreel-strip-9x16` / `-above` are the portrait forms | `CAPABILITIES.md:45` |
| 50 | The icon CHIP | `species/chip.mjs`; `CAPABILITIES.md:96` | **GOLDEN** (`chip-board`) | none | - | `CAPABILITIES.md:96` |
| 51 | The SPAN | `species/span.mjs`; `CAPABILITIES.md:100` | **GOLDEN** (`span-decade`) | none | - | `CAPABILITIES.md:100` |
| 52 | The numbered AGENDA (+ page form) | `species/agenda.mjs`; `CAPABILITIES.md:43` | **GOLDEN** (`agenda-page`, `agenda-two`) | none | - | `CAPABILITIES.md:43` |
| 53 | The isometric COUNT ARRAY | `species/countarray.mjs`; `CAPABILITIES.md:42` | **GOLDEN** (`count-array`) | none | - | `CAPABILITIES.md:42` |
| 54 | Checklist species = THE TEST CARD | `species/checklist.mjs`; `CAPABILITIES.md:209` | **CUT as a CARD** | **build-f s47 @ 492.3 s** (`recipe:test-card-rows`) - as a rendered document dock; the species itself has the 16:9 golden `test-card` | - | `CAPABILITIES.md:209` |
| 55 | The VERDICT STACK (the evidence wall) | `species/verdict.mjs`; `CAPABILITIES.md:189` | **CUT as DOCKS** | **build-f s67 @ 701.73 s** (`recipe:verdict-recap`, 9 proofs) - built from docks in August. The species has BOTH goldens: `verdict-stack` (16:9) and `verdict-stack-9x16` | `REF_W: 1920 / REF_H: 1080` - the burst normalisers were measured on the LANDSCAPE stage | `CAPABILITIES.md:189` |
| 56 | The FLOW DIAGRAM (chips + clothoid arrows + swap) | `species/flow.mjs`; `CAPABILITIES.md:99` | **GOLDEN** (`flow-swap`) | none | - | `CAPABILITIES.md:99` |
| 57 | The continuity three (edge arrival, thread, occluder) | `species/thread.mjs`; `CAPABILITIES.md:108` | **GOLDEN** (`thread-baseline`, `occluder-dock`) | none | - | `CAPABILITIES.md:108` |
| 58 | Curvature stroke (the two-thirds law) | `kinetics/stroke.mjs`; `CAPABILITIES.md:59` | **GOLDEN** | none in a cut - a pure function of t, aspect-free | - | `CAPABILITIES.md:59` |
| 59 | The full spring | `kinetics/spring.mjs`; `CAPABILITIES.md:61` | **GOLDEN** | none in a 16:9 cut | - | `CAPABILITIES.md:61` |
| 60 | Area-preserving squash | `kinetics/squash.mjs`; `CAPABILITIES.md:62` | **GOLDEN** | none in a 16:9 cut | - | `CAPABILITIES.md:62` |
| 61 | The CLOTHOID fitter | `kinetics/clothoid.mjs`; `CAPABILITIES.md:98` | **GOLDEN** (`race-path-clothoid`) | none | - | `CAPABILITIES.md:98` |
| 62 | Morph METHOD A + ARAP | `kinetics/morph_a.mjs`, `arap.mjs`; `CAPABILITIES.md:105`, `:121` | **GOLDEN** | none | - | `CAPABILITIES.md:105` |
| 63 | Kubelka-Munk ink | `kinetics/ink.mjs`; `CAPABILITIES.md:60` | **GOLDEN** | none; RULED OFF for the soak | - | `CAPABILITIES.md:60` |
| 64 | Stop-action: throw and land with weight | `kinetics/stopaction.mjs`; `CAPABILITIES.md:75` | **GOLDEN** | none | render clock 24 fps, plate life quantised at 12 (E99 s36 `:3172`) | `CAPABILITIES.md:75` |
| 65 | The camera: one persistent 2D similarity per timeline | `kinetics/camera.mjs` (`camNow`, `camCss`); `CAPABILITIES.md:85` | **GOLDEN** (13 byte-identical) | **none - build-f has 0 camera rows**; `camIdentity(STAGE_W, STAGE_H)` takes the stage, so it is aspect-free | LOCKED is the default (Bravos: 37 of 45 held compositions still) | `CAPABILITIES.md:85` |
| 66 | The camera ARRIVAL (the eye goes to the landed card) | `scene-evidence-engine.mjs` `camArr`; `CAPABILITIES.md:84` | **GOLDEN** | none | `CAMERA_ARRIVAL_S` 0.45 s, same both ways | `CAPABILITIES.md:84` |
| 67 | The camera over LAYERS (parallax with a reason) | `kinetics/camera.mjs` `camLayerState`; `CAPABILITIES.md:149` | **GOLDEN** (`camera-layers`) | none | plane ks far 1.0 / board 1.05 / mid 1.15 / near 1.40 - not per-format | `CAPABILITIES.md:149` |
| 68 | Attention ("landings" pulls the eye 1.06) | `kinetics/camera.mjs` `camAttentionState`, `ATTN` | **GOLDEN** | none | - | `CAPABILITIES.md:84` |
| 69 | The targeting law (declared targets, M09 mirror) | `build_scene_timeline_f.validate_species`; `CAPABILITIES.md:124` | **GOLDEN** | none in a cut - build-f predates it | - | `CAPABILITIES.md:124` |
| 70 | Beds + the press pack; the bed BREATHES | `authoring/audio.py:171` `bed_envelope`; `CAPABILITIES.md:65`, `:80` | **NONE** | none - build-f's sound block is a bare list; the envelope is a pure function of the rows | bed -20 LU (E70) both formats | `CAPABILITIES.md:65` |
| 71 | Page sound cues | `configs/sound_palette.json`; `CAPABILITIES.md:125` | **NONE** | none | - | `CAPABILITIES.md:125` |
| 72 | Cue binding + the bind report (R26-198) | `authoring/audio.py:396` `bind_report`, `:428` `bind_cues` | **NONE** | none | - | `CAPABILITIES.md:65` |
| 73 | The Remotion kit outro + the brand-line stitch | `authoring/audio.py:28` `outro_clock`, `:38` `stitch_brand_line`; `CAPABILITIES.md:63` | **NONE** | none. The **mechanism** is pure time arithmetic and format-free; the **asset** is not: `remotion-kit/src/Root.tsx` hardcodes `width={1080} height={1920} fps={30}`, and `ffprobe outro-v2.mov` returns `1080,1920,30/1,6.200000` | lead 0.1 s, card 6.2 s, brand gap 0.7 s, tail 1.0 s - constants, unchanged by runtime | `CAPABILITIES.md:63` |
| 74 | THE AUTHORING KIT - one door for both formats | `authoring/__init__.py`; `authoring/table.py:115` `compile_timeline(..., aspect=...)`; `CAPABILITIES.md:90` | **NONE** | none - **no long-form build has ever imported it**. `aspect` and `caption_style` are already parameters | `aspect="9:16"` is passed explicitly by both shorts (`tokyo build_short.py:580`) | `CAPABILITIES.md:90` |
| 75 | THE SHAPE COMPILER (the approved skeleton as the base) | `authoring/shapes.py`; `generate_base_table.py`; `CAPABILITIES.md:91` | **NONE** | none; its skeletons are the approved **shorts** | - | `CAPABILITIES.md:91` |
| 76 | THE RECIPE LAB | `lab_build.py`; `effects/lab/beat-shapes.json`; `CAPABILITIES.md:92` | **NONE** | none; every lab bed is the Tokyo (9:16) bed | - | `CAPABILITIES.md:92` |
| 77 | THE ONE-SHOT BAR (self-watch as a build artifact) | `self_watch.py`; `CAPABILITIES.md:94` | **NONE** | none | - | `CAPABILITIES.md:94` |
| 78 | EYES: the probe CLI + layout gate M25 | `probe.py`; `CAPABILITIES.md:93` | **NONE** | none - it reads the built player's own DOM, so the stage is whatever the build is | - | `CAPABILITIES.md:93` |
| 79 | The override sidecar + the thin editor | `editor/editor.html`; `CAPABILITIES.md:110`, `:112` | **NONE** | none | - | `CAPABILITIES.md:110` |
| 80 | Hot reload with the determinism check | `serve_player.py`; `determinism_check.py`; `CAPABILITIES.md:111` | **NONE** | none | - | `CAPABILITIES.md:111` |
| 81 | The verified build receipt + the director-critic | `recall_verify.py`; `authoring/table.py:169` `recall_receipt_block`; `CAPABILITIES.md:275` | **NONE** | none - build-f is stamped `legacy` (pre-P67, `table.py` `LEGACY_REASON`) | - | `CAPABILITIES.md:275` |
| 82 | The render door | `render_episode.py:38` `FPS = 24`, `:94` `RAW_W, RAW_H = STAGE_W * 4 // 3` | **CUT** | build-f is its default subject (`:31` `BUILD = RENDER_BUILD or EP/"build-f"`) | **16:9 gives 2560x1440** (the default, no flag); `RENDER_ASPECT=9:16` gives 1440x2560. 24 fps both (E99 s36 `:3172`). This is exactly the operator's "1440p confirmed" | `CAPABILITIES.md:18` |

**Row count: 82**, counted with
`awk '/^\| [0-9]+ \|/{n++} END{print n}' docs/research/LONG-FORM-CAPABILITY-AUDIT-2026-09-18.md`.

**The tally that answers the operator.** **CUT at 16:9: 12 rows** (1, 2, 3, 7, 12, 36, 37, 38,
48, 54, 55, 82) - and every one of them is a plate, a dock, a badge, a caption, a wipe or the
renderer. **GOLDEN but never in a 16:9 cut: 45 rows. NONE: 25 rows.** Not one ledger page,
species, chart transform, camera move, declared idle, sound cue or authored arrival has ever
drawn a landscape frame in a cut.

### The proven recipes, by the format that proved them

`docs/EFFECTS-CATALOG.jsonl` carries 189 records, 45 of them recipes: **15 proven, 30
candidates**. Of the 15 proven:

| Proven in | Count | Recipes |
|---|---|---|
| **16:9 (`steel-and-paper/build-f`, August)** | **5** | `badge-ladder` (s05, 50.4 s), `held-dock-across-the-cut` (s05, 50.4 s), `plate-dock-wipe` (s57, 595.5 s), `test-card-rows` (s47, 492.3 s), `verdict-recap` (s67, 701.73 s) |
| 9:16 (`japan-tariff-trick/build-short`) | 7 | `card-becomes-the-chart`, `dock-lands-page-renames`, `emphasized-bar-lit`, `outro-clip-life`, `read-park-build-write`, `spotlight-held-past-the-cut`, `trace-callout-ladder` |
| 9:16 (`tokyo-tea-break/build-short.v2`) | 3 | `held-page-hosts-the-docks`, `punch-then-callout`, `still-life-breather` |

**Read the five.** Every one is a plate + a dock + a badge + a wipe. Not one involves a ledger
page, a species, a chart transform or the camera - because ep1's timeline contains none of
those. And `recipe:plate-dock-wipe` is the one the operator **DENIED** on 2026-09-17 (E99 s72
`OPERATOR-RULINGS.md:3262`: *"too-slow: You literally dokced and wiped then held a still frame
for 30 seconds"*). **The honest count of proven, still-approved 16:9 recipes is four.**

### The approved mix (`effects/skeletons/approved-mix.json`)

Both `approved` cuts are shorts: `tokyo-tea-break/build-short` (7 scenes, vocabulary of 10)
and `japan-tariff-trick/build-short` (12 scenes, vocabulary of 4). `target.scenes = 19`,
`max_share.value = 0.4167` ("the maximum share ONE signature reaches inside a single approved
cut - the number M46 leans on"), `vocabulary.min_distinct = 4`. **The measured mix a long form
would be judged against is 19 scenes of 9:16 totalling about 2.5 minutes.** H is ~13 minutes
and `build-f` alone has 75 scenes. See (b), M46.

---

## (a) The caption layer at 16:9 - the verdict

**A 16:9 caption strip is not missing. It is the DEFAULT, and it has no capability row.**

`docs_find "caption strip 16:9"` returns `0 hit(s)` across all nine layers. That zero is a
**documentation** hole, not an engine one. What is actually on disk:

1. **The base rule is landscape.** `scene-evidence-player.template.html:484` - `#caption`
   at `left: 145px; right: 145px; bottom: 120px; font-size: 40px; font-weight: 700;
   z-index: 50`, with the comment naming why 120 px: *"YouTube's hover controls bar overlays
   roughly the bottom 10-12 % of the frame (~110-130 px at 1080p) ... 120px = 11.1 %, clear
   of the bar with margin"* (doc 29 s9.15 ruling 7). Every `html[data-aspect="9:16"]` rule
   (48 of them in the template) is an **override** of this.
2. **The anchored strip is a named 16:9 constant.** `ledger_page.py:1159`:
   `CAPTION_ANCHOR = {"9:16": (80, 1290, 800, 150), "16:9": (145, 878, 1630, 82)}` - so the
   16:9 strip is x[145, 1775], y[878, 960], **82 px tall**, which the template's own comment
   (`:305-317`) explains is *"exactly two lines at 33px/1.24"*.
3. **STAGE mode is landscape-first too.** `template:524`: `#caption.stage { top: 40%;
   left: 200px; right: 200px; font-size: 64px; font-weight: 800 }`. The 9:16 variant
   (`:234`) moves it to `bottom: 480px` inside the safe box.
4. **The per-format size dial is real and it is E62's.** The portrait quiet caption was
   raised to **48 px / 800** because the operator read 33 px / 600 as *"losing its
   size/punch"* on a phone; the template states the landscape side is deliberately untouched:
   *"The LANDSCAPE quiet size is untouched at 33px/600 ... E62 names a floor for the short,
   and 16:9 is above its own."*
5. **The page builder is aspect-blind and ep1-bound.** `build_caption_pages.py` has no CLI
   and hardcodes `BUILD = REPO / ".../steel-and-paper/build-f"` (`:15`). The kit wraps it by
   monkey-patching module globals - `authoring/table.py:106-113`: `CP.BUILD = build;
   CP.CHAR_BUDGET, CP.MAX_WORDS = char_budget, max_words; CP.main()`. Nothing about the
   aspect enters; only the character budget (34 / 6 long, 28 / 6 on the Tokyo short) does.
6. **PHRASE is a ruling, not a branch.** `scene-evidence-engine.mjs:7532`:
   `const PHRASE = TL.caption_style === "phrase"`. There is no aspect test anywhere near it.
   `CAPABILITIES.md:66` titles it "(shorts)" because of the operator's 2026-09-05 ruling
   (*"letting people read the captions on shorts"*), not because the engine refuses it at
   16:9.

**What ep1 actually shipped:** 464 word-level pages, 5.3 words/page, **34.5 pages/min** over
806.47 s, in `caption_modes: ["stage", "anchor"]` with `caption_style: null` - 110 stage /
354 anchor. M06 PASSes. So the 16:9 caption layer is the one part of this audit with real,
measured, gate-passing evidence.

**What R26-201's engine order costs a 16:9 page punch.** R26-201 (`BACKLOG.md:632`) is a
**9:16** finding: every Tokyo page's foot sits 13 px above the caption strip, so the largest
whole-page zoom is 1.03, and the row's ENGINE ORDER is *"the caption yields under a camera
key as under a dock (E62 for the camera)"* - because *"the engine has NO caption door for a
camera key - E62's band is written on dock entries only (`_dock_live_at`,
`CAPTION_BAND_ORDER`)"*. Two consequences for H:

- **The missing door is aspect-free.** The band is stamped from **dock** entries, so a 16:9
  page punch has no caption door either. The engine order is owed identically at 16:9; it is
  not a portrait-only fix.
- **The headroom arithmetic is not.** At 16:9 the strip is 82 px of a 1080 stage (7.6 %);
  at 9:16 it is 150 px of 1920 (7.8 %) but sits inside a safe box that also surrenders the
  top 280 and the right 200. The 16:9 page has the *cite* and *pill row* clearance the 9:16
  page does not, so **a 16:9 page punch is probably affordable where the 9:16 one was not** -
  but the number has never been measured, because no 16:9 cut has ever carried a page.
  **That measurement is owed before T4 puts a punch in the treatment** (gap G-01).

---

## (b) The gates - which bind a long form and which bind shorts only

`docs/GATES-REGISTRY.md` header: *"165 records, 151 distinct ids, across 7 checkers."*
Counted by section:

| Section | Ids | Binds a long form? |
|---|---|---|
| `opening-long` | 62 | **YES - this is the long form's own set** (G01-G48) |
| `opening-short` | 13 | **NO** - S01-S08, J50, J51 run only under `run_short` |
| `opening-shared` | 6 | YES (G00, G45, G47, G47b, G48) |
| `motion` | 37 (35 M-ids + J01, J02) | YES, with per-format branches - see below |
| `floor` | 10 | **calibrated on shorts only** - see below |
| `lint` / `audit` / `viewer` / `package` | 11 / 17 / 5 / 1 | YES, format-free |

**The routing switch.** `CAPABILITIES.md:201`, G2 short mode: *"a MEASURED clock under 3:00
(or `--short`) routes `gate_opening_structure` to the shorts shape"*. **The long-form shape
is the default**, and `--long` forces it. The same word appears on the species lint -
`lint_species_choice.py --help` prints verbatim:

```
  --long         apply E61's plate-use check regardless of runtime
```

That is the flag T5/T6 must carry, and the one the plan's step 5 already names.

**Gates that bind a long form and nothing else:** G46 (*"long form is never under 8
minutes"*, `gate_opening_structure.py:669`, E74 `OPERATOR-RULINGS.md:2393`), G36's 60 s
rehook cycle (against S06's 30 s), and G19-G28's P2 loop geometry, whose windows **scale with
runtime** (`gate_opening_structure.py:650`) - so H's true verdict only settles on H's own
take, exactly as the plan says.

**Gates that bind shorts only, by the tools' own words:**

- **M16, the pulse.** `build-f/GATES-MOTION.md:41` prints it verbatim:
  `[INFO ] M16 longest gap between visual events 17.7s at 2:24; 64 gap(s) over 2.5s - a
  long-form build; the pulse law binds shorts`. The gate knows what format it is looking at
  and stands down. **A long form therefore has no gap ceiling at all** - M01/M02/M08 carry
  the stillness law instead.
- **`gate_vertical_safe_box.py` is 9:16 by construction.** Its docstring: *"G-l - the
  vertical safe-box gate (P37 T8): on a 9:16 stage every dock, and the anchored caption, must
  sit inside x[80,880] y[280,1340] / the caption strip y[1340,1440]"*, with
  `SAFE_X = (80, 880)`, `SAFE_Y = (280, 1340)`, `STAGE_H = 1920` as module constants.
  **There is no landscape equivalent.** The 16:9 analogue exists only as a CSS comment (the
  YouTube hover bar, `template:484`) and is enforced by nothing. That is gap G-02.
- **S07** (*"the brand line ... is stitched under the outro card - a script that speaks it
  doubles it"*) lives in `opening-short`. **A long form has no gate against speaking the
  brand line twice.** Gap G-08.
- **M11** branches explicitly: *"the first chart enters 0:08-0:20, or 0:00-0:10 on a short"*.
- **M31 / M32 / M33** are format-free in code but **calibrated on the Japan short**: M31's
  number came from *"8.9 % of a 69 s short"*, M32's near-black threshold was *"MEASURED on
  the approved Japan short's six dips"*, M33 is *"WARN until the approved shorts show a real
  example"*.

**The one-shot floor in its current state - what M37 / M39 / M40 / M46 actually mean.**
`gate_one_shot_floor.py:90` reads
`REFERENCE_REL = f"{PROJECTS_REL}/japan-tariff-trick/build-short"`, commented
`# the best approved short (09-09), the reference`. And `:114-118`, `PREDATES_E96`, contains
`("steel-and-paper", "build-f")` pinned to its timeline sha - with the comment *"ADDING A
BUILD TO THIS TABLE NEEDS A RULING - it is an exemption from the floors, not a configuration
knob."* So today:

- **M37** ("docks on at least 1/3 of the beats ... **and never under the reference's own
  share**") measures H's dock density against an 89-second vertical cut whose whole argument
  is one mechanism. Over ~13 minutes that comparison is **not meaningful**; it is a number
  from another format wearing the word "reference".
- **M39** ("narrative : chart at least 1:1 ... **held to the reference's own ratio too**") -
  same defect. Japan's ratio is a short's ratio.
- **M40** is a **JUDGE** row: *"read against the best approved short, never against the
  gates"*. Read literally, **there is no long form to read H against except ep1, which the
  rewrite order already calls faulty**. M40 on H is a judgement with no valid comparator.
- **M46** compares H's signature mix to `approved-mix.json`, whose ceiling `M46_MAX_SHARE =
  0.42` is *"Japan's five dips over twelve scenes"* and whose vocabulary floor
  `min_distinct = 4` is Japan's own. Over 75+ scenes a 0.42 share ceiling is nearly
  unreachable; the **consecutive-repeat** clause (no two adjacent scenes on a signature the
  approved cuts do not themselves repeat) is the part that will actually fire, dozens of
  times, against a 19-scene sample. **M46's verdict on a long form is not evidence.**
- **M35 / M36** go to **INFO** on `build-f` because of its exemption, so even the reference
  long form never had to clear them.

**The scale of what has never been printed for a long form.** `gate_motion_density.py`
defines **35 distinct M ids** today. `build-f/GATES-MOTION.md`, regenerated **2026-09-17**,
prints **16** of them (M01-M12, M14, M15, M16, M18) plus J01. **19 motion-gate rows -
M17, M19-M34, M43, M44 - have never printed a verdict on a long-form build**, because their
subjects (pages, species, chart transitions, camera keys, collisions, frozen frames) are all
things ep1's timeline does not contain. The current verdict line is
`VERDICT: FAIL (8 FAIL)`, and `ledger_pages: 0` sits at `:9`.

**What this means for T4 and T6:** the gate set is not the problem; the **calibration** is.
The plan's rule holds - a shorts-reference caveat is quoted, never silently passed - and
gaps G-03 and G-04 file the work.

---

## (c) The camera and the outro at 16:9

**The camera is aspect-free and completely unproven in the format.** Every stage-dependent
value is a parameter: `camIdentity(STAGE_W, STAGE_H)`, `camKeyState(K, t, STAGE_W, STAGE_H)`,
`camCssFor({...}, STAGE_W, STAGE_H)` (`scene-evidence-engine.mjs:12435-12451`), and the
engine's own comment at `:12401` records the bug that made it so: *"the stage's centre, not
the landscape's (2026-09-08: 960/540 zoomed a portrait short about the wrong point)"*.
`CAPABILITIES.md:85` is one persistent 2D similarity per timeline with LOCKED as the default
(*"Bravos, measured: 37 of 45 held compositions still"*); `:84` is the arrival
(`enter=camera=<dock>`, 0.45 s, min-jerk, `extend_camera_cards`, M14 exempted against its own
card); `:124` is the targeting law (`validate_species` fails the build on a pointing species
without a DECLARED target, and M09 mirrors it); `:149` is the camera over layers (plane ks
far 1.0 / board 1.05 / mid 1.15 / near 1.40).

**`build-f` has 0 camera rows and `kinetics: null`.** Everything above is a golden.

**What changes at ~13 minutes** (the plan's re-derived clock: 13:19 estimated, 12:56 on the
timeline):

1. **One camera, 75+ scenes.** The state is per **timeline**, not per scene. At 89 s with 7
   scenes an authored key is a local decision; at 13 minutes with 75+ windows the camera is a
   through-line, and every key must return to identity or the next scene inherits a zoom
   nobody authored. Nothing in the engine enforces a return. **Gap G-05.**
2. **M09's "one camera move per window" is cheap at 89 s and load-bearing at 13 minutes.**
   E99 s76 (`:3270`) - a light only where there is a specific callout - applies to the camera
   the same way: 75 windows will not survive a camera habit.
3. **The outro mechanism does not change at all.** `authoring/audio.py:28` `outro_clock` is
   pure arithmetic on `t_vo_end`: `t_outro = t_vo_end - outro_lead`, `t_line = t_vo_end +
   brand_gap`, `runtime_s = max(t_outro + outro_s, t_line + line_s + brand_tail)`. The Tokyo
   constants are `OUTRO_S, OUTRO_LEAD = 6.2, 0.1` and `BRAND_GAP, BRAND_TAIL = 0.7, 1.0`
   (`tokyo build_short.py:95-96`). Feed it 806 s or 13 minutes and it returns the same
   6.2-second tail. `stitch_brand_line` (`:38`) concatenates take + 0.7 s silence + the brand
   line and `apad`s to the runtime - runtime-independent.
4. **The outro ASSET does change, and it is the only hard blocker in this section.**
   `remotion-kit/src/Root.tsx` declares exactly one composition: `durationInFrames={186}
   fps={30} width={1080} height={1920}`. `ffprobe` on the shipped clip returns
   `1080,1920,30/1,6.200000`. All four movs in `tokyo-tea-break/outro/` are that portrait
   render. **There is no 16:9 outro card on disk**, and the row the operator wants for
   YouTube (`outro-yt`, with "subscribe") is portrait too. A landscape re-render is a
   parameterised Remotion composition plus one render - small, but it is work nobody has
   done, and the cut cannot close without it. **Gap G-06, blocks T6.**
5. **The brand line has no long-form gate.** S07 is short-only (see (b)). H's script must be
   checked by hand for the doubled line. **Gap G-08.**
6. **E47 says the card is a world change - the dip, not a dissolve.** The Tokyo row uses
   `"dip"` into the outro (`build_short.py:444`) while `CAPABILITIES.md:63` still describes
   the 2026-09-05 dissolve. `build-f` has no dip token at all, so the outro transition itself
   is unproven at 16:9.

---

## (d) The door - what `authoring/` covers, and what ep1's door does that the kit cannot

**The kit is real and it is already both-format.** `authoring/__init__.py` states the
contract: *"THE RULE: nothing in this package names an episode. No episode id, no crop, no
quote, no file name, no absolute path."* The surfaces:

| Module | What it owns | Long-form ready? |
|---|---|---|
| `Project` (`__init__.py`) | `here / build / take / take_stem / script_name / episode_id / take_name`, `audio_master`, `mkdirs` | YES - path-shaped, format-free |
| `words.py` | the take's clock: `take_words`, `shifted_words`, `phrase_start`, `word_time`, `cut_before`, `next_sentence_start`, `split_sentences(part=N)`, `write_timeline`, `apply_edit_pauses` | YES - and `part=N` already anticipates a chained multi-part take |
| `docks.py` | `register`, `seekable_clip`, `zoom_clip`, `dock_clip`, `dock_still`, `still_card`, `chart_card(..., aspect=...)`, `centred_card_point`, `record_words`, `record_asset` | YES - `aspect` is a parameter |
| `audio.py` | `outro_clock`, `stitch_brand_line`, `vo_tone_filter` (chain G), `bed_gain`, `bed_envelope`, `stop_dials`, `landing_contact`, `fired` / `cue_key` / `bind_report` / `bind_cues` / `unsounded` (R26-198) | YES |
| `table.py` | `write_shot_table`, `load_rows`, `apply_sidecar`, `hold_until`, `caption_pages`, `compile_timeline(..., aspect, caption_style, kinetics)`, `recall_receipt_block`, `write_compile_manifest` | YES - `aspect` and `caption_style` are arguments |
| `shapes.py` / `recipes.py` / `effects.py` | the shape compiler, the recipe names, the catalogue's axes | **calibrated on shorts** (see (b)) |

**`CAPABILITIES.md:90` is right that the kit is one door for both formats. It has simply
never been walked through by a long form.**

**ep1's legacy door - what it does that the kit has no function for.**
`steel-and-paper/build_scene_evidence_cut.py` is 459 lines and is **not a compiler client at
all**: it emits a `scene_evidence_timeline.v1` dict by hand and base64-inlines its own
images. Specifically:

1. **A hardcoded worktree path.** `:10` -
   `REPO = Path(r"C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16")`,
   and `:14` `DMP = Path(r"C:\Users\Snipe\Downloads\Decoding_Market_Physics_slides")`. It
   cannot run in the main checkout. R26-197's law (a named constant with its receipt in the
   docstring) has no purchase on it. **Do not extend it** - the plan already says so.
2. **Hand-written chart SVGs.** `svg_divergence`, `svg_ai_debt`, `svg_arithmetic`,
   `svg_steel_test`, `svg_tripwires` (`:45-155`) each compute their own point strings and
   return a `<svg viewBox="0 0 1376 768">` string. **The kit has no function that turns a
   series into a flat SVG document**; its nearest relative is `docks.chart_card` ->
   `chart_card.render_card`, which renders a **ledger page** once as a dock. That is a
   different object: a page, not a document. **Every one of ep1's five hand-drawn charts must
   be re-authored as a ledger page or a chart card - there is no port.** This is the
   single largest piece of T4 work the kit does not shorten. **Gap G-09.**
3. **A multi-scene take stitched by the build script.** `scene_offsets()` (`:34`) walks
   `VO_SCENES` (seven directories) reading `scene_N.words.json` and accumulating offsets. The
   kit reads **one** take (`words.take_words`); the repo's answer for a chained take is
   `join_chained_take.py` + `retime_to_take.py` (`CAPABILITIES.md:212`, `:214`), which the
   kit does not wrap. For H this is moot - T2 is a single local Kokoro take (E99 s81) - but
   it is why the F door exists in that shape.
4. **Caption JS/CSS injected as source strings.** `CAPTION_JS_OLD` / `CAPTION_JS_NEW` /
   `CAPTION_CSS` (`:271-307`) patch the template text. The modern path is the engine plus
   `caption_pages`; nothing is owed here except "never do that again".
5. **Its own window table.** `WINDOWS` (`:234`) is 18 tuples of
   `(scene_index, rel_start, rel_end, plate, ken_burns, docks)` on a **per-scene relative**
   clock. `SHOT-TABLE-F.py` (75 rows on the absolute 806.5 s clock) is the real reference for
   T4, not this list.

**Verdict: H's door is `build_episode_h.py` written fresh against `authoring/`, beside the F
door, importing nothing from it** - exactly the Tokyo v3 pattern the plan names. The kit
covers the take clock, the docks, the audio, the cue binding, the sidecar, the receipt and
the compile hand-off. What it does **not** cover is (2) - the charts - and that is the work.

---

## (e) The host - Mike on the studio and newsroom plates

**Ruled IN by E99 s81** (`OPERATOR-RULINGS.md:3280`): *"We could incorporate mike into the
studio, newsroom scenes etc. flow is available and if wee add character+image prompt should
be good to go."* Apply (3): *"the shot table reserves Mike's windows in the studio and
newsroom scenes as plate-thrown character stills through Flow with the character + image
prompt ... each window a named plate use (E61) with its idle."*

**What the record gives today.**

- `Recall: docs_find "Mike" -> CAPABILITIES.md:159` - the Flow stdio dispatcher:
  `create_flow_image` over the MCP's stdio JSON-RPC, one order file per prompt, the same
  prompt run against `@MikeMasterV3` / `@Mike2` / `@HollowStickMike`. LIVE, zero credits.
- `Recall: docs_find "flow character pack" -> CAPABILITIES.md:181` - the identity as a
  **validated, hashed, non-renderable contract**: `finance-host-v1` (retention) and
  `finance-host-stick-v1` (acquisition), each with front / profile / three-quarter / back,
  five named expressions and five named poses; `@Mike` is bound in Flow project `d171ec1f`,
  entity `dab5d902`. The row's own warning: *"A character edit cannot adopt a new reference -
  it re-renders from the old one; bind from the file."*
- `docs/agent-memory/operator/mp-host-identity.md` - @Mike is a **bound** Flow character,
  colour cartoon + indigo suit, and *"works for motion (R4 closed)"*.
- On disk in `assets/generated/host/`: **6 files** - two master sheets
  (`finance-host-flow-character-sheet-master.png`,
  `finance-host-identity-master-v3.png`) and four reference stills
  (`flow-ref-fullbody-standing`, `flow-ref-halfbody-crossed`, `flow-ref-halfbody-open`,
  `flow-ref-halfbody-pointing`).

**Three built paths for a person on screen, none of them host-specific:**

1. **The cutout dock** - `scene-evidence-engine.mjs:15125-15127`: *"P53 T7 / R26-59: a CUTOUT
   dock is a person, not a document - the card's chrome stands down (`.dock.cutout`)"*,
   keyed off `evidence[aid].kind === "cutout"`. Proven with the five approved heads
   (`myth-of-historical-normal/assets/heads/manifest.json`, E68, `render_eligible: true`).
2. **Plate-life cutouts** - `scene-evidence-engine.mjs:15077`: *"our cutouts on a bare plate:
   stepped time, throw-and-land with squash, two-frame boil"*. Positions are stage fractions
   (`c.x * STAGE_W`), so it is aspect-free; this is the literal "plate-thrown character
   still" the ruling describes.
3. **The plate's own foreground layer** - HF-17's `#fgover`, the layer that sits above the
   cards (`engine:15197`, `:15468`) - the host baked into the plate as its front plane.

**What a long form's 3-5 host windows still need:**

- **A plate to stand on.** The plate library holds **330** plates; searching the ids returns
  **0 "studio"**, **0 "newsroom"**, **0 "anchor"**, and exactly **2** broadcast plates -
  `world-broadcast-set-v1` / `-v2`. `build-f` already holds `world-broadcast-set-v2` from
  **173.9 s to 204.3 s** (30.4 s, the longest single plate window in the cut, per the species
  lint). **That window is the host's, and it is the only one that exists.** A newsroom and a
  studio plate are net-new Flow orders. **Gap G-10.**
- **Transparent per-pose cutouts.** The character pack is explicitly *non-renderable* - it
  is a contract enumerating poses, not a set of PNGs. The four `flow-ref-*` stills are
  references, not alpha cutouts. Each host window needs one approved transparent PNG, cut the
  way the five heads were, catalogued with a sha and a `review_state`. Quarantine first, and
  **no image is ever `git add -f`'d** (E99 s31).
- **A named plate use and an idle per window** - E61 (`OPERATOR-RULINGS.md:1991`) and E49
  (`:1494`). `idle=figure` is the kind built for a person: doc 48 s48.4's asymmetric breath
  (I:E 1:1.75, a 0.7 s post-expiratory pause, never a sine) plus the two-rate sway
  (`kinetics/idle.mjs:96`). It has **never run in any cut, either format**.
- **A sentence that names him.** E99 s76: a light is applied only where there is a specific
  callout. The same discipline is owed to a host window - it is a beat, not decoration.

**AMENDED 2026-09-18 02:55, mid-audit - the plates arrived while this was being written.**
A concurrent P68 slice rolled three host stills through the driver and they are on disk,
**quarantined**, at `steel-and-paper/host/`: `H-1-studio.png`, `H-2-desk.png`,
`H-3-newsroom.png`, each with a `_meta.json` carrying its frozen order, its beat and
`"review_state": "quarantined until the operator approves the frame"`, and every prompt
`"ratio": "16:9"` with `"references": ["Mike"]`. `HOST-NOTES-H.md` records the form that
actually came back and it is **better than the one the ruling described**:

> *"The treatment's host section said 'Mike as a docked character card on the plate'; the
> plates came back as full scenes WITH Mike, which is the stronger form (one world, the cards
> land on it). The build takes the plate as the landing surface with `;use=landing`, the ken
> push and the 20 px drift."*

So the asset gap is closed and the **mechanism** question changes shape. A full-scene host
plate is an ordinary flat plate: `;use=landing`, Ken Burns + the 20 px drift (E99 s65
`OPERATOR-RULINGS.md:3248`). That is the right plate life and it needs no new code.

**But it gives Mike no breath, and there is no mechanism that would.** `IDLE_KINDS`
(`build_scene_timeline_f.py:86`) accepts `;idle=figure` on **any** plate id, and
`idle=figure` is doc 48 s48.4's asymmetric breath plus the two-rate sway applied to the
**whole element** (`kinetics/idle.mjs:96`) - on a full-scene plate that breathes and sways
**the entire room**, which is worse than stillness. Animating one region of a flat plate is
exactly what the mask-pinned AMBIENT lane is for (`CAPABILITIES.md:145`, LIVE 2026-09-05,
the effect PROVEN 2026-09-16 on the Tokyo harbour: `comfy_sam2_mask.py` +
`comfy_vace_ambient.py`) - and it has **never been run on a person**. For H the answer is
Ken Burns + 20 px and no breath; a breathing host is a separate, unproven order.

**Remaining T4 cost:** 3 shot-table rows (`;use=landing;idle=drift;drift=20` + a ken push),
the operator's eye on H-1's drawn chart print, and the two re-rolls `HOST-NOTES-H.md` already
names - H-3 carries printed text a plate must never carry, H-2's wardrobe differs from the
binding. **No engine change.**

---

## Proposed backlog rows - ready to paste into `docs/content-video-engine/BACKLOG.md`

Ids left as `R26-TBD`; the parent assigns them in T3b. Column shape matches the file's
existing rows: `| id | what | status | ruling |`. Each carries the measurement that found
it, the owed work, an **owner** and a **blocking verdict**.

| id | what | status | ruling |
|---|---|---|---|
| **R26-205 (audit G-01)** | **THE 16:9 CAPTION STRIP HAS NO CAPABILITY ROW, AND NO PAGE HAS EVER BEEN PUNCHED OVER IT** - *measurement:* `docs_find "caption strip 16:9"` returns `0 hit(s)` across all nine layers, while the strip is a named constant (`ledger_page.py:1159` `CAPTION_ANCHOR["16:9"] = (145, 878, 1630, 82)`) and the template's default rule (`scene-evidence-player.template.html:484`, `:524`, `:533`). *Owed:* (a) a CAPABILITIES row for the 16:9 caption layer naming the strip, the STAGE geometry and the 33 px / 600 quiet size, so `docs_find` stops returning zero; (b) the headroom measurement R26-201 did for 9:16, re-run at 16:9 - the largest whole-page zoom that keeps a page's cite and pill row clear of the 82 px strip. *Owner:* **doctrine** (a) + **build script** (b). | proposed | E99 s81 / P68 T3 |
| **R26-206 (audit G-02)** | **THERE IS NO LANDSCAPE SAFE-BOX GATE** - *measurement:* `gate_vertical_safe_box.py` is 9:16 by construction (`SAFE_X = (80, 880)`, `SAFE_Y = (280, 1340)`, `STAGE_H = 1920`); the 16:9 equivalent - YouTube's hover-controls bar over the bottom ~11 % - exists only as a CSS comment at `template:484` and is enforced by nothing. The portrait-parity gate (`tests/test_portrait_parity.py`) protects 9:16 from landscape literals; **nothing protects 16:9**. *Owed:* a landscape reader in the same tool (a 16:9 mode, not a new file) asserting every dock and the anchored caption clear the bottom 120 px and the 145 px rails. *Owner:* **engine**. | proposed | E99 s81 / P68 T3 |
| **R26-207 (audit G-03)** | **THE ONE-SHOT FLOOR HAS NO LONG-FORM REFERENCE** - *measurement:* `gate_one_shot_floor.py:90` `REFERENCE_REL = ".../japan-tariff-trick/build-short"` (an 89 s, 12-scene, 9:16 cut) is the comparator for **M37** ("never under the reference's own share") and **M39** ("held to the reference's own ratio too"); **M40** is a JUDGE row reading the cut "against the best approved short"; and `("steel-and-paper", "build-f")` is in `PREDATES_E96` (`:117`) so M35/M36 go INFO on the only long form we have. *Owed:* (a) `--reference` is required, not defaulted, when the build's runtime is over 3:00; (b) M37/M39/M40 print "reference is a SHORT" in their own text until a long form is approved; (c) H's own approved cut becomes the long-form reference at HG4. *Owner:* **engine**. | proposed | E99 s81 / P68 T3 |
| **R26-208 (audit G-04)** | **M46 JUDGES A 13-MINUTE CUT AGAINST 19 SCENES OF SHORTS** - *measurement:* `approved-mix.json` holds two approved cuts, both 9:16 (`target.scenes = 19`); `M46_MAX_SHARE = 0.42` is "Japan's five dips over twelve scenes"; `vocabulary.min_distinct = 4` is Japan's. `build-f` alone has **75 scenes**. Over 75+ scenes the share ceiling is nearly unreachable while the consecutive-repeat clause fires against a 19-scene sample. *Owed:* M46 is INFO (not WARN) on a build over 3:00 until a long form is in `approved`, and its line says so. *Owner:* **engine**. | proposed | E99 s81 / P68 T3 |
| **R26-209 (audit G-05)** | **THE CAMERA IS PER-TIMELINE AND NOTHING MAKES IT RETURN TO IDENTITY** - *measurement:* `CAPABILITIES.md:85` - one persistent 2D similarity per **timeline**; `build-f` has **0** camera rows, so the mechanism has never run over more than 12 scenes. At 75+ windows an authored key that does not return leaves the next scene at an un-authored zoom, and no gate checks it (M09 is per window, M14 is per overlap). *Owed:* a compiler check that a camera key set closes on identity by the end of its scene unless the next row declares a carry, plus an INFO line listing the open zoom at every scene boundary. *Owner:* **engine**. | proposed | E99 s81 / P68 T3 |
| **R26-210 (audit G-06)** | **THERE IS NO 16:9 OUTRO CARD** - *measurement:* `remotion-kit/src/Root.tsx` declares one composition at `width={1080} height={1920} fps={30}`; `ffprobe` on `tokyo-tea-break/outro/outro-v2.mov` returns `1080,1920,30/1,6.200000`; all four movs (`outro.mov`, `outro-v2.mov`, `outro-brand.mov`, `outro-yt.mov`) are that portrait render. The outro **mechanism** is format-free (`authoring/audio.py:28` `outro_clock` is arithmetic on `t_vo_end`), the **asset** is not. *Owed:* `Root.tsx` takes width / height / fps as composition props (or gains a 1920x1080 sibling), and `outro-yt` is re-rendered at 1920x1080 for the YouTube re-upload. *Owner:* **engine** (the kit) + one render. **BLOCKS T6** - the cut cannot close. | proposed | E99 s81 / P68 T3 |
| **R26-211 (audit G-07)** | **`idle.mjs`'s OWN COMMENT CONTRADICTS THE RULING ON THE LONG-FORM DRIFT** - *measurement:* `kinetics/idle.mjs:137` reads *"30 px is the named long-form setting, 40 the shorts one"*, which is E99 s55. E99 s64 (`OPERATOR-RULINGS.md:3246`) and s65 (`:3248`) amended it to **20 px for long form**, and `CAPABILITIES.md:71` already carries 20. A builder reading the module sets the wrong number. Also measured: every authored drift on disk is `drift=35` (157 uses); the 19 instances of `drift=20` are all in the R26-133 alive **probe**, never a cut. *Owed:* one comment fix citing s64 / s65. *Owner:* **engine**. **BLOCKS T4** - the treatment names a drift per plate. | proposed | E99 s81 / P68 T3 |
| **R26-212 (audit G-08)** | **A LONG FORM HAS NO GATE AGAINST SPEAKING THE BRAND LINE TWICE** - *measurement:* S07 (*"the brand line ... is stitched under the outro card - a script that speaks it doubles it"*, `gate_opening_structure.py:617`) is in the registry's `opening-short` section and runs only under `run_short`. H is long form, so the check never fires. *Owed:* S07 becomes `opening-shared` (the brand line is stitched in both formats), or a G-numbered twin runs in the long shape. *Owner:* **engine**. | proposed | E99 s81 / P68 T3 |
| **R26-213 (audit G-09)** | **EP1'S FIVE HAND-DRAWN CHART SVGs HAVE NO PORT INTO THE KIT** - *measurement:* `build_scene_evidence_cut.py:45-155` defines `svg_divergence`, `svg_ai_debt`, `svg_arithmetic`, `svg_steel_test`, `svg_tripwires`, each emitting a flat `<svg viewBox="0 0 1376 768">` document from its own arithmetic. The kit's nearest function, `docks.chart_card` -> `chart_card.render_card`, renders a **ledger page** as a dock - a different object. `build-f`'s 38 evidence entries are all `kind: doc`, i.e. flattened renders. *Owed:* nothing in the engine - this is a T4 re-authoring cost, recorded here so it is not discovered mid-build: each of ep1's five charts becomes a ledger page (with its builder and variant) or a chart card, with its series sidecar. *Owner:* **build script** (T4/T6). **BLOCKS T4** - the treatment cannot cite a chart form it has not chosen. | proposed | E99 s81 / P68 T3 |
| **R26-214 (audit G-10)** | **A PERSON INSIDE A FLAT PLATE CANNOT BREATHE; THERE IS STILL NO STUDIO/NEWSROOM PLATE IN THE LIBRARY** - *measurement:* `sources/PLATE-LIBRARY.json` indexes **330** plates; the ids give **0 "studio"**, **0 "newsroom"**, **0 "anchor"** and **2** broadcast plates (`world-broadcast-set-v1` / `-v2`, the latter held in `build-f` for 173.9-204.3 s). The three 16:9 host plates rolled 2026-09-18 02:55 (`steel-and-paper/host/H-{1,2,3}-*.png`, quarantined) are project-local and **not in the library** - correctly, since generated images stay out of git (E99 s31), but the resolver therefore cannot find them by id. Second and larger: `IDLE_KINDS` (`build_scene_timeline_f.py:86`) accepts `;idle=figure` on any plate id, but `idle=figure` (`kinetics/idle.mjs:96`) breathes and sways the **whole element** - on a full-scene host plate that animates the entire room. There is no mechanism to give one region of a FLAT plate its own life; the mask-pinned ambient lane (`CAPABILITIES.md:145`) is that mechanism and has never been run on a person. *Owed:* (a) once the operator approves the frames, the three plates enter the library the way approved plates do, with their layer sidecars; (b) a stated rule that `;idle=figure` is for a declared figure / cutout and is refused on a `plate_option:world` plate (the compiler should say so by name); (c) a decision - recorded, not built - on whether a breathing host is worth an ambient-lane order. *Owner:* **engine** (b), **build script** (a), **doctrine** (c). **BLOCKS T4** only for (b) - the treatment must not write `idle=figure` on a host plate. | proposed | E99 s81 / P68 T3 |
| **R26-215 (audit G-11)** | **`lint_species_choice.py` CANNOT FIND A LONG FORM'S SHOT TABLE BY DEFAULT** - *measurement:* the plan's own step 5 command exits **2** with `lint_species_choice: no shot table at content\video_engine\projects\systems-and-blowups\steel-and-paper\SHOT-TABLE-SHORT.py (the build writes SHOT-TABLE-SHORT.py; --table names another)`. `--table SHOT-TABLE-F.py` also exits 2 - `--table` takes a **path**, not a name; only the full repo-relative path works. *Owed:* (a) `--table` accepts a bare file name resolved against the project dir; (b) the default table name follows the build (`SHOT-TABLE-H.py` for `build-h`), or the error prints the names it did find. *Owner:* **engine**. Informational for H (the full path works, and `build_episode_h.py` can write `SHOT-TABLE-SHORT.py`), but it cost this slice two runs. | proposed | E99 s81 / P68 T3 |
| **R26-216 (audit G-12)** | **EP1'S GATE REPORT PRINTS 16 OF 35 MOTION ROWS; 19 HAVE NEVER JUDGED A LONG FORM** - *measurement:* `gate_motion_density.py` defines 35 distinct `M` ids; `build-f/GATES-MOTION.md` (regenerated 2026-09-17) prints M01-M12, M14, M15, M16, M18 and J01 - **16**. M17, M19-M34, M43, M44 never fire because their subjects (ledger pages, species, chart transitions, camera keys, collisions, frozen frames) are all zero in that timeline. `ledger_pages: 0` is printed at `:9`; `VERDICT: FAIL (8 FAIL)`. *Owed:* nothing to fix - this is the baseline H is measured against, recorded so HG4 can say which rows are **new verdicts** rather than regressions. *Owner:* **doctrine** (the HG4 card). Informational. | proposed | E99 s81 / P68 T3 |
| **R26-217 (audit G-13)** | **THE PORTRAIT STAGE IS BAKED INTO THREE PAGE-LEGIBILITY CONSTANTS** - *measurement:* `ledger_page.py:605` `TREEMAP_VALUE_FONT = 18  # the absolute legible floor on a 1080x1920 stage`, `:607` `TREEMAP_PAD = 6  # ... at 1080x1920`, and the N-tier band floor (`CAPABILITIES.md:102`: *"four bands of a 9:16 plot are ~250 px each, the floor a band can carry"*). On a 1920x1080 stage the arithmetic inverts - fewer, wider bands, and a different legible floor. *Owed:* each constant resolved from the stage it is rendering on, or a stated 16:9 value beside it. *Owner:* **engine**. Informational until T4 chooses a treemap or a tiers page - then it blocks that row. | proposed | E99 s81 / P68 T3 |

**Three of these block T4** (the treatment): **G-09** (ep1's five charts have no form chosen
and no port into the kit - the largest single piece of T4 work), **G-07** (`idle.mjs`'s own
comment names the wrong long-form drift and every plate row in the treatment names a drift),
and **G-10(b)** (`;idle=figure` on a full-scene host plate breathes the whole room - the
treatment must write `idle=drift;drift=20` on the three host rows instead). **One blocks T6**:
**G-06** (there is no landscape outro card, so the cut cannot close). The rest are calibration and documentation, and
each is quotable as a caveat rather than a workaround - per the plan, **no engine gap is ever
worked around inside the build script**.
