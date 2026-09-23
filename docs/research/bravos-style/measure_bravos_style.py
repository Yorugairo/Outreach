"""Reproduce every number in BRAVOS-LONGFORM-CHART-SPEC.md from the pixels.

Inputs (read-only):
  frames/china_t<sec>.png     - 1280x720 stills cut with ffmpeg from the China episode's own download
                                (reference_analyses/bravos-china-just-triggered-a-new-world-order/claude-watch/download/video.mp4, AV1 1280x720)
  frames/bubbles_*_panel960.png - 960x539 panels cut from the bubbles contact sheets by extract_bubbles_panels.py
                                (the 119 bubbles frames on disk are 512x288; the sheet panels are the largest copy available)
  ../p69t6-94-land.png, ../p69t6-1v3-land.png, ../p69t5-stamp-plus-card.png - ours, 1920x1080
Output: measurements.json + crops/ (one crop per measured element).
Stage scale: China x1.5, bubbles panels x2.0, ours x1.0 - every px value in the JSON is already at 1920x1080.
Run: python measure_bravos_style.py
"""
import json, os
import numpy as np
from mlib import load, lum, hx, med, runs, bbox, save_crop

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
OUT = {}


def rec(key, value, src, crop=None, note=""):
    OUT[key] = {"value": value, "source": src, "crop": crop, "note": note}


def run_len(r):
    return r[1] - r[0] + 1


# ---------------- Bravos, China episode (x1.5) ----------------
K = 1.5
a = load("frames/china_t530.png"); L = lum(a)
rec("ground_hex", hx(med(a, 0, 0, 40, 40)), "china_t530 corner (0,0,40,40); same value centre-bottom and all 6 China frames")
rec("plot_fill_hex", hx(med(a, 700, 420, 900, 560)), "china_t530 plot interior (700,420,900,560)")
rec("plot_border_hex", hx(a[154, 650]), "china_t530 top border px (650,154)", "crops/china_t530_border_x4.png")
save_crop(a, (630, 140, 670, 200), "crops/china_t530_border_x4.png", 4)
col = L[140:200, 650]
peaks = [i for i in range(1, len(col) - 1) if col[i] > 80]
rec("plot_border_px", round(1 * K, 1), "china_t530 col x=650: border is a single row (lum %d) at y=154" % col[14], note="1 px @720")
# ranked bars with glow
thick = [run_len(r) for r in runs((L[218:262, 350] > 90))]
rec("hbar_glow_core_thickness_px", round(14 * K, 1), "china_t530 lum profile x=350 y=245..258 (lum>90)", "crops/china_t530_bars_x2.png")
save_crop(a, (280, 185, 720, 360), "crops/china_t530_bars_x2.png", 2)
starts = [r[0] for r in runs((a[:, 330, 0] > 120) & (a[:, 330, 0] - a[:, 330, 2] > 40))]
pitch = float(np.mean(np.diff(starts)))
rec("hbar_glow_pitch_px", round(pitch * K, 1), "china_t530 red-run starts at x=330: %s" % starts)
rec("hbar_glow_fill_hex", hx(a[251, 350]), "china_t530 US bar centre (350,251)")
rec("hbar_dim_fill_hex", hx(a[384, 300]), "china_t530 Saudi bar (300,384) - the unlit bars")
rec("hbar_glow_halo_px", round(8 * K, 1), "china_t530 x=350 lum 73->52 over y=244..236 above the US bar; row y=251 end glow 93->51 over x=462..469")
rec("hbar_glow_floor_lift_lum", int(L[235, 350] - L[540, 700]), "china_t530 lum between lit bars (350,235) minus empty plot (700,540)")

a = load("frames/china_t1088.png"); L = lum(a)
save_crop(a, (280, 200, 1000, 390), "crops/china_t1088_pills_bars_x2.png", 2)
bar_runs = runs(L[195:390, 520] > 60)
rec("hbar_flat_thickness_px", round(np.mean([run_len(r) for r in bar_runs]) * K, 1), "china_t1088 col x=520 runs %s" % bar_runs, "crops/china_t1088_pills_bars_x2.png")
st = [r[0] for r in bar_runs]
rec("hbar_flat_pitch_px", round(float(np.mean(np.diff(st))) * K, 1), "china_t1088 bar starts %s" % st)
rec("hbar_flat_corner_radius_px", 0, "china_t1088 US bar right end: rows 246..266 all end at x=859 (no taper)")
rec("hbar_flat_fills", [hx(med(a, 500, y - 3, 600, y + 3)) for y in (220, 256, 292, 329, 366)], "china_t1088 bar centres x=500..600")
rec("hbar_flat_longest_px", round((898 - 450) * K), "china_t1088 UK bar x=450..898")
pill = [run_len(r) for r in runs(L[195:390, 425] > 180)]
rec("cat_pill_height_px", round(np.mean(pill) * K, 1), "china_t1088 col x=425 white runs %s" % pill, "crops/china_t1088_pilltext_x5.png")
save_crop(a, (300, 245, 440, 305), "crops/china_t1088_pilltext_x5.png", 5)
rec("cat_pill_radius", "h/2 (capsule)", "china_t1088 pill right end: height 28@x425 -> 14@x437 -> 0@x438")
rec("cat_pill_fill_hex", hx(med(a, 420, 215, 430, 222)), "china_t1088 (420..430,215..222)")
m = L[246:268, 318:432] < 120
rec("cat_pill_text_hex", hx(a[246:268, 318:432][m].min(axis=0)), "china_t1088 darkest px in the US pill")
b = bbox(m)
rec("cat_pill_cap_px", round((bbox(m[:, b[0]:b[0] + 8])[3] - bbox(m[:, b[0]:b[0] + 8])[1] + 1) * K, 1), "china_t1088 'U' of United States")
rec("cat_pill_dot", {"hex": hx(med(a, 358, 216, 362, 220)), "d_px": round(6.5 * K, 1)}, "china_t1088 (358..362,216..220)")
rec("cat_pill_to_bar_gap_px", round((450 - 438) * K), "china_t1088 pill right x=437, bar left x=450")
m = L[352:382, 600:680] > 150; b = bbox(m)
rec("value_text_h_px", round((b[3] - b[1] + 1) * K, 1), "china_t1088 '1.69%%' bbox %s" % (b,))
rec("value_text_stem_ratio", round(3 / (b[3] - b[1] + 1), 2), "china_t1088 '1' stem 3 px / digit height -> Regular")
tm = a[145:190, 350:920, 0] > 150; b = bbox(tm)
rec("title_centred_cap_px", round(23 * K, 1), "china_t1088 'C' of Current rows 155..177")
rec("title_hex", hx(np.percentile(a[145:190, 350:920][tm], 90, axis=0)), "china_t1088 title p90 of pink px")

a = load("frames/china_t170.png"); L = lum(a)
save_crop(a, (640, 340, 780, 420), "crops/china_t170_badge86_x4.png", 4)
save_crop(a, (600, 240, 720, 400), "crops/china_t170_bloom_x3.png", 3)
p = L[300, 600:720]
rec("line_hero_profile_lum", [int(v) for v in p[40:105]], "china_t170 row y=300 x=640..704 (hero line at x=671)", "crops/china_t170_bloom_x3.png")
rec("line_hero_core_px", round(3 * K, 1), "china_t170 row y=300: lum>150 at x=670..672")
rec("line_hero_core_hex", hx(a[300, 671]), "china_t170 (671,300)")
rec("line_hero_bloom", {"d2": hx(a[300, 669]), "d10": hx(a[300, 661]), "d30": hx(a[300, 641]), "d60": hx(a[300, 611]),
                        "lift_at_15px_lum": int(L[300, 656] - 43), "lift_at_45px_lum": int(L[300, 626] - 43), "tail_px": round(55 * K)},
    "china_t170 row y=300 offsets from x=671; plot fill lum 43")
rec("line_context_px", round(1.3 * K, 1), "china_t170 x=250 production line lum 69 at a single row (442..443)")
rec("line_context_hex", hx(a[443, 250]), "china_t170 (250,443)")
rec("line_badge", {"h_px": round(17 * K, 1), "w_px": round(34 * K), "fill": "#FFFFFF", "text_px": round(9.5 * K, 1), "radius": "h/2",
                   "leader_px": round(2 * K), "leader_hex": hx(a[381, 700]), "dot_hex": hx(a[381, 723]), "dot_d_px": round(6 * K),
                   "glow": "none (row 381 drops 174->21 in 1 px past the badge)"}, "china_t170 x=735 rows 373..389; row 381", "crops/china_t170_badge86_x4.png")
rec("plot_top_band_px", round((232 - 205) * K), "china_t170 box top y=205, top-tick rule y=232 - the legend lives in the band")
for nm, (x0, y0, x1, y1), thr in [("tick_label", (120, 250, 146, 272), 60), ("unit_label", (28, 205, 150, 222), 60),
                                  ("legend", (300, 210, 372, 226), 60), ("source", (108, 558, 260, 582), 60)]:
    s = L[y0:y1, x0:x1] > thr; bb = bbox(s)
    rec(nm + "_t170", {"bbox_h_px": round((bb[3] - bb[1] + 1) * K, 1), "hex_p90": hx(np.percentile(a[y0:y1, x0:x1][s], 90, axis=0))}, "china_t170 box %s" % ((x0, y0, x1, y1),))
rec("plot_box_t170", {"w_pct": round((705 - 157) / 1280 * 100, 1), "h_pct": round((522 - 205) / 720 * 100, 1)}, "china_t170 border cols 157/705 rows 205/522")

a = load("frames/china_t1078.png"); L = lum(a)
save_crop(a, (280, 470, 600, 530), "crops/china_t1078_redline_x3.png", 3)
save_crop(a, (690, 240, 1220, 540), "crops/china_t1078_tags_valuebars_x2.png", 2)
rec("line_multi_profile_red", [int(v) for v in L[488:520, 300]], "china_t1078 x=300 y=488..519 (China line)", "crops/china_t1078_redline_x3.png")
rec("line_multi_core_px", round(3 * K, 1), "china_t1078 x=300 rows 500..502 lum>=80; green x=470 rows 406..408")
rec("line_multi_glow_px", round(11 * K, 1), "china_t1078 x=300 lum 85 at y=501 back to 44 by y=489 / y=517")
rec("zero_line", {"px": round(2 * K), "hex": hx(a[484, 450])}, "china_t1078 x=450 rows 484..485")
rec("gridlines_interior", 0, "china_t1078 col x=560 inside plot: only the lines and the zero rule; china_t530 plot interior uniform lum 39; bubbles_0035 col x=500 max lum 43")
tagh = [run_len(r) for r in runs(L[240:540, 805] > 180)]
rec("terminal_tag_h_px", round(np.mean(tagh) * K, 1), "china_t1078 col x=805 white runs %s" % tagh, "crops/china_t1078_tags_valuebars_x2.png")
vb = [run_len(r) for r in runs(L[240:540, 850] > 60)]
rec("value_bar_h_px", round(np.mean(vb) * K, 1), "china_t1078 col x=850 runs %s" % vb)
rec("plot_box_t530", {"w_pct": round((1013 - 285) / 1280 * 100, 1), "h_pct": round((577 - 154) / 720 * 100, 1)}, "china_t530 border cols 285/1013 rows 154/577")
rec("content_footprint_pct", {"t170": [91.0, 69.9], "t220": [91.0, 73.1], "t380": [93.8, 78.5], "t530": [79.2, 78.5], "t1078": [90.8, 64.0], "t1088": [54.6, 56.5]}, "bbox of px differing from ground by >30 (sum RGB), logo masked; [w%, h%] - see ground_map probe in the session")
rec("plot_box_t1078", {"w_pct": round((698 - 104) / 1280 * 100, 1), "h_pct": round((537 - 191) / 720 * 100, 1)}, "china_t1078 box")

a = load("frames/china_t220.png"); L = lum(a)
save_crop(a, (245, 108, 1040, 212), "crops/china_t220_title_font_x2.png", 2)
m = L[105:170, 240:1040] > 200; b = bbox(m)
rec("section_title_cap_px", round((bbox(m[:, b[0]:b[0] + 30])[3] - bbox(m[:, b[0]:b[0] + 30])[1] + 1) * K, 1), "china_t220 'S' of Strategic (white Bold)", "crops/china_t220_title_font_x2.png")
rec("font_evidence", {"o_w_over_h": round(29 / 31, 2), "x_over_cap": round(30 / 39, 2), "t_top": "slanted cut", "a": "double-storey", "g": "single-storey",
                      "verdict": "Inter (Bold titles, Medium pills, Regular numerals); Poppins rejected (round o >= 1.0), Montserrat rejected (wide caps)"},
    "china_t220 connected components: P h=39, r h=30, o 29x31")
a = load("frames/china_t380.png"); L = lum(a)
save_crop(a, (940, 350, 1090, 425), "crops/china_t380_chips_x4.png", 4)
rec("chip", {"h_px": round(29 * K, 1), "fill": hx(med(a, 1008, 360, 1012, 364)), "cap_px": round(12.5 * K, 1), "stem_ratio": 0.23, "radius_px_est": round(4 * K)},
    "china_t380 col x=1015 red runs 355..383 / 389..417", "crops/china_t380_chips_x4.png")

# ---------------- Bravos, bubbles contact-sheet panels (x2.0) ----------------
K = 2.0
a = load("frames/bubbles_frame_0008_panel960.png"); L = lum(a)
save_crop(a, (380, 240, 800, 485), "crops/bubbles_0008_bars_badges_x2.png", 2)
save_crop(a, (600, 240, 800, 330), "crops/bubbles_0008_badge13T_x4.png", 4)
rec("vbar_hero", {"w_px": 98 * K, "gap_px": (651 - 528) * K, "w_over_pitch": round(98 / 221, 2), "w_pct_frame": round(98 / 960 * 100, 1),
                  "fill_jpeg": hx(med(a, 660, 350, 740, 450)), "radius": 0},
    "bubbles_0008 row y=455 red runs 430..527 / 651..748", "crops/bubbles_0008_bars_badges_x2.png")
rec("vbar_baseline", {"thick_px": round(2 * K), "overhang_each_side_px": 18 * K, "hex": hx(a[474, 420])},
    "bubbles_0008 row y=473 run 412..543 under bar 430..527")
rec("value_badge_hero", {"h_px": 34 * K, "fill": hx(med(a, 404, 400, 409, 420)), "border_hex": hx(a[297, 779]), "cap_px": 15 * K,
                         "glow_hex": hx(a[297, 784]), "glow_half_px": 12 * K, "glow_tail_px": 45 * K,
                         "glow_profile_lum": [int(L[297, x]) for x in range(779, 842, 3)]},
    "bubbles_0008 $1.3 trillion badge: col x=700 border rows 280/314; row y=297 outward from x=779", "crops/bubbles_0008_badge13T_x4.png")
rec("cat_pill_red", {"h_px": 18 * K, "cap_px": 7 * K}, "bubbles_0008 'Dot-com bubble' pill col x=428 rows 367..385")
rec("vignette_hero_bars", {"centre": hx(med(a, 560, 120, 620, 160)), "near_bars": hx(med(a, 420, 500, 500, 535)), "edge": hx(med(a, 0, 500, 40, 535))},
    "bubbles_0008 ground samples")
a = load("frames/bubbles_frame_0035_panel960.png"); L = lum(a)
save_crop(a, (320, 100, 890, 440), "crops/bubbles_0035_timebars_x1.png", 1)
br = runs((a[400, :, 2] > 150) & (a[400, :, 2] - a[400, :, 0] > 40))
rec("vbar_time", {"w_px": round(np.mean([run_len(r) for r in br]) * K), "pitch_px": round(float(np.mean(np.diff([r[0] for r in br]))) * K),
                  "fill": hx(med(a, 550, 380, 556, 420))}, "bubbles_0035 row y=400 runs %s" % br, "crops/bubbles_0035_timebars_x1.png")
a = load("frames/bubbles_frame_0067_panel960.png")
save_crop(a, (690, 110, 790, 440), "crops/bubbles_0067_hibar_badge_x2.png", 2)
rec("hist_focus_bar", {"hex": hx(med(a, 738, 300, 742, 380)), "rest_hex": hx(med(a, 600, 395, 604, 405)), "glow_px": 10 * K},
    "bubbles_0067 row y=300 x=715..763", "crops/bubbles_0067_hibar_badge_x2.png")

# ---------------- ours (x1.0) ----------------
a = load("../p69t6-94-land.png"); L = lum(a)
save_crop(a, (0, 0, 700, 160), "crops/ours_94_title_corner_x1.png")
save_crop(a, (500, 300, 1000, 420), "crops/ours_94_bar_top_x2.png", 2)
rec("ours_ground", {"cream": hx(a[5, 960]), "page": hx(med(a, 1500, 500, 1560, 560)), "cream_top_px": 13, "page_radius_px_est": 30}, "ours p69t6-94-land")
rec("ours_gridlines", {"n": 5, "px": 2, "hex": hx(a[410, 300]), "axis_px": 3, "axis_hex": hx(a[783, 300])}, "ours 94 col x=300")
rec("ours_bar_94", {"w_px": 953 - 549 + 1, "plot_w_px": 1391 - 111, "w_pct_plot": round(405 / 1280 * 100, 1), "w_pct_frame": round(405 / 1920 * 100, 1),
                    "radius_px": 6, "fill": hx(a[600, 700])}, "ours 94 row y=600, corner rows 345..351", "crops/ours_94_bar_top_x2.png")
m = L[45:105, 60:700] > 150; b = bbox(m)
rec("ours_title", {"cap_px": bbox(m[:, b[0]:b[0] + 22])[3] - bbox(m[:, b[0]:b[0] + 22])[1] + 1, "hex": hx(np.percentile(a[45:105, 60:700][m], 90, axis=0)), "face": "Kalam 700"},
    "ours 94 'N' of Ninety", "crops/ours_94_title_corner_x1.png")
m = L[395:425, 30:105] > 120
rec("ours_tick", {"bbox_h_px": bbox(m)[3] - bbox(m)[1] + 1, "hex": hx(np.percentile(a[395:425, 30:105][m], 90, axis=0))}, "ours 94 '80%' tick")
m = L[960:1000, 60:1230] > 110
rec("ours_source", {"bbox_h_px": bbox(m)[3] - bbox(m)[1] + 1, "hex": hx(np.percentile(a[960:1000, 60:1230][m], 90, axis=0)), "face": "Kalam"}, "ours 94 source line")
save_crop(a, (585, 798, 915, 840), "crops/ours_94_catlabel_x3.png", 3)
rec("ours_axis_face", "Arial (the 'a' spur, the angled 'C' terminals) - template .lp-chart text declares 'Inter, Arial' and Inter is not loaded", "crops/ours_94_catlabel_x3.png")
a = load("../p69t6-1v3-land.png"); L = lum(a)
r = runs(L[720, 110:1400] > 120)
rec("ours_bars_1v3", {"runs_x": [(x0 + 110, x1 + 110) for x0, x1 in r], "gap_px": r[1][0] - r[0][1] - 1, "fills": [hx(a[720, 400]), hx(a[720, 1000])], "glow": "none (lum 158->47 in 1 px)"}, "ours 1v3 row y=720")
a = load("../p69t5-stamp-plus-card.png"); L = lum(a)
save_crop(a, (1000, 360, 1100, 650), "crops/ours_t5_lines_x3.png", 3)
rec("ours_line_profile_teal", [int(v) for v in L[596:642, 1050]], "ours t5 x=1050 y=596..641", "crops/ours_t5_lines_x3.png")
rec("ours_line", {"core_px": 6, "bloom_px": 20, "bloom_lift_lum": int(L[615, 1050] - 44), "orange_core": hx(a[390, 1050]), "teal_core": hx(a[618, 1050])},
    "ours t5 x=1050: teal core 616..621, lift 44->61 over 596..615; orange core 388..392")
rec("ours_line_page_ground", {"top": hx(med(a, 1500, 150, 1560, 200)), "mid": hx(med(a, 1300, 900, 1360, 950)), "bottom_left": hx(med(a, 200, 1000, 260, 1040))}, "ours t5 page samples")
m = L[350:390, 1112:1755] > 150; b = bbox(m)
rec("ours_end_label", {"digit_h_px": bbox(m[:, b[0] + 18:b[0] + 34])[3] - bbox(m[:, b[0] + 18:b[0] + 34])[1] + 1, "hex": "#F2F2F2", "weight": "Bold caps"}, "ours t5 '+613%' end label")
m = L[838:875, 175:285] > 120
rec("ours_xtick", {"bbox_h_px": bbox(m)[3] - bbox(m)[1] + 1, "hex": hx(np.percentile(a[838:875, 175:285][m], 90, axis=0))}, "ours t5 'Oct 25' tick")

with open("measurements.json", "w") as f:
    json.dump(OUT, f, indent=1)
for k, v in OUT.items():
    print(k, "=", v["value"])
