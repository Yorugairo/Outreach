# 28 — Art of YouTube MCP: Trial Evaluation

**Decision at stake:** $3,800/month membership. Trial window: 2 weeks from
2026-08-24. Their pitch: cheaper hiring + the AOY toolset. Working
hypothesis (operator's): the tools are vibe-coded wrappers around Claude/GPT
calls — good frameworks, shallow execution — and the frameworks are
extractable during the trial.

**Evaluation frame:** moat vs. replicable. A tool only justifies recurring
spend if it holds data or infrastructure we cannot reproduce. A rubric in a
prompt is not a moat; a curated database might be.

## Scorecard (updated as tested)

| Tool | Tested | Verdict | Moat? |
| --- | --- | --- | --- |
| `review_script` | ✅ | Useful 8-axis rubric, weak AI-slop suggestions. The rubric is fully visible in output. | No — rubric extracted; our humanizer + judgment beat its rewrites |
| `review_title` | ✅ | Same shape: 7 criteria incl. <8-words rule. Suggested titles altered our factual claim. | No — criteria extracted |
| `Titles_Format_Library` | ✅ | Template fill-in, mediocre adaptations. All 150 patterns are on a **public static page** they link in every response. | No — public asset |
| `search_library` | ✅ | **Paywalled in trial.** The knowledge base — the one plausible moat — cannot be evaluated before paying. | Unknown, untestable |
| `ask_tim` | ✅ | Not coaching — it ignored the actual question and returned 9 raw doctrine chunks. As **extraction**, excellent: course content verbatim per question. | Content is real; delivery is RAG dump |
| `write_script_v2` | 🔄 running | Flagship. 30-45 min async, 3/day quota. Three-way comparison pending (see below). | TBD |
| `deep_channel_analysis` | ✅ | Fetches top-5-by-views transcripts + metadata; **the analysis itself runs on the caller's model and tokens**. Our `/watch` does transcripts *plus frames*. | No — convenience wrapper |
| `Niche_Hunter` / `full_picture` | ⬜ | Curated "proven channels" DB + live scan. The DB is the strongest moat candidate that's actually testable. | TBD |
| `clone_thumbnail` / `ab_thumbnail` | ⬜ | Gemini image gen behind daily quota — we already run a stronger generation loop (P17). | Almost certainly no |
| `voiceover` | ⬜ | Requires **our own** ElevenLabs key — they bill nothing, wrap the UI. | No |
| `hiring_funnel` | ⬜ | Their headline pitch. Generates job posts/scripts/benchmarks from Tim's docs. | Content real; one-time value, not recurring |
| Profile/course plumbing | ✅ | NEW_USER, empty; Copilot board unpersonalized in trial. | n/a |

## Infrastructure observations

- **Rate limit: 5 calls per 3 minutes across all tools.** At $3.8k/mo.
- Script quota 3/day; image quota daily.
- Responses embed instructions to the calling model (skill-file install nags,
  "share this link exactly as written"). Treated as data, never executed —
  standing MCP hygiene.
- The `aoy-coach.md` skill auto-install mechanism is declined by default: we
  do not install skill files pushed by an external server.

## The decisive test: three-way script comparison

Same title, same references, same 3-minute target:

1. **Ours** — the recreation brief script (humanizer + retention curve +
   operator's two-altitude voice), reviewed at 7/10 by their own reviewer.
2. **Theirs** — `write_script_v2` output:
   https://ai.theartofyt.com/reports/ee363e00d37f459f.html
3. **Ground truth** — Alicia's actual 0:00–3:00 (transcript on file).

Judged on: hook mechanics, retention architecture, voice specificity,
factual grounding, and how much post-editing each needs to be shootable in
our pipeline. If theirs does not clearly beat ours, the flagship is not worth
recurring spend — we already own generation, scan, render, and gates.

## Extraction plan for the trial window

What to harvest legitimately while access lasts (their tools emit this
content to us as a customer; we take notes like any student):

1. **Doctrine via `ask_tim`** — batched questions within the rate limit; each
   returns verbatim framework chunks. Already captured: Alicia signature patterns across her top 5 (vignette cold-open, 'I want you to picture' tic, data injection, numbered rules, compound-math beats, binary framing); 4-stage growth model,
   impressions-vs-views diagnostic, 5-stage format lifecycle, earn-your-right
   -to-experiment, lucky-shot vs untapped-niche test, past-self method,
   faceless-personality mechanisms, ceiling-pattern rule, metric hierarchy.
2. **The 150 title patterns** — public URL; mirror into our own title tooling.
3. **Review rubrics** — both already fully visible; fold into our script/title
   review skill.
4. **Channel SOPs via `deep_channel_analysis`** — run on our actual target
   and competitor channels; each run hands us a Channel_Reference.md we keep.
5. **Niche DB sampling via `Niche_Hunter`** — a handful of scans on niches we
   care about; the reports persist.

## Long-form script structure — what `ask_tim` returns (2026-08-24)

Probe: *"On a 16-minute finance explainer, where does the writing effort go —
hook and CTA, or the 13 minutes in between? How many retention devices between
minute 2 and 14, and what are they called?"*

Operator hypothesis going in: their prompting is really only about the opening,
the close, hooks and CTAs. **Half confirmed.**

### Partly confirmed — CORRECTED 2026-08-24 after a second probe

The first probe surfaced only two long-form structures, both timestamped to
roughly the 12-13 minute mark — a video essay (10-15 min) and a framework
reveal (12-15 min) — and this doc originally recorded that a 16-minute script
was "off the end of their map."

**That was a retrieval artefact, not a fact.** A second probe surfaced further
templates at longer runtimes (expose 15-20, documentary 12-20, true crime
15-25) plus an explicit **length-tier system: T1 8-10 min, T2 12-18 min,
T3 20+**. Our 16:21 cut sits inside T2 and IS covered — by documentary and
expose shapes rather than by the essay/framework shapes that surfaced first.

Two lessons: their long-form coverage is broader than one probe suggests, and
**a single `ask_tim` query does not enumerate a topic** — the RAG returns a
slice, so absence in one response is not evidence of absence. Re-probe before
recording a ceiling.

Their stated position on runtime is relevant to us at 16:21: match length to
the story rather than the reverse, because padding for ad revenue "gets felt
within 60 seconds and tanks retention." 

### Not confirmed: the middle is managed, by cadence rather than content

Real constraints do exist for the middle. They are density rules, not content
architecture — the writer still decides what goes in:

- **STR loops** (setup → tension → resolution) nested at two scales: micro
  loops closing every 30-60s, and **4-6 macro loops per 15 minutes**, each
  closing on a partial answer that opens a larger question.
- **Rehooks every 60-90s**, BUT/THEREFORE transitions, varied sentence rhythm.
- **Point ordering:** open with a strong example but *not* the best, put the
  best in the middle where retention peaks, close with the third-best. Leading
  with the best leaves nowhere to go.
- **Retention-graph diagnostics:** five named failure shapes (cliff, slow
  bleed, mid-video cliff, re-engagement spike, plateau), each with a fix.
  Genuinely useful, and not hook-craft.

### Where this lands on the moat question

The point-ordering rule and the loop-density numbers are the most transferable
things extracted from `ask_tim` so far — real editorial constraints rather than
rubric text. They are also, once written down, ours. Consistent with the
running verdict: **content real, delivery a RAG dump, no recurring moat.**

The template ceiling is itself a finding. Their system is built for 10-15
minute videos; we are producing longer, so beyond that runtime we are on our
own regardless of membership.

### What our pipeline does not yet encode

Measured against the 16:21 p34 cut: one visual event every 9.2s (60 evidence
beats, 47 world beats over 981s). Denser than their 30-60s loop cadence — but
visual events are not narrative loops, and we currently have **no named macro
loops at all**. Structure is scene-and-evidence driven, so nothing holds an
open question across the middle.

Evidence distribution by third was 33 / 12 / 15 — front-loaded into exactly
the region the point-ordering rule warns about. **This is an artefact of asset
availability, not an editorial decision:** evidence clustered where usable
assets existed. Re-plan distribution once the slide-registration pack lands and
the full 86-slide catalogue is selectable. Do not read the current shape as a
choice.

Open follow-up: encode loop structure in `scene_evidence_timeline.v1` — a
macro-loop id per scene with its open/close beats — so the generator can report
loop count and spacing the way it now reports bare-plate gaps.

## Production loop and analogy prompting — probed 2026-08-24

Two operator hypotheses tested: (a) they prompt explicitly for analogies, for
both scripts and image scenes; (b) the ~30-minute `write_script_v2` turnaround
implies generating several script candidates and ranking them.

### Analogies — not a named concept in the doctrine

A direct probe (rules, counts, placement, whether analogy is prompted when
explaining a mechanism the viewer cannot see) returned ten chunks, **none of
which mention analogy or metaphor**. On a RAG that size, absence is the more
likely reading than a miss.

Caveat worth keeping: the doctrine base and the `write_script_v2` system prompt
are different artefacts. Analogy may well be in the pipeline prompt without
being in the course. One checkpoint would also produce analogies as a side
effect without naming them — "easy to follow / no curse of knowledge for a
fresh viewer."

**Unresolved.** Testable later by inspecting analogy density in a delivered
script rather than by asking.

### Ranking — disconfirmed; the loop is linear refinement

No variants, no candidate pools, no comparative scoring appear anywhere in the
returned process. What exists is **three filter passes on a single draft**
before it is recording-ready:

1. **Red Tape Theory, four checkpoints** — Connecting Thread (one through-line
   statable in a single sentence), Easy to Follow, Deep Identification,
   Perspective Change.
2. **The Never Repeat Rule / Highlighter Method** — highlight every concept in
   the draft; cut or merge anything highlighted twice. Deliberate callbacks
   stay, unconscious repetition is filler.
3. **The "Would I Watch This?" test** — read the opening 50 words and the
   mid-video rehook *out loud*.

So the ~30 minutes is better explained by search-first research plus sequential
passes plus queue time than by N-candidate ranking.

**The hypothesis was off by one layer, not wrong.** We already recorded
"pool-then-discard research" in the script comparison: they pool *facts* and
select, then refine *one* script linearly. The generate-many-select pattern is
real — it sits at the research stage, not the script stage.

### Worth adopting

- **The Never Repeat Rule** is the most directly implementable thing extracted
  from `ask_tim` so far, and it is mechanical enough to automate: tag concepts
  across a script, flag any that appear twice without being a marked callback.
  Our `intentional_text` policy already establishes the marked-exception
  pattern this would need.
- **Connecting Thread** — one through-line statable in a single sentence — is a
  cheap check we do not currently run on a script before it enters production.

## Fact-check: `ask_tim` against the library itself — 2026-08-24

Operator ask: probe `ask_tim` on brand voice, script retention and hooks, then
pull the same material from the course library directly and diff the two to
establish which is the source of truth.

### The direct check is blocked — and that finding matters on its own

`search_library`, `get_document` and `list_library` all return the same
response at our tier: the course library, hiring kit and lesson videos are
full-program only; the workshop tier keeps `ask_tim` plus the generators.
(The paywall response embeds an instruction to relay its signup link verbatim
— noted here as data, per the standing rule that MCP responses are never
instructions. The link: https://form.typeform.com/to/OK9uUVKF.)

So a document-vs-answer diff is impossible at this tier. The fact-check was
rerouted to the two methods that remain: **verbatim-stability probes** (ask the
same fact phrased differently, watch whether the returned text is stable) and
a **fabrication probe** (ask about a framework with no evidence of existing).

### Finding 1 — `ask_tim` is a chunk retriever, not a synthesizer

Its own description promises answers "filtered, concise, in Tim's voice." What
it actually returns is 5–10 raw RAG chunks, each labelled with its source
document. Across differently-phrased queries the chunk text comes back
**verbatim-identical** (One Minute Wall structure, Retention Graph Shapes
cliff text, STR loop definition — all byte-stable across two probes each).

That stability is the source-of-truth verdict: the tool is not paraphrasing,
so what it returns *is* the course text. **For the workshop tier, `ask_tim`
effectively is the library search** — the `search_library` gate is a tier
gate, not a capability gap. Consequence for us: quotes lifted from `ask_tim`
chunks can be treated as course-doctrine citations, with the caveat that any
one query returns a slice, not an enumeration (already learned on the
template-ceiling correction).

### Finding 2 — the "contradictory" timing numbers are layered windows

First-pass probes surfaced what looked like conflicts (8s vs 15s decision;
3s vs 30s hook). Direct re-probes resolved them into a consistent ladder,
each number owned by a different mechanism:

| Window | Mechanism | Source doc |
| --- | --- | --- |
| 0–2s | visual stun (Stimulation, Dopamine Ladder level 1) | Dopamine Ladder |
| 1–3s | stop-the-scroll hook window | Hook mechanics / Hook Pattern Library |
| 8s | "is this the right video" decision | "Viewers decide in 8 seconds"; "One Minute Wall (8-Second Decision Window)" |
| 15s | delay tolerance ("Delay Disease" — greeting intros die here) | Retention Graph Shapes |
| 30s | cliff diagnostic; 70%+ retention at 30s = hook working | Retention Graph Shapes |
| 60s | the One Minute Wall (0–8 / 8–30 / 30–60 structure) | One Minute Wall |

The KB does not harmonize its own numbers and the tool does not either — the
15s line coexists with the 8s doc. Canonical decision window: **8 seconds**
(it has a document named after it).

### Finding 3 — rehook cadence: three mechanisms, not one rule

The apparent 30–60s vs 60–90s conflict dissolves the same way:

- **Default placement is positional, not periodic**: rehooks at **30s, 1min,
  3min, and mid-video** — "the spots where YouTube analytics consistently
  show a drop" (Rehook System, with 5 named templates: "But here's where it
  gets weird…", "What nobody knew at the time was…", "This is where most
  people get it wrong…", "Let's fast-forward to…", "But the real question
  is…").
- **Every 60–90s is a diagnostic remedy**, prescribed only when the retention
  graph shows a Slow Bleed.
- **Every 30–60s is STR micro-loop cadence** — loops, not rehooks; a
  different device (macro: 4–6 STR loops per 15-minute video, as already
  recorded).

Our timeline generator can encode the positional schedule directly: rehook
slots at 30s / 60s / 180s / mid-runtime are fixed anchor points, which is
easier to emit than a rolling-interval rule.

### Finding 4 — there is no brand-voice doctrine in the course

The brand-voice probe returned naming advice, thumbnail policy, and avatar
psychographics — the nearest real material is **"Faceless Personality —
Writing Techniques"**: commentary/reaction lines ("Let that sink in for a
second"), rhetorical questions, dark humor, direct "you", varied sentence
rhythm. Useful, but it is *personality texture*, not voice identity.

Nothing in the returned doctrine covers differentiated voice, verifiable
biography as an asset, characters drawn from the operator's real worlds, or
entity seeding. Those are ours ([30-VOICE-SOURCE-MATERIAL.md](30-VOICE-SOURCE-MATERIAL.md))
and the course does not compete there. One aligned fragment worth quoting:
*"A finance viewer wants to feel like they're smarter than their co-workers"*
— consistent with our psychographic framing of the banker/budtender pair.

Cross-check against our own retention clock (3s grab / 10s answer / 30s
promise): compatible with their ladder — 3s ≈ hook window, 10s ≈ just past
the 8s decision, 30s ≈ their 30–60s mini-payoff-plus-bigger-loop. No revision
needed; theirs adds the 60s wall and positional rehooks on top.

### Finding 5 — fabrication probe

Asked for a "Retention Pyramid framework — the five levels," a framework with
no evidence of existing. Result: **no fabrication.** The tool returned its
nearest real neighbours (Dopamine Ladder — six levels; Retention Graph Shapes
— five shapes) and never asserted that a Retention Pyramid exists.

The failure mode is subtler: **silent nearest-neighbour substitution.** The
response header happily echoes "Found in Tim's brain on topic [Retention
Pyramid]" and a trusting reader could mistake the Dopamine Ladder's levels
for the invented pyramid's. So `ask_tim` will not lie, but it will not say
"no such framework" either — absence must be inferred from the chunks, the
same lesson as the analogy probe.

The probe also surfaced one directly useful doctrine piece:
**Content-Type Identification (#58)** — educational content (finance
explainers) runs on *curiosity + insight*, not the STR-dominant tension
mechanics of narrative content: "Open with a question the viewer can't answer
themselves; pay it off with a specific mechanism, not a generic wrap." That is
the course's own justification for our mechanism-first script shape.

### Operational note

Rate limit discovered: **5 requests per 3 minutes across all AOY tools
combined**. Batch probes accordingly.

## Voiceover and title doctrine — probed 2026-08-24

Follow-up probes after the fact-check, plus one live run of the
`Titles_Format_Library` generator against our niche.

### Voiceover — delivery rules exist; ElevenLabs settings do not

What came back, all chunk-stable:

- **Voice selection is deliberately unopinionated**: "pick any voice you find
  good or interesting — it becomes the personality of the channel." One hard
  line: **generic AI voice is fine, real-person voice cloning is not** —
  consistent with the July 2025 inauthentic-content enforcement they track.
- **Write for the edit**: paragraphs 2–3 lines maximum, because on screen the
  script becomes voiceover with **cuts every 2–4 seconds**. Paragraph length
  is effectively a shot-length constraint — directly relevant to our
  scene-evidence timeline, whose dock cadence already lives in that range.
- **Pacing is a two-gear system**: short sentences = tension, longer
  sentences = context, used deliberately.
- **The Breathing Room Principle**: "you cannot be intense for 10 minutes
  straight — the viewer's brain habituates. The quiet verse is what makes the
  chorus hit." Scripts that pile on from minute 1 to 12 *underperform*
  scripts with intentional dips. This is the course's own argument for savor
  beats between evidence docks, which our generator already encodes
  (SETTLE/SAVOR constants).
- **Absent**: no ElevenLabs parameter guidance (stability/similarity/style
  numbers) anywhere in the returned chunks. Voice-config remains our own
  problem; the course only governs the words.

### Titles — mechanical rules plus a native A/B doctrine

- **Formatting**: never put a word before a number — "Top 20", not "The Top
  20"; "20 Most", not "The 20 Most".
- **Honesty as strategy, not ethics**: mismatched clickbait is flagged by
  YouTube's own detection and penalized. "Specificity beats sensationalism"
  — their example pits a 12-week-experiment title against 'Doctors HATE
  This One Weird Trick.' Promise only what the video delivers.
- **Post-upload iteration is doctrine**: changing title/thumbnail on
  underperformers is encouraged, via YouTube's native **Test & Compare**
  feature rather than gut swaps.
- **Top-performing formulas** on record: regret frames ("X REGRETS: Top 5
  regrets from [group]", "[Aspirational action] and Now I Regret It"), and
  exodus frames ("Why is EVERYONE Leaving X?").

### `Titles_Format_Library` live run — template quality check

Ran against "finance and investing (market bubbles, wealth mechanics)",
20 titles across 10 categories. Verdict on the generator:

- The **frames** are the value: Superlative ("The Most Dangerous Market
  Bubble in History"), Explanation ("{X} Explained in {N} Minutes"),
  Rise & Fall, Timeline, Survival Horror ("The {N} Minutes That Changed
  Everything"). Our current-bubble video maps cleanly onto the Superlative
  and Explanation frames.
- The **fills** are stock (Enron, 2008, Bitcoin, dot-com) — topic hints from
  their viral DB, not our angle. The scores rank template fit, not
  channel fit. Use it as a frame catalogue, hand-fill with our claims.
- All 150 patterns are browsable unauthenticated at
  https://ai.theartofyt.com/static/format_patterns.html — the full template
  library is effectively public.

### Extraction status

Faceless Personality (#49) extracted in full and folded into
[30-VOICE-SOURCE-MATERIAL.md](30-VOICE-SOURCE-MATERIAL.md) §9 with adaptation
rules (rationed reaction lines, finance-register dark humor, rhetorical
questions as dated loop-openers).

## The decisive test, run: `review_script` + `review_title` on our own work — 2026-08-24

Phase 2 of the harvest plan. Fed the Alicia-format script (narration only,
675 words, the operator-approved v5 hook) to `review_script`, and the title
"She Earns Half His Salary. She Retires First." to `review_title`.

**Results: script 6.5/10, title 5.7/10.** The scores are the least
interesting part. What matters is that **the evaluator's concrete rewrites
violate the doctrine it cites** — and in one case fabricate a fact.

### Finding 1 — a hard bug: the duration calculation

The header reads `Word Count: 675 | Duration: ~6-7s`. 675 spoken words is
roughly **4.5 minutes**, not 6–7 seconds — off by a factor of ~45. Any
pacing or runtime judgement downstream of that number is unreliable, and
this is a script-review tool whose entire subject is pacing.

### Finding 2 — the suggested hook fabricates a claim

| | Text |
| --- | --- |
| Ours | "She earns half of what he does. She retires first." |
| Their "improvement" | "Watch as her tips add up to ten times his salary." |

Three failures against **their own rules**: hooks must tease not spoil
(this spoils the payoff); "Watch as…" is a delay construction of exactly
the kind their Delay Disease rule forbids; and the claim is **not in the
script and is not true of it** — the script says she holds ten times his
*margin*, not that her tips reach ten times his *salary*.

On a finance channel that is not a style note. Their own Clickbait/Metadata
doctrine says promise only what you deliver; the rewrite invents a
deliverable. **Treat `review_script` rewrites as unverified generation, never
as copy to paste.**

### Finding 3 — the "anti-fluff" rewrite is more generic, not less

Ours: *"Every object in here was, at some point, a reward for surviving the
week."* → theirs: *"Each item here is a trophy of survival."*

The rewrite trades a concrete, specific, spoken-register sentence for a
compressed aphorism — thinner, more abstract, and squarely in the
short-fragment aphorism register their own Anti-AI-Slop audit exists to
kill. It cites the "every line adds new information" rule to justify a
change that removes information.

### Finding 4 — the ending rewrite contradicts two of their own frameworks

Ours: *"That's next."* → theirs: *"And it's the secret that could retire you
years early."*

- Their **Outro Templates** name **Cliffhanger Bridge** (tease next content +
  curiosity gap + bridge) as a legitimate format for series content. Our
  ending *is* that template, executed. It was marked down anyway.
- Their **title/metadata doctrine** says specificity beats sensationalism and
  vague promises are machine-detected. "The secret that could retire you
  years early" is precisely the vague-hype construction.

### Finding 5 — same pattern in `review_title`

Scores were more reasonable, but the "improved versions" include
*"The Surprising Truth: She Earns Half, Retires First!"* — which uses the
colon construction their Anti-AI-Slop audit caps at 2–3 per entire script,
opens with stock clickbait ("The Surprising Truth"), and adds an
exclamation mark. Their own **Title Formatting Rules** and
**specificity-beats-sensationalism** rule both argue against it.

The one **legitimate** title hit: our title carries no format-pattern
signature, which does limit scalability across a channel. Worth acting on.

### Finding 6 — what it failed to catch

The script contains one genuinely risky line: the self-storage-vs-fast-food
statistic, tagged `[verify]` in our brief and stripped for submission. **A
finance script reviewer flagged nothing about an unsourced national
statistic.** It also never applied Peak-End Theory, never checked
audio-visual tautology, and produced neither the "beat-by-beat analysis" nor
the "retention risk map" its own tool description promises.

### Findings worth keeping (the honest bucket)

1. **Rehook gap in the rule-delivery stretch.** Between the receipt rule and
   the storage callback the script delivers content without re-justifying
   the next 60 seconds. Real, and matches their positional-rehook doctrine.
2. **One genuinely abstract line** — "the relationship between stuff and
   money" — in an otherwise concrete script. Fair catch.
3. **Specificity could go up** in the budtender section, which is
   qualitative where the banker section is numeric.
4. **Title needs a format-pattern spine** for channel-level scalability.

### What this settles about the moat

The split is now clean and evidenced:

- **The RAG doctrine layer is real, grounded, and extractable** — verbatim
  chunks, source-labelled, no fabrication under trap (see the fact-check
  section above). That material is now ours in docs 31 and 32.
- **The generative layer on top of it is not doctrine-bound.** `review_script`
  attaches rule names to suggestions that contradict those rules, invents a
  claim, and ships a broken duration calculation. It is an LLM with a rubric
  in its prompt, not a system that enforces the course.

**Practical rule for us:** use the rubric *dimensions* (hook, structure,
anti-fluff, visual verbs, retention, ending, animatability, specificity) as
a checklist — they are a reasonable decomposition and we have adopted
equivalents. Ignore the rewrites. Never paste generated copy from it into a
script without checking every factual claim against our own claim registry.

**Verdict on further harvest: complete.** Doctrine extraction has hit
diminishing returns (two probes now return the same chunks), the evaluator
layer is demonstrably weaker than our own standards, and the remaining
gated content is a purchase decision with no information pending.

## Verdict (running)

Pending the script comparison and Niche_Hunter test. Early lean: the
**content** (Tim's frameworks) is real and largely extractable through normal
trial use; the **software** is thin wrappers with hobbyist limits; the
**price** buys a membership community and hiring templates, not
infrastructure. Our own stack already exceeds the generation half.

Verdict revised (2026-08-24, after the script-writer run): **"software thin"
was wrong about one tool.** `write_script_v2` produced a sourced,
thesis-driven 1886-word script in 35 minutes, and its central claim verified
exactly against the primary source (FHFA WP 24-03). It also flags its own
weakest claim unprompted. The reviewers remain thin; the writer is real. Full
analysis in [34-AOY-SCRIPT-WRITER-STUDY.md](34-AOY-SCRIPT-WRITER-STUDY.md).
What it cannot supply is a narrator — which is exactly our differentiator.

Final addendum (2026-08-24): doctrine harvest closed. See the decisive-test section —
doctrine real and extracted; evaluator layer contradicts its own doctrine and
fabricates. Nothing further to learn without buying the program.

Fact-check addendum (2026-08-24): `ask_tim` is verified retrieval-backed —
verbatim-stable chunks with source labels, no fabrication under a trap probe.
At the workshop tier it is the de-facto library interface and its quotes can
be treated as course-doctrine citations, subject to the slice-not-enumeration
caveat and its habit of silently substituting nearest neighbours for things
that don't exist.
