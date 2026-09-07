# Wealth Logic — where the picture change sits relative to the narration (J-cut / L-cut, measured)

*Pass-1 · 2026-09-06 · sources: the measured boundaries, video.en.vtt · for: TR-2*

## The question

TR-2 (`docs/content-video-engine/TRANSITIONS-REVIEW-2026-09-06.md` §1, from research brief B3,
"the only question no pass touched"): on the Wealth Logic reference, where does each picture
change sit relative to the narration? Is the cut **before** the sentence boundary (an **L-cut**,
picture leads), **after** it (a **J-cut**, audio leads), or **on** it — and by how much? The
distribution, not the mean.

The design proposal on file
(`docs/content-video-engine/briefs/ANSWERS-RESEARCH-BRIEF-animation-craft.md:370-386`, B3
"Voice-driven split-edit grammar") says J-cut = audio leads by 4–8 frames (166–333 ms) and
L-cut = picture leads by 6–10 frames (250–416 ms), tagged `[DERIVED]` from Pincus & Ascher and
explicitly "never measured on a reference". This pass measures it.

Method: `content/video_engine/scripts/measure_cut_offsets.py` over the 99 boundaries in
`wealth_logic_transitions_measured.csv` (TR-1) against the reference's word timing. Because the
reference's transcript is not reliably punctuated, a sentence boundary is defined two ways and
**both are reported**: **(a)** a caption gap ≥ 0.30 s between consecutive words (doc 46 §46.3's
settled threshold) and **(b)** a gap ≥ 0.45 s (the floor §46.3 overturned). The offset to the
nearest **word edge** is also reported, which needs no pause rule at all. Sign convention:

| | meaning | verdict |
|---|---|---|
| `t < gap_start` | the picture changed before the speech paused | picture leads (**L-cut-like**) |
| `gap_start ≤ t ≤ gap_end` | the picture changed during the pause | **on the pause** |
| `t > gap_end` | the speech had already resumed | audio leads (**J-cut-like**) |

Two word timelines, same audio, both on file. The **caption** timeline (`video.en.vtt`) carries
word *onsets* only — YouTube's auto-captions have no word end times — so a "gap" there is the
onset-to-onset interval and is an **upper bound** on the silence; its `gap_end` (the next word's
onset) is exact. The **Whisper** timeline (`wealth-logic-6-ways.words.json`, `small.en`) carries
real word ends, so its gap is the true silence; it is the timeline TR-2 and doc 46 §46.3 both
name. Every table below gives both.

## Verdict up front

**1. There is no split-edit grammar to find: the reference puts the picture change *on* the
pause, late in it, a median 100 ms — 3 frames at 30 fps — before the next word begins.** That
single mode holds under both transcripts and both gap rules: `t − gap_end` median −100 ms
(caption rule a and Whisper rule a and Whisper rule b), −80 ms (caption rule b); p25 −220 ms,
p75 −10 ms to +40 ms. Share on the pause 83 % / 66 % (caption / Whisper, rule a)
`[DERIVED: from wealth_logic_cut_offsets.csv, rule (a) gap >= 0.30 s]`.

**2. The 4–8 / 6–10 frame proposal is not what the reference does.** Nothing leads the pause by
a designed 6–10 frames: 1 of 99 changes (caption) and 7 of 99 (Whisper) sit before the pause at
all, and the Whisper seven lead by ≥ 0.9 s — mid-sentence cuts far from any pause, not L-cuts.
The changes that trail the pause trail by a median 2–3 frames, not 4–8. The correct single
number for our kit is **the picture changes ~3 frames before the next word's onset**.

## 1. Inside the pause — the dominant case

The nearest gap and the boundary's position inside it, all 99 boundaries.

| | caption rule (a) ≥ 0.30 s | caption rule (b) ≥ 0.45 s | Whisper rule (a) ≥ 0.30 s | Whisper rule (b) ≥ 0.45 s |
|---|---|---|---|---|
| on the pause | **82 (83 %)** | 76 (77 %) | **65 (66 %)** | 45 (45 %) |
| picture leads (L-cut-like) | 1 (1 %) | 2 (2 %) | 7 (7 %) | 15 (15 %) |
| audio leads (J-cut-like) | 16 (16 %) | 21 (21 %) | 27 (27 %) | 39 (39 %) |

`[DERIVED: from wealth_logic_cut_offsets.csv, rules (a) and (b), 99 boundaries]`

**Caption timeline, rule (a) ≥ 0.30 s — the distribution:**

| series | p10 | p25 | median | p75 | p90 |
|---|---|---|---|---|---|
| t - gap_start (ms) | 412 | 630 | 820 | 1000 | 1148 |
| t - gap_start (frames @30) | 12.4 | 18.9 | 24.6 | 30.0 | 34.4 |
| t - gap_end (ms) | -304 | -220 | **-100** | -10 | 40 |
| t - gap_end (frames @30) | -9.1 | -6.6 | **-3.0** | -0.3 | 1.2 |
| nearest word edge (ms) | -264 | -180 | -80 | 0 | 40 |
| nearest word edge (frames @30) | -7.9 | -5.4 | -2.4 | 0.0 | 1.2 |
| position in gap (0 = onset, 1 = next word) | 0.63 | 0.75 | **0.86** | 0.96 | 1.00 |

**Whisper timeline, rule (a) ≥ 0.30 s — the distribution:**

| series | p10 | p25 | median | p75 | p90 |
|---|---|---|---|---|---|
| t - gap_start (ms) | 180 | 310 | 460 | 610 | 888 |
| t - gap_start (frames @30) | 5.4 | 9.3 | 13.8 | 18.3 | 26.6 |
| t - gap_end (ms) | -340 | -220 | **-100** | 40 | 144 |
| t - gap_end (frames @30) | -10.2 | -6.6 | **-3.0** | 1.2 | 4.3 |
| nearest word edge (ms) | -204 | -140 | -40 | 60 | 180 |
| nearest word edge (frames @30) | -6.1 | -4.2 | -1.2 | 1.8 | 5.4 |
| position in gap (0 = onset, 1 = next word) | 0.47 | 0.57 | **0.78** | 0.89 | 0.94 |

**Whisper timeline, rule (b) ≥ 0.45 s** — reported for completeness; its tails are an artifact,
not a finding. At 0.45 s only 206 gaps exist in 1013 s, so a boundary that misses one is matched
to a gap seconds away (p10 −3000 ms, p90 +2936 ms). The centre is unchanged: `t − gap_end`
median **−100 ms**, `t − gap_start` median 540 ms, position in gap median 0.76.

| series | p10 | p25 | median | p75 | p90 |
|---|---|---|---|---|---|
| t - gap_start (ms) | -2412 | 320 | 540 | 1000 | 3644 |
| t - gap_end (ms) | -3000 | -250 | **-100** | 180 | 2936 |
| position in gap (0 = onset, 1 = next word) | 0.50 | 0.57 | 0.76 | 0.85 | 0.92 |

**Position in the gap corroborates doc 46 §46.3.** §46.3 settled `cut = gap_start + 0.8 · gap`
from the reference's 99 *ledger* cuts; these are the 99 *measured* boundaries of TR-1, a
separately derived list, and they give median 0.78 (Whisper) / 0.86 (caption)
`[DERIVED: from wealth_logic_cut_offsets.csv, pos_in_gap_a]`. The in-gap share reproduces too:
applying §46.3's tolerance to the Whisper timeline gives 71 % at ±0.05 s and 80 % at ±0.10 s
against §46.3's reported 72–81 % `[DERIVED: from wealth_logic_cut_offsets_whisper.csv, rule (a)
with tolerance 0.05 / 0.10 s]`.

**The one-line rule this pass supports:** the picture changes **~3 frames (100 ms) before the
next word's onset**, i.e. at ~0.8 of the silence — the same place §46.3 named, now stated as an
offset from the *speech* rather than as a fraction of the *gap*, which is what TR-2 asked for.
55 % of boundaries (caption) and 42 % (Whisper) land within 4 frames of the next word's onset;
85 % / 76 % within 8 frames `[DERIVED: from wealth_logic_cut_offsets.csv, |off_a_end_ms|]`.

## 2. Picture leads (L-cut) — 1 to 7 of 99, and they are not L-cuts

| | caption rule (a) | Whisper rule (a) |
|---|---|---|
| boundaries before the pause | 1 (1 %) | 7 (7 %) |
| how far ahead (median) | 100 ms (3.0 f) | 1580 ms (47 f) |
| how far ahead (p10 / p90) | 100 / 100 ms | 936 / 3652 ms |

`[DERIVED: from wealth_logic_cut_offsets.csv, rule (a), verdict_a = picture-leads]`

**There is no L-cut population.** Under the caption timeline exactly one boundary of 99 leads the
pause, by 3 frames — inside the ±100 ms the caption times themselves are worth (§ *Sources*).
Under the Whisper timeline the seven "leads" lead by 0.9–3.7 s: those are cuts placed in the
middle of continuous speech with the next ≥ 0.30 s silence a second or more away. They are
mid-speech cuts, the same population doc 46 §46.3 counted as mid-word (15–25 % at the ledger's
precision), not a deliberate picture-first split edit. Nothing in the 99 boundaries looks like
"picture leads by 6–10 frames".

## 3. Audio leads (J-cut) — the real minority, and it is 2–3 frames, not 4–8

| | caption rule (a) | Whisper rule (a) |
|---|---|---|
| boundaries after the pause | 16 (16 %) | 27 (27 %) |
| how far behind (median) | **60 ms (1.8 f)** | **100 ms (3.0 f)** |
| p10 / p25 / p75 / p90 (ms) | 20 / 40 / 70 / 100 | 40 / 70 / 1460 / 2812 |
| p10 / p25 / p75 / p90 (frames @30) | 0.6 / 1.2 / 2.1 / 3.0 | 1.2 / 2.1 / 43.8 / 84.4 |

`[DERIVED: from wealth_logic_cut_offsets.csv, rule (a), verdict_a = audio-leads]`

Under the caption timeline the whole trailing population is inside 100 ms — p90 = 3.0 frames.
This is not a J-cut technique; it is the same "just as the phrase starts" placement as §1, landing
a frame or two on the late side of the next word's onset. Under the Whisper timeline the median is
the same 3 frames, and the upper half again runs away (p75 1.46 s) for the same reason as §1: the
tail is the mid-speech cuts being matched to a distant gap, not an editing choice.

## 4. By kind — the dip is the one real offset, and it is an offset of the *transition*, not of the cut

Caption timeline, rule (a) ≥ 0.30 s:

| by kind | n | on pause | picture leads | audio leads | median t - gap_end (ms) | median pos in gap |
|---|---|---|---|---|---|---|
| blur-zoom | 28 | 21 (75%) | 0 (0%) | 7 (25%) | -30 | 0.96 |
| dip | 35 | 35 (100%) | 0 (0%) | 0 (0%) | -220 | 0.77 |
| hard-cut | 36 | 26 (72%) | 1 (3%) | 9 (25%) | -50 | 0.89 |

Whisper timeline, rule (a) ≥ 0.30 s:

| by kind | n | on pause | picture leads | audio leads | median t - gap_end (ms) | median pos in gap |
|---|---|---|---|---|---|---|
| blur-zoom | 28 | 14 (50%) | 2 (7%) | 12 (43%) | -20 | 0.88 |
| dip | 35 | 31 (89%) | 2 (6%) | 2 (6%) | -220 | 0.57 |
| hard-cut | 36 | 20 (56%) | 3 (8%) | 13 (36%) | -30 | 0.86 |

`[DERIVED: from wealth_logic_cut_offsets.csv and wealth_logic_cut_offsets_whisper.csv, rule (a),
grouped by the kind column of wealth_logic_transitions_measured.csv]`

**Hard cut and blur-zoom sit on the next word's onset** (median −30 to −50 ms, 1–1.5 frames
early). Both are instantaneous or near-instantaneous, so their boundary time *is* the moment the
world changes.

**The dip through black looks 220 ms early — because its boundary time is where the fade *starts*,
and the dip is 14 frames (0.47 s) wide at every one of its 35 instances (TR-1).** Correcting for
that: the dip's **black midpoint lands at the next word's onset, median +13 ms** — +13 ms under
both transcripts, p25 −37/−47 ms, p75 +73/+93 ms
`[DERIVED: from wealth_logic_cut_offsets.csv + duration_frames in
wealth_logic_transitions_measured.csv, off_a_end_ms + duration_frames/2 at 30 fps]`. The dip is
not offset from the speech at all; it is *centred* on the same instant the hard cut lands on. It
is also the only kind that never trails (0 of 35 audio-leads under the caption rule), because a
14-frame dip started after the phrase resumes would hold black over live narration.

**The rule this yields, if the dip enters our kit (TR-12 RULED, E47):** place the dip so its
midpoint, not its start, sits ~1 frame before the next word's onset — i.e. `dip_start = onset −
0.24 s` for a 14-frame dip `[DERIVED: from the dip midpoint measurement above, at 30 fps]`.

## 5. Against the design proposal (B3, `[DERIVED]`, never measured)

| B3 design proposal | proposed | measured on Wealth Logic (99 boundaries) | verdict |
|---|---|---|---|
| J-cut, audio leads by | 4–8 frames (166–333 ms) | trailing boundaries trail by a median **1.8 f (60 ms)** caption / **3.0 f (100 ms)** Whisper; caption p90 = 3.0 f | **not supported** — the real offset is half the proposed floor, and it is a placement scatter, not a technique |
| L-cut, picture leads by | 6–10 frames (250–416 ms) | **1 of 99** boundaries (caption) leads, by 3.0 f; the Whisper 7 lead by 0.9–3.7 s (mid-speech cuts) | **not supported** — no L-cut population exists in the reference |
| the grammar itself (split edits under continuous narration) | two distinct edit types chosen by narrative context | **one** mode: on the pause, at 0.78–0.86 of it, ~3 f before the next word's onset; 83 % / 66 % on the pause | **replaced** — the reference has a *placement* rule, not a split-edit grammar |
| dip through black | not addressed | 14 f wide, **midpoint centred on the next word's onset** (median +13 ms), never trails | **new** — the only kind with a designed offset, and it is a centring, not a lead |

`[DERIVED: from wealth_logic_cut_offsets.csv and wealth_logic_cut_offsets_whisper.csv, rule (a);
proposal figures quoted from ANSWERS-RESEARCH-BRIEF-animation-craft.md:370-386]`

The B3 table should be retagged: its frame bands are film-craft doctrine converted at 24 fps from
Pincus & Ascher (sources not on file), and the one reference we can measure does not do it. What
the reference *does* do is already ours in another form — doc 46 §46.3's `cut = gap_start + 0.8 ·
gap` — and TR-2's contribution is the equivalent statement anchored to the speech instead of the
silence: **picture change ≈ next word's onset − 3 frames**, which is checkable without a gap
threshold at all.

**Caution on the mount.** TR-2 was asked because "the mount is already an L-cut by construction and
we do not know if the reference does it". Measured answer: the reference does not use L-cuts. That
does not by itself condemn the mount — the mount is a signature, and E47 kept the signatures — but
it removes the "the reference does this too" justification. Treat the mount's picture-lead as a
deliberate deviation to be judged by eye, not as reference practice. Nothing in this report is an
instruction; the ruling is the operator's.

## Sources

- `docs/research/motion/wealth_logic_transitions_measured.csv` — the 99 boundaries with kind and
  `duration_frames` (TR-1, `measure_cut_kinds.py`, 2026-09-06). Boundaries span 10.6 s – 1002.7 s.
- `content/video_engine/sources/reference_analyses/6-ways-rich-people-make-money-with-debt/video.en.vtt`
  — YouTube auto-captions, 3083 inline word onsets parsed (441 live cue lines; the roll-up cues and
  the repeated context lines carry no word timing and are skipped). Last word 1012.6 s.
- `content/video_engine/sources/reference_analyses/6-ways-rich-people-make-money-with-debt/audio/wealth-logic-6-ways.words.json`
  — local Whisper `small.en int8 cpu`, 3158 words with start **and end**, duration 1013.46 s, source
  `https://www.youtube.com/watch?v=rCHYttyvaw8`.
- `content/video_engine/sources/reference_analyses/.../video.info.json` — `duration` 1014 s,
  `automatic_captions` present, `subtitles` empty: the caption track is machine-generated, not
  author-supplied.
- `docs/content-video-engine/46-REFERENCE-RHYTHM.md` §46.3 (the 0.30 s threshold and the 0.8-of-gap
  placement) and §46.5 (the kinds).
- `content/video_engine/scripts/measure_cut_gaps.py` — the gap definition, imported by this pass
  rather than restated.
- `content/video_engine/scripts/measure_cut_offsets.py` — this pass. Tests:
  `content/video_engine/tests/test_measure_cut_offsets.py` (13, synthetic VTT, no video).
- Row-level data: `docs/research/motion/wealth_logic_cut_offsets.csv` (caption timeline, the named
  artifact) and `docs/research/motion/wealth_logic_cut_offsets_whisper.csv` (Whisper timeline).

**Auto-caption timing error, measured rather than assumed.** The two transcripts were compared
word-for-word over the first 400 tokens; on the 225 that matched by text the caption onset differs
from the Whisper onset by a **median 40 ms and a p90 of 120 ms**
`[DERIVED: from video.en.vtt and wealth-logic-6-ways.words.json, |caption onset − Whisper onset| on
matched tokens]`. So caption word times are worth roughly ±1 frame typically and ±4 frames at the
tail — enough to move a single boundary's verdict, not enough to move a 99-boundary median. The
common claim that YouTube auto-caption word times are accurate to ~100 ms is `[UNVERIFIED]`: no
source for it was found on file (searched `docs/`, `docs/research/`,
`sources/reference_analyses/`); the 40 / 120 ms figures above are our own measurement and stand in
its place.

## NOT FOUND WHERE I LOOKED

- **Punctuated sentence boundaries for the reference.** Searched
  `sources/reference_analyses/6-ways-rich-people-make-money-with-debt/` (all files) and
  `video.info.json` (`subtitles` is empty, only `automatic_captions` exist). The auto-caption
  transcript's punctuation is machine-inserted and was not trusted; hence the two pause rules and
  the pause-free "nearest word edge" column. A human transcript would let §2 and §3 be re-cut on
  real sentence ends. Not searched: the web, any paid transcript service (no spend).
- **A published figure for YouTube auto-caption word-timestamp accuracy.** Searched
  `docs/DOCS-MANIFEST.jsonl`, `docs/DOCS-INDEX.jsonl`, `docs/research/`, `docs/content-video-engine/`
  and `sources/reference_analyses/` for caption/timestamp accuracy claims; nothing on file. The
  ±40 / ±120 ms above is measured here, not cited. Coverage limit: no web access in this pass.
- **The last 11 s of the video.** The caption track's final word is at 1012.6 s against a 1014 s
  runtime; the final boundary is at 1002.7 s, so no boundary is affected. Not investigated further.
- **A frame-exact boundary list.** The 99 boundaries come from TR-1's detector at 30 fps; their own
  precision (±1 frame ≈ 33 ms) is inside the caption timing error and was not separately bounded.
- **Whether any of this transfers to a second reference.** One reference, 99 boundaries. Nothing
  here is a cross-channel law; searched `docs/research/motion/` for any other measured boundary set
  and found none.
