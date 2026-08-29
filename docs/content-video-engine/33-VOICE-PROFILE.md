# 33 — Voice Profile

The reusable artefact. Scripts and work orders reference **this file by
path** instead of re-deriving voice each session. This governs how the voice
sounds; [36-WRITER-PERSONA.md](36-WRITER-PERSONA.md) governs who is speaking
— worldview, standing theses, and the persona pass for generated scripts.
Apply both.

Built by `brand-voice` from [30-VOICE-SOURCE-MATERIAL.md](30-VOICE-SOURCE-MATERIAL.md)
(operator-derived evidence: worked hook example, corrections, observed
rejections, natural cadence), constrained by
[31-FACELESS-CHANNEL-DOCTRINE.md](31-FACELESS-CHANNEL-DOCTRINE.md) and
[32-WRITING-FOR-THE-EAR.md](32-WRITING-FOR-THE-EAR.md).

Schema note: `brand-voice` ships an X/LinkedIn/Email channel block. Our
medium is spoken narration, so Channel Notes is remapped to the surfaces
that actually exist here. Everything else follows the schema.

---

```text
VOICE PROFILE
=============
Author:      Faceless finance channel — first-person narrator with a
             verifiable two-altitude biography (JPMorgan risk, dispensary
             owner, PM building with AI). Channel is faceless; the operator
             is not anonymous.
Goal:        Spoken narration for long-form finance explainers that earns
             attention on mechanism and verifiability rather than hype.
Confidence:  HIGH on what is rejected (one full worked example plus seven
             in-session rejections). MEDIUM on breadth — the corpus is one
             approved 3:00 script and one hook; widen after 3-4 more.

Rhythm
- Shot list, not paragraphs. One cut per sentence; each sentence is a
  frame someone has to render.
- Present tense, viewer-facing. "She earns half of what he does." Not
  "she earned" and not "let's consider."
- 10-15 words average, deliberately varied: short punchy for tension,
  longer breathing for context, in a wave rather than an alternation.
- Terminal stress — the surprising word lands last. "…and no floor under
  any of it." Never end on a qualifier or preposition.
- Paragraphs run 2-3 lines max; the edit cuts every 2-4 seconds and the
  script is a performance document, not prose.
- Fragments are allowed singly for impact, never stacked. Three
  short-period fragments in a row is the AI-slop tell.
- Tricolon (operator-priority device): baseline, extension, then completion
  — or SUBVERSION for the humor turn. One per thesis-grade line; the final
  triad closes every video.
- Anaphora (operator-priority device): hold the opening phrase constant so
  the listener processes only the evolving ends; run it across a video's
  progressive points, land it as the closing triad.
- Phonetic anchors: alliteration/assonance reserved for the lines that must
  be remembered — the promise, the payoff, the tell.

Compression
- Dense with concrete nouns, thin on abstraction. A suit rack, a watch
  box, a rowing machine holding up laundry — objects, not adjectives.
- Numbers are load-bearing and specific: "eighteen hundred a month for
  nine hundred square feet," "forty dollars a month." Arithmetic is shown,
  not asserted.
- Explanation is earned, not front-loaded. No context dump before
  something is working on screen.
- One abstraction per beat at most, and it must be immediately cashed out
  into an object or a number.

Question Use
- Rhetorical questions are loop-openers, and every one is a dated promise:
  ask it, and the payout is owed by a stated point ("by the end of this
  video you'll calculate yours").
- Never bait questions. Never "have you ever wondered."
- The narrator asks the viewer's question and then answers it, rather than
  quizzing the viewer.

Claim Style
- Verifiability is the differentiator, not a constraint on it. Credentials
  are stated exactly — "I worked in risk at JPMorgan," never "I traded."
  A stronger claim is never worth a small truth-bend.
- Biography arrives as the twist after the paradox, not as credentials up
  front.
- Attribution comes first, not trailing: "The Fed's own data shows…" not
  "…, according to the Fed."
- Claims are self-contained arithmetic or tagged for the research gate.
  An unsourced national statistic is a defect, not a flourish.
- Characters are people from real worlds — the banker, the budtender —
  never demographics ("someone earning $95k"). Archetype in a specific
  setting.
- One bigger adjacent authority named per video, primary source cited.
- Sharp, dry, blunt. Comfortable saying a thing is wrong. Hedges are
  marked explicitly when real ("I think", "probably"), never used to soften
  a claim the narrator actually holds.

Personality (faceless — the words carry it)
- Reaction asides in the operator's dry register: "yeah — that's the whole
  trick." Rationed. Never a stock gasp ("Absolute shocker, right?").
- Dark humor as the finance reversal — the bonus that rounds to zero after
  the lifestyle ledger — not morbid irony.
- Direct second person throughout. Write to one person, never "you guys."
- Self-correction stated plainly: give the change and the reason, don't
  perform the reversal.

Structure defaults
- Retention clock per beat: grab in the FIRST sentence (0-3s), answer by
  10s, promise the payout by 30s, repeat.
- Anecdote ↔ reflection alternation — THE engine (operator-priority,
  Glass): anecdote is chronological bait that keeps raising unresolved
  questions; reflection interrupts to say why it matters. All-anecdote =
  shallow list; all-reflection = alienating lecture. Alternate continuously.
- Ring close: the ending echoes the opening image, transformed. The
  receipt opens the video and the viewer calculates theirs at the end.
- One CTA per outro, never three, placed inside the 15-30s action window
  after the payoff.

Never
- Opening on a black screen, or on atmosphere before the grab.
- Book-intro register — expository, past tense, paragraph-shaped.
- Inflated, rounded, or unverifiable credentials.
- Generic characters where specific ones exist.
- Copying a reference channel's verbal tics ("I want you to picture…")
  while borrowing its structure.
- Production scaffolding on screen — deck names, slot indices, approval
  states.
- Padding to hit a runtime.
- Narration that captions the visual it sits on (tautology).
- Stock AI register: "not X, just Y", "no fluff", "the secret to",
  "in today's world", colon-stacking, the "Most people believe…" opener.
- Hype closers that promise what the video does not deliver.

Channel Notes
- Narration: everything above. Judge by ear against synthesized audio,
  never on the page — a line that reads well and sounds wrong is wrong.
- Titles: specificity over sensationalism; no word before a number; the
  title must be a promise the video pays. A format-pattern spine helps
  channel-level scalability — a bare clever line does not scale.
- Description / community: same claim discipline, cite primary sources,
  link the biography rather than restating it.
- Pause marks: script carries explicit [pre-key] / [post-key] annotations;
  they become TTS breaks and timeline beat gaps, not performance accidents.
  Compilation table and all synth settings: 37-TTS-DELIVERY-STANDARDS.md.
```

---

## Worked reference — the line the profile is calibrated against

Rejected (operator: *"written like the entry to a book not a youtube
video"*) versus accepted, with the rules that separate them, is preserved
in [30-VOICE-SOURCE-MATERIAL.md](30-VOICE-SOURCE-MATERIAL.md) §2. Read that
example before writing a new hook; it carries the line more reliably than
any rule list above.

## Maintenance

Widen the corpus after three or four more approved scripts and re-derive —
`Confidence` on breadth stays MEDIUM until then. When a new rejection
happens, add it to doc 30 §7 first; this profile is downstream of that
evidence, never a substitute for it.
