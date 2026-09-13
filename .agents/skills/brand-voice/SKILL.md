---
name: brand-voice
description: Build a source-derived writing style profile from real posts, essays, launch notes, docs, or site copy, then reuse that profile across content, outreach, and social workflows. Use when the user wants voice consistency without generic AI writing tropes.
---

# Brand Voice

Build a durable voice profile from real source material, then use that profile everywhere instead of re-deriving style from scratch or defaulting to generic AI copy.

## When to Activate

- the user wants content or outreach in a specific voice
- writing for X, LinkedIn, email, launch posts, threads, or product updates
- adapting a known author's tone across channels
- the existing content lane needs a reusable style system instead of one-off mimicry

## Source Priority

Use the strongest real source set available, in this order:

1. recent original X posts and threads
2. articles, essays, memos, launch notes, or newsletters
3. real outbound emails or DMs that worked
4. product docs, changelogs, README framing, and site copy

Do not use generic platform exemplars as source material.

## Collection Workflow

1. Gather 5 to 20 representative samples when available.
2. Prefer recent material over old material unless the user says the older writing is more canonical.
3. Separate "public launch voice" from "private working voice" if the source set clearly splits.
4. If live X access is available, use `x-api` to pull recent original posts before drafting.
5. If site copy matters, include the current ECC landing page and repo/plugin framing.

## What to Extract

- rhythm and sentence length
- compression vs explanation
- capitalization norms
- parenthetical use
- question frequency and purpose
- how sharply claims are made
- how often numbers, mechanisms, or receipts show up
- how transitions work
- what the author never does

## Output Contract

Produce a reusable `VOICE PROFILE` block that downstream skills can consume directly. Use the schema in [references/voice-profile-schema.md](references/voice-profile-schema.md).

Keep the profile structured and short enough to reuse in session context. The point is not literary criticism. The point is operational reuse.

## Confirmed Profiles (check FIRST, before deriving anything)

Before collecting samples or deriving a new profile, check whether a
confirmed profile already exists for the current project. If one does, load
it and use it — do not re-derive.

- **Outreach Program repo (faceless finance YouTube channel)** — canonical
  profile lives in the repo, on the content-generation branch:
  - `docs/content-video-engine/33-VOICE-PROFILE.md` — HOW the voice sounds
    (rhythm, compression, claim style, never-list, channel notes).
  - `docs/content-video-engine/36-WRITER-PERSONA.md` — WHO is speaking
    (three-altitude biography, twelve standing theses T1-T12, named
    frameworks, voice synthesis, the persona pass for generated scripts).
  - Apply BOTH. The evidence base behind them is
    `docs/content-video-engine/30-VOICE-SOURCE-MATERIAL.md`; new corrections
    land there first, then the profile is re-derived.
  - Delivery north stars: Vox evidence-forward clarity, in Obama
    build-and-pause cadence, with Chappelle story loops that snap shut on a
    hard truth. Humor is playful setup, cutting landing.
  - Operator-priority writing devices (marked session 2026-08-24): the Ira
    Glass anecdote/reflection alternation is the master engine of every
    script; tricolon (third stroke completes or subverts) and anaphora
    (constant opening, evolving ends) on thesis-grade lines;
    attribution-first is a hard gate, not a style note. Full map:
    docs/content-video-engine/patterns/FULL-VIDEO-MAP.md

## Affaan / ECC Defaults

If the user wants Affaan / ECC voice and live sources are thin, start here unless newer source material overrides it:

- direct, compressed, concrete
- specifics, mechanisms, receipts, and numbers beat adjectives
- parentheticals are for qualification, narrowing, or over-clarification
- capitalization is conventional unless there is a real reason to break it
- questions are rare and should not be used as bait
- tone can be sharp, blunt, skeptical, or dry
- transitions should feel earned, not smoothed over

## Hard Bans

Delete and rewrite any of these:

- fake curiosity hooks
- "not X, just Y"
- "no fluff"
- forced lowercase
- LinkedIn thought-leader cadence
- bait questions
- "Excited to share"
- generic founder-journey filler
- corny parentheticals

## Persistence Rules

- Reuse the latest confirmed `VOICE PROFILE` across related tasks in the same session.
- If the user asks for a durable artifact, save the profile in the requested workspace location or memory surface.
- Do not create repo-tracked files that store personal voice fingerprints unless the user explicitly asks for that.

## Downstream Use

Use this skill before or inside:

| Consumer | Installed | Medium |
|---|---|---|
| `script-editor` | yes | spoken VO for the faceless channels — **the primary consumer in this repo** |
| `content-engine` | yes | multi-channel content generation |
| `article-writing` | yes | articles, launch notes, essays |
| `crosspost` | **no** | social crossposting (ECC plugin, not installed here) |
| `lead-intelligence` | **no** | outbound (ECC plugin, not installed here) |

Plus cold or warm outbound across X, LinkedIn, and email.

If another skill already has a partial voice capture section, this skill is the canonical source of truth.

**Spoken vs written.** `script-editor` is the one consumer whose medium is
the ear, and several defaults invert there. Sentence length is **10–15 words
for speech** (15–20 is where listener comprehension drops), attribution is
**first, never trailing**, and the spread matters more than the mean. Written
lanes take the profile as-is; the spoken lane takes it through docs 32 and 37
as well. Never apply a written-prose figure to a script — that mistake put
"15–16 words" into the video docs and it survived several revisions before
anyone checked it against a speech standard.

## Money Physics — locked voice profile

Channel `@MoneyPhysicsHQ`. Operator: **Micheal Golliet ("Mike")** — the
spelling "Micheal" is canonical and operator-confirmed. Never "correct" it.

Derived from the pinned community post (`content/video_engine/
channel-assets/money-physics/`). Reuse this profile; do not re-derive.

### Positioning

The bridge between engineers and analysts. "Financial fluency, not
financial literacy." Systems thinking and bottleneck analysis — the
financial mechanics engineers don't know, the technical realities analysts
can't parse. Faceless and AI-assisted, disclosed openly, accountability
human.

Credibility altitudes, in order: the mud → JPMorgan risk → dispensary
owner → growth strategist building with AI. Never "trader".

### Rhythm

- Short declaratives against long argued sentences. Alternate deliberately.
- Em-dashes carry the turns.
- Colons introduce evidence.
- One idea per paragraph, then a break.

### Hard rules

- **`That's a thesis, not advice.`** Any claim shaped like a directive gets
  reframed as a thesis the channel will test. Education, not investment
  advice — this is a guardrail, not a disclaimer to bury.
- **Name the sources.** TrendForce, Bravos, SemiAnalysis, Cappy Army,
  Fabricated Knowledge. Cite roster names explicitly.
- **Check the quantity the line claims.** A figure is checked against what
  the sentence asserts, not the nearest counter: "people watched a chart" is
  reach across the re-makes, a different quantity from one upload's view
  counter, so calling that hook fabricated was an overcall - the operator,
  2026-08-30: *"I also don't know that the hook is completely fabricated,
  because I saw a lot of people re-making the chart."* (LEDGER `4793cf2b0b71`).
  A share that holds only for a sub-class (83% for high-current implanters)
  gets a narration qualifier, not a cut (2026-09-02, `ea50af729b58`).
- **Name the gap.** Stating what is *not* yet known is voice, not weakness:
  "That's the difference between a risk and a thesis, and I'd rather name
  the gap than paper it."
- **Invite correction.** Close on a real question, not engagement bait.
  "I'd rather be corrected here than right on my own."

### Banned in this voice

- greeting-card register ("so we can all grow together")
- unsourced claim clusters — the weakest link discredits the strongest
- advice-shaped phrasing ("the risk:reward says, tie your money to…")
- hype adjectives standing in for mechanism
- "AI made this in 30 seconds" framing — the channel's counter-position

### Signature closers

- `That's a thesis, not advice.`
- `It's not magic. It's mechanics.` — outro/brand line
- `Thanks for watching — follow for the next teardown.` — CTA. Names the
  next unit of value; never "subscribe for more content", which asks for
  the action without naming what it buys.

### Facebook dials

For post structure, length dials, and the three-module architecture, see
the **Facebook Dials** section of `article-writing`. Audio bed levels for
this channel's video lane: **24–26 LU under the VO on Facebook, 26–28 LU
on YouTube.**

**Superseded for the short 2026-09-08 (E54, `docs/portable/OPERATOR-RULINGS.md`):** "The bed stays at
−20 LU and goes no louder" - *"I'm providing more actual content depth for them so I
don't want too much musical interference."* E70 (2026-09-12) splits the VOICE by platform
again (Facebook keeps Chirp; YouTube's voice is open) and does not change the bed. The
short's bed is −20 LU and no louder (E54); a long-form level is not re-ruled - see
`docs/portable/SOUND-SOURCING.md` 'Levels'.

### Platform register: Facebook vs YouTube

Same voice, different door. Operator ruling 2026-09-02.

**YouTube is search.** The viewer arrived on purpose, typed something, and
chose a 12–20 minute deep dive. They bring context. Short-form on YouTube
is pure technical response — answer the query, assume the domain.

**Facebook is stumble-across.** Nobody went looking. No intent, no prior
context, no reason to grant patience. The post has to welcome, introduce,
and assume less — *without* getting thinner.

This is a **register** dial, not a **rigor** dial. The data density rules
in `article-writing` still apply in full. What changes:

| | YouTube | Facebook |
|---|---|---|
| Reader intent | searched for it | scrolled into it |
| Prior knowledge | assumed | assume none |
| First line | answer the query | earn the stop |
| Jargon | use it | use it *and* define it in passing |
| Register | analyst to analyst | one person to another |

**Define as you go, in-line, never in a glossary aside.** "A tool that
coats the wafer and then develops it — like film." Six words of plain
analogy buys a reader who'd otherwise scroll. The term still appears; it
just arrives with a handle on it.

**"From the neighborhood."** Mike came up out of the mud before JPMorgan.
That's the register on Facebook: direct, plain, welcoming, no hedging into
jargon to signal credentials. Warm is not soft — the numbers stay, the
claims stay sharp, the reader just gets let in instead of tested.

Failure mode to watch: an opener like "The market has decided ASML is the
chokepoint in advanced chips." Correct, dense, and a wall to anyone who
doesn't already know what ASML is. On Facebook, that reader is most of
them.

**The JPMorgan rule (operator, 2026-09-02):** *"The more simply you can
convey the complex thing, the more mastery you display."* This governs
everything below it. Jargon is not evidence of depth — it is what a
writer reaches for when they can't yet say the thing plainly. On this
channel, the simple sentence *is* the credential.

**The Dimon rule (word level):** *"Don't use a bigger word when a smaller
one is available."* Framed as an investment: the cheaper thing that does
the same job is the better buy. Every word is a purchase — pay for the
work it does, not for how it looks. The two rules stack: Dimon governs
the word, the mastery rule governs the sentence. "Utilize" → "use".
"Leverage" (verb) → "use". "Facilitate" → "help". "Approximately" →
"about". "Commence" → "start". "Sufficient" → "enough". If the small word
does the job, the big one is waste.

**Depth is not jargon.** The escalating-depth rule (warm Module 1, denser
2 and 3) is about *how much* you explain, not *how technically* you say
it. Module 3 can go deeper than Module 1 and still be in plain words.
Failure example, operator-caught 2026-09-02: "a rising r meets a flat g"
and "it's a feedback loop, and it has a sign" — shorthand that announces a
mechanism without stating it. Test: if a clever-sounding sentence can't be
restated plainer, it wasn't saying anything. Rewrite it as what the loop
*is*: "the thing making Japan's machines valuable is the thing making
Japan's spending expensive."

### Doc-29 captions on light paper (NotebookLM lane) — 2026-09-02

Doc 29 assumes dark plates: white glyphs + shadow. On cream/paper footage
that vanishes. Lane adaptation, operator-gated on legibility:
- Ink near-black `#141414`; accent woodblock red `#C8353A` (keywords:
  numbers, %, currencies, named entities). High contrast AND legible.
- **Cream outline stroke ~5px** (`-webkit-text-stroke`, paint-order stroke
  fill) plus soft cream shadow. Invisible on paper, decisive on dark or red
  art. Still transparent glyphs, no pill, no panel.
- One fixed anchor at ~64% of frame height: below NotebookLM's own diagram
  text (runs to ~63% on card scenes), above the 75% collapsed-caption line.
- 2–4 word groups from local-Whisper `words.json`, punch-in 0.3s
  `power3.out`, scale 1.14→1.0, y 12→0. Rendered in Remotion as an alpha
  layer (`--pixel-format=yuva444p10le --image-format=png`) and composited.
- NotebookLM's burnt plates are removed by cropping the bottom 16% of the
  source (plates sit at 86–94%), scaling to full width, cream-padding below.
- Ken Burns is PER SCENE with alternating direction, 1.01→1.055, one ffmpeg
  run per scene (five zoompans in one graph OOMs). A single global drift is
  NOT the standard.
