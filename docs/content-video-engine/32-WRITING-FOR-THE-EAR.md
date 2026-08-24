# 32 — Writing for the Ear (craft doctrine, non-YouTube)

The fundamental-craft layer under the YouTube layer. Doc 31 holds the
platform doctrine (AOY); this doc holds what broadcast journalism,
screenwriting, speechwriting, documentary narration and oral tradition
figured out *before* YouTube existed. Division of labour, per the operator:
AOY + NotebookLM harvesting covers the "YouTube sauce" — this covers the craft.

**Provenance:** distilled from operator-supplied deep research
(2026-08-24, preserved verbatim at
[docs/research/2026-08-24-writing-for-the-ear-craft-source.md](../research/2026-08-24-writing-for-the-ear-craft-source.md)).
Source quality is mixed — several citations are secondary summaries (Scribd,
Reddit, blog recaps) rather than the primary works. The core doctrines
themselves (Block/BBC broadcast rules, Humes' pauses, McKee's gap, Truby's
steps, Snyder's beat sheet, Glass's anecdote/reflection) are standard,
well-attested craft; treat the *numbers and named terms* here as sound and
the source list as pointers, not authority. §7 diffs everything against
doc 31 so only additive material carries weight.

---

## 1. Sentence mechanics for the ear

Audio is temporal, linear, ephemeral — the listener cannot backtrack. Every
rule below exists to keep working memory from overloading:

| Rule | Spoken standard | Why |
| --- | --- | --- |
| One idea per sentence | no nested clauses, no parentheticals | a missed clause can't be re-read |
| Sentence length | **15–16 words average**, varied rhythm | breath control + discrete processing units |
| Voice | active, strictly — Subject-Verb-Object | passive holds the actor in suspense |
| Attribution | **first, not trailing** — "The Fed's own data shows…" not "…, according to the Fed" | frame before assertion; trailing attribution forces retroactive re-processing |
| Word choice | concrete nouns, strong verbs, plain language | faster mental imagery |
| Ambiguity | eliminate homophones and phonetic collisions | they're invisible on the page, fatal aloud |
| Punctuation | full stops over commas/semicolons; punctuation = breath and inflection cues, not grammar | the script is a performance document |

**Terminal Stress Principle:** the ear anchors hardest to the last word
before a pause. Put the critical/surprising word at the END of the sentence;
never end on a preposition, qualifier, or subordinate clause. This is the
sentence-level twin of AOY's point-ordering rule.

**Signposting:** the listener has no headings. Explicit transitions —
where we've been, where we are, where we're going — are the audio
equivalent of chapter structure.

## 2. Delivery — strategic silence (the missing voiceover doctrine)

AOY's corpus contains no VO delivery guidance (doc 28). This is it.
Humes' three power pauses:

1. **Pre-opener pause** — silence before the first word; claims the
   acoustic space, forces attention. (Bent for YouTube: the video cannot
   open on dead air — see §7.)
2. **Pre-key pause** — a stop immediately before the reveal/thesis;
   tells the brain "process what comes next."
3. **Post-key pause** — silence immediately after the heavy point;
   lets it settle into memory before new load arrives.

**Pipeline encoding:** these are directly implementable as SSML/break tags
in ElevenLabs input and as beat gaps in the timeline — a `pre-key` pause is
a scripted mark, not a performance accident. Pauses also pair with the
savor beats: post-key silence over a bare plate IS the breathing-room dip.

## 3. Rhetorical figures — engineering acoustic memory

- **Tricolon (Rule of Three):** first item = baseline, second = pattern,
  third = completion — or *subversion* for surprise/comedy. The subverted
  third beat is the same shape as the dark-humor setup-snap in doc 31 §5.
- **Anaphora:** repeat the opening phrase across successive clauses; the
  constant opening frees the listener to process only the changing ends.
- **Phonetic anchoring:** alliteration and assonance make key phrases
  audibly distinct — use on the lines that must be remembered (the promise,
  the payoff, the receipt line).
- **The cadence wave:** longer rhythmic setup sentences building tension,
  resolved by one short declarative. Same mechanism as AOY's two-gear
  pacing, with the added instruction that the gears form a *wave*, not an
  alternation.

## 4. Macro narrative machinery (screenwriting)

- **McKee — the Expectation-Reality Gap:** tension lives exclusively in the
  gap between what the narrator/subject expects and what reality returns.
  When an action produces the expected result, momentum dies. Every turning
  point opens a gap and flips a value charge. This is the *why* under
  BUT/THEREFORE — the connector rule is the sentence-level shadow of the gap.
- **McKee — Principle of Antagonism:** the story is only as compelling as
  the forces against it — and antagonism includes systemic obstacles,
  paradoxes, and internal failures, not villains. For finance explainers
  the antagonist is usually a mechanism (incentive structure, compounding
  cost), which is exactly our claim-cluster shape.
- **McKee — archetype vs stereotype:** trendy, culture-specific formulas
  decay; a universal experience (betrayal, systemic failure, moral
  compromise) wrapped in a highly specific setting endures. The banker and
  the budtender are an archetype pair in a specific setting — keep them so.
- **Truby — seven organic steps:** Weakness/Need → Desire → Opponent →
  Plan → Battle → Self-Revelation → New Equilibrium, organized by a
  **Designing Principle** (one abstract strategy that holds the whole
  story). His **Moral Argument**: real choices are between two goods or two
  evils, never good-vs-evil — deliver theme through dilemmas, not preaching.
- **Snyder — the Midpoint:** a false peak (seems solved) or false collapse
  (hypothesis fails) at the halfway mark; stakes rise, the mode shifts from
  exploration to survival, driving toward an "all is lost" beat before
  resolution. This is the strongest known cure for act-two sag — the
  mid-video cliff in AOY's diagnostics, treated structurally instead of
  with a mini-hook patch.

## 5. The nonfiction engine (Glass / documentary)

**Anecdote ↔ Reflection alternation** (Ira Glass): the anecdote is
sequential bait — chronological action that keeps raising unresolved
questions; the reflection interrupts to answer *why this matters*. All
anecdote = shallow event list; all reflection = alienating lecture. The
alternation is the engine. AOY has no reflection engine — its loops close
on reveals, not meaning. This is the biggest single addition for us: the
reflection beat is where a finance video earns authority.

Two shapes for the whole piece:

- **Martini glass:** sharp opening anecdote → linear chronological body
  building to a crisis → widening thematic reflection and coda.
- **Kabob:** multiple discrete anecdotes skewered on one thematic thread,
  alternating anecdote → reflection → next anecdote.

**Ring composition (chiasmus):** themes introduced in the first half return
in reverse order in the second, around a central revelation. Cognitive
closure without visual aids — and it prescribes exactly what the ending
does: echo the opening image, transformed. (Our v5 hook's "single receipt"
is the natural ring anchor: open on it, close on it calculated.)

> **Independent convergence:** AOY arrives at the same place from platform
> data rather than oral tradition — their **Story Close** outro template
> (documentary register) is "return to opening theme + reflective statement
> + soft CTA woven into content" (doc 31 §8b). Two unrelated traditions
> prescribing the same ending shape is the strongest cross-validation in
> either document, and it makes the ring the default close for our format.

## 6. Audio-visual counterpoint

The narration and the visuals are two independent vectors that intersect to
create a third, unstated meaning. Narrating what the screen already shows
is tautology — the scene loses depth. The VO should supply context, motive,
or ironic contrast to the image, and let the viewer synthesize.

**Apparent tension with AOY's camera test** (every line filmable, doc 31
§4) — resolved: *filmable* ≠ *duplicated*. The camera test demands that a
line can be paired with an image; counterpoint demands the pairing not be
an echo. Our plates-as-evidence-layer doctrine already lives here: the
plate carries world and mood while the narration carries mechanism — keep
that separation deliberate, and treat any line that merely captions its
own visual as a defect.

## 7. Diff against doc 31 — what is additive

| This doc | vs AOY (doc 31) | Status |
| --- | --- | --- |
| Sentence mechanics (§1: 15–16 words, active, attribution-first, terminal stress, homophones, punctuation-as-breath) | AOY has only "short = tension, long = context" | **additive** — whole layer |
| Power pauses (§2) | absent from AOY corpus | **additive** — fills the VO hole |
| Tricolon / anaphora / phonetic anchors (§3) | absent | **additive** |
| Cadence wave (§3) | two-gear pacing | refines |
| McKee gap (§4) | BUT/THEREFORE rule | **additive depth** — the why + beat-level machinery |
| Antagonism, archetype-vs-stereotype (§4) | absent | **additive** |
| Truby steps + designing principle (§4) | connecting-thread checkpoint | **additive depth** — the thread gets a generative method, not just a check |
| Snyder midpoint (§4) | mid-video cliff diagnostic + rehooks | **additive** — structural cure vs patch |
| Anecdote↔Reflection (§5) | STR loops (reveal-driven) | **additive** — the meaning engine AOY lacks |
| Martini glass / kabob / ring (§5) | script format templates (named, not taught) | **additive** |
| A/V counterpoint (§6) | camera test | **additive + resolved tension** |
| Direct "you", signposting, varied rhythm | present in AOY | overlap — reinforcing |
| Pre-opener pause | conflicts with never-open-on-dead-air (doc 30 §7) | **bent**: no cold silence; the "pause" becomes a visual-only opening beat (plate breathes before the first word — ~0.5–0.8s, not a black hold) |

## 8. Pipeline adoption candidates

1. **Script QC additions** (join doc 31 §4's three passes): terminal-stress
   check on beat-final sentences · attribution-first sweep · tautology scan
   (any VO line that captions its own visual) · one-idea-per-sentence lint.
2. **VO pause marks:** script format gains explicit `[pre-key]` /
   `[post-key]` pause annotations → SSML breaks in TTS, beat gaps in the
   timeline. Post-key pauses land on savor beats by construction.
3. **Macro-loop encoding** (open follow-up in doc 28): when `scene_evidence_timeline.v1`
   gains macro-loop ids, model them as Glass alternation — each macro loop
   = anecdote (evidence run) + reflection (savor + meaning line) — with a
   Snyder midpoint flagged at mid-runtime.
4. **Ring check:** does the ending echo the opening image, transformed?
   One-line review question, cheap to ask of every script.
