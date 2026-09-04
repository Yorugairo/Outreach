# 53 — The stickman lane: the workflow, read off the tutorial

Source: the explainer the operator supplied, watched 2026-09-04 (14:48, transcript +
100 frames). **This is the technique I said we did not have, and it runs on our stack.**

---

## 53.1 The workflow, end to end

| stage | tool | settings named in the video |
|---|---|---|
| 1 · interview | **ChatGPT** | one long stage-gated prompt, pasted from a Google Doc |
| 2 · character lock | ChatGPT | **upload a reference sheet image**; the model reads it and writes a textual lock |
| 3 · choose | ChatGPT | niche → aspect ratio → duration → pick from 10 generated ideas |
| 4 · script out | ChatGPT | concept · character profile · **scene-by-scene, each with an image prompt AND an animation prompt** |
| 5 · stills | **Google Flow** | agent mode OFF · image mode · 9:16 · **outputs 2** · model **Nano Banana 2** |
| 6 · animate | **Google Flow** | video mode · 9:16 · **output 1** · ~~duration 4 s~~ -> **10 s, verified native Omni length** (operator, 2026-09-04) · model **Omni flash** |
| 7 · assemble | Flow | chain clips with the `+` → add clips → download as one file |
| 8 · voice | **ElevenLabs** | paste the script, generate, download |
| 9 · edit | **CapCut** | drag clips in order · import VO · text → **auto captions** → template "quick" · resize and position clear of the frame |

~~Seven scenes x 4 s = a 30-second short.~~ **Corrected: 10 s is the verified native Omni
duration, so a 30-second short is THREE renders, not seven** - and a 60-second video is six.
That is a 2.3x cut in generation cost, before counting that a single 10-second render can be
punched into two or three timeline cuts (1.0x -> 1.25x -> wide) without another generation.

**We already hold every tool in this chain.** Flow is configured, ElevenLabs is the
YouTube voice lane, and the only unfamiliar piece is CapCut, which is doing captions and
assembly that our own player already does better.

## 53.2 The identity mechanism — this is the part that matters

The prompt's own words, from the Doc:

> *"First, upload a reference image of your stickman character. Once you upload it, I'll
> study the exact design — the proportions, line style, color, face, any clothing or
> features — and lock it in so your character stays identical across every single scene."*

The reference is a **model sheet** — the character drawn from several angles, in several
poses, with a colour swatch strip. Not a single portrait.

That gets converted to a **CHARACTER LOCK paragraph, repeated verbatim in every scene's
image prompt.** Read off the screen:

> *CHARACTER LOCK: Simple clean 2D cartoon stickman boy with a white round head outlined
> in thin black line art, two large solid black oval eyes, a tiny curved black smile,
> tousled dark-brown messy spiky hair with soft bangs, slim black stick arms and slim
> black stick legs, small black mitten-like hands, casual teenage proportions, wearing a
> medium dusty-blue short-sleeve hoodie with drawstrings and a front kangaroo pocket, dark
> blue-gray slim pants, and blue-and-white low-top sneakers with white toe caps, white
> laces, and white soles… **This is the exact same stickman character — identical design,
> do not alter or redesign.***

**That is a text-based character binding — and we already have a better one.**

**Corrected 2026-09-04 by the operator: the character lock is solved for us natively.**
`@Mike` is a bound Flow character and it is already exercised on Tokyo, in prompts for
**both stills and motion**:

- `plates/plate-01-fed-briefing-mike-v3_meta.json` — *"@Mike standing beside a wooden
  podium in a Federal Reserve press briefing room, wearing his tailored indigo suit…"*
- `omni-video/scene-01-02-red-arrow-transformation_meta.json` — *"starting on @Mike in the
  investment bank boardroom as a bold red yield arrow spikes…"*, with `bound_frame_0s`
  through `bound_frame_8s` captured as the identity evidence.

**The tutorial needs the paragraph because its audience has no character feature. We do.**
A native binding beats a described one: it carries the actual reference, not a description
of it, and it cannot drift through paraphrase.

**And re-describing a pinned character is actively harmful, not merely redundant** - from
`FLOW-OMNI-EXPLAINER-PROMPT-PLAN.md` #9: a pinned Flow asset is already conditioned into
the model as a visual latent, so re-pasting a text description creates **cross-attention
competition** - text tokens fight reference tokens, producing facial warping, extra limbs
or clothing shifts. **Refer to a bound character by name and nothing else.**

**What the text technique is still worth:** portability. If we ever generate outside Flow —
Nano Banana direct, another model, a different platform — the paragraph travels and the
`@` token does not. Keep it as the documented fallback, derived *from* the bound character
rather than instead of it.

## 53.3 The two prompt schemas

**Image prompt** — every field appears in every scene:

```
CHARACTER LOCK    the paragraph above, verbatim, unchanged
POSE & ACTION     what the figure is doing this beat
BACKGROUND        the setting, and that it stays consistent
PROPS             enumerated: "Pencil, notebook, face-down phone, desk, chair."
SUBJECT COUNT     "ONE stickman only, appearing exactly once."
COMPOSITION       "Medium shot from slightly above eye level, character centered."
ASPECT RATIO      9:16
NEGATIVE RULES    no character redesign, no duplicate characters, no extra limbs,
                  no distorted proportions, no style drift, no watermark, no text frames
```

**Animation prompt** — for the image-to-video step:

```
INPUT FRAME       this scene's generated image
MOTION            the primary action
SECONDARY MOTION  "Slight foot bounce under the desk, tiny page movement."
CAMERA            "Static hold."
SOUND DESIGN      "Faster pencil scratching, subtle chair movement, quiet room tone. NO music."
DURATION          4 seconds
ANTI-GLITCH LOCK  "Maintain the exact stickman design from the input frame in every single
                  frame — same proportions, same line style, same color, same features. No
                  morphing, no distortion, no extra limbs appearing, no face changes, no
                  style drift. Motion is smooth and continuous. Background stays consistent."
```

### What to steal — and what not to

**Take the positive fields.** They tell the model what *is* there:

1. **`SUBJECT COUNT: ONE stickman only, appearing exactly once.`** A **count**, not a
   negation — the right way to express it.
2. **`CAMERA: Static hold.`** The motion is *generated*, not camera-moved. One job per
   prompt; do not ask the model to pan while it animates.
3. **`SECONDARY MOTION` as its own field.** Prompt engineers arrived independently at
   48 §48.6's separation of primary from secondary motion.

### The animation prompt is PROSE, not fields - settled from our own artifacts

**Corrected 2026-09-04.** The schema above records the field-based animation prompt as the
thing to steal. **That was wrong, and our own working prompts already said so.**

`omni-video/scene-01-02-red-arrow-transformation_meta.json` - a prompt that produced usable
output - is **768 characters, zero newlines, and carries no field markers at all.** It opens
*"full bleed edge-to-edge 9:16 vertical. A continuous cinematic transition starting on
@Mike..."* Our plate prompts are the same shape.

| source | says | is it evidence? |
|---|---|---|
| **our own Omni prompts** | **prose, one paragraph** | **yes - it shipped** |
| `FLOW-OMNI-EXPLAINER-PROMPT-PLAN.md` | prose; bracketed tags are *"noise tokens"* | advice |
| `Untitled document (1).md` | prose; *"the single most important formatting rule"* | advice |
| the video tutorial | fields | advice |

**Backlog X15 is closed - we did not need a test roll, we needed to read our own metadata.**
I had recorded a tutorial's schema over our own working practice without checking it. The
field list is still a useful *checklist of what to cover*; it is not the format to send.

### Do NOT take the negative blocks

**Operator ruling, 2026-09-04, from observed behaviour on our own stack:**

> *"Negative rules can actually summon the issues. The models are pretty strong — we
> should trust and verify instead of try to contain, when contain means writing negative
> rules into the prompt. Better is for whichever agent is driving Google Flow to check for
> those things."*

`NEGATIVE RULES: no duplicate characters, no extra limbs, no style drift…` and the
`ANTI-GLITCH LOCK`'s *"no morphing, no distortion, no extra limbs appearing"* put those
exact tokens into the conditioning. **Naming the failure is a way of describing it.**

| | goes in the prompt | goes in the driver |
|---|---|---|
| what IS there | one figure · static camera · this pose · this prop · 9:16 | — |
| what must NOT be | — | duplicate figures · extra limbs · style drift · watermark · text |

**Why they write negatives and we should not: they have no verification step.** A human
clicking between browser tabs can only contain in advance. **We have an agent driving
Flow**, and it can look at what came back and re-roll. That is the same missing-runtime
observation as §53.8, arriving from the other direction — and it makes our prompt
*shorter* than theirs, again.

**This becomes a real job for the driver** (backlog B7): a post-generation verifier that
checks subject count, style match against the bound `@Mike`, and text/watermark presence,
and re-rolls on failure — an automated pre-filter *before* the contact sheet reaches the
operator, not a replacement for it.

**The mechanism, added 2026-09-04 from the Flow plan's #10:** modern transformer video
models have **no separate negative-conditioning vector** the way SD 1.5 did. They process
the prompt as unified natural language, so self- and cross-attention attend to every token -
`no extra limbs` injects `extra limbs` into the same attention matrix. That is the "pink
elephant" effect, and it is why the empirical ruling is true.

*Scope note: recorded as observed on our stack (Flow / Nano Banana / Omni), not as a
universal law. Models with a dedicated negative-prompt field are a different case — the
defect here is negations placed in the **positive** prompt.*

## 53.4 What this corrects in my own claims

**Two corrections, both mine.**

**First:** I said of the Finance Theory listicle *"those are three different people — style
consistency, not character consistency,"* and then implied generation cannot hold a
character at all. The first half was accurate about that channel; the generalisation was
not. This tutorial holds one character across every scene.

**Second, and larger: I then presented the lock paragraph as "the answer to the @Mike
identity problem." We had already solved that.** `@Mike` is a bound Flow character,
exercised on Tokyo across stills and motion (§53.2). I read a tutorial technique as filling
a gap that our own artifacts show was closed.

Three approaches, and ours is the strongest:

| | Finance Theory listicle | this tutorial | **ours** |
|---|---|---|---|
| character | new figure per item | one, described | **one, bound** |
| mechanism | none needed | reference sheet → paragraph → repeated verbatim | **native `@Mike` reference** |
| drift risk | n/a | paraphrase can wander | carries the reference itself |
| our use | A2a icon ring | portable fallback off-platform | **primary** |

## 53.5 What we would do differently

The workflow is sound; two stages are worse than what we already have.

| their stage | our replacement | why |
|---|---|---|
| CapCut auto-captions + a template | **our player** | word-timed captions in brand tokens, the mobile safe box (49 §49.1), and stage mode already exist. Their caption is a stock template resized by eye |
| manual clip chaining in Flow | our timeline | we assemble from a timeline, not by dragging |

And two things we would **add**, from our own doctrine, because the tutorial has neither:

- **the spine** (46 §46.4) — their sample script is seven motivational beats with no
  mechanism. Ours would be one mechanism, N instances.
- **evidence discipline** — there are no figures in their sample at all, so nothing to
  source. The moment a real number appears, our rules apply.

## 53.6 The honest read on the sample output

The 30-second demo (*"You don't need a perfect plan… you just need 5 minutes"*) is
competent and empty. It is pure motivational filler with no claim in it. **The production
technique is what is worth taking; the content model is not.**

## 53.7 What this unblocks

- **A2a′ (hero illustrations)** now has a concrete spec: a model sheet, a CHARACTER LOCK
  paragraph, and the eight-field image schema.
- ~~The @Mike identity problem~~ — **already solved** by the bound Flow character; see the
  correction in §53.2. The paragraph technique is kept only as an off-platform fallback.
- **51's shorts format** gains its art pipeline. The format spec said *icons and a script*;
  this is the third piece for the illustrated variant.

**Next concrete step:** not a model sheet — `@Mike` already binds. The useful piece is the
**eight-field image schema and the seven-field animation schema** (§53.3) as *templates our
pipeline fills*, with `@Mike` in the character slot instead of a paragraph. The fields that
earn their place are the **positive** ones — `SUBJECT COUNT`, `CAMERA: static hold`,
`SECONDARY MOTION` — none of which our current Flow prompts carry. **The negative blocks
move to the driver** (§53.3).

## 53.8 "Are they over-engineering prompts instead of learning Codex?"

Operator's hypothesis, 2026-09-04. **Half right — and the wrong half is the important one.**

### The half that is right

The **orchestration** is a program pretending to be a prompt. Stage gates ("wait for the
user's response before proceeding"), the niche → ratio → duration interview, generating ten
ideas, formatting the output into Parts 1/2/3 — all of that exists because **ChatGPT has no
state between turns and no filesystem.** The prompt has to carry the control flow because
there is nowhere else to put it.

That is exactly what a coding agent replaces. It should be a script, not a paragraph.

### The half that is wrong, and it matters more

**The `CHARACTER LOCK` paragraph is not bloat. It is state injection into a stateless
system.** The image model has no memory of scene 3 when it renders scene 4, so the
invariant must *physically travel with every request*. No amount of Codex removes that —
it makes it **generated and version-controlled instead of copy-pasted.**

Same for `NEGATIVE RULES`, `SUBJECT COUNT`, and the `ANTI-GLITCH LOCK`. Those are not
verbosity; they are the actual interface to a diffusion model.

### The reframe

> **They are not over-engineering prompts. They are hand-executing a pipeline.**

The 30-page prompt pack is a program written in English and run by a human clicking
between four browser tabs. **The prompt is fine. The runtime is missing.**

And the *length* is a symptom of that: **if you cannot diff, test or reuse a prompt,
exhaustiveness is the only reliability mechanism you have.** Thirty pages is what
correctness looks like without version control.

**We can diff, test and reuse — so our prompts should be shorter than theirs, not longer,
because the constraints live in the pipeline instead of in the text:**

| their prompt carries | our pipeline carries it as |
|---|---|
| the stage-gated interview | a CLI with arguments |
| "use the same stickman as before" | a versioned `CHARACTER LOCK` asset, injected |
| the output schema (Parts 1/2/3) | a dataclass with `to_dict()` |
| "aspect ratio MUST be 16:9" | a field in the timeline, gated by G-l |
| "at least one prop in every scene" | a validator, like `ledger_page.py`'s |
| ten idea options | a script over the topic bank |
| copy → paste → Flow → download | the Flow MCP driver we already registered |
| CapCut assembly | a timeline and our own player |

**What survives into the prompt is only what the model must see at generation time.**
Everything else is ours to hold.

### What `Prompts.txt` adds that the video did not

- **10 scenes × ~6 s for a ~59 s video** (the video used 7 × 4 s for 30 s). Two workable
  cadences.
- **"Only animate: arms, head, facial expression, or props. Body position remains mostly
  static."** A real constraint that cuts morph risk at the source — restrict what may move.
- **"At least one prop (required in every scene)."** A *mechanical forcing function for
  concreteness* — and it is `RULE-abstract-to-concrete.md` arrived at independently, by a
  prompt engineer, as a hard requirement rather than a principle. **Worth stealing as a
  validator**, not as advice.

`updated master prompt.txt` is bundle file `03`, already extracted into
`RULE-abstract-to-concrete.md`. Nothing new there.

## 53.9 A third prompt — and it contradicts §53.3

Source: `Untitled document (1).md`, the "Stickman Explainer Engine". Better engineered than
the other two, and it overturns something I recorded as a finding.

### The contradiction: Omni Flash wants prose, not fields

> *"Omni Flash does NOT understand templated prompts. It ignores or mangles section
> headers, bracketed labels, bullet lists, timestamps, and field-style formatting. Every
> animation prompt must be ONE single flowing paragraph of plain natural-language English…
> This is the single most important formatting rule in this system. Breaking it produces
> glitched output."*

**§53.3 recorded the field-based animation schema** (`INPUT FRAME` / `MOTION` /
`SECONDARY MOTION` / `CAMERA` / `SOUND DESIGN` / `ANTI-GLITCH LOCK`) as the thing to steal.
**This source says that exact format is what breaks the model** — and both tutorials use
Omni Flash.

**They genuinely conflict.** Do not adopt either on faith:

| stage | model | source A (§53.3) | source B (this one) |
|---|---|---|---|
| stills | Nano Banana 2 | fields | *(not addressed)* |
| motion | **Omni Flash** | **fields** | **one prose paragraph, no line breaks** |

**SOURCES-TO-VERIFY — one test roll settles it:** same scene, same bound `@Mike`, once as
fields and once as prose. Cheap, and it decides how every animation prompt we ever send is
shaped. **Until then, prose is the safer default** — a model that parses prose will parse
fields poorly at worst, whereas a model that mangles fields fails loudly.

### The hard production numbers

- **6-second clips, 10 credits each. 50 credits = 5 clips = one 30-second video.**
- **6 seconds holds ~13 spoken words.** Every scene's line must be *exactly* 13 — longer
  gets cut off mid-sentence before the clip ends.

~~**That is a gate, not a guideline.**~~ **Moot, corrected 2026-09-04.** With voice decoupled
to ElevenLabs, **the video model never speaks** - so there is no per-clip word constraint at
all. The budget becomes a timeline question (how much narration a clip covers), not a prompt
constraint. **Backlog X16 is withdrawn.** For the record, the original claim was checkable.
(Their own prompt contains a bug here: it says *"rewrite any line that is not exactly 15"*
two sentences after establishing 13. A prompt with no version control, per §53.8.)

### The character-sheet spec is concrete and reusable

Three labelled rows on a plain cream ground: **front, side, three-quarter and back** views
standing neutral · **five head-only expressions** — happy, neutral, surprised, worried,
angry · **five full-body poses** — waving, thinking, presenting, explaining, shrugging.

We do not need it for `@Mike` (already bound, §53.2), but it is the right shape for **any
new recurring figure**, and it is a better artifact than a single portrait.

### Voice can be generated in Omni

A **LOCKED VOICE BLOCK** — one sentence fixing apparent age, gender presentation, accent,
pitch, pace, warmth and delivery energy — copied verbatim into all five prompts, so the
narration comes out of the video model itself. **Different from source A, which used ElevenLabs.**

**Not adopted — operator, 2026-09-04: relying on Omni for voice generation is not viable.**
Our voice lane is settled: ElevenLabs for YouTube, Chirp 3 HD Charon for the
Facebook/NotebookLM lane. Recorded so a later pass does not re-propose it.

### It also violates the operator's own ruling — with a useful distinction

Every animation paragraph ends with *"no glitching, no warping, no morphing, no flickering,
no extra limbs, no duplicate characters, no on-screen text, subtitles, watermarks or logos,
and no background music."* That is exactly the pattern §53.3 rules against.

**But not all of those are the same kind of thing:**

| | example | verdict |
|---|---|---|
| **content exclusion** — something that is simply not in the scene | *no background music* · *no on-screen text* · *no watermark* | **fine.** It describes the scene's contents |
| **defect naming** — a failure mode described back to the model | *no morphing* · *no warping* · *no extra limbs* · *no duplicate characters* | **strip it.** This is what summons the issue (B7) |

**Refines B7: exclude content, do not name defects.** Defect detection moves to the driver.

## 53.10 Two Mikes, and the character pack needs upgrading

Operator, 2026-09-04:

> *"We need a 'stick figure' Mike variant + our current Mike variant, and the character
> pack needs to be upgraded to the standard we learned here."*

### The gap in what we hold

`finance-host-flow-character-pack.v1.json` is well-formed — schema, art-bible hash, rights
policy, a detailed prompt, a dedicated `negative_prompt` field (the acceptable case; the
B7 ruling is about negations in the *positive* prompt). But measured against §53.9's
standard:

| model-sheet standard | the pack today |
|---|---|
| front · side · three-quarter · **back** | `front`, `three_quarter`, `full_body` — **no side, no back** |
| **five head expressions**, named | `expression_sheet` — declared but **unenumerated** |
| **five full-body poses**, named | **absent** |
| the sheet existing as registered assets | **`reference_asset_ids: []` — empty** |

**The pack describes a character sheet that was never generated.** `render_eligible` is
`False`, correctly.

### Two variants, and what makes them one character

| | **`finance-host-v1`** — retention | **`finance-host-stick-v1`** — acquisition |
|---|---|---|
| lane | world plates, long form | shorts, listicles, thumbnails |
| detail | deep-indigo suit, pale blue shirt, copper tie, gold circuit lapel pin, brown cap-toe shoes with red-and-gold floral textile | **only what survives simplification** |
| ground | woodblock crinkle-paper | flat, high contrast, phone-legible |

> **A character's stick variant is defined by the features that survive at 5 % of the
> pixels.** For Mike that is **the locs, the glasses, the goatee, and the indigo/copper
> colour pair.** The lapel pin, the shoe textile and the suit's tailoring do not survive —
> they are retention-lane detail, and carrying them into the stick variant is what would
> make it muddy.

Both bind as Flow characters. Both are the same person; the second is the first at
acquisition abstraction (51 §51.7).

### The convergence worth noting

The model sheet's **five expressions and five poses** map directly onto the cutout rig's
`HeadSlot` / `TorsoSlot` / `HandSlot` enumerations (43 §43.6). **One artifact serves the
generative lane now and the rig later** — which is a reason to enumerate the rows
deliberately rather than take whatever a generation returns.

## 53.11 Status after the Flow plan

`briefs/FLOW-OMNI-EXPLAINER-PROMPT-PLAN.md` (2026-09-04) is the production version of this
lane, reviewed in its Part 4. What it changed here:

| this doc said | now |
|---|---|
| 4-second clips, 7 per short | **10-second clips, 3 per short** (verified) |
| field-based animation prompt | **prose, one paragraph** (X15 closed from our own metadata) |
| 13 words per clip is a gate | **moot** - decoupled voice means the model never speaks (X16 withdrawn) |
| ElevenLabs at stage 8 | **ElevenLabs first**; clips generate silent |
| CapCut assembly | **Remotion / our own player**, snapped to Whisper gaps (M13) |

**The dependency: A0 gates the plan.** It is written for the stick lane, and
`finance-host-stick-v1` does not exist yet as a bound Flow character. Everything else in it
is ready to run.

## 53.12 Sources

`https://www.youtube.com/watch?v=qb7QSsxefZY`, watched 2026-09-04 — transcript plus 100
extracted frames. Prompt text read directly off frames 16, 30 and 44.
