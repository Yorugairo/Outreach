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
| 6 · animate | **Google Flow** | video mode · 9:16 · **output 1** · **duration 4 s** · model **Omni flash** |
| 7 · assemble | Flow | chain clips with the `+` → add clips → download as one file |
| 8 · voice | **ElevenLabs** | paste the script, generate, download |
| 9 · edit | **CapCut** | drag clips in order · import VO · text → **auto captions** → template "quick" · resize and position clear of the frame |

**Seven scenes × 4 s = a 30-second short.** That is the whole unit.

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

**That is a text-based character binding**, and it is more portable than Flow's own
Characters feature because it travels with the prompt to any model.

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

### Three details worth stealing outright

1. **`SUBJECT COUNT: ONE stickman only, appearing exactly once.`** A named defence against
   the duplicate-figure failure we have hit repeatedly.
2. **`CAMERA: Static hold.`** The motion is *generated*, not camera-moved. They do not ask
   the model to pan while it animates — one job per prompt.
3. **`SECONDARY MOTION` as its own field.** Prompt engineers arrived independently at
   48 §48.6's separation of primary from secondary motion. It is the same idea.

## 53.4 What this corrects in my own claims

**I said, of the Finance Theory listicle, "those are three different people — they hold
style consistency, not character consistency."** That was accurate *about that channel*,
and I then implied generation cannot hold a character. **This tutorial is the counter-
example**: it exists specifically to hold one character across every scene, and the
mechanism is a reference sheet plus a verbatim lock paragraph.

So both approaches are live, and they are different products:

| | Finance Theory listicle | this tutorial |
|---|---|---|
| character | new figure per item | **one, locked** |
| mechanism | none needed | reference sheet → CHARACTER LOCK → repeated verbatim |
| our analogue | A2a icon ring | **the answer to @Mike** |

**This is the answer to the identity problem we spent real effort on** — the re-rolls, the
character binding, the hair drift on a 6-second clip. A model sheet and a locked paragraph.

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
- **The @Mike identity problem** has a candidate solution that does not need a platform
  feature.
- **51's shorts format** gains its art pipeline. The format spec said *icons and a script*;
  this is the third piece for the illustrated variant.

**Next concrete step:** write a @Mike model sheet — the colour cartoon, navy suit, orange
tie, glasses, locs — several angles and poses on one sheet, then derive the CHARACTER LOCK
paragraph from it. That paragraph becomes a reusable asset, versioned like a plate.

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

## 53.9 Sources

`https://www.youtube.com/watch?v=qb7QSsxefZY`, watched 2026-09-04 — transcript plus 100
extracted frames. Prompt text read directly off frames 16, 30 and 44.
