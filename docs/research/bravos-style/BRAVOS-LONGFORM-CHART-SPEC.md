# Bravos Research long-form chart style: a measured spec, set against our long-form page (2026-09-23)

Status: MEASURED, not adopted. Every override in section (c) is the operator's call.
Reproduce: `python measure_bravos_style.py` (in this folder) writes `measurements.json` and `crops/`. Helpers are in `mlib.py`; `extract_bubbles_panels.py` cuts the bubbles panels.

## Sources and resolution (read this first)

| Set | What is on disk | What I measured | Scale to 1920x1080 | Precision at 1080 |
|---|---|---|---|---|
| China episode | `frames/` holds 512x288 stills, but `claude-watch/download/video.mp4` is the real **1280x720 AV1** | 20 stills cut with ffmpeg at chart shots (SHOT_LEDGER.claude rows 29-41, 50-55, 88, 99-106), saved as `frames/china_t<sec>.png` | x1.5 | +/-0.75 px |
| Bubbles episode | `frames/` holds 89 files at **512x288** (the brief said 119); no video on disk | the contact-sheet panels, **960x539**, which are the largest copy (`frames/bubbles_frame_00NN_panel960.png`) | x2.0 | +/-1-2 px, heavy JPEG (hex values +/-10) |
| Ours | `p69t6-94-land.png`, `p69t6-1v3-land.png`, `p69t5-stamp-plus-card.png` | native | x1.0 | exact |

Frames used (12 Bravos): china_t170 (line with a hero drop, a value badge and a dock), t220 (small multiples and a section title), t380 (line with a dashed ellipse and red chips), t530 (ranked bars with glow), t1078 (multi-line with terminal tags and value bars), t1088 (ranked bars with white pills); bubbles 0008 (three hero bars with pills, value badges and a short baseline), 0035 (time-series bars), 0052 (line with end badges), 0064 (glowing line), 0067 (histogram with a focus bar and a badge), 0016 (multi-line). All px values below are at the 1920x1080 stage.

**Caveat on size.** Bravos pushes the camera onto each chart, so type sizes change with the chart's scale (a chart title's cap height is 22 px on t170, 28.5 on t530 and 34.5 on t1088). I report ranges and name the frame for each end.

## (a) The measured table

| Element | Bravos (frame, crop) | Ours today (frame) | The gap |
|---|---|---|---|
| **Ground** | `#14181E` flat; corner = centre on all 6 China frames (t530 `(0,0,40,40)`); bubbles `#14191D` | cream `#F2E4C5` rim (13 px top) + charcoal page `#25313C`, page corner r~30 (94-land); line page is a vertical gradient `#222E39` (top) to `#16222D` (bottom) (t5) | ~15 lum darker (L 23 vs 47); no cream, no deckle, no gradient |
| **Vignette / radial light** | none on chart pages; only the hero-bar page has a soft lift, edge `#14191D` to near-bars `#1C232B` (bubbles 0008) | a vertical darkening on the line page (t5) | Bravos adds light only behind a hero object |
| **Plot panel** | fill `#222830` (+14 lum over ground), border **1.5 px `#696D73`** (t530 `crops/china_t530_border_x4.png`) | no panel; the plot sits on the page | Bravos frames the plot as a lit panel |
| **Top band** | 40 px (t170) to 45 px (t1078) band above the top-tick rule; it holds the legend | none | new element |
| **Interior gridlines** | **0** (t530 plot interior is a uniform lum 39; bubbles 0035 max lum 43 in a plot column) | **5 x 2 px `#414C55`** (94-land col x=300) | remove 5 lines |
| **Zero / axis line** | a zero rule only when the data crosses zero: 3 px `#675C66` (t1078 x=450); otherwise the panel border | full-width 3 px axis `#8A94A0` (94-land y=782..784) | ours is lighter and always present |
| **Y-axis** | tick labels only, outside the panel on the left; no axis line | tick labels + gridlines | - |
| **Tick labels** | digit height **15 px** (t170) to **18 px** (t530); `#868A8E` to `#9C9DA4` | **22-23 px** `#C9CED4` (94) / x ticks `#848C94` (t5) | ours ~1.4x larger and ~50 lum brighter |
| **Bars, ranked horizontal (flat)** | thickness **35 px**, pitch 55 px (**ratio 0.64**), gap 19 px, **radius 0**, flat series hues `#DE788B #4E7FBB #7F62A0 #31974C #C91D3C`, no glow (t1088 col x=520, `crops/china_t1088_pills_bars_x2.png`) | - | - |
| **Bars, ranked horizontal (lit)** | core 21 px, pitch 66 px (ratio 0.32), lit `#E74072` with a 12 px halo and a +14 lum floor lift; unlit `#572536` (about 0.38x the lit colour's brightness) (t530, `crops/china_t530_bars_x2.png`) | - | a focus treatment we have for lines only |
| **Bars, vertical hero (<=3)** | width **196 px (10.2% of frame)**, gap **246 px**, **w/pitch 0.44**, radius 0, crimson (JPEG `#B81748`; REPORT says `#D82650`) (bubbles 0008, `crops/bubbles_0008_bars_badges_x2.png`) | width **405 px (21.1% of frame, 31.6% of plot)**, radius **6 px**, `#FF8A4C` flat, no glow; 1v3: 405 + 405 px, gap 209 px, grey `#B8C4D0` + orange (94, 1v3) | our bars are 2.07x wider, rounded, and not dimmed |
| **Bars, vertical time series** | 34 px wide, pitch 190 px (**0.18**), `#7AAED6` (bubbles 0035) | engine slot ratio 0.62 (engine.mjs:9895) | 3.4x our density ratio |
| **Bar baseline** | a **short 4 px rule under each bar**, 36 px overhang each side, `#7A7C89` (bubbles 0008 y=473) | a full 1280 px axis | new element |
| **Category pill** | **white capsule, h 40.5 px**, r = h/2; text `#1E1F22`, cap **15 px** (cap/pill 0.37); a red dot `#D01C3E`, d 10 px, on its left end; 18 px gap to the bar (t1088, `crops/china_t1088_pilltext_x5.png`). A second form: a red capsule, h 36 px, white Bold cap 14 px (bubbles 0008) | bare Arial label, cap 23 px, `#C9CED4`, under the bar | new container; type 35% smaller |
| **Value text beside a bar** | white, digit height **31.5 px**, **Regular** (stem/height 0.14) (t1088 "1.69%") | Kalam in the bar, bbox 30 px, dark (94); Bold sans "1x" above the bar, bbox 25 px (1v3) | Bravos: Regular Inter, outside the bar end |
| **Value badge (hero bars)** | dark rounded rect **h 68 px**, fill `#1D2124` to `#313842` (JPEG), **1.5 px border `#465461`**, white Bold cap **30 px**; **outer glow `#2D404F`, half-intensity at 24 px, tail 90 px** (lum 81, 66, 60, 57, 54, 49, 46... every 6 px) (bubbles 0008, `crops/bubbles_0008_badge13T_x4.png`) | none | new element; the only glowing badge |
| **Line-end badge** | white capsule **h 25.5 px, w 51 px**, dark digits 14 px, **no glow**; leader 3 px `#8F9DAC`; red dot d 9 px `#D91C48` (t170, `crops/china_t170_badge86_x4.png`) | bold uppercase text label, digit h 23 px `#F2F2F2` + a coloured suffix (t5) | Bravos contains the label; ours is bare text |
| **Terminal tag + value bar** | white capsule tag h 30 px, text cap ~10.5 px; then a value bar in the series hue, h 26 px, and white Regular value text, 24 px (t1078, `crops/china_t1078_tags_valuebars_x2.png`) | - | new element |
| **Red chip (callout)** | h 43.5 px, `#C91F40`, radius ~6 px (estimate), white Bold cap 19 px (stem ratio 0.23) (t380, `crops/china_t380_chips_x4.png`) | - | - |
| **Hero line** | core **4.5 px, white-hot `#15E1FF`**, body `#0089DB` at 2 px; **bloom: +13 lum at 15 px, +3 at 45 px, gone at ~82 px**; hue `#19467A` at 10 px, `#1F3452` at 30 px (t170 row y=300, `crops/china_t170_bloom_x3.png`) | core **6 px**; **bloom +17 lum at the edge, gone at ~20 px** (t5 x=1050, `crops/ours_t5_lines_x3.png`) | Bravos' hero bloom reaches **4x further**, and its core is thinner and hotter |
| **Multi-line, every series** | core 4.5 px; glow ~16.5 px each side, +41 lum peak (t1078 x=300, `crops/china_t1078_redline_x3.png`) | core 6 px, glow ~20 px | close: ours is 1.5 px thicker |
| **Context lines** | **2 px**, muted (`#4A4544` = the orange at ~0.3), no bloom (t170 x=250) | E67 muted history: series hue at 0.45, thinner, no bloom | similar; the alpha differs |
| **Legend** | a dash + name, centred in the top band, 15 px, `#838A91` (t170, t1078), **alongside** the terminal tags | none (end labels, per E53.8) | see (c) |
| **Chart title** | **Inter Bold, pink `#DB8497` to `#E38296`**, cap **22 px** (t170) / **28.5 px** (t530) / **34.5 px** (t1088), top-left over the panel or centred | **Kalam 700, `#F2F2F2`, cap 29 px**, top-left at x=68 (94) | face, colour |
| **Section title** | white Inter Bold, cap **60 px**, subtitle white Regular below it (t220 "(SPR)") | the subtitle is Kalam, cap 18 px, `#C9CBCD` | - |
| **Source line** | two lines, "Date: ..." / "Source: ..., Bravos Research."; bbox 28.5 px for both, `#6F7378` to `#868A8F`; left-aligned with the panel, 54 px (t170) to 75 px (t530) below it | Kalam, one line, bbox 27 px, `#D3D5D6`, at the page bottom y~965 (94) | Bravos' source is ~0.5x the size and ~90 lum dimmer |
| **Annotation** | white Bold, cap 18 px, with a 42 px arrow (t530 "Oil Supply for 60 Days") | Bold sans reference label, bbox 29 px `#B8C4D0` (94) | - |
| **Font family** | **Inter** (letter shapes: 't' has a slanted cut; 'a' double-storey; 'g' single-storey; 'o' w/h 0.94; x/cap 0.77; t220 connected components). Poppins is rejected because its round 'o' is 1.0 or more; Montserrat is rejected for its wide caps. Weights: Bold titles, Medium pills, Regular numerals. | Kalam (hand) + **Arial**: the tick and category text renders with Arial's 'a' spur (`crops/ours_94_catlabel_x3.png`). The template declares `Inter, Arial` (template.html:185), but loads only Kalam (template.html:3). | we fall back to Arial without meaning to |
| **Footprint** | plot panel **43-57% of width x 44-59% of height** (t170 42.8x44.0, t1078 46.4x48.1, t530 56.9x58.8); chart plus annotations 79-94% x 64-79%; compact bar ranking 55x57% (t1088) | plot 66.7% of width (94, x 111..1391); line plot 49% (t5) plus 40% of labels | Bravos leaves the right ~35% to a dock or tags on line pages |

## (b) A proposed `longform` page profile (each dial is traced to a frame)

This is a page-scoped profile in the manner of `axes.readability: "landscape-phone"` (engine.mjs:7909). Values are at 1920x1080.

```
longform:
  ground: "#14181E"                      # china_t530 (0,0,40,40); flat, no vignette     [OVERRIDES E22 - see (c)1]
  plot_panel: {fill: "#222830", border_px: 1.5, border: "#696D73"}   # t530 interior (700,420,900,560); border (650,154) [(c)4]
  top_band_px: 42                        # t170 40 / t1078 45; carries the UNIT label, never a legend  [(c)6]
  top_rule: {px: 1.5, at: max_tick}      # t530 y=190, t170 y=232
  gridlines: 0                           # t530, t1078, bubbles 0035           [(c)7]
  zero_rule: {px: 3, color: "#675C66", when: "data crosses zero"}   # t1078 x=450 y=484..485 (E28 keeps it)
  ticks: {digit_px: 16.5, color: "#9A9DA2"}   # t170 15 / t530 18; #868A8E..#9C9DA4   [tension with E99 s90, (c)10]
  title: {face: "Inter 700", cap_px: 28, color: "#DB8497"}   # t530 cap 28.5, p90 #DB8497   [(c)3, (c)5]
  source: {lines: ["Date: ...", "Source: ..."], cap_px: 10.5, color: "#868A8F", below_panel_px: 60}  # t170/t530
  bars:
    corner_radius: 0                     # t1088 US bar end rows 246..266
    hbar_ratio: 0.64                     # t1088 35/55 px
    vbar_ratio_hero: 0.44                # bubbles 0008, 196/442 px (<=3 bars)
    vbar_ratio_series: 0.18              # bubbles 0035, 34/190 px (>=6 bars)
    hero_baseline: {px: 4, overhang_px: 36, color: "#7A7C89", when: "all values >= 0"}   # bubbles 0008 y=473
    focus: {halo_px: 12, floor_lift_lum: 14, unlit_brightness: 0.38}   # t530 US vs Saudi bar   [(c)9]
  category_pill: {h_px: 40, radius: "h/2", fill: "#FFFFFF", text: "#1E1F22", cap_px: 15, face: "Inter 500",
                  dot: {d_px: 10, color: "#D01C3E"}, gap_to_bar_px: 18}   # t1088
  value_text: {digit_px: 31, face: "Inter 400", color: "#FFFFFF", at: "bar end"}   # t1088 "1.69%"
  value_badge_hero: {h_px: 68, fill: "#1D2124", border_px: 1.5, border: "#465461", cap_px: 30, face: "Inter 700",
                     glow: {color: "#2D404F", half_px: 24, tail_px: 90}}   # bubbles 0008 $1.3T
  line_badge: {h_px: 25.5, radius: "h/2", fill: "#FFFFFF", digit_px: 14, leader_px: 3, leader: "#8F9DAC",
               dot: {d_px: 9, color: "#D91C48"}, glow: none}   # t170 "86"   [E99 s90 key, (c)10]
  terminal_tag: {h_px: 30, value_bar_h_px: 26, value_digit_px: 24}   # t1078
  lines:
    core_px: 4.5                         # t170 hero, t1078 multi
    hero: {core: white-hot, bloom_tail_px: 82, lift_15px_lum: 13}   # t170 row y=300
    multi_glow_px: 16.5                  # t1078 x=300
    context: {px: 2, bloom: 0}           # t170 x=250
  footprint: {panel_w: 0.47, panel_h: 0.48, right_reserve: 0.35}   # t1078 46.4x48.1, t170 42.8x44.0
  face: Inter (load it: today the template falls back to Arial)
```

## (c) Where adopting this would OVERRIDE a ruling or a brand decision (the operator's calls)

1. **The ground and the register (E22).** *"Register decided: cream `#F4E6C7` + charcoal `#25313C` + one accent token. Docks stay near-black."* BRAND-SHEET.md:176-177 adds: *"Docks stay near-black so the two registers never blur."* Bravos' `#14181E` is our DOCK register, so a near-black long-form page would blur the two.
2. **The deckle and the cream (E22 addenda 4 and 5).** *"The deckle is the feature that makes it look hand-drawn without the roughness."* *"it has to be cream."* Bravos has no paper, no deckle and no cream. E22 also makes it the signature: *"Every episode carries at least one; the payoff chart is one by default."*
3. **Kalam (E22 addendum 7; BRAND-SHEET.md:127, :177).** *"The charcoal fill onto that cream border with the handwriting font is absolutely what's needed."* The brand sheet assigns *"The ledger page's hand (title, source, ticks, values) | Kalam 400"*. Inter titles, ticks and values override this. (BRAND-SHEET.md:126 already names Inter for evidence charts and docks, so Inter is on-brand there.)
4. **The outline (E22 addendum 7).** *"We should just drop the outline entirely ... it's useless here, not pulling weight."* The template adds (template.html:66): *"NO black frame on a page"*. Bravos' 1.5 px panel border and its lit panel are an outline around the plot.
5. **One accent and the palette (E22; E67; BRAND-SHEET.md:45, :55).** E22 allows *"one accent token"*. E67 set the order: *"teal first, the Claude orange second, cobalt third, amber fourth"*. The brand sheet: *"the sunflower callout is the ONLY yellow on a chart"*. Bravos' pink titles (`#DB8497`), magenta bars (`#E74072`) and red pill dots (`#D01C3E`) add hues that are not in our tokens.
6. **The legend (E53.8).** *"a tag at the series' terminal point in the series' colour ... never a legend box."* Bravos puts a legend in the top band as well as its terminal tags (t170, t1078). The profile above keeps the band for the unit label only. Adopting Bravos' legend would override E53.8.
7. **Gridlines (E53.4; template.html:187).** In the overlay case E53.4 says *"the bars own every gridline"*, which assumes gridlines exist. The template draws `.lp-chart .grid` at `rgba(242,242,242,.14)`. Setting zero interior gridlines changes the overlay contract. Whether E53.4 then needs a tick-only form is the operator's call.
8. **The zero baseline (E28.1).** *"A drop is a bar going DOWN from a zero baseline."* The per-bar short baseline (bubbles 0008) is only honest when every value is 0 or more. With mixed signs, the 3 px zero rule stays, and Bravos keeps one too (t1078). This is a constraint on the profile, not a waiver.
9. **The muted alpha (E67.2).** *"the muted history ... in the SERIES' OWN hue at 0.45, never grey."* Bravos dims unlit bars to about 0.38x and context lines to about 0.3. A move from 0.45 changes a number the ruling states.
10. **The badge key and the type scale (E99 s90).** *"apply badges as the key"*: Bravos' white capsule tags support this. But s90 also says: *"Before this becomes default, long names must have a home, subtitle and y-axis label must not collide, and x-tick labels must clear the axis line ... Record only in this merge pass; build and visual judgment come after it."* s90 also says *"The opt-in T17 landscape-phone 16:9 page's roughly 12.5 px phone type is the direction over main's roughly 6.5 px"*, which points to LARGER type. Bravos' ticks are smaller than ours (15-18 px against 22-23 px). Copying Bravos' tick size therefore runs against s90's direction and needs the operator.
11. **Rounded bars.** The engine hard-codes `rx: 4/5/6` (engine.mjs:9654, 9901, 8984). I found no ruling that states them, but radius 0 changes every chart golden, and E67 names regenerating the goldens "on purpose in the commit that says why".

## (d) Which proposals fit existing engine dials, and which need new engine work

**Existing dials and literals, main checkout `docs/content-video-engine/samples/`:**
- Palette: `LP_INK`, `LP_CYCLE` (engine.mjs:9154-9155) and the template vars `--lp-char`, `--lp-chalk`, `--lp-pos`, `--lp-neg` (template.html:50).
- Line bloom alpha and radius: `LINE_BLOOM = 0.35` (engine.mjs:9157) and `LP_BLOOM_PX = 6` (engine.mjs:9165), which is tagged "[DERIVED: Bravos' yield lines, measured at 1080p]". My t170 hero bloom reaches ~82 px and t1078's multi-line glow ~16.5 px, so the tag matches the multi-line case, not the hero line.
- Muted history alpha: `LP_MUTED` (engine.mjs:9156) and the 0.45 history (subject to (c)9).
- Gridline alpha: `.lp-chart .grid` stroke (template.html:187). Alpha 0 hides them.
- Tick size and colour: `.lp-chart .lab` 24px `#c9ced4` (template.html:194).
- Title and source: `.lp-title` 34px (template.html:94) and `.lp-src` 22px (template.html:95).
- Faces: `LP_FACES` (engine.mjs:7997) and `.lp-ink` font-family (template.html:89).
- Bar ratios: `BAR_H = PITCH*0.62` (engine.mjs:9626) and `slotW*0.62` (engine.mjs:9895). These are literals, easy to lift into dials.
- Bar radius: the `rx` literals (engine.mjs:8984, 9654, 9901).
- Pill size and radius: `CP {w,h,rx}` (engine.mjs:9056).
- Badge timing and key: `LP_BADGE0/STEP/IN` and `LP_BADGE_COL` (engine.mjs:7941, 7963).
- The profile switch itself: the `LP_READABILITY` enum (engine.mjs:7909) already scopes a profile per page. `longform` would be a new value there, a small change.

**New engine work:**
1. The plot panel species: fill, a 1.5 px border, a top band and a top rule. None exists, and E22 addendum 7 retired the page line.
2. The white capsule category pill with a red dot on bar rows. Today the row name is bold text (`LP_ROW_NAME`, engine.mjs:9499).
3. The hero value badge: dark fill, border and a cool outer glow with a 24 px half and a 90 px tail.
4. The short per-bar baseline, conditional on all values being 0 or more.
5. A bar focus treatment: a halo on the lit bar, a floor lift, and dimming of the unlit bars. Bloom exists for lines only (`lpBloom`).
6. A two-layer hero stroke (a white-hot core over the hue body) plus a hero-only wide bloom that is separate from the multi-line glow.
7. The terminal tag plus value bar pair (t1078).
8. **Actually load Inter.** The template fetches only Kalam (template.html:3), so every "Inter" text renders as Arial today, as the 'a' spur in `crops/ours_94_catlabel_x3.png` shows. This is worth fixing whatever the operator decides about Bravos.

## Open items
- Bubbles hex values come from JPEG contact sheets (+/-10 per channel). The badge fill (`#1D2124` to `#313842`) and the pill red (`#AC2E5D`) are the weakest numbers. A 720p download of RUH3BPQ5fTo would firm them up, but it needs the operator's word; BRAVOS-RIG-VERIFIED.md records that the last copy was deleted after the read.
- The chip radius (~6 px) is an estimate from a 4x crop, not a scan.
- The font verdict is from letter shapes, not from a file. Confidence is medium-high for Inter.
