# 34 — AOY Script Writer Study

Focused study of `write_script_v2`, the one AOY capability our own evaluation
rated as possibly real. Everything else in their toolchain has now been
assessed: doctrine is extractable (docs 31), the reviewers contradict their
own doctrine ([28-AOY-MCP-EVALUATION.md](28-AOY-MCP-EVALUATION.md)).

**Operator framing (2026-08-24):** *"the script review is light work, the only
thing that might be 'real' is their script writer… have them re-write these
scripts so we can learn how AoY would transform real breaking market chart
stories, and how it claims it would modify already highly viral financial
explainers. That gives us insight without exposing more of our information to
their data feed."*

---

## 1. How the tool actually works — it does not rewrite

The premise needed adjusting on contact. **`write_script_v2` accepts no
script input.** Its parameters are:

| Param | What it takes |
| --- | --- |
| `references` | 1–3 competitor **video URLs or @handles** whose FORMAT to model — explicitly supports "bend this exact video" |
| `niche_bend` | one line on where the video is going |
| `title` | ours stays on the page; it audits and offers three alternatives |
| `length_words` | target in words, not minutes |
| `style` | `vidrush` · `whiteboard` · `2d_animation` |
| `must_include`, `format`, `saturation_report` | optional |

So it is a **format-transfer engine**, not a rewriter: point it at a video,
tell it where to aim, and it models the structure.

**This is strictly better for the exposure concern.** We hand it public
YouTube URLs and a one-line direction. No script of ours, no claim
vocabulary, no evidence architecture. The information flow is one-way in our
favour.

## 2. Hard operational limits (discovered by hitting them)

- **One script at a time.** Submitting a second while one runs is refused:
  *"queueing several at once just makes all of them slower."*
- **3 per day**, beta-limited. After our first submission the response read
  "1 more today" — implying a third was consumed earlier in the day, so the
  counter is per-account per-day, not per-session.
- **~30 minutes typical, 45 max.** Returns a report URL immediately.
- The report page is server-rendered HTML that reloads itself on a timer;
  the placeholder is ~5 KB and grows when the script lands. No JSON
  endpoint — poll the same URL and watch the size.
- Rate limit across all AOY tools remains **5 requests / 3 minutes**.

Planning consequence: this is a **3-experiments-per-day instrument**. Design
each submission to answer a distinct question; do not spend runs on variants.

## 3. Experiment design

Source material: five caption sets the operator pulled, cleaned locally to
plain narration (kept in scratchpad, **not committed** — third-party
copyrighted transcripts). Two families:

| Family | Video IDs | Shape |
| --- | --- | --- |
| Breaking chart story ("bravos") | `Jw8ykhoOVBQ`, `YXFvwJQBzJc` | opens on two diverging lines, explains the mechanism that broke them |
| Viral book explainer ("casual finance") | `T4LDBJJ2A9E` (Psychology of Money), `zxVoCw3P1Gc` (Sowell), `BLBRRNwMZNE` (Getting to Yes) | behavioural lessons, paired stories, arithmetic |

**Bend policy — deliberately adjacent and public.** Each bend targets a
well-covered public topic rather than our actual angle, so the study teaches
transformation mechanics while revealing nothing about our roadmap. This is
the operative half of the operator's "without exposing more of our
information" constraint.

### Run 1 — chart-story transfer *(submitted, in flight)*

- reference `https://www.youtube.com/watch?v=Jw8ykhoOVBQ`
- bend: home prices vs median household income diverging since 2021
- title "Why Home Prices Stopped Following Wages" · 1900 words · `vidrush` · explainer
- report: `https://ai.theartofyt.com/reports/4e7a267deeb1490a.html`

### Run 2 — viral-explainer transfer *(queued; blocked by the 1-at-a-time rule)*

- reference `https://www.youtube.com/watch?v=T4LDBJJ2A9E`
- bend: Bill Perkins' *Die With Zero* in place of *The Psychology of Money*
- title "The Book That Says Dying Rich Is a Mistake" · 2600 words · `2d_animation` · explainer

## 4. What to measure when the scripts land

Baselines are the cleaned originals, so every question is a **delta against
the source format**, not an absolute judgement:

1. **Structural fidelity** — does it reproduce the reference's beat shape, or
   fall back to a generic template? Compare opening move, midpoint, close.
2. **Doctrine compliance** — does its own output obey doc 31? Check the
   8-second establish, positional rehooks (30s/1min/3min/mid), BUT/THEREFORE
   connectors, one-CTA outro, point ordering. **The reviewers failed this
   test; the writer is the more interesting case.**
3. **Sourcing integrity** — it promises "a sources block for every figure."
   Verify a sample against primary sources. Our review of `review_script`
   caught it fabricating a claim, so this is the load-bearing check.
4. **Craft against doc 32** — sentence length, active voice,
   attribution-first, terminal stress, anecdote↔reflection alternation,
   ring close. This is where a genuinely good script separates from a
   competent one.
5. **What it does that we don't** — the actual harvest. Anything that beats
   our own script on a dimension we already care about.
6. **Title audit quality** — it returns three alternatives; judged against
   their own title rules, which `review_title` violated.

## 5. Findings

*Pending — Run 1 in flight.*
