# 50 — The phone is the screen: ep1's real analytics, and what they say

Operator-supplied YouTube analytics for ep1, 2026-09-04. **This is ground truth, not
research** — and it is a sharper instrument than anything docs 42–49 gave us, because it
is our own audience rather than a reference channel.

---

## 50.1 The numbers

**Impressions funnel** (Sep 2–3, 2 days):

| | |
|---|---|
| thumbnail impressions | **77** |
| from YouTube recommending | 70.1 % |
| thumbnail CTR | **6.5 %** (was ~20 %) |
| engaged views from impressions | **5** |
| **average view duration, that cohort** | **1:05** |
| watch time from impressions | 0.09 h |

**Traffic sources** (since published): YouTube search **34.6 %** · channel pages **23.1 %**
· direct/unknown **19.2 %** · **suggested videos 11.5 %** · other features 3.9 % ·
others 7.7 %.

**Device** (lifetime watch time): **mobile phone 75.2 %** · computer 24.8 %.

**Overall average view duration: 4:39.** Cold traffic from impressions: **1:05.**

## 50.2 The finding: our type is illegible on a phone

75.2 % of watch time is a phone. Our stage is 1920 px wide. On a phone in portrait —
**YouTube's default player** — a 16:9 video fills the viewport width, ~390 CSS px:

```
scale = 390 / 1920 = 0.203        a 4.9x downscale
```

| our stage size | renders as | verdict |
|---|---|---|
| 12–15 px | 2.4–3.0 px | illegible |
| 21–26 px | 4.3–5.3 px | illegible |
| 30–34 px | 6.1–6.9 px | illegible |
| 40 px | 8.1 px | marginal |
| 60–64 px | 12.2–13.0 px | readable |

> **A font must be ≥ 59 px on our stage to reach 12 px on a phone in portrait.
> Fourteen of the sixteen distinct sizes in the template fall below that.** [DERIVED: from our own template font sizes and 390/1920 (sources: this repo, 50 §50.2), arithmetic]

A `DERIVED` tag marks a computed figure: a starting reference to test, never a research finding (R6; E42 2026-09-06).

> **Addendum 2026-09-05 (P41): the same arithmetic on the native 9:16 stage.** A 1080 x 1920
> short fills the 390 px phone width, a 2.77x downscale, so 12 px on the phone is **34 px on
> that stage** (59 px there is 21 px on the phone). The portrait ledger page is set to 40 px
> secondary / >= 59 px primary against that floor - `doc 49 §49.1`. The 59 px figure above is
> the LANDSCAPE stage's floor and must not be carried across as a number.

Axis labels, source lines, badge text, dock notes and captions all render between 2 and
7 px for three-quarters of our watch time.

**In landscape fullscreen** the video fills ~844 px, a 2.3× downscale, and the threshold
drops to 27 px — most sizes recover. But that requires the viewer to rotate *and* tap
fullscreen. **A cold viewer scrolling a feed is in portrait.**

**Status: arithmetic, not observation.** This is computed from declared font sizes, not
read off a rendered frame. **Verify by rendering one frame at 390 px and looking** before
treating it as established. It is recorded now because it fits the retention data better
than anything else we have hypothesised, and because it is cheap to check and cheap to fix.

## 50.3 What the retention split actually says

**Two cohorts, and they behave differently:**

- **Cold** (arrived from an impression): **1:05** average view duration.
- **Everyone** (including channel pages, direct links, the personal network): **4:39.**

That 4.3× gap is the signal. And because *average* view duration includes the viewers who
stayed, **the mass departure is earlier than 1:05** — if a handful watch 3–4 minutes, most
are leaving well before a minute.

This is consistent with `SCRIPT-G-VIEWER-CALIBRATION.md`'s drop at 0:45–1:00, and sharper:
that document located a visible step in the curve; this locates *who* steps off.

**Operator's caveat, recorded:** people who know him personally likely stayed longer and
sit outside the impression cohort. That inflates the 4:39 and does not touch the 1:05 —
the gap is real either way.

## 50.4 Reading the other two numbers honestly

**The CTR fall, 20 % → 6.5 %.** The operator's mechanism — YouTube seeding first to an
audience already primed for that thumbnail style, then normalising — is real and
documented. **But these numbers cannot show it.** 77 impressions × 6.5 % = **5 clicks**;
the earlier 20 % sat on a smaller base still. Five clicks against two is not a trend. The
conclusion may be right; it is not established here.

**"YouTube is serving it, so I can't blame them."** 70.1 % of 77 is ~54 recommended
impressions across two days. That is serving, but at a volume that is not really a test —
a video genuinely in the algorithm's trial pool sees hundreds to thousands. This reads
more like the initial push having ended than like a fair trial we failed.

**The traffic mix is the diagnostic, and it was not called out.**

```
search 34.6 + channel 23.1 + direct 19.2  =  76.9 %  came looking
suggested                                 =  11.5 %  algorithmic discovery
```

**Suggested is where growth lives.** A high search share on a tiny base is actually a good
sign about packaging — the title and thumbnail match a real query. Low suggested is
downstream of watch-time performance.

**The loop:** cold retention is poor → suggested placement stays low → impressions stay low
→ there is no data to learn from. §50.2 is a candidate root cause of the first link, and it
is the only link we can act on directly.

**Two reading rules, added later** (P54 fold). *Meta views are plays; 3-second views are
people.* Meta's views count any play, autoplay and replays included, and Insights lags
hours to a day; only 3-second views mean a person stayed, so a retention curve is drawn
from that small number (the Tokyo short's first hours: a notification at 300 views, stats
at 79, 3-second views 8; operator ledger 2026-09-06, `d3aa5f72dcf8`). A first short's zero
YouTube traction is the default for a channel with no history, not a verdict. *A bump near
a dock proves nothing when docks are dense.* On an absolute retention curve a rise can
only come from rewinds, so a bump is real; but with docks every ~22-30 s every bump lands
near a dock by chance, so the coincidence carries no causal information at this sample
size. Ask the inverse: which few docks produced a rewind, and what they share (ep1,
2026-09-08, `88109e64ea2a`).

## 50.5 What this changes

| | |
|---|---|
| **new gate** | **mobile legibility** — every rendered text size, at the portrait scale, against a 12 px floor. Mechanical, trivial, and it FAILs almost the whole template today. The 12 px floor itself is [DERIVED: from an asserted mobile-legibility threshold (sources: not on file - no citation in doc 50, doc 49 or the bundle), everything above rests on it; X0 tests it by reading a frame] |
| **reprioritises** | this may be a larger retention lever than any animation work in P38, and it is a fraction of the cost |
| **sharpens P40** | the target is no longer "the first minute" — it is **the cold cohort's first ~60 seconds on a 390 px screen** |
| **does not overturn** | anything in 42–49. It sits in front of them: the finest stroke in the world is invisible at 5 px |

**The uncomfortable version:** we have spent the week making the drawing better, and the
most likely reason people leave may be that they cannot read it.

## 50.6 Sources

Operator-supplied YouTube Studio analytics, 2026-09-04 (funnel Sep 2–3; traffic sources
and device lifetime). Scale arithmetic computed against
`scene-evidence-player.template.html`'s declared font sizes. Retention-curve context:
`SCRIPT-G-VIEWER-CALIBRATION.md`.

## 50.7 The lifetime curve and the intent cohort (read 2026-09-07; promoted from the parent's memory 2026-09-17, E99 s73)

**ep1 at lifetime** (the operator: *"we just gave it time to breathe"*): 13:27 long, 6:01 average view duration,
44.7 % average percentage viewed. The shape, not the average:

| window | what the curve does |
|---|---|
| 0:00 - ~1:30 | **the bleed** - ~95 % down to the low 40s; more than half the audience leaves in ninety seconds |
| ~2:00 - ~11:00 | **flat**, 40-48 % with only small jitter - everyone who got past the entrance stayed |
| ~11:00 - 13:27 | a gentle fade to the mid 30s |

It confirms E21 and E25 on data: E25 put the drop-off on the charts held 0:09-0:50 and 0:50-1:11, E21 named 0:57 as
the first-drop point, and the curve's steep section is the same window arrived at independently. What the curve ADDS:
the body was never the problem, so all of ep1's loss is the first ninety seconds and E24/E25's first-minute rules
(the promise by 0:45, the 6 s chart ceiling in the opening minute) point at exactly the right place. None of the
engine work after 0:90 is tested by this curve.

**The intent cohort** (the first YouTube-search breakdown, same day): search overall 19 views, 10:42 average view
duration, 79.7 % viewed. Inside it, *"ai bubble"* - 5 views, 1:15, 9.4 % viewed (a broad topical query; five
people, one consistent bounce - the statistically meaningful row, and the negative one); *"bravos research"* - 1
view, 12:56, 96.2 % viewed (an intent query; the person the video was for watched essentially all of it). The
operator: *"the youtube video got minimal traction, and had a high bounce rate. But the one person so far who found
the video from searching for Bravos Research, who was our target audience for the video, watched for 13 minutes."*
**Apply:** judge a video on the intent cohort, never the blended retention number; a topical query's bounce reads
"the package answered a question that viewer was not asking", not "the video is weak". Sits with 50.3's cold-cohort
read and E27 (the package first).
