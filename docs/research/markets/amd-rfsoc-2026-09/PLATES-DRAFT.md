# AMD / Patel "treason" long form: the NARRATIVE SCENE PLATE schedule (draft)

> **DECISION 2026-09-26 (the operator: "yes"):** AMD is COBALT, Nvidia teal; coral is kept for the alarm / treason beats only. Every prompt below that paints AMD coral is recoloured to cobalt before generation.


Drafted 2026-09-26 by architect_sol for the parent. Draft only. Nothing is generated, dispatched or approved here.
Episode: "AMD's Cover-up Is Not Just Money (Tried for Treason)". Opening v3 is APPROVED (memory `amd-episode-title-ruling.md`).
The order this answers (the operator, 2026-09-26): *"we should produce at least 1 narrative scene per 10 seconds to have as
options, even if we never use them."* Runtime assumed at ~12:00, so the floor is 72. This draft schedules **96 plate options**.
Of those, **16 reuse library plates** and **80 need generation** (12 of the 80 are edits of another new plate: a later state of the same world).

Research used: `fable-p68/docs/research/markets/amd-rfsoc-2026-09/RESEARCH.md` (pack 1) and `RESEARCH-2.md` (pack 2).
Tiers are quoted as C (CONFIRMED), P (PLAUSIBLE) and U (UNSOURCED). A plate sets the world and asserts nothing. Every
figure and quote lands as a docked, sourced evidence card, never painted into a plate.

---

## 0. Recall (run from `fable-p68`; SigMap first: `python scripts/sigmap_context.py query "plate library semantic channel-aware" --top 5`)

- Recall: docs_find "plate library": CAPABILITIES.md:258 "Plate library — LIVE - 326 plates indexed by SEMANTIC across all worktrees and CHANNEL-AWARE (money-physics 134 / martial-matters 192); channels are identity walls — the resolver refuses cross-channel plates". The index on disk is `content/video_engine/sources/PLATE-LIBRARY.json`. It holds 330 rows, 138 of them money-physics. Only **77** are `approved` + `render_eligible` with the file on disk. The index was last committed at b4b556f (2026-09-16), so it predates the P69 waves. Rebuild it before the reuse list is locked.
- Recall: docs_find "plate library": CAPABILITIES.md:152 "a plate's sidecar `<plate>.layers.json` lists `layers[] {path, role, depth, alpha, generator}` back to front ... generator gpt-image-2.5 / gpt-image-2.0 / depth-split / depth-split-sam / flow".
- Recall: docs_find "alive plate": CAPABILITIES.md:154 "THE ALIVE PLATE - a layered plate whose background WALL is a clip ... **E99 s65 (2026-09-16): the long-form plate life is the ALIVE FLAT plate (the life region over the approved still as ONE plane ...) under Ken Burns**".
- Recall: docs_find "ambient lane": CAPABILITIES.md:149 "an approved still, a SAM 2 object mask, a LIFE region, a prompt -> an mp4 where everything outside the region is the still bit-for-bit ... **ONE backend that generates: Wan 2.1 VACE 1.3B** ... the prompt must NAME the motion ("waves rolling", "glints sliding")".
- Recall: docs_find "plate life": `plate-life-is-directional.md` "a held plate's life has ONE direction the story gave it". OPERATOR-RULINGS.md:3296 E99 s84 amends it: "the long-form plate life is KEN BURNS ALONE - `plate_idle_paints` OFF (the 20 px drift s65 paired with it is withdrawn for long form ...); a plate's motion has ONE direction the story gave it."
- Recall: docs_find "layered plate": CAPABILITIES.md:151 "a plate is GENERATED one layer at a time (far / board / mid / near), never cut out of a stacked generation; an existing flat plate may be split instead".
- Recall: docs_find "world plate": scene-evidence-engine.mjs "The narrative plate world — plate_option:world - A generated still IS the scene". OPERATOR-RULINGS.md:1991 E61: "A plate appears for ONE of three uses and names which on its row: (1) a **landing surface** ... (2) a **bridge** ... (3) a **reset** ... a plate with no named use is a WARN".
- Recall: docs_find "Money Physics brand sheet": `money-physics-brand-sheet.md`. BRAND-SHEET.md §3 says "no numbers, logos or watermarks in generated art; no text unless the narrative needs it - any text is named in the prompt, spelled exactly and verified on the frame read (E99 s113) ... no real-person likeness; no flags or political symbols", and "**Quiet zone:** one side of every frame stays mostly bare cream or charcoal as the landing zone for evidence."
- Recall: docs_find "host" / "@Mike": CAPABILITIES.md:256 "**`@Mike`** (retention, entity `dab5d902`, bound FROM the approved sheet)". `mp-host-identity.md` says "Name a bound character and do not re-describe him". `steel-and-paper/host/HOST-NOTES-H.md` says "The driver refuses `@Mike` inside the prompt text - the character goes in `references` and the text says "the character"". **No slot below uses the host.** This is a narrative-plate schedule. A host window is a separate order if the parent wants one.
- Recall: docs_find "props bare": 1 hit, manifest-only. The memory `props-bare-but-weighted` says props never sit on cards and carry a resting shadow from the one stage light. It governs the prop lane (chip and board cutouts), not these plates.
- Recall: docs_find "text on plates": OPERATOR-RULINGS.md:3357 E99 s113 "every piece of text on a plate or prop ... is chosen for the narrative, spelled exactly, and verified against the record ... generator-garbled text is refused on the frame read". OPERATOR-RULINGS.md C7 adds: "no LEGIBLE numerals or labels asserting a specific figure baked into a plate".
- Recall: docs_find "generated images": `generated-images-stay-out-of-git.md` "Generated images never go into the repo, approved or not ... what gets committed is its record".
- Recall: docs_find "GPT Image 2.5": `gpt-image-2-5-generator.md` "generate EACH LAYER as a separate transparent asset with a shared camera brief and a reference image" and "every layer prompt ... states the intent - 'designed for 2.5D parallax compositing'".
- Recall: docs_find "Flow": CAPABILITIES.md:161 "Google Flow driver - zero-credit multi-reference generative diffusion over an ACTIVE Chrome CDP session". OPERATOR-RULINGS.md:1845 E57: "a WORK-ORDER for an episode's plate set (a batch ...) is a bridge packet to the Gemini lane (P46)".
- Recall (rulings read directly): OPERATOR-RULINGS.md:1229 the amended atom "A light application of 2.5D woodblock print and vox newspaper meets rich anime colors." ("from this date every new plate order uses the amended sentence"). E56 (:1815) "a picture's focus is a LIGHT" (no rings on a picture). E99 s38 (:3194) "plate life comes from the local stack ... not a pixel drift". E99 s60 (:3238) "a proof is a SCENE". E99 s71 (:3260) "a light is never the move". C3 (:197) "Target runtime / 12s of distinct world plates". E49 (:1494) "every held thing carries a NAMED idle".
- Recall: CAPABILITIES.md:39 (lane B `p69-s90`) E68 "a public figure's cutout docks beside its datum (`assets/heads/manifest.json` -> `approved`, `render_eligible: true`)". `assets/heads/manifest.json` was **not found** in `fable-p68` or the main checkout, so every real-person photo below needs intake first.

## 1. Rules applied to every slot

1. **Real people are never generated.** Patel, Su, Huang, Trump, Xi and the First Lady appear only as (a) a sourced press photo docked as evidence (the photo to source is named per slot) or (b) an unidentifiable silhouette, back, or hands. Faces are never shown, and no signature wardrobe is drawn (no leather jacket on the stage silhouette).
2. **No logos or brand marks** (AMD, Nvidia, Xilinx, X, DigiKey, Crowd Supply, NYSE, Mouser). The colour cues follow the brief, mapped onto the six tokens because the spine allows no other hue:
   - "Nvidia green" is **teal #178C83**.
   - "AMD red" is **coral #ED6A4A**.
   - PARENT DECISION: the brand sheet fixes teal = positive and coral = negative/alarm ("a chart line and a plate accent must mean the same thing"). Painting AMD in coral reads as editorial alarm. The alternative is AMD in cobalt, Nvidia in teal, with coral kept for alarm. The rows below use the brief's teal/coral and name the swap where it matters.
3. **No fabricated documents presented as real.** The following are never painted: an indictment, an X-post UI, a listing page, a Federal Register page. Every screen and document on a plate is BLANK or illegible scrollwork. The real capture docks, or embeds on the plate's screen quad (art-embed homography, CAPABILITIES "art-embed" / E66).
4. **No flags, seals or political symbols** (spine hard rule). Map tables show carved coastlines only, and state buildings are generic colonnades.
5. **Life (E49 / s65 / s84)**:
   - The default life on every plate is **Ken Burns in ONE direction the line gives it**. It pushes IN on an arrival or reveal, pulls BACK on a reflection or reset, and moves LATERAL across a wide world or a flow. The direction is named per slot.
   - Where a plate has a true life region, the slot also names the **alive-flat** option: the VACE ambient lane on that region with the motion verb for its prompt (CAPABILITIES:149). The alive region is optional. The Ken Burns is not.
6. **Layers.** FLAT is the default (s65: parallax under a free drift reads as random). LAYERED is marked only where a push LANDS on a named thing (E51 / s65 "a camera move with a direction of its own"). A layered plate is generated one layer at a time (GPT Image 2.5 route, section 2).
7. **Use (E61)** is named on every row: `land` (evidence docks on it), `bridge` (B-roll between ideas) or `reset` (covers the world so the next page mounts clean).
8. **Quiet zone.** Every composition names the side kept bare for the dock.
9. **Aspect.** New plates are 16:9. Library plates are mostly 1536x1024 (3:2) and lose about 11 % of their height in a 16:9 crop, so the crop band is named per reuse.
10. **Hero picks** are marked HERO (1-2 per section). Plant/payoff pairs are marked PAIR. A PAIR plate is generated as an edit of its partner (GPT Image 2.5 edit), so the world stays one world.

## 2. Style block (from BRAND-SHEET.md §2-3, style spine STYLE block, amended atom OPERATOR-RULINGS.md:1229)

Each row's prompt holds only the **scene text**. The dispatcher assembles the full prompt mechanically:

**FLAT order** (Flow Nano Banana Pro zero-credit, or GPT Image 2.5) = `P16` + scene text + `STYLE-A` + `NEG-A`.

```
P16:     full bleed edge-to-edge 16:9 horizontal, at least 1920x1080.
STYLE-A: A light application of 2.5D woodblock print and vox newspaper meets rich anime colors. Carved woodblock ink
         contours with visible cut character, flat editorial newsprint colour fields, crisp registration like a fine art
         print; bold clean silhouettes readable at small size; subtle newsprint grain. Matte, never glossy, never
         photographic. Palette strictly: cream #F4E6C7, charcoal #25313C, cobalt #1769C2, teal #178C83, sunflower
         #F5B72E, coral #ED6A4A. Soft even light from the upper left, gentle shadow lower right, low contrast. Camera
         eye-level and straight-on unless the scene says top-down. Adult editorial tone, financially credible, never
         childish. One side of the frame stays mostly bare as a quiet zone.
NEG-A:   Negative: no borders, no margins, no outer frame, no paper matting, no torn or deckle edges, no washi, no
         collage, no photorealism, no 3D render, no logos, no brand marks, no watermarks, no flags, no seals or
         emblems, no political symbols, no recognisable face or real-person likeness, no numbers, no text, no letters,
         no captions - except any words this prompt names, spelled exactly as given. Screens and documents are blank
         or show only illegible engraved scrollwork.
```

**LAYERED order** (GPT Image 2.5, P58 T1 route (a); one call per layer, back to front: `far` opaque, then `mid`, `subject`, `near` as transparent RGBA):

```
P16 + "Create ONLY the <far|mid|subject|near> layer of this scene as an isolated <opaque|transparent PNG> asset. " +
"SCENE: <scene text>. CAMERA (shared by every layer): <the row's camera line>. This layer holds: <the row's layer
line>. Designed for 2.5D parallax compositing: clean edge separation, no cropped limbs, no cast shadow outside the
layer, nothing from the other layers. " + STYLE-A + NEG-A
```

The depth, roles and camera path stay ours (the `<plate>.layers.json` sidecar). Never ask one generation for a layered scene.

**ALIVE-FLAT** (after the still is approved): `comfy_vace_ambient.py` on the named life region, with the row's motion verb in the prompt. The mp4 is gitignored, and the sidecar + life mask + job JSON are the record (CAPABILITIES:154).

**Routing (the parent's call; nothing is dispatched here):**
- By E57, the episode batch is a bridge packet to the Gemini lane (Flow, zero credit).
- The LAYERED heroes go to GPT Image 2.5 through the codex claim (`codex-fulfillment-flow`).
- No paid roll happens without the operator's word (E99 s37).
- Every still is quarantined until the operator approves the frame. Images never enter git (E99 s31).

Column key for the tables: `win` = the time window; `LIFE` = the Ken Burns direction, plus `alive:` where a life region exists; `L` = FLAT or LAYERED (with its layers); `txt` = text on the plate; `ppl` = how real people appear; `src` = REUSE `<library id>` or GEN; `use` = E61 use + the quiet side + what docks.

---

## 3. OPENING 0:00-0:34 (approved v3; 13 options, about one per 2.6 s because every line gets a choice)

Line timings assume about 170 wpm; re-time on the take. The pivot line runs to about 0:34, so the opening closes there.

| id | win | line / beat | picture (subject · composition · camera · light) | LIFE | L | txt | ppl | src | use |
|---|---|---|---|---|---|---|---|---|---|
| O-01 | 0:00-0:04 | "AMD told you China cost it eight hundred million dollars." | A glass corporate tower at night, one full floor lit coral, the rest dark; the tower on the right third, low sky with carved clouds on the left. Eye-level from across a plaza. | KB push-in toward the lit floor (the claim arrives). alive: clouds drift L→R in the sky band ("clouds drifting") | FLAT | none | none | GEN | land · quiet left sky · the 8-K line "$800 million" (Q2'25, sources/36, C). PAIR with C6-11 |
| O-02 | 0:00-0:04 (alt) | same | Accelerator crates stacked in a dim warehouse, a chain and padlock across the front row, one coral hold lamp above; the stack on the left, the aisle bare on the right. | KB push-in to the padlock | FLAT | none (no tag text) | none | GEN | land · quiet right · the $800M charge card. PAIR with C4-01 |
| O-03 | 0:04-0:08 | "The most-read analyst in chips says it cost America something worse:" | **HERO.** The analyst's desk at 2 a.m.: a figure seen from BEHIND, head and shoulders dark against two monitors, a phone glowing face-up by the keyboard, datasheets pinned to a corkboard (illegible scrollwork), a bare chip under a desk loupe; the desk fills the left two-thirds. | KB push-in over the shoulder to the phone. alive: the phone's glow and the monitor light breathe ("screen glow pulsing") | LAYERED: far = wall + corkboard; mid = desk, monitors, phone; subject = the figure's back; near = a desk-lamp edge, left | none | Patel: NOT drawn. An anonymous back only. His sourced portrait (semianalysis.com/dylan-patel page photo; E68 heads intake) docks beside it | GEN | land · quiet right third · the head dock + "the most-read analyst" badge (SemiAnalysis 200k+ subscribers, P). PAIR with C6-09 |
| O-04 | 0:04-0:08 (alt) | same | The same desk with NOBODY at it: chair pushed back, phone lit, the loupe over the chip; it carries no likeness question at all. | KB push-in to the phone | FLAT | none | none | GEN (edit of O-03's far + mid) | land · quiet right |
| O-05 | 0:08-0:11 | "AMD needs to be investigated for treason." | **HERO.** An investigator's hanging lamp swung low over one silicon wafer on a dark table, a magnifying loupe resting on the wafer's edge, a hard sunflower cone of light, everything else charcoal; the wafer centre-left. | KB push-in to the wafer under the loupe. alive: the hanging lamp sways, cone swinging L→R ("lamp swaying") | FLAT | none | none | GEN | land · quiet right charcoal · the real X post (sources/01, 28; a captured screenshot, C) as a press card. The word matches the claim: *investigated* |
| O-06 | 0:08-0:11 (alt) | same | A wooden gavel resting on a silicon wafer on a charcoal bench, one sunflower rim light. | KB push-in | FLAT | none | none | GEN | land · quiet left. ATTRIBUTION NOTE: a gavel reads as a trial, and Patel said "investigated". Use it only under his quoted line or the title card, never under a narrated fact |
| O-07 | 0:11-0:15 | "Nvidia never had to beat AMD on chips. Nvidia beat them on trust." | A chessboard whose squares are chip packages; teal pieces on one side, coral on the other; above the board a teal-sleeved hand shakes a charcoal-sleeved hand (the state), while the coral side's hand hovers over its piece alone. Hands only, from the wrists. Board low centre, handshake upper right. | KB lateral L→R from the coral hand to the handshake | FLAT | none | none (hands, no faces, no insignia) | GEN | bridge · quiet upper left. PAIR with C6-07 |
| O-08 | 0:11-0:15 (alt) | same | A brass balance scale with one identical chip on each pan, level; a small iron key drops onto the teal pan and tips it. | KB push-in to the key | FLAT | none | none | GEN | bridge · quiet right |
| O-09 | 0:15-0:18 | "Lisa Su is a phenomenal CEO." | An empty keynote stage in coral wash, one podium, a vast wall of lit server racks behind it (the success); the podium right of centre, the stage floor bare on the left. | KB push-in to the podium | FLAT | none | Su: NOT drawn. Sourced photo dock: the NYSE opening bell 2026-09-23 (Fox Business / NYSE photo desk) or an AMD newsroom executive photo | GEN | land · quiet left · the photo + "$1T, +193% YTD" (P) |
| O-10 | 0:18-0:22 | "But Jensen Huang takes a call from the President on stage -" | **HERO.** A keynote stage from the back rows: a lone silhouetted presenter, backlit, holding a phone up to a handheld microphone, teal stage wash; a row of audience heads in silhouette across the bottom; the big screen behind him blank. | KB push-in toward the phone at the mic. alive: stage haze drifts L→R, audience phone screens flicker ("haze drifting") | LAYERED: far = blank screen + stage; subject = the presenter silhouette; near = audience heads row | none | Huang: silhouette only, a plain dark jacket, no leather texture. Sourced dock: an All-In Summit 2026-09-14 press photo (TechCrunch / NBC coverage of the call, sources/36, C) | GEN | land · the blank screen is the embed quad · the photo + Trump quote card "The whole thing is a hoax." (NBC, C) |
| O-11 | 0:22-0:25 | "- while Dylan Patel accuses AMD of playing for the other side." | The O-07 chessboard seen closer: a single coral piece standing on the far rank among charcoal pieces, on the wrong side of the board's centre line. | KB pull-back from the lone piece to the whole board (the reveal) | FLAT | none | none | GEN (edit of O-07) | bridge · quiet left · Patel's quote card (his allegation, attributed) |
| O-12 | 0:25-0:31 | "And five days after that post, Lisa Su sat two seats from the President... at dinner with Xi." | **HERO.** A state-dinner head table in white linen, candle lamps, gold-rimmed settings; the two centre chairs high-backed and EMPTY; two seats to the left of centre a blank place card lit by the nearest candle. No flags, no seals, no crests. Table runs L→R across the lower half, a dark panelled wall above. | KB lateral L→R along the table, landing on the blank card. alive: candle flames flicker ("candle flames flickering") | LAYERED: far = wall; mid = the table and chairs; near = one candle lamp foreground right | none on the card (blank) | Su / Trump / Xi: NONE drawn; empty chairs. Sourced dock: the White House pool photo of the head table, 2026-09-24 (Yahoo Finance / Werschkul, sources/36, C) | GEN | land · quiet upper wall · the pool photo + "two seats away" quote (C). PAIR with C6-02 |
| O-13 | 0:31-0:34 | "So how did a chip become a geopolitical flashpoint?" | **HERO.** One chip resting exactly on the seam of a carved wooden map table where two coastlines face each other across an ocean (no labels, no flags); a single overhead light on the chip, the rest of the map in charcoal shadow. Top-down, straight-on. | KB push-in to the chip (the question lands) | LAYERED: far = the map; subject = the chip; near = the lamp's rim at top | none | none | GEN | reset · the map is the quiet ground · nothing docks: the question holds |

**Prompts: opening (scene text only; assemble per section 2)**

- **O-01**: A tall glass corporate office tower at night seen from across an empty stone plaza. One entire floor near the top glows warm coral from inside; every other floor is dark charcoal glass. The tower stands in the right third of the frame; the left two-thirds is a deep cobalt night sky with a few carved woodblock clouds. No signage, no logo on the building.
- **O-02**: A dim warehouse interior. Wooden and metal crates of computer accelerators stacked three high on the left half of the frame, a heavy chain and padlock run across the front row, and a single coral hold lamp glows above them. The right half is an empty concrete aisle fading into shadow. No labels, no writing on the crates.
- **O-03**: Night, 2 a.m. An analyst's desk seen from behind a seated figure: only the dark silhouette of the head and shoulders, no face visible. Two monitors glow a soft cobalt, a smartphone lies face-up by the keyboard with its screen lit and blank, a corkboard behind is pinned with technical datasheets drawn as illegible engraved scrollwork, and a bare square computer chip sits under a small desk loupe. The desk fills the left two-thirds; the right third is a dark charcoal wall.
- **O-04**: The same late-night analyst's desk with nobody at it: the chair pushed back and turned, the smartphone lit face-up and blank, the monitors glowing, the chip under the loupe, datasheets as illegible scrollwork on the corkboard. Right third a dark charcoal wall.
- **O-05**: A low hanging metal lamp swung down over a dark wooden table, throwing a hard sunflower-yellow cone onto a single round silicon wafer, its die grid catching the light. A round magnifying loupe rests on the wafer's edge. Centre-left composition; everything outside the cone falls to charcoal; the right side is bare dark.
- **O-06**: A wooden judge's gavel resting across a round silicon wafer on a charcoal wooden bench, a thin sunflower rim light along the gavel's edge, the rest in shadow. Composition on the right; the left half bare dark.
- **O-07**: A chessboard seen slightly from above, its squares made of small square computer chip packages. Teal chess pieces on one side, coral chess pieces on the other. Above the board on the right, a hand in a teal sleeve shakes a hand in a plain charcoal suit sleeve; on the left, a hand in a coral sleeve hovers alone over a coral piece. Hands and forearms only, no faces, no insignia. The upper left is bare cream.
- **O-08**: A brass balance scale on a cream ground, one identical square computer chip on each pan, perfectly level; a small iron key is falling onto the teal-rimmed pan, beginning to tip it. The scale sits left of centre; the right third is bare.
- **O-09**: An empty conference keynote stage washed in soft coral light, one plain podium right of centre, and behind it a vast wall of lit server racks in charcoal and cobalt. The stage floor on the left is bare and dark. No screens with content, no logos.
- **O-10**: A large keynote auditorium seen from the back rows. On the distant stage a single presenter stands in silhouette, backlit, holding a smartphone up against a handheld microphone. Teal stage light washes the floor. A row of audience heads in silhouette runs across the bottom of the frame. The giant screen behind the presenter is blank and softly lit. No faces, no logos, no text.
- **O-11**: Close view of a chessboard made of computer chip packages: one coral chess piece stands alone on the far rank, surrounded by charcoal pieces, clearly past the board's centre line on the opponent's side. Soft light from the upper left. The left third of the frame is bare.
- **O-12**: A formal state dinner head table with white linen, gold-rimmed plates, crystal glasses and small candle lamps, running left to right across the lower half of the frame. The two chairs at the centre are tall, high-backed and empty. Two seats to the left of the centre, a folded blank place card is lit warmly by the nearest candle. Behind the table, a dark panelled wall. No flags, no seals, no crests, no people, no writing on the cards.
- **O-13**: Top-down, straight-on: a carved wooden map table showing two coastlines facing each other across a wide ocean, with no labels, borders or flags. A single square computer chip rests exactly on the ocean between them. One overhead lamp lights the chip; the rest of the map falls to charcoal shadow.

---

## 4. WORLD-SETTING 0:34-1:30 (the hot, flashy stories, then the turn to the chip; 13 options)

This stretch is not scripted yet. The beats follow the approved shape: the post, the call on stage, the dinner and the $1T day, then deeper. They run in calendar order so each plate can carry a date stamp:
- 09-14: the call on stage
- 09-19: the post
- 09-21: $1T
- 09-22: AMD's answer via Patel
- 09-23: the bell, and Xi arrives
- 09-24: the dinner
- then the turn: one chip and what it does

| id | win | line / beat | picture | LIFE | L | txt | ppl | src | use |
|---|---|---|---|---|---|---|---|---|---|
| W-01 | 0:34-0:39 | Sept 14, Los Angeles: the phone rings on stage | The WIDE room, distinct from O-10: a vast summit hall from the balcony, rows of seated silhouettes, a small bright stage far off with one figure and a huge blank screen; balcony rail across the foreground. | KB lateral R→L across the hall toward the stage | FLAT | none | Huang: a distant silhouette only. Dock: the All-In Summit press photo (TechCrunch 2026-09-14: "handed a foldable phone to answer it", C) | GEN | land · the blank screen is the embed quad for the photo |
| W-02 | 0:39-0:44 | Sept 19: the post | **HERO.** A smartphone lying face-up on a dark desk at night, its screen lit and BLANK, filling the centre third; a cold coffee cup and a pen at the edges, the rest charcoal. Straight-on top-down. | KB push-in into the phone screen (the post arrives on it) | FLAT | none (the screen is blank) | none | GEN | land · **art-embed**: the captured real post (sources/01/28, C) is projected onto the screen quad; nothing is painted |
| W-03 | 0:44-0:48 | the post travels (392,528 views) | A night city of apartment blocks; hundreds of windows, and in many of them a small cobalt glow of a phone screen, lighting up in a wave across the facade. | KB pull-back (the reach widens). alive: window glows switch on in a wave L→R ("windows lighting up one by one") | FLAT | none | none | GEN | bridge · quiet sky top · views badge 392,528 (C) |
| W-04 | 0:48-0:53 | Sept 21: AMD +9.95%, briefly $1 trillion | A trading floor at the opening: a tall ticker wall of carved bars and arrows turning teal from the bottom up, desks with silhouettes in the lower third; no letters, no tickers spelled. | KB tilt/push UP the wall. alive: the ticker band scrolls R→L ("ticker lights scrolling") | FLAT | none (abstract marks only; C7 allows a trend arrow, no figure) | none | GEN | land · quiet upper left · the AMD close chart 559.82 → 615.52 (sources/29, C) + "$1T" (P) |
| W-05 | 0:53-0:57 | "the market didn't care" | REUSE `world-broadcast-set-v2`: an empty finance broadcast set between takes, world-map screens, the anchor chairs empty. | KB push-in to the empty chairs | FLAT | none | none | REUSE (1536x1024; crop the 16:9 band from the top: keep the screens, lose the floor cables) | bridge · the press finding "none mentions Patel" (E6, P) |
| W-06 | 0:57-1:01 | Sept 22: AMD's answer, through Patel | REUSE `world-internal-memo-v1`: a single typed page (illegible lines, a coral seal ring) under a cobalt desk lamp, a mug. | KB push-in to the page | FLAT | none (the lines are illegible) | none | REUSE (crop the centre band) | land · quiet cream top · Patel's follow-up quoting AMD: "they did not ship / sell this dual use chip to this firm and they're investigating the sourcing" (sources/28, C as his post) |
| W-07 | 1:01-1:05 | Sept 23: Su rings the opening bell with the First Lady | A balcony podium high above an exchange floor, a brass bell on the rail, confetti falling through shafts of light; two small figures at the rail seen from BEHIND. No exchange name, no flags. | KB pull-back from the bell to the floor below. alive: confetti falls ("confetti falling") | FLAT | none | Su + First Lady: two unidentifiable backs. Dock: the NYSE opening-bell photo 2026-09-23 + Su's quote "I will be at the dinner tomorrow night" (Fox Business, sources/36, C) | GEN | land · quiet lower right floor |
| W-08 | 1:05-1:10 | Xi arrives: the first US state visit in over a decade | An airport apron at dusk: a large jet's nose and a mobile stair, a long carpet running to it, a line of honour-guard silhouettes; no insignia, no flags, no livery. | KB lateral L→R along the carpet to the stair. alive: runway edge lights chase L→R ("runway lights blinking in sequence") | FLAT | none | Xi: NOT drawn (the stair is empty). Dock: an NBC arrival photo (sources/30; the date is 09-22 or 09-23, P, so say "this week") | GEN | land · quiet dusk sky top |
| W-09 | 1:10-1:15 | Sept 24: over thirty CEOs at the state dinner | A grand state dining room from the doors: chandeliers, dozens of round tables of evening-wear silhouettes, one long head table far away under a lit wall. | KB push-in toward the far head table. alive: chandelier glints sparkle ("crystal glints shimmering") | FLAT | none | all guests faceless silhouettes | GEN | land · quiet ceiling band · the Yahoo headline press card "over 30 CEOs ... 4 got a spot at the head table" (C) |
| W-10 | 1:15-1:19 | the four at the head table | The head table closer: four tall empty chairs, each with a blank place card, each card catching its own candle. | KB lateral L→R card to card | FLAT | none | Musk / Huang / Cook / Su: NONE drawn. Four sourced photo cutouts dock over the four cards (E68 heads intake) | GEN (edit of O-12's far + mid) | land · the four cards are the dock anchors |
| W-11 | 1:19-1:24 | "underneath the headlines, there's one chip" | **HERO.** A wall of pinned clippings (every column illegible scrollwork, no mastheads) with red thread running from them down to a desk, where the thread ends at a single chip under a lamp. Wall upper two-thirds, desk bottom. | KB tilt DOWN from the clippings to the chip (the turn) | LAYERED: far = the clipping wall; mid = the desk; subject = the chip under the lamp | none | none | GEN | reset · the wall clears the headlines · the next page mounts clean |
| W-12 | 1:24-1:30 | what the chip is for | **HERO.** A coastal phased-array radar at dusk: a flat, tilted panel of many small square elements on a concrete mast on a headland, fan-shaped carved beam lines reaching over the sea; low sun, cobalt sky. No military markings. | KB pull-back from the panel to the headland and sea (the scale). alive: a shimmer sweeps across the panel's elements L→R, sea swell ("light sweeping across the panel", "waves rolling") | LAYERED: far = sky + sea; mid = the headland; subject = the radar panel and mast | none | none | GEN | land · quiet sky right · Xilinx Gen-3 RFSoC 2019 release "Advanced phased-array radar" (sources/11, C) |
| W-13 | 1:24-1:30 (alt) | the tug of war over one chip | A rope made of copper circuit traces stretched across an ocean between two coastlines, a team of small silhouettes pulling on each shore, one chip tied at the rope's midpoint over the water. No flags, no labels. | KB lateral L→R along the rope to the chip | FLAT | none | none | GEN | bridge · quiet sky top |

**Prompts: world-setting**

- **W-01**: A vast summit auditorium seen from a high balcony, the balcony's dark rail across the bottom foreground. Hundreds of seated audience silhouettes fill the rows. Far away, a small bright stage with one standing figure in silhouette and a huge softly lit blank screen behind it. Teal stage light, the hall in charcoal. No faces, no logos, no text.
- **W-02**: Top-down, straight-on: a smartphone lies face-up on a dark wooden desk at night, its screen lit bright and completely blank, centred in the frame. A cold coffee cup at the upper left edge and a pen at the lower right edge; everything else is charcoal shadow.
- **W-03**: A city of tall apartment blocks at night, seen straight-on. Across the facades hundreds of small windows; in many of them a tiny cobalt glow of a phone screen, the glows spreading across the buildings like a wave from left to right. Upper third a dark cobalt sky.
- **W-04**: A stock exchange trading floor at the opening seen straight-on. A tall wall of carved ticker bars and upward arrows occupies the upper two-thirds, turning teal from the bottom up; desks and seated trader silhouettes fill the lower third. Only abstract bars and arrows on the wall, no letters, no numbers. The upper left corner is bare.
- **W-07**: A high balcony podium above a busy exchange floor, a polished brass bell mounted on the balcony rail, bright confetti falling through shafts of light. Two small figures stand at the rail seen from behind, faces not visible. The exchange floor below on the lower right is soft and bare. No names, no flags, no logos.
- **W-08**: An airport apron at dusk: the nose of a large plain jet and a mobile stair on the right, a long carpet running from the lower left to the foot of the empty stair, and a line of honour-guard silhouettes along it. Runway edge lights in a row. No insignia, no flags, no livery, no writing. Wide cobalt and sunflower dusk sky across the top.
- **W-09**: A grand formal state dining room seen from its open doors: crystal chandeliers, dozens of round tables with evening-wear guests drawn as faceless silhouettes, and far away a long head table under a softly lit panelled wall. No flags, no seals, no crests. The ceiling band is quiet charcoal.
- **W-10**: Closer view of a formal head table: four tall empty chairs in a row, each with a folded blank place card in front of it, each card lit by its own small candle lamp. White linen, gold-rimmed plates. A dark panelled wall behind. No people, no writing on the cards, no flags.
- **W-11**: A wall covered in pinned newspaper clippings whose columns are only illegible engraved scrollwork, with no mastheads, no headlines and no photos. Red threads run from several clippings down to a wooden desk at the bottom of the frame, where they meet at a single square computer chip under a small desk lamp. The wall fills the upper two-thirds.
- **W-12**: A coastal phased-array radar at dusk: a large flat tilted panel made of a grid of many small square elements mounted on a concrete mast on a rocky headland. Fan-shaped carved beam lines reach out over the sea. Low sunflower sun, cobalt sky, charcoal sea. No markings, no insignia, no text. The right side of the sky is quiet.
- **W-13**: A long rope made of braided copper circuit traces stretched across a wide ocean between two coastlines. On each shore a team of small silhouetted figures pulls on it. At the rope's midpoint over the water hangs a single square computer chip. No flags, no labels. Carved woodblock sea and sky.

---

## 5. CHAPTER 1: chips become weapons, 2016-2019 (1:30-3:10, 100 s; 11 options)

Beats, all from pack 2 §2:
- 2016-02: AMD forms the THATIC joint venture, licensing $293M (C).
- 2017-08-15: ECCN 3A001.a.14 controls RFSoC-type chips; BIS expects "50 or fewer" licence applications a year (C).
- The 2015 counterfeit-Xilinx case (P).
- 2018: Hygon's Dhyana goes on sale (P).
- 2019-02-20: Gen-3 RFSoC is announced with phased-array radar among its uses (C).
- 2019-06-24: Hygon, AMD's JVs and Sugon go on the Entity List, citing Sugon's "military end uses" (C).
- AMD complies (C).

| id | win | line / beat | picture | LIFE | L | txt | ppl | src | use |
|---|---|---|---|---|---|---|---|---|---|
| C1-01 | 1:30-1:39 | 2017: Washington draws a line around a kind of chip | REUSE `world-license-cabinet-v1`: a cobalt card cabinet of locked drawers, one drawer open, four coloured hands reaching for it. | KB push-in to the one open drawer | FLAT | none (the drawer labels are blank) | hands only | REUSE (3:2; crop the centre band) | land · quiet cream top-left · FR 2017-16904 excerpt "Paragraph 3A001.a.14 is added..." (C) |
| C1-02 | 1:39-1:48 | what the rule controls: a chip that turns radio into data | **HERO.** An antenna mast on a hill; the sky is full of carved wave lines that converge and pour into one small chip on a stone plinth in the foreground; the chip emits neat stepped lines out the other side. | KB push-in along the waves to the chip. alive: the wave lines flow L→R into the chip ("waves flowing") | LAYERED: far = sky with waves; mid = the hill and mast; subject = the chip on its plinth | none | none | GEN | bridge · quiet lower right · then the flow diagram (antenna → ADC → fabric → DAC) mounts clean |
| C1-03 | 1:48-1:56 | "50 or fewer" licence applications a year | A quiet government licensing office: a single wooden in-tray holding a thin stack of forms, a rubber stamp at rest beside it, one tall window with grey light; the desk left, the wall bare right. | KB push-in to the thin stack | FLAT | none (forms illegible) | none | GEN | land · quiet right wall · "50 or fewer" badge (FR 2017, C) |
| C1-04 | 1:56-2:05 | dual use: the same chip on both sides | One chip at the centre of a workbench under split lighting: the left half warm sunflower, with a miniature cell tower and a cable box; the right half cool cobalt, with a miniature radar dish. The chip sits exactly on the light's seam. | KB lateral L→R (civil to military) | FLAT | none | none | GEN | bridge · quiet top band · Tom's line "technically aimed at civil, commercial, and industrial applications" (P) |
| C1-05 | 2:05-2:14 | 2015: three traders try the swap | A jeweller's workbench under a magnifier lamp: two identical chips side by side on a felt pad, tweezers lifting a blank label off one, a small tray of blank labels. | KB push-in to the tweezers | FLAT | none (blank labels) | hands only | GEN | land · quiet right · DOJ 2015 case card "counterfeit Xilinx brand label" (P, keep the tier) |
| C1-06 | 2:14-2:23 | 2016: AMD licenses its server design to a Chinese venture | Two hands across a boardroom table passing a sealed blueprint tube: one sleeve coral, one sleeve plain charcoal; a rolled server-board drawing (illegible) on the table. | KB push-in to the tube changing hands | FLAT | none | hands only | GEN | land · quiet upper left · AMD 10-K R11 "$293 million" (C) |
| C1-07 | 2:23-2:31 | 2018: Hygon's own server chip goes on sale | REUSE `world-memory-fab-floor-v1`: a cleanroom aisle of tool bays, a single suited figure far down the aisle, overhead transport pods. | KB push-in down the aisle | FLAT | none | an anonymous suited figure | REUSE (crop the centre band) | bridge · the evidence page mounts over the aisle's cream ceiling |
| C1-08 | 2:31-2:40 | 2019: Xilinx's Gen-3 RFSoC, pitched for radar | REUSE `world-circuit-terrain-v1`: a circuit board as a night terrain of chips, one socket empty. It is a slight register drift (paper-toy sheen) but approved. | KB push-in to the empty socket (the part to come) | FLAT | none | none | REUSE (crop the centre band) | bridge · the socket is where the chip prop lands (bare prop, `arrive: stamp`) |
| C1-09 | 2:40-2:49 | 2019-06-24: the blacklist | **HERO.** A heavy bound register open on a wooden lectern, its columns illegible engraved scrollwork, a quill drawing a firm line through one entry, a round ink stamp poised above the page; one lamp. | KB push-in to the quill's line. alive: the quill's ink line extends L→R ("ink line being drawn") | LAYERED: far = the dark room; mid = the lectern + register; near = the stamp in the foreground top | none (a generic register, NOT the Federal Register) | hand only | GEN | land · quiet left dark · FR 2019-13245 "This rule is effective June 24, 2019." (C). PAIR with C5-14 |
| C1-10 | 2:49-2:58 | Sugon: "military end uses" | REUSE `world-datacenter-aisle-v1`: a long hot aisle of server racks with heat waves rising, one rack door open. | KB push-in down the aisle | FLAT | none | none | REUSE (crop the centre band) | land · quiet cream sky top · FR quote Sugon "publicly acknowledged a variety of military end uses" (C) |
| C1-11 | 2:58-3:10 | AMD complies; the gate shuts | A factory gate at dusk swung almost shut by a single guard (a silhouette from behind), a short queue of delivery trucks outside, floodlights coming on. | KB pull-back (the door closes on the chapter). alive: floodlights flicker on in sequence ("floodlights switching on") | FLAT | none | an anonymous guard | GEN | reset · the next chapter mounts clean · 10-K "complying with U.S. law pertaining to the Entity List designation" (C) |

**Prompts: chapter 1**

- **C1-02**: A tall radio antenna mast on a grassy hill under a cobalt sky filled with carved woodblock wave lines. The wave lines converge from the sky and pour into one small square computer chip resting on a stone plinth in the lower right foreground; out of the chip's other side run neat stepped lines, like a staircase signal. No text, no numbers.
- **C1-03**: A quiet government licensing office seen straight-on. On the left, a wooden desk with a single wooden in-tray holding a thin stack of forms (illegible scrollwork) and a rubber stamp resting beside it. One tall window with soft grey light. The right half of the frame is a bare cream wall.
- **C1-04**: A long workbench with one square computer chip at its exact centre. The left half of the frame is lit warm sunflower and holds a miniature cell-phone tower and a small cable modem; the right half is lit cool cobalt and holds a miniature radar dish. The chip sits on the seam where the two lights meet. Top band bare.
- **C1-05**: A jeweller's workbench under a round magnifier lamp. Two identical square computer chips sit side by side on a charcoal felt pad; a pair of tweezers lifts a small blank label off one of them; a little tray of blank labels sits nearby. Hands only at the edge of the frame. Right third bare and dark.
- **C1-06**: A boardroom table seen from the side. Two hands pass a sealed cylindrical blueprint tube across the table: one sleeve coral, the other a plain charcoal suit sleeve, no insignia. A rolled technical drawing of a server board (illegible lines) lies on the table. The upper left is bare.
- **C1-09**: A heavy bound register book open on a tall wooden lectern in a dark room, its columns filled with illegible engraved scrollwork. A quill pen draws a firm straight line through one entry. A round ink stamp hovers in the foreground at the top of the frame. One lamp lights the page. The left side of the frame is dark and bare.
- **C1-11**: A factory's tall iron gate at dusk, a single guard seen from behind pushing it almost shut. Outside the gate a short queue of plain delivery trucks with their lights on. Floodlights on poles are switching on. No signage, no writing.

---

## 6. CHAPTER 2: Hong Kong stops being a loophole, 2020 (3:10-4:40, 90 s; 11 options)

Beats:
- 2020-06-29: the military end-use rule (C).
- 2020-07-14: EO 13936 (C).
- 2020-12-23: HK is treated as China (C); BIS: "Sometimes, a US export is routed through Hong Kong to avoid US export regulations." (C).
- 2020: China (incl. HK) is AMD's largest billing region, $2,329M vs US $2,294M (C).
- HK carries 52% of China's chip imports, $124B in Jan-May 2026 (P).
- Operation Gatekeeper: at least $160M relabelled via an HK logistics firm (P).
- Kharon: 1,400+ firms at 16 addresses (P).
- Singapore: US$390M in alleged transactions (P, allegations).

| id | win | line / beat | picture | LIFE | L | txt | ppl | src | use |
|---|---|---|---|---|---|---|---|---|---|
| C2-01 | 3:10-3:18 | Hong Kong: the door into China | **HERO.** Hong Kong's container harbour at night: towering stacks, gantry cranes, the ridge of the peak behind; on a quay in the foreground, among the containers, ONE small parcel lit sunflower. | KB push-in to the small parcel (it lands). alive: harbour water ripples, crane lights ("water rippling") | LAYERED: far = the peak + sky; mid = cranes + stacks; subject = the lit parcel on the quay; near = a bollard + mooring rope | none | none | GEN | land · quiet night sky top · BIS HK page quote (C) |
| C2-02 | 3:10-3:18 (alt) | same | REUSE `world-korea-port-v1`: a container port at dusk printed as a square block on the left, bare cream on the right half. | KB push-in to the crane | FLAT | none | none | REUSE (3:2; the cream right half is the ready quiet zone) | land · the right half takes the evidence page |
| C2-03 | 3:18-3:27 | 2020: the barrier comes down | A harbour road checkpoint: a striped barrier arm LOWERED across the lane, a coral warning lamp on its post, a truck stopped before it, the harbour behind. | KB push-in to the barrier arm. alive: the warning lamp blinks ("warning lamp blinking") | FLAT | none | none | GEN | land · quiet upper right · FR 2020-28101 "treated ... as transactions destined for the People's Republic of China" (C) |
| C2-04 | 3:27-3:36 | the customs bench | **HERO.** A customs inspection bench: an X-ray monitor showing the ghostly teal outline of a boxed parcel with a chip's pin grid glowing inside; an officer's gloved hand on the conveyor; the monitor right of centre. | KB push-in into the X-ray screen. alive: the scan line sweeps top→bottom ("scan line sweeping down") | FLAT | none (the screen is image only, no readout) | a gloved hand only | GEN | land · quiet left · BIS: "a US export is routed through Hong Kong to avoid US export regulations" (C) |
| C2-05 | 3:36-3:45 | routed through Hong Kong | Top-down: a carved map table of a river delta coastline, no labels; a hand pressing a pin into one harbour, a string running from a far port through the pin and on inland. | KB lateral along the string, from the far port through the pin | FLAT | none | a hand only | GEN | bridge · the map is the ground for the route page |
| C2-06 | 3:45-3:54 | 2020: China billed more than the US | REUSE `world-till-drawer-v1`: an open till drawer, cash being counted. | KB push-in to the drawer | FLAT | none | hands only | REUSE (crop the centre band) | bridge · the two-bar page $2,329M vs $2,294M (C) mounts after |
| C2-07 | 3:54-4:03 | half of China's chips come through here | A river of small parcels flowing through a narrow harbour mouth between two headlands, fanning out into a wide delta beyond; seen from high above. | KB lateral following the flow L→R. alive: parcels drift along the channel ("parcels drifting with the current") | FLAT | none | none | GEN | land · quiet sky top · "52% of China's chip imports, $124B Jan-May 2026" (P: Bloomberg via TNW) |
| C2-08 | 4:03-4:12 | Operation Gatekeeper: the relabel | A logistics warehouse at night: gloved hands peeling a label off a chip carton and pressing on a blank one, stacks of cartons behind in charcoal. | KB push-in to the hands | FLAT | none (both labels blank) | hands only | GEN | land · quiet right · DOJ via Arnold & Porter "relabeled Nvidia chips with a nonexistent fake brand", at least $160M (P) |
| C2-09 | 4:12-4:21 | 1,400 firms, 16 addresses | A narrow building lobby whose whole wall is hundreds of small brass letterboxes, one lit; a single bulb. | KB pull-back (the wall keeps growing) | FLAT | none (the slots are blank) | none | GEN | land · quiet floor · the Kharon count (P) |
| C2-10 | 4:21-4:30 | the long way round (a third country) | Night cargo apron: a plain freighter's nose door open, pallets rolling in on a loader, rain on the tarmac. No livery. | KB lateral with the pallets. alive: rain falling ("rain falling") | FLAT | none | anonymous loaders | GEN | land · quiet sky top · Singapore case card "US$390M of transactions" (P, ALLEGED) |
| C2-11 | 4:30-4:40 | the door that stays ajar | REUSE `world-gpu-crate-dock-v1`: accelerator crates on a dock at sunset, a forklift, a ship. | KB pull-back | FLAT | none | none | REUSE (crop the centre band) | reset · into chapter 3 |

**Prompts: chapter 2**

- **C2-01**: Hong Kong's container harbour at night: towering stacks of shipping containers in cobalt, teal and coral, tall gantry cranes, and the dark ridge of the peak behind the city lights. On a stone quay in the foreground among the containers, one small cardboard parcel is lit sunflower-yellow as if by a single lamp. A bollard and mooring rope in the near foreground. No writing on any container, no flags, no logos. Night sky across the top.
- **C2-03**: A harbour road checkpoint at dusk: a striped barrier arm lowered across the lane, a coral warning lamp on its post, a plain truck stopped in front of it, cranes and water behind. No signs, no text. The upper right sky is quiet.
- **C2-04**: A customs inspection bench seen straight-on. An X-ray monitor stands right of centre, showing the ghostly teal outline of a boxed parcel with the glowing grid of a computer chip's pins inside it, image only with no readouts or text. An officer's gloved hand rests on the conveyor belt below. The left third is bare dark.
- **C2-05**: Top-down, straight-on: a carved wooden map table showing a river delta coastline with no labels, borders or flags. A hand presses a round pin into one harbour; a single string runs from a distant port at the map's edge through the pin and on inland.
- **C2-07**: Seen from high above: a river of small cardboard parcels flowing through a narrow harbour mouth between two rocky headlands and fanning out into a wide delta beyond. Carved woodblock water. The sky band at the top is quiet.
- **C2-08**: A logistics warehouse at night: close on gloved hands peeling a label off a small cardboard chip carton and pressing a new blank label on. Stacks of cartons fade into charcoal behind. Both labels blank. Right third bare.
- **C2-09**: A narrow building lobby whose entire back wall is covered in hundreds of small brass letterboxes in a tight grid, one of them lit from within. A single bare bulb hangs from the ceiling. The floor is bare. No names or numbers on the boxes.
- **C2-10**: A night cargo apron in the rain: the raised nose door of a large plain freighter aircraft, pallets rolling in on a loader, anonymous loaders in silhouette, rain streaking the light. No livery, no insignia, no text. Quiet dark sky across the top.

---

## 7. CHAPTER 3: the Xilinx deal's promise to Beijing, 2020-2022 (4:40-6:20, 100 s; 11 options)

Beats:
- 2020-10-27: AMD announces the Xilinx deal (C).
- SAMR's conditional approval, text dated 2022-01-21 and announced 01-27 (C):
  - keep supplying Xilinx FPGAs and AMD CPUs/GPUs to China on FRAND terms (C);
  - no bundling (C);
  - report every six months (C);
  - AMD may ask to lift the conditions after six years, about 2028 (arithmetic).
  - The "no US-law carve-out" reading is P: verify by eye before it airs.
- The deal closes 2022-02-14 at $48.8B, all stock (C).
- CSET, June 2022: the PLA buys US-designed chips, including Xilinx, through intermediaries (C).
- Embedded revenue: $4,552M (2022) → $5,321M (2023) → $3,454M (2025), down 35% from the peak (C).

| id | win | line / beat | picture | LIFE | L | txt | ppl | src | use |
|---|---|---|---|---|---|---|---|---|---|
| C3-01 | 4:40-4:49 | 2020: AMD agrees to buy Xilinx | Two office towers on opposite banks of a river, one coral-lit and one cobalt-lit, joined by a new bridge whose last span is being lowered by a crane at dusk. | KB lateral L→R across the bridge. alive: river current ("water flowing") | FLAT | none | none | GEN | land · quiet sky top · AMD 10-K R20 "$48.8 billion" (C) |
| C3-02 | 4:49-4:58 | a deal this size needs Beijing's signature too | **HERO.** A long approvals desk with three places, each with a round ink stamp and pad; the document at the centre already carries two stamped impressions (plain circles, no emblems); the third place's chair is EMPTY and its stamp waits. | KB push-in to the unstamped space | LAYERED: far = the panelled wall; mid = the desk + document; subject = the waiting third stamp | none (the stamp faces are blank circles) | none | GEN | land · quiet wall top · SAMR decision date card (MOFCOM mirror, C) |
| C3-03 | 4:58-5:07 | the promise | REUSE `world-signature-close` ("a promise made in a good year"): a fountain pen finishing a signature on a sheet, a coral ledger and an inkwell. | KB push-in to the nib | FLAT | none (the signature is a scrawl, no name) | none | REUSE (crop the centre band) | land · quiet charcoal top-right · the SAMR condition in Chinese + translation "向中国境内市场继续供应...赛灵思FPGA" (C). **HERO alt** |
| C3-04 | 5:07-5:16 | "keep supplying" | A warehouse loading bay: a conveyor of identical small cartons moving steadily out of a door toward a waiting truck. | KB lateral following the cartons. alive: the conveyor carries cartons L→R ("conveyor belt moving") | FLAT | none | none | GEN | land · quiet upper left · the FRAND supply condition (C) |
| C3-05 | 5:16-5:25 | report every six months | A bookshelf of identical bound report volumes with blank spines; a hand slides a new volume onto the end of the row. | KB lateral along the spines to the new volume | FLAT | none (blank spines) | a hand only | GEN | land · quiet top · "每半年向市场监管总局报告" (C) |
| C3-06 | 5:25-5:34 | the earliest AMD can ask out: about 2028 | An hourglass on the approvals desk from C3-02, sand running, the empty chair soft behind it. | KB push-in to the hourglass neck. alive: sand falls top→bottom ("sand falling") | FLAT | none | none | GEN (edit of C3-02) | bridge · the "6 years → ~2028" badge (arithmetic, labelled). PAIR with C6-05 |
| C3-07 | 5:34-5:43 | what an FPGA is: a chip you rewire after it ships | Top-down: a chip die drawn as a city grid seen from above; lit paths re-route between the blocks like traffic being redirected. | KB push-in toward the grid's centre. alive: light paths reroute across the grid ("light paths rerouting") | FLAT | none | none | GEN | bridge · the flow diagram mounts clean after |
| C3-08 | 5:43-5:52 | CSET 2022: the military buys through middlemen | **HERO.** A corridor of three doorways; a small box passes hand to hand through them, from a plain sleeve, to a plain sleeve, to a charcoal sleeve with no insignia. | KB lateral along the chain of hands | FLAT | none | hands only | GEN | land · quiet upper right · CSET "Nearly all of them were designed by Nvidia, Xilinx (now AMD), Intel, or Microsemi." (C) |
| C3-09 | 5:52-6:01 | the business cooled: Embedded down 35% from its peak | REUSE `world-empty-racks-v1`: vast empty warehouse racking, one pallet in a shaft of light. | KB pull-back (emptiness grows) | FLAT | none | none | REUSE (crop the centre band) | bridge · the Embedded bars page (C) mounts after. NOTE: C5-06 needs a separate shelf plate, so this one stays here |
| C3-10 | 6:01-6:10 | paid in stock: 429 million shares | REUSE `world-certificate-wall-v1`: a wall papered with ornate share certificates, a lone chair, a cobalt shaft of light. Register: Steel and Paper's paper motif; a weak fit, and the first to cut. | KB push-in to the certificates | FLAT | none | none | REUSE (3:2; the bare cream right is the quiet zone) | land · "429M shares at $113.18" (C) |
| C3-11 | 6:10-6:20 | the bridge holds; a thread runs east | The C3-01 towers at night, the bridge finished and lit, one thin sunflower line of light running from it out across dark water to the horizon. | KB pull-back to the horizon | FLAT | none | none | GEN (edit of C3-01) | reset · into chapter 4 |

**Prompts: chapter 3**

- **C3-01**: Two modern office towers on opposite banks of a wide river at dusk, one lit warm coral from inside, the other lit cool cobalt. A new steel bridge joins them; its final middle span is being lowered into place by a tall crane. Carved woodblock water below. No signage, no logos. The sky at the top is quiet.
- **C3-02**: A long, formal approvals desk seen straight-on against a dark panelled wall. Three places at the desk, each with a round ink stamp on a pad. On the desk's centre lies one document already bearing two round stamped impressions, plain circles with no emblem. The third chair is empty and its stamp waits unused. No people, no flags, no seals, no text.
- **C3-04**: A warehouse loading bay: a long conveyor carries identical small plain cartons steadily out of an open door toward a waiting truck at the right. No labels, no writing. The upper left is bare.
- **C3-05**: A long bookshelf of identical bound report volumes with blank charcoal and cobalt spines; a hand slides one new volume onto the end of the row. No titles, no numbers. The top band is quiet.
- **C3-06**: A tall hourglass standing on a formal approvals desk, sand running from the upper bulb to the lower, a round ink stamp beside it, an empty high-backed chair soft behind. Warm light from the upper left.
- **C3-07**: Top-down, straight-on: a computer chip's silicon die drawn as a city grid seen from above, blocks and avenues in charcoal and cream; bright sunflower paths of light run between the blocks, some of them bending to new routes like traffic being redirected.
- **C3-08**: A long corridor with three open doorways in a row. A small plain box passes from hand to hand through the doorways: first a plain grey sleeve, then a plain cobalt sleeve, then a plain charcoal sleeve with no insignia. Hands and forearms only. The upper right is quiet.
- **C3-11**: The same two river towers at night, the new bridge between them finished and lit. One thin sunflower line of light runs from the bridge out across the dark water to the far horizon. Wide cobalt night sky.

---

## 8. CHAPTER 4: the China tax, 2025 (6:20-7:50, 90 s; 10 options)

Beats:
- 2025-04-15: the MI308 licence requirement, charges of up to about $800M (C); Q2'25 GAAP operating loss of $134M (C). This is the ring back to the opening's first line.
- Aug 2025: a reported 15% of China AI-chip revenue paid to the US (P); CBS: "'Will you make it 15%?' so we negotiated a little deal." (P).
- The 10-K: "the U.S. government has not published a regulation" (P, snippet).
- 2025-12-04: Su is "prepared to pay a 15% tax" (P).
- Q4'25: $390M of MI308 sold to China (P).
- 2026-01-13: H200/MI325X move to case-by-case review (C).
- China's counter-controls (P): gallium/germanium 2023, rare earths 2025; the US took 71% of its rare earths from China (P).
- The truce runs to 2026-11-10, then 2027-01-10 (P).

| id | win | line / beat | picture | LIFE | L | txt | ppl | src | use |
|---|---|---|---|---|---|---|---|---|---|
| C4-01 | 6:20-6:29 | April 2025: the chip China wanted can't ship; $800M written off | **HERO.** The O-02 warehouse later: the same chained crates, now dust-sheeted, the coral hold lamp dimmer, a clerk's clipboard hanging on the chain (blank). | KB push-in to the chain. PAIR with O-02 (plant → payoff) | FLAT | none | none | GEN (edit of O-02) | land · quiet right aisle · the 8-K "charges of up to approximately $800 million" (C) |
| C4-02 | 6:29-6:38 | the quarter went red: an operating loss | REUSE `world-receipt-macro-v1`: one tall receipt on dark ground, a coral second line. | KB push-in to the coral line | FLAT | none (bars, no figures) | none | REUSE (crop the centre band) | land · "operating loss $(134)M, Q2'25" (C) |
| C4-03 | 6:38-6:47 | then a deal: 15% to Washington | **HERO.** A toll booth on a long bridge between two shores; accelerator trucks roll through one by one, and each drops a coin into a charcoal-sleeved hand reaching from the booth; the barrier lifts. | KB lateral with the trucks L→R. alive: the barrier rises and falls, coins drop ("barrier lifting and lowering") | LAYERED: far = sea + far shore; mid = the bridge + trucks; subject = the booth and the hand | none | a sleeve only | GEN | land · quiet sky top · the CBS quote card (P) |
| C4-04 | 6:47-6:56 | a tax with no written rule | A heavy rule book open on a lectern, BOTH pages blank, a pen resting across them, a lamp. | KB push-in to the blank pages | FLAT | none (blank pages) | none | GEN | land · the 10-K line "has not published a regulation" (P, snippet: flag it) |
| C4-05 | 6:56-7:05 | money on one pan, access on the other | REUSE `world-scales-coin-paper-v1`: a balance, coins on one pan, a sealed certificate stack on the other. | KB push-in to the heavier pan | FLAT | none | none | REUSE (crop the centre band) | bridge · Su "prepared to pay a 15% tax" (P) |
| C4-06 | 7:05-7:14 | licensed crates roll again: $390M in a quarter | A customs desk where a clerk's hand brings down a sunflower stamp on a crate's blank tag, and the gate behind stands open to a waiting ship. | KB push-in to the stamp landing | FLAT | none (the tag is blank) | a hand only | GEN | land · "$390M MI308 to China, Q4'25" (P) |
| C4-07 | 7:14-7:23 | the wide door for AI chips, the bricked door for the radio chip | **HERO alt.** A long wall with two doors: the wide door on the left stands open with a toll hand beside it and big crates passing; the small door on the right is bricked shut, a tiny parcel waiting before it. | KB lateral L→R, from the open door to the bricked one | FLAT | none | a sleeve only | GEN | bridge · BIS 2026-01-13 "Nvidia H200, AMD MI325X, and similar chips" (C) against 3A001.a.14 (P) |
| C4-08 | 7:23-7:32 | Beijing's reply: the metals | An open-pit mine at dusk with ore carts halted before a closed iron gate, the terraces carved in charcoal and coral. | KB pull-back to the pit's scale | FLAT | none | none | GEN | land · quiet sky top · gallium/germanium 2023, rare earths 2025, "71%" (P) |
| C4-09 | 7:32-7:41 | a truce under pressure | REUSE `world-pressure-gauge-v1`: a brass pressure gauge on a pipe, the needle near the red, steam at the right. | KB push-in to the needle | FLAT | none (the dial has colour bands, no numbers) | none | REUSE (crop the centre band) | bridge · "truce to 2026-11-10" → "to 2027-01-10" (P) |
| C4-10 | 7:41-7:50 | chips against rocks | A balance scale on a cream ground: one chip on one pan, a heap of dark ore on the other, level. | KB push-in to the chip's pan | FLAT | none | none | GEN | reset · into chapter 5 |

**Prompts: chapter 4**

- **C4-01**: A dim warehouse interior: stacks of accelerator crates on the left, now covered in dust sheets, a heavy chain and padlock across the front row, a blank clipboard hanging from the chain, a single coral hold lamp above glowing dimmer than before. The right half is an empty concrete aisle in shadow. No labels, no writing.
- **C4-03**: A long bridge between two shores at dusk with a small toll booth at its centre. Plain trucks roll through one by one; from each, a coin drops into a hand in a plain charcoal suit sleeve reaching out of the booth window. The striped barrier is rising. No logos, no flags, no signs. The sky across the top is quiet.
- **C4-04**: A heavy rule book lying open on a wooden lectern, both pages completely blank, a fountain pen resting across them, one warm lamp from the upper left, the room in charcoal.
- **C4-06**: A customs desk seen close: a clerk's hand brings a sunflower-yellow rubber stamp down onto the blank paper tag of a large crate. Behind, an iron gate stands open onto a quay where a ship waits. No writing on the tag, no insignia.
- **C4-07**: A long stone wall seen straight-on with two doors. On the left, a wide door stands open; large crates roll through it on a cart and a hand in a plain charcoal sleeve reaches out beside it. On the right, a small door has been bricked shut, and a tiny parcel waits on the ground in front of it. No text, no flags.
- **C4-08**: An open-pit mine at dusk, its terraced walls carved in charcoal and coral bands. A line of ore carts has stopped in front of a closed iron gate at the pit's rim. Wide sky across the top. No text, no flags.
- **C4-10**: A balance scale on a cream ground, perfectly level: a single square computer chip on the left pan and a heap of dark raw ore on the right pan. Centred; soft light from the upper left.

---

## 9. CHAPTER 5: the chip on a crowdfunding page, 2026 (7:50-10:20, 150 s; 16 options)

Beats:
- **The board**:
  - Puzhi (Shanghai) puts its PZSDR P047 board, built on the XCZU47DR RFSoC, on Crowd Supply (Mouser-owned, Portland) (C).
  - $6,699 pledge (P), $8,749 now (C); $57,143 raised from 5 backers (C); "boards in hand" (C).
  - Puzhi lists phased-array radar among the uses of multi-board sync (C); a 7-board, 56-channel demo (P).
- **Patel's numbers**:
  - "$36k" list = DigiKey $35,979.02 qty 1, 40 weeks (C).
  - "$4-5k" at volume (U, his claim); "$1k" quoted in China (U, his claim, and not a public offer per Tom's).
- **The mechanism**: qty-1 catalogue price vs volume; AMD's own academic board sells at $2,499 (C).
- **AMD's answer**: "did not ship / sell ... investigating the sourcing" (C as Patel's post).
- **Clones**: "bitstream compatible FPGAs not from AMD" (his claim); Fudan on the Entity List 2025-09-12 (C); the FMZQ28DR "compatible" advert (U).
- **Kept off every plate and card**: the eBay $400 lots are U and never dock.

| id | win | line / beat | picture | LIFE | L | txt | ppl | src | use |
|---|---|---|---|---|---|---|---|---|---|
| C5-01 | 7:50-7:59 | a Shanghai workshop puts the chip on a crowdfunding page | **HERO.** A small electronics workshop at night: a monitor on the bench shows a BLANK campaign-page layout (a hero image block, a progress bar, no words); beside it, on an anti-static mat, a software-defined-radio board with a row of coax connectors; a soldering station, parts drawers. | KB push-in to the monitor (the page arrives). alive: the soldering iron's thin smoke rises ("smoke curling up") | LAYERED: far = the shelves + drawers; mid = the bench, monitor, board; near = the soldering station, left foreground | none (the screen is layout only) | none | GEN | land · **art-embed**: the captured Crowd Supply page (sources/02, C) projects onto the monitor quad |
| C5-02 | 7:59-8:08 | the board: eight channels in, eight out, one chip | Top-down on cream: a large SDR board, a row of eight gold coax connectors along one edge, one big square chip at the centre under a heatsink, no markings. | KB push-in to the chip | FLAT | none (no part marking; OPTIONAL "XCZU47DR" on the chip lid: a verified string, C, sources/02; refuse it on the frame read if garbled) | none | GEN | land · quiet right · the Crowd Supply spec "based on the AMD Zynq UltraScale+ XCZU47DR RFSoC" (C) |
| C5-03 | 8:08-8:17 | $57,143 from five backers | A vast, nearly empty exhibition hall; at its centre one glowing box on a pedestal, and five small silhouettes standing around it. | KB pull-back (the emptiness shows) | FLAT | none | five anonymous silhouettes | GEN | land · quiet ceiling · "$57,143 / 5 backers" (C) |
| C5-04 | 8:17-8:26 | "boards in hand" | Two gloved hands holding a finished circuit board up to a workshop lamp, its connectors catching the light. | KB push-in to the board | FLAT | none | hands only | GEN | land · quiet left · Puzhi update "we have PZSDR P047 boards in hand" (C) |
| C5-05 | 8:26-8:35 | lock seven together and it's a radar | **HERO alt.** Seven identical boards in a row on a lab rack, their coax cables braided to one clock unit, all status lights lit in unison. | KB lateral L→R along the seven boards. alive: status lights pulse in unison ("lights pulsing together") | FLAT | none | none | GEN | land · quiet top · Puzhi "Phased Array Radar" (C) + "7 boards, 56 channels, ±3°" (P) |
| C5-06 | 8:35-8:44 | the US price: $36,000, 40 weeks' wait | A parts distributor's aisle of small grey bins; one bin at eye level is EMPTY, its tag lit by an aisle light. | KB push-in to the empty bin | FLAT | none by default. OPTION: the tag reads "40 WEEKS" (DigiKey lead time, C, sources/03 + 06; s113 intentional + verified); the default keeps the tag blank and the badge carries it | none | GEN | land · quiet aisle floor · DigiKey "$35,979.02", 40 weeks (C) |
| C5-07 | 8:44-8:53 | Patel's three prices for one chip | **HERO.** One chip hanging on a thread with three price tags tied beneath it: a large tag, a medium tag, a tiny tag, all BLANK. | KB lateral from the big tag to the tiny one | FLAT | none (the tags stay blank; the numbers dock) | none | GEN | land · quiet right · three badges: $36k (list, C) / $4-5k (Patel's claim, U) / $1k (Patel's claim, U; "not a publicly advertised retail offer", Tom's P) |
| C5-08 | 8:53-9:02 | a quantity-one price is not the price | A single chip in a velvet-lined jewellery case on a shop counter in the foreground, and behind it, out of focus, pallets of chip reels stacked to the ceiling. | KB pull-back from the case to the pallets | FLAT | none | none | GEN | bridge · the mechanism line (pack 1 §4) |
| C5-09 | 9:02-9:11 | AMD sells its own RFSoC board to universities for $2,499 | A university lab bench: students' hands (no faces) plugging a dev board into a laptop, a chalkboard of hand-drawn sine waves (no text) behind. | KB push-in to the board | FLAT | none | hands only | GEN | land · quiet chalkboard · realdigital "Academic Price: $2,499.00" + the End Use Form (C) |
| C5-10 | 9:11-9:20 | once a chip is walled off, its price is set by whatever leaks | A night-market stall under a tarp and one bulb, trays of loose, unmarked chips, a hand sifting them. | KB push-in to the tray | FLAT | none | a hand only | GEN | bridge · the mechanism, NOT this chip: the eBay figures (U) never dock |
| C5-11 | 9:20-9:29 | AMD: "we did not sell this chip to this firm" | An empty press-briefing room: one lectern, one microphone, lights on, nobody there; rows of empty chairs. | KB push-in to the microphone | FLAT | none | none | GEN | land · quiet back wall · Patel's follow-up quoting AMD (C as his post) + Tom's "This recent instance is unrelated to any direct AMD sales or shipments." (P) |
| C5-12 | 9:29-9:38 | "investigating the sourcing" | REUSE `world-ledger-page-v1`: an open ledger under a green banker's lamp, a pencil, an inkwell, a coral box. | KB push-in to the ledger's lit page | FLAT | none (ruled blank columns) | none | REUSE (crop the centre band) | bridge · AMD "We investigate all suspected diversion cases..." (P) |
| C5-13 | 9:38-9:47 | or the chip isn't AMD's at all: clones | **HERO.** A chip on a workbench facing a small upright mirror; its reflection is ALMOST identical (one corner pin missing, the surface a shade off). | KB push-in to the mirror (the doubt). alive: a light glint slides across the mirror ("glint sliding") | FLAT | none | none | GEN | land · quiet left · Patel "bitstream compatible FPGAs not from AMD" (his claim) + FR 2025-17893 Fudan on the Entity List (C) |
| C5-14 | 9:47-9:56 | 2025: the US blacklists China's own FPGA maker | The C1-09 register, a page later: a NEW line struck through, fresh ink, the stamp now down on the page. | KB push-in to the fresh line. PAIR with C1-09 | FLAT | none | a hand only | GEN (edit of C1-09) | land · FR 2025-17893 "Shanghai Fudan Microelectronics Co., Ltd. has supplied technology to Russian military end users." (C) |
| C5-15 | 9:56-10:05 | three stories; which one is true? | A signpost at a night crossroads with three BLANK arms, fog on the road, a circuit-trace pattern in the tarmac. | KB tilt up to the three arms. alive: fog drifts L→R ("fog drifting") | FLAT | none | none | GEN | bridge · the press stack of three claims with the "?" veil (engine: CAPABILITIES "The '?' at the unknown") |
| C5-16 | 10:05-10:20 | one small chip, two coastlines | A single chip on a small raft on a vast night ocean, the lights of two coasts far apart on either horizon. | KB pull-back (scale). alive: ocean swell ("waves rolling") | FLAT | none | none | GEN | reset · into chapter 6 |

**Prompts: chapter 5**

- **C5-01**: A small electronics workshop at night seen straight-on. On the bench, a computer monitor shows a blank web campaign-page layout: a large empty image block, a thin progress bar and empty grey text blocks, with no words or numbers. Beside it on a charcoal anti-static mat lies a software-defined-radio circuit board with a row of gold coax connectors along one edge. A soldering station with a thin curl of smoke in the left foreground; shelves of small parts drawers behind. No logos, no text.
- **C5-02**: Top-down, straight-on on a cream ground: a large rectangular circuit board with a row of eight gold coax connectors along its top edge and one big square chip at the centre under a black heatsink. Traces in teal. No markings, no logos, no text. The right third of the frame is bare cream.
- **C5-03**: A vast, nearly empty exhibition hall seen straight-on, a high charcoal ceiling. At the centre of the floor one small glowing box sits on a pedestal, and five small figures in silhouette stand around it. The rest of the hall is empty.
- **C5-04**: Two gloved hands hold a finished circuit board up toward a workshop lamp, its gold connectors catching the warm light. Dark workshop behind. No markings. The left third is bare.
- **C5-05**: A lab rack holding seven identical circuit boards in a row, their coax cables braided together and running to one small clock unit at the end; every board's small status light glows sunflower in unison. Straight-on. The top band is quiet.
- **C5-06**: A long parts distributor's aisle of small grey plastic bins on steel shelving, seen straight-on. One bin at eye level in the centre is empty, and its small paper tag is lit by an overhead aisle light; the tag is blank. The aisle floor is bare.
- **C5-07**: On a cream ground, a single square computer chip hangs from a thin thread. Tied beneath it on strings hang three paper price tags of very different sizes - one large, one medium, one tiny - all completely blank. Soft light from the upper left. The right third is bare.
- **C5-08**: A shop counter: in the foreground, a single square computer chip in an open velvet-lined jewellery case under a small lamp. Behind it, soft and out of focus, industrial pallets of chip reels stacked to the ceiling in a warehouse. No labels, no text.
- **C5-09**: A university electronics lab bench: the hands of students (no faces) plug a development circuit board into a laptop. A chalkboard behind shows hand-drawn sine waves only, no writing. The chalkboard's right side is quiet.
- **C5-10**: A night-market stall under a canvas tarp lit by a single hanging bulb. Shallow trays hold heaps of loose, unmarked square computer chips; one hand sifts through a tray. The surrounding market fades to charcoal. No signs, no text.
- **C5-11**: An empty press-briefing room seen straight-on: one lectern with a single microphone at the front, stage lights on, rows of empty chairs in the foreground, a plain back wall. No emblem, no seal, no text, no people.
- **C5-13**: A square computer chip lying on a wooden workbench in front of a small upright mirror. Its reflection is almost identical but not quite: one corner pin is missing and the surface is a slightly different tone. One lamp from the upper left; a thin glint on the mirror's edge. The left third is bare.
- **C5-15**: A wooden signpost at a crossroads at night with three blank arms pointing in three directions, low fog drifting across the road, a faint circuit-trace pattern carved into the road surface. No words on the arms.
- **C5-16**: A single square computer chip resting on a small wooden raft in the middle of a vast night ocean. On the far left horizon the lights of one coast, on the far right horizon the lights of another. Carved woodblock waves. Wide cobalt night sky.

---

## 10. CHAPTER 6: the dinner, and the ring back to the opening (10:20-12:00, 100 s; 11 options)

Beats:
- **The dinner (09-24)**:
  - Xi's first US state visit in over a decade (P).
  - Su at the head table, "only two seats away from President Trump"; Huang "across from the President" (C, Yahoo).
  - The truce extended to 2027-01-10 (P).
- **What the record says**: Patel alleges; AMD denies; no charge, investigation or finding was found (both packs).
- **The trade itself**: 22.4% of AMD revenue was billed to China in FY2025 (C). The radio chip is still walled off.
- **Close**: the ring back to the opening's world.

| id | win | line / beat | picture | LIFE | L | txt | ppl | src | use |
|---|---|---|---|---|---|---|---|---|---|
| C6-01 | 10:20-10:29 | back to that dinner | A generic colonnaded state building at night (NOT an identifiable landmark), every window lit, black cars arriving along a curved drive. | KB push-in toward the doors. alive: headlights sweep along the drive L→R ("headlights sweeping") | FLAT | none | none | GEN | bridge · quiet night sky |
| C6-02 | 10:29-10:38 | two seats from the President | **HERO.** The O-12 table later in the evening: candles burned lower, glasses half full, napkins dropped on the chairs; the blank card two seats from the centre still lit. PAIR with O-12 (plant → payoff). | KB push-in to the card | LAYERED (same layers as O-12) | none | none drawn. Dock: the pool photo (C) | GEN (edit of O-12) | land · quiet wall · "only two seats away from President Trump" (C) |
| C6-03 | 10:38-10:47 | Huang across from the President; Su two seats away | Top-down flat-lay of the head-table section: chairs as shapes, one teal napkin across from the centre, one coral napkin two places along, each lit by its candle. | KB lateral L→R across the seat positions | FLAT | none | none; the place geometry only. Head cutouts (E68) may dock on the seats | GEN | land · the seating as a diagram · Yahoo "across from the President" / "two seats away" (C). The teal/coral mapping follows §1 rule 2 |
| C6-04 | 10:47-10:56 | the toast | Close on raised crystal glasses meeting across the candlelit table, hands only, a spark of light where they touch. | KB push-in to the clink. alive: candle flicker ("candle flames flickering") | FLAT | none | hands only | GEN | bridge · quiet dark top |
| C6-05 | 10:56-11:05 | the truce, extended | A hand turning an hourglass over on the white tablecloth (the C3-06 hourglass, a callback), the sand starting again. | KB push-in to the hourglass. alive: sand falling ("sand falling") PAIR with C3-06 | FLAT | none | a hand only | GEN (edit of C3-06, the cloth swapped) | land · "truce extended to 2027-01-10" (P) |
| C6-06 | 11:05-11:14 | a chip at the table | **HERO alt.** A single chip resting on a folded white napkin at a formal place setting, exactly where a guest's name card would stand; one candle. | KB push-in to the chip | FLAT | none | none | GEN | bridge · the thesis line: a chip is now a seat at the table |
| C6-07 | 11:14-11:23 | trust | The O-07 chessboard reset: the pieces back in their ranks; above it, the teal hand, the coral hand and the charcoal hand all meeting over the board. PAIR with O-07. | KB lateral L→R across the three hands | FLAT | none | hands only | GEN (edit of O-07) | bridge · quiet upper left |
| C6-08 | 11:23-11:32 | what's on the record and what's claimed | Two stacks of papers on a desk under one lamp: the left stack's top sheet carries a round stamp mark (plain circle), the right stack's top sheet is blank; a pen between them. | KB lateral L→R, stamped to blank | FLAT | none | none | GEN | land · the two-column recap: sourced (C) vs claimed (U / his claim). Research gate tiers on screen |
| C6-09 | 11:32-11:41 | the analyst's desk at dawn | The O-03 desk at dawn: the phone face-down now, blue-gold window light, the chip still under the loupe, the chair empty. PAIR with O-03. | KB pull-back (reflection) | FLAT | none | none | GEN (edit of O-04) | bridge · quiet right |
| C6-10 | 11:41-11:50 | the Pacific at dawn: the trade goes on | High above a wide ocean at dawn, two coastlines at the edges, a few container ships as tiny marks crossing, one thin line of sunflower light joining them. | KB lateral drift L→R. alive: sea glitter ("light glittering on the sea") | FLAT | none | none | GEN | land · "22.4% of FY2025 revenue billed to China" (C) |
| C6-11 | 11:50-12:00 | outro underlay | The O-01 tower at dawn: the coral floor dark now, the sunrise on the glass. PAIR with O-01. | KB pull-back (the close) | FLAT | none | none | GEN (edit of O-01) | reset · the end-screen quiet zone: the left two-thirds of the sky |

**Prompts: chapter 6**

- **C6-01**: A generic neoclassical colonnaded government building at night, not any identifiable landmark: tall columns, every window lit warm, a curved drive where a line of plain black cars arrives with headlights on. No flags, no seals, no emblems, no text. Wide cobalt night sky.
- **C6-02**: The same formal state-dinner head table later in the evening: candles burned lower, crystal glasses half full, napkins dropped on the empty high-backed centre chairs; two seats to the left of the centre, the folded blank place card is still lit by its candle. Dark panelled wall behind. No people, no flags, no writing.
- **C6-03**: Top-down, straight-on flat-lay of one section of a formal dinner table on white linen: chairs seen from above as simple shapes, gold-rimmed plates in a row, one teal napkin at a place across from the centre and one coral napkin two places along the same side, each lit by a small candle. No people, no writing.
- **C6-04**: Close view of crystal glasses raised and meeting across a candlelit white tablecloth, hands only, no faces, a small spark of light where the glasses touch. The top of the frame is dark and quiet.
- **C6-05**: A hand turning a tall hourglass over on a white linen tablecloth among gold-rimmed plates and small candle lamps, the sand just beginning to fall again. Warm light from the upper left.
- **C6-06**: A formal place setting on white linen: gold-rimmed plate, crystal glass, polished cutlery, and on a folded white napkin, standing exactly where a guest's name card would be, a single square computer chip, lit by one candle. Dark background.
- **C6-07**: A chessboard made of square computer chip packages with the teal and coral pieces reset in their starting ranks. Above the board, three hands meet at the centre: one in a teal sleeve, one in a coral sleeve, one in a plain charcoal suit sleeve. Hands and forearms only. The upper left is bare cream.
- **C6-08**: A wooden desk under one lamp with two stacks of paper side by side: the top sheet of the left stack bears a single round stamped mark (a plain circle, no emblem); the top sheet of the right stack is blank. A fountain pen lies between them. All writing on the sheets is illegible scrollwork.
- **C6-10**: Seen from high above at dawn: a wide ocean with a coastline at the far left edge and another at the far right edge. A few container ships cross as tiny marks, and one thin line of sunflower light joins the two coasts. Carved woodblock sea glittering.

---

## 11. Counts

| section | window | options | reuse | gen (of which edits) | HERO |
|---|---|---|---|---|---|
| Opening | 0:00-0:34 | 13 | 0 | 13 (2) | O-03, O-05, O-10, O-12, O-13 (the opening gets five because every line needs one) |
| World-setting | 0:34-1:30 | 13 | 2 | 11 (1) | W-02, W-11, W-12 |
| Ch1 chips become weapons | 1:30-3:10 | 11 | 4 | 7 (0) | C1-02, C1-09 |
| Ch2 Hong Kong | 3:10-4:40 | 11 | 3 | 8 (0) | C2-01, C2-04 |
| Ch3 the Xilinx promise | 4:40-6:20 | 11 | 3 | 8 (2) | C3-02, C3-08 (alt C3-03) |
| Ch4 the China tax | 6:20-7:50 | 10 | 3 | 7 (1) | C4-01, C4-03 (alt C4-07) |
| Ch5 the crowdfunding page | 7:50-10:20 | 16 | 1 | 15 (1) | C5-01, C5-07, C5-13 (alt C5-05) |
| Ch6 the dinner | 10:20-12:00 | 11 | 0 | 11 (5) | C6-02 (alt C6-06) |
| **Total** | ~12:00 | **96** | **16** | **80 (12)** | |

The totals by rule:
- 96 options over 720 s is one per 7.5 s. The operator's floor (1 per 10 s) is 72, and the C3 plate target (runtime / 12 s) is 60.
- 13 plates are LAYERED: O-03, O-10, O-12, O-13, W-11, W-12, C1-02, C1-09, C2-01, C3-02, C4-03, C5-01, C6-02. That comes to 3-4 GPT Image 2.5 calls each.
- 33 rows name an alive region (VACE).
- 12 PAIR/edit plates keep one world across a plant and its payoff:
  - O-01 → C6-11
  - O-02 → C4-01
  - O-03/O-04 → C6-09
  - O-07 → O-11, C6-07
  - O-12 → W-10, C6-02
  - C1-09 → C5-14
  - C3-01 → C3-11
  - C3-02 → C3-06 → C6-05
## 12. Library reuse list (all `approved`, `render_eligible`, file on disk, read by eye 2026-09-26)

Paths are under `C:/Users/Snipe/Downloads/Outreach Program/content/video_engine/projects/systems-and-blowups/review/claims/`.

| slot | plate id | path (under claims/) | fit |
|---|---|---|---|
| W-05 | world-broadcast-set-v2 | steel-and-paper-plates-wave-4/objects/world-broadcast-set-v2.png | good: empty set, "nobody reported it" |
| W-06 | world-internal-memo-v1 | steel-and-paper-plates-wave-3/objects/world-internal-memo-v1.png | good: the landing page for AMD's statement |
| C1-01 | world-license-cabinet-v1 | steel-and-paper-plates-wave-3/objects/world-license-cabinet-v1.png | strong: licences as locked drawers with reaching hands |
| C1-07 | world-memory-fab-floor-v1 | finance-episodes-plates-wave-1/objects/world-memory-fab-floor-v1.png | fair: a generic fab (Hygon's chip) |
| C1-08 | world-circuit-terrain-v1 | steel-and-paper-plates-wave-1/objects/world-circuit-terrain-v1.png | fair: the empty socket; a register drift (paper-toy sheen) |
| C1-10 | world-datacenter-aisle-v1 | steel-and-paper-plates-wave-3/objects/world-datacenter-aisle-v1.png | good: the supercomputer hall |
| C2-02 | world-korea-port-v1 | finance-episodes-plates-wave-1/objects/world-korea-port-v1.png | good as a landing (cream right half); not HK-specific |
| C2-06 | world-till-drawer-v1 | finance-episodes-plates-wave-1/objects/world-till-drawer-v1.png | fair: billing |
| C2-11 | world-gpu-crate-dock-v1 | steel-and-paper-plates-wave-3/objects/world-gpu-crate-dock-v1.png | good: crates on a dock |
| C3-03 | world-signature-close | steel-and-paper-plates-wave-5/objects/world-signature-close.png | strong: "a promise made in a good year" |
| C3-09 | world-empty-racks-v1 | steel-and-paper-plates-wave-3/objects/world-empty-racks-v1.png | good: the cooled business |
| C3-10 | world-certificate-wall-v1 | steel-and-paper-plates-wave-1/objects/world-certificate-wall-v1.png | weak: Steel and Paper's paper motif; cut it first |
| C4-02 | world-receipt-macro-v1 | finance-episodes-plates-wave-1/objects/world-receipt-macro-v1.png | strong: the hidden coral line = the loss |
| C4-05 | world-scales-coin-paper-v1 | steel-and-paper-plates-wave-3/objects/world-scales-coin-paper-v1.png | fair: money vs access |
| C4-09 | world-pressure-gauge-v1 | steel-and-paper-plates-wave-3/objects/world-pressure-gauge-v1.png | good: the truce under pressure |
| C5-12 | world-ledger-page-v1 | steel-and-paper-plates-wave-3/objects/world-ledger-page-v1.png | good: "investigating the sourcing" |

**Considered and NOT scheduled** (so nobody re-checks them):
- `world-seoul-fab-skyline-v1`: its semantic says "fab country", but the frame is a POWER STATION with cooling towers. It is a library mislabel; flag it for the next library rebuild.
- `world-tokyo-customs-dock-v1` (+ `-alive-flat`): `review_only`, not render-eligible. Its skyline carries Tokyo's Skytree, which would be wrong for Hong Kong.
- `world-trading-desk-dark`: a burning city outside the windows, which reads as a crash. It is wrong for a +9.95% day.
- Also not scheduled: `world-sell-ticket-v1` (available for the 2026-08-04 after-hours drop if a line needs it), `world-memory-wafer-v1`, `world-hbm-die-stack`, `hero-korea-italy-v1`.
- The Tokyo/Japan short-lane stills (`tokyo-tea-break/plates/*`, `japan-tariff-trick/omni-video/stills/*`) are 9:16 host-lane stills, not long-form plates.

## 13. Sourced material the plates depend on (intake, not generation)

These dock ON the plates. None exists as an approved asset yet, and `assets/heads/manifest.json` was not found. Each photo needs E68 intake (a head cutout, or a press photo framed on a surface, never full-frame as ours):
1. Patel portrait: the semianalysis.com/dylan-patel page photo (O-03, W-02).
2. The All-In Summit 2026-09-14 photo of Huang with the phone (TechCrunch / NBC, sources/36) (O-10, W-01).
3. The NYSE opening bell 2026-09-23, Su with the First Lady (Fox Business / NYSE) (O-09, W-07).
4. The White House state dinner 2026-09-24 head-table pool photo (Yahoo Finance / Werschkul, sources/36) (O-12, W-10, C6-02, C6-03).
5. Xi's arrival photo (NBC, sources/30) (W-08).
6. Head cutouts for Musk / Huang / Cook / Su (W-10).
7. Screen captures (evidence, not plates):
   - Patel's root post and follow-up (sources/01, 28; a browser screenshot of the real post is still owed, since the pack holds the JSON and his two attached images);
   - the Crowd Supply page (sources/02);
   - Tom's Hardware (sources/04);
   - DigiKey (sources/03, 06).

## 14. Generation queue (priority order; the parent dispatches; nothing here is sent)

**P0: the opening and 0:30-1:30.** Bases first, because later edits depend on them.
1. O-03 (LAYERED)
2. O-12 (LAYERED)
3. O-10 (LAYERED)
4. O-13 (LAYERED)
5. O-05
6. O-01
7. O-02
8. O-07
9. W-02
10. W-11 (LAYERED)
11. W-12 (LAYERED)
12. O-09
13. O-08
14. O-06
15. W-04
16. W-07
17. W-09
18. W-08
19. W-01
20. W-03
21. W-13
22. Then the P0 edits: O-04 (from O-03), O-11 (from O-07), W-10 (from O-12)

**P1: the chapter heroes.**
1. C1-02 (LAYERED)
2. C1-09 (LAYERED)
3. C2-01 (LAYERED)
4. C2-04
5. C3-02 (LAYERED)
6. C3-08
7. C4-03 (LAYERED)
8. C4-01 (edit of O-02)
9. C5-01 (LAYERED)
10. C5-07
11. C5-13
12. C6-02 (edit of O-12)
13. C6-06

**P2: the rest, in chapter order.**
- Ch1: C1-03, C1-04, C1-05, C1-06, C1-11
- Ch2: C2-03, C2-05, C2-07, C2-08, C2-09, C2-10
- Ch3: C3-01, C3-04, C3-05, C3-07, then the edits C3-06 (from C3-02) and C3-11 (from C3-01)
- Ch4: C4-04, C4-06, C4-07, C4-08, C4-10
- Ch5: C5-02, C5-03, C5-04, C5-05, C5-06, C5-08, C5-09, C5-10, C5-11, C5-15, C5-16, then the edit C5-14 (from C1-09)
- Ch6: C6-01, C6-03, C6-04, C6-08, C6-10, then the edits C6-05 (from C3-06), C6-07 (from O-07), C6-09 (from O-04), C6-11 (from O-01)

**P3: alive regions.** VACE runs only on plates the operator has approved and a row actually picks, never on the whole option set.

Batch shape by E57:
- The P0 + P1 bases (about 37 stills) go as ONE bridge packet to the Gemini lane for Flow (zero credit), with the 13 LAYERED rows split out to GPT Image 2.5 via the codex claim.
- The edits follow once their base is approved.
- Every still is quarantined until the operator approves the frame. The frame read verifies no text, no logos, no likeness and no flags before a still reaches the operator (s113 / E99 s38: a visible read first).

## 15. Open decisions for the parent (not asked of the operator here)

1. **Colour mapping**: teal = Nvidia, coral = AMD, as the brief says, against the brand semantics where coral = alarm. The alternative is cobalt = AMD (§1 rule 2). This touches O-07, O-11, C1-06, C3-01, C6-03 and C6-07.
2. **O-06, the gavel**: keep it or drop it. Patel said "investigated", and a gavel reads as a trial (an attribution check, not a title objection).
3. **Optional verified text**: C5-02 "XCZU47DR" on the chip lid, and C5-06 "40 WEEKS" on the bin tag. Both strings are CONFIRMED. The default is blank, with badges carrying the text.
4. **The library index is stale**: it was last committed 2026-09-16 and predates the P69 waves. Rebuild it (`build_plate_library.py`) before locking §12, and fix the `world-seoul-fab-skyline-v1` semantic.
5. **The operator's order needs a carrier row** (1 plate option per 10 s, as options): memory `rulings-need-carriers`. That is the parent's ledger edit, not this file's.
6. **Windows are estimates**: they are set at ~170 wpm on an unscripted body. They re-time once the script and take exist.
