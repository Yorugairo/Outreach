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

## 4b. Baseline analysis — the chart-story reference (`Jw8ykhoOVBQ`)

Analysed before the AOY script lands, so the comparison is measured rather
than impressionistic. Structural observations only; no transcript text is
reproduced or committed.

### The finding that matters most: this is our topic

The reference video is **not** a neutral format sample. It argues the same
claim cluster as our current-bubble work — the semiconductor-vs-hyperscaler
performance divergence, AI capex without demonstrated ROI, and AI builders
at **20% of the S&P 500 against a 2–4% historical norm**. It is a direct
competitor to the video we are planning, and it is a strong one.

That changes its value: it is both a format reference *and* the best
available benchmark for what our own video has to beat.

### Beat map

| Beat | Move |
| --- | --- |
| Hook | Two lines that tracked since 2021 stopped tracking. First sentence, present tense, no greeting. |
| Identify | Names both lines concretely — chipmakers vs hyperscalers, actual tickers. |
| Stake | If the spenders aren't earning a return, the infrastructure meltup is a house of cards. |
| Evidence run | Three real instances: a named CEO's on-air remark, a company that burned its annual AI budget in four months, a second restricting internal AI tools on cost. |
| Escalate | Concentration — 20% of the index vs 2–4% historically, so a pop now transmits to everything. |
| **Reframe** | Pivots from news to a **model**: the Gartner hype cycle, laid out in full. |
| **Analogue 1** | 1840s railway mania — capital scale in today's money, the doubling, the ~70% decade-long crash. |
| The lesson | The technology was real; the *timing* was mispriced — ~3 years expected against ~20 actual. |
| **Measurement** | One number carries the thesis: capital into the tech as a share of GDP. Today ~8%; dot-com and railways both peaked near 7%. |
| **Trigger** | Rate cycles. Both prior bubbles turned when the central bank raised *above the level where the boom began*. |
| **Falsifiable tell** | Names the specific threshold to watch, and says the conditions are **not** met yet. |
| De-escalate | Explicitly refuses the panic close. |
| Action | Don't try to time the peak; don't be passive either. |
| CTA | Single ask — book a call. |

### What it does better than our current script

1. **Analogy is the spine, not decoration.** Railways and dot-com are not
   garnish; they supply the model, the measurement, and the trigger. This
   also **resolves the open analogy question** from doc 28 — whether or not
   AOY prompts for analogy, the best competitor in this lane runs on it.
2. **A falsifiable tell.** It names a specific, checkable threshold and
   states plainly that it has not been crossed. Enormous authority per word:
   it can be wrong, in public, on a date. Our receipt device does this for
   personal finance; we have no macro equivalent.
3. **It declines the sensational move.** "Not the end of the world, not a
   time to panic sell" — refusing the obvious doom close is what makes the
   warning credible, and it inoculates against the standard criticism.
4. **One number carries the argument.** The GDP-share threshold does more
   work than any other line. Compare our tendency to distribute evidence
   across many surfaces.
5. **Escalation is structural.** Anecdote → concentration → model →
   history → measurement → trigger. Each beat raises the altitude. Nothing
   is merely additional.

### Where it is weak — the gaps we can take

- **The close is a pitch, not a peak.** Roughly the last 8% of the runtime
  is sales copy for a strategy call. By Peak-End Theory (doc 31 §8b) that
  is the single worst place to sag, and by ring doctrine (doc 32 §5) the
  ending should return transformed to the opening chart. It never does.
  **The strongest structural opening we have against this competitor.**
- **Attribution is loose in places** — "many are concerned," "we think" —
  where our claim registry forces a source.
- **The headline GDP-share figure is a contested construction** and arrives
  unsourced. Our verbatim-figure and `[verify]` discipline is genuinely
  stronger here.
- **No reflection beat.** It is all mechanism and evidence; it never stops
  to say what this means for the viewer's life. Doc 32 §5 predicts that
  costs it emotional range, and the abrupt swerve into a sales pitch is
  arguably the symptom.

### Consequences for our own work

- Adopt the **falsifiable tell** as a format device: every macro video names
  one checkable threshold and states where we currently sit.
- Adopt **analogy-as-spine** for mechanism explainers — a historical
  parallel that supplies model, measurement, and trigger, not a passing
  comparison.
- Keep our **sourcing discipline** as the visible differentiator; the
  competitor's weakest seam is exactly our strongest system.
- **Ring the close.** Return to the opening chart transformed, and put the
  CTA inside the action window rather than in place of the ending.

## 4c. The competitor template, extracted (`Jw8ykhoOVBQ` + `YXFvwJQBzJc`)

Two videos from the same channel (Braavos Research, self-identified in the
narration) run **the same formula with different variables**. Two samples is
enough to extract it, and the formula is good enough to adopt.

### The template

| # | Beat | Video A (AI capex) | Video B (confidence gap) |
| --- | --- | --- | --- |
| 1 | Cold open on a **divergence** — two lines that used to track | relationship "completely broken" since 2021 | "first time in over 30 years" |
| 2 | Name both lines concretely, with their source | chipmakers vs hyperscalers | consumer stock-confidence vs U. Michigan personal outlook |
| 3 | State the paradox plainly | infra +300%, spenders flat | confident about stocks, depressed about own prospects |
| 4 | Assert depth — this is a symptom, not a blip | "house of cards" | "extremely deep roots… requires a reset" |
| 5 | **Name a formal framework** for authority | Gartner hype cycle | Friedman's permanent income (1957) |
| 6 | Establish the long-run baseline it violates | 2–4% index share historically | 2.8%/yr real income since the 1960s |
| 7 | Mid-roll CTA | — | service discount (~50% mark) |
| 8 | **Mechanism chain**, each link causal | cheap debt → capex → no ROI → unwind | profits → shareholders → assets → housing → no savings → stuck |
| 9 | **Historical analogue with dates and magnitudes** | railway mania, dot-com | 1929 peak, 1930s tax rise |
| 10 | **Reduce to ONE policy trigger variable** | central-bank rate | top corporate tax rate |
| 11 | **Name the threshold and where we sit now** | above 5.5% → unwind; not there yet | when the line reverses |
| 12 | **State current position** — refuse the doom close | hyperscalers may be a near-term catch-up | "we remain long" stocks, gold, crypto |
| 13 | Name the flip condition | — | "our strategy will flip to defensive" |
| 14 | Closing CTA | book a call | service |

### The core device, and it is worth stealing

> **Reduce the macro thesis to one policy variable, one threshold, your
> current position, and the condition that would flip it.**

That single move does an enormous amount of work at once. It converts an
unfalsifiable vibe ("stocks look bubbly") into a dated, checkable claim; it
gives the viewer something to *do* — watch one number; it earns trust by
declining the doom close; and it makes the channel's next video inevitable,
because the threshold is a standing open loop across the catalogue.

It is the macro equivalent of our receipt device. We do not have one, and we
should: **every macro video names one variable, one threshold, where we sit
today, and what would change our mind.**

### Two secondary devices

- **Concept-naming for authority.** Both videos invoke a *named formal
  framework* — Gartner, Friedman — rather than a person to follow. This
  refines our entity-seeding rule (doc 30 §6): seed *concepts* as well as
  people. A named framework is citable, non-competitive, and makes the
  narrator sound like someone who reads.
- **The stated position as a trust device.** Saying what they currently hold,
  and that the bearish conditions are *not yet met*, is the single strongest
  credibility move in either script. A warning from someone who refuses to
  panic reads as analysis; the same warning from a perma-bear reads as noise.

### Where our system still wins

Both scripts carry unsourced headline constructions — a capex-to-GDP share,
a wealth-share series, a "likely" causal attribution for the Great
Depression — presented with the same confidence as the sourced figures. Our
verbatim-figure extraction and `[verify]` gate are genuinely stronger, and
that gap is the differentiator to make visible on screen.

## 5. Findings

*Pending — Run 1 in flight.*
