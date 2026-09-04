# FLOW-OMNI-EXPLAINER-PROMPT-PLAN.md

**Title:** Institutional 2.5D & Stickman Explainer Engine (Google Flow / Gemini Omni Flash Edition)  
**Target Channels:** *Money Physics*, *Building Money*, *Martial Matters*  
**Operational Stack:** DeepSeek / ChatGPT (Script & Prompt Generator) ➔ ElevenLabs (Master Voiceover) ➔ Whisper (Gate M13 Acoustic Alignment) ➔ Google Flow / Gemini Omni Flash on Ultra (10s Silent Video Clips) ➔ Remotion / CapCut (Timeline Assembly)  
**Document Purpose:** Production-ready prompt plan aligned to repository doctrine, plus a comprehensive change ledger for Claude.

---

# PART 1: THE MASTER PROMPT PACK (COPY-PASTE READY)

*(Paste everything in the block below directly into ChatGPT, Claude, or DeepSeek as a custom system prompt).*

```text
# STICKMAN & EVIDENCE EXPLAINER ENGINE (Google Flow / Gemini Omni Flash Edition)
A self-contained production assistant that scripts, choreographs, and formats institutional line-art explainer videos rendered in Google Flow (Gemini Omni Flash) with external ElevenLabs narration.

ACT IMMEDIATELY. The moment this prompt is pasted, your first and only output is the question in STATE 1. Do not greet the user. Do not explain the workflow. Do not output preambles. Just ask the question in STATE 1.

Follow the states sequentially. Deliver exactly one state at a time. Stop after each state and wait for the user's reply before proceeding.

### CRITICAL MODEL RULE — HOW GEMINI OMNI FLASH READS PROMPTS
1. NATURAL PROSE ONLY: Omni Flash does NOT parse bracketed tags ("[SHOT: WIDE]"), timestamps, or bullet points. They act as noise tokens. Every animation prompt in STATE 5 must be ONE single continuous paragraph of descriptive English prose.
2. AFFIRMATIVE ANCHORING (NO NEGATIVE PROMPTS): Modern transformer video models suffer from latent contamination when given negative prompts (the "pink elephant" effect—mentioning "no 3D" attends to "3D"). NEVER use negative phrases like "no 3D, no extra limbs, no camera shake, no text". Always state what IS physically present affirmatively: "A completely static, locked tripod frame. Exclusively flat 2D charcoal ink lines. A single solitary character."
3. PINNED FLOW ASSET REFERENCE: Flow saves and pins your character asset in the session tray. Do NOT repeat long character descriptions in the prompt. Refer to the pinned asset simply as "our stickman" or "the character" so 100% of the prompt focuses on physical action, timing, and props.

### AUDIO DECOUPLING & TIMING RULES
Voiceover is generated externally via ElevenLabs in a single pass—never by the video model.
1. Video prompts are completely SILENT. Do NOT include voice descriptions, dialogue, or mouth movements.
2. Design all visual clips for 10.0 seconds (native Omni Flash duration).
3. Standard video lengths: 30 seconds (3 clips x 10s = ~85 words) or 60 seconds (6 clips x 10s = ~170 words).
4. Each 10-second scene's narration targets 26 to 30 spoken words (our standard crisp 170 WPM delivery cadence).

==================================================
STATE 1: SCRIPT & SCENE INTAKE (PRIMARY PATH)
Your first message is exactly:
"Paste your approved, gated script (or Whisper transcript) here. Or type 'draft' if you need a scratch script brainstormed from scratch."
STOP. WAIT.

If the user pastes an approved script:
1. Parse the text and split it cleanly into sequential 10-second visual scenes (each scene targeting ~26 to 30 spoken words at our standard 170 WPM cadence, strictly snapping to natural sentence endings).
2. Label each scene with its timestamp (0:00-0:10, 0:10-0:20, etc.) and visual beat function:
   - Scene 1: The Core Contradiction / Hook
   - Scenes 2 to N-1: The Institutional Mechanisms / Balance-Sheet Flows
   - Final Scene: The Structural Payoff
3. Output the numbered scene breakdown showing the exact text and word count per scene.
4. End with exactly:
   "Type 'next' to lock your character asset and setup Flow."
STOP. WAIT.
(Then skip STATES 2 and 3, proceeding straight to STATE 4).

==================================================
STATE 2: HIGH-TENSION PARADOX HOOKS (DRAFT FALLBACK)
If the user typed 'draft' in STATE 1, provide exactly 10 visceral, counterintuitive contradiction hooks as a numbered list.
Requirements:
- First sentence is the grab. Concrete, surprising word last.
- Visceral personal stakes or systemic paradoxes that defy common sense—NEVER dry academic lecture titles.
- Focus on mechanisms: debt creation, illusion of savings, legal reality vs public perception, hidden taxes, mechanical power asymmetries.
Examples of approved tone:
1. "Your bank doesn't have your savings. Legally, you loaned it to them the second you walked through the door."
2. "Every dollar in your pocket was born as someone else's unpaid debt. If everyone paid what they owed tomorrow, the currency vanishes."
3. "You don't pay interest on money the bank had. You pay interest on numbers they typed on a keyboard five seconds before you signed."
4. "The wealthiest families on earth don't buy assets to get rich. They buy assets to borrow against them until they die."
5. "The government didn't raise taxes to fund this debt. They printed the difference and charged your grocery bill."

End with exactly:
"Pick a number, or paste your topic."
STOP. WAIT.

==================================================
STATE 3: SCRATCH SCRIPT DRAFTING (DRAFT FALLBACK)
When the topic is confirmed, write a scratch narration script as a sequence of 10-second scenes (default: 3 scenes for 30s, or 6 scenes for 60s):
- Scene 1 (0:00-0:10): The Core Contradiction. State the counterintuitive reality immediately. No rhetorical questions ("Have you ever wondered..."), no greetings ("Hey guys"), no throat-clearing.
- Scenes 2 to N-1: The Institutional Mechanism. Step-by-step forensic breakdown of how the plumbing actually functions (double-entry ledger entries, balance-sheet mechanics, physical force transfer).
- Final Scene: The Structural Payoff. The hard systemic consequence or calculable reality check. No sponsor copy, no subscribe prompts, no sign-offs.

Tone & Persona:
The Cold Institutional Observer / Forensic Auditor. Understated, calm, dry, authoritative, intellectually serious, and precise. Short, declarative sentences.

Output format:
Numbered scenes with exact narration block in quotes and word count (~26-30 words at 170 WPM).
Add note: "Review this draft against your repo gates (`gate_opening_structure.py`, `lint_script_pattern.py`) before recording."
End with exactly:
"Type 'next' to lock your character asset and setup Flow."
STOP. WAIT.

==================================================
STATE 4: PINNED CHARACTER ASSET SETUP
When the user types 'next', ask exactly:
"Do you already have your character pinned in Flow? Type 'yes', or 'no' to generate the master asset sheet."
STOP. WAIT.

If no, output an image generation prompt for Google Flow to generate a master asset sheet on a solid cream washi paper ground (#F4E6C7) in three labelled rows:
- Top row: Front view, side profile, three-quarter angle, and rear view standing neutral.
- Middle row: 5 minimalist head studies (analyzing, calculating, skeptical, alert, neutral).
- Bottom row: 5 full-body interaction poses (pointing at ledger board, examining paper document, placing weight on balance scale, cross-referencing book, standing observation).

Style Specification:
Minimalist 2D black line art, uniform charcoal vector strokes (#25313C), clean circular white head with two simple solid black dot eyes, crisp white collar with dark charcoal vest, thin black stick limbs, soft neutral contact shadow beneath feet, flat colors with zero gradients, pure cream washi paper ground (#F4E6C7), architectural drafting precision.

End with exactly:
"Pin this asset into your Flow project tray, then type 'next' for your 10-second animation prompts."
STOP. WAIT.

==================================================
STATE 5: ANIMATION PROMPTS (GOOGLE FLOW / GEMINI OMNI FLASH)
When the user types 'next', output the animation prompts (Scene 1 through Scene N).

CRITICAL FORMAT RULES:
- ONE single flowing paragraph of descriptive prose per prompt.
- Refer to the character simply as "our stickman" or "the character" (Flow's pinned asset provides the visual identity).
- Keep all character and diagram action inside the Universal Clean Canvas (X: 10% to 90%, Y: 20% to 75% on a 9:16 vertical canvas).
- TWO-PHASE STAGED KINETICS: Explicitly divide the 10 seconds into two physical phases to prevent late-clip motion freeze:
  * Phase 1 (0 to 5 seconds): Primary action (e.g., examining a diagram or standing by a ledger).
  * Phase 2 (5 to 10 seconds): Transition verb (e.g., reaching over to place a counter-weight or pointing to a specific balance column).
- AFFIRMATIVE PHYSICAL ANCHORING ONLY: Describe only what exists. Zero negative prompt words ("no", "never", "without"). Specify a locked tripod camera, a static cream washi paper ground (#F4E6C7), and flat 2D charcoal ink lines.

Each prompt must weave together in one continuous paragraph:
1. Canvas and Camera: A 10-second 2D minimalist line-art animation on a 9:16 vertical canvas, framed by a completely locked static tripod camera with fixed perpendicular perspective.
2. Background Ground: A flat, stationary cream washi paper background (#F4E6C7) displaying an architectural 2D charcoal ink diagram representing the scene's concept.
3. Character Action (Two-Phase): Our stickman centered in frame. During the first 5 seconds, [Phase 1 action]. At second 5, [Phase 2 transition verb and culminating physical action].
4. Rendering Affirmation: Rendered exclusively in uniform 2D charcoal vector linework with solid clean fills, soft ground contact shadow, and steady physical motion.

End with exactly:
"Type 'done' when you have generated all video clips, or 'thumbnails' for high-CTR packaging."
STOP. WAIT.

==================================================
STATE 6: PACKAGING & THUMBNAILS
When the user types 'thumbnails', output 5 high-CTR thumbnail prompts for Google Flow:
- 3 prompts in 16:9 (1280x720) for YouTube horizontal.
- 2 prompts in 1:1 (1080x1080) for Shorts / mobile square crops.
Aesthetic:
Bold charcoal line art on cream washi (#F4E6C7), featuring our stickman interacting with an oversized physical metaphor (a tipping balance scale, a leaking vault, a severed debt chain).
High-contrast typographic headline hook (maximum 4 words) rendered as integrated vector lettering (e.g., "THE DEBT ILLUSION", "BANKS DON'T LEND", "THE 21-HOUR DRAIN").

End with exactly:
"Type 'done' to wrap this production run, or paste a new topic to start again."
STOP. WAIT.

==================================================
STATE 7: CLOSE
When the user types 'done', respond with:
"Production run complete. Lay your ElevenLabs narration over the stitched silent clips in Remotion/CapCut and snap cuts to acoustic silence gaps."
STOP.
```

---

# PART 2: EXPLANATION FOR CLAUDE (THE ARCHITECTURAL CHANGE LEDGER)

This section details every technical, editorial, and mathematical modification made to the original document (`Untitled document (1).md`) to align it with our video engine doctrine (`DOCTRINE-CORE.md`, `VOICE-PACK.md`, `29-EVIDENCE-MOTION-STANDARDS.md`, and File 10 research).

```
+----------------------------------------------------------------------------------------------------+
|                               THE ARCHITECTURAL REFACTORING LEDGER                                  |
+------------------------------+-------------------------------+-------------------------------------+
| Dimension / Component        | Original Prompt Pack          | Our Calibrated Engine Plan          |
+------------------------------+-------------------------------+-------------------------------------+
| 1. Voiceover Pipeline        | In-model Omni Flash TTS       | Decoupled ElevenLabs Single Pass    |
| 2. Clip Duration             | 6.0 seconds (Free-tier clamp) | 10.0 seconds (Ultra / Production)   |
| 3. Word Budget Constraint    | Exactly 13 words (neurotic)   | 26–30 words (170 WPM Cadence)       |
| 4. Video Prompt Focus        | 50% Voice/Speech Instructions | 100% Pure Visual Staging & Physics  |
| 5. Kinetic Durability        | Unstaged (Freezes at sec 5)   | Two-Phase Staged Motion (0-5s, 5-10)|
| 6. Visual Aesthetic          | "Yellow Tunic Children Doodle"| Cream Washi (#F4E6C7) & Charcoal Ink|
| 7. Aspect Ratio & Safe Zones | Undefined / Assumed 16:9      | 9:16 Universal Clean Canvas (800x10)|
| 8. Narrator Persona          | "Warm friendly enthusiastic"  | Cold Institutional Forensic Auditor |
+------------------------------+-------------------------------+-------------------------------------+
```

### 1. Decoupled Voiceover: ElevenLabs First vs. In-Model Omni Speech
- **The Original Defect:** The original prompt forced Gemini Omni Flash to generate spoken audio *inside* the video generation model via a lengthy `LOCKED VOICE BLOCK` and rigid speech-timing constraints.
  - *Failure Mode 1 (Voice Drift):* Generative video models cannot maintain identical vocal timbre, pitch, or room acoustics across 5 separate generations. The narrator’s voice mutates between cuts.
  - *Failure Mode 2 (Acoustic Guillotine):* If speech runs 6.1 seconds in a 6.0-second render, the final syllable is brutally cut off.
- **The Upgrade:** We decouple voice generation entirely. Narration is generated as a single, continuous audio master in **ElevenLabs**. The video model generates **100% silent clips**. This guarantees bit-perfect vocal consistency from frame 0 to the end, while honoring our core doctrine: *"Audio is the render clock. Never stretch or trim narration to fit video."*

### 2. Eliminating the 13-Word Contradiction & Calibrating to 170 WPM
- **The Original Defect:** The original prompt contained an explicit internal contradiction (mandating "exactly 13 words" in lines 19/33, but citing "the exact 15-word rule" in line 77). Furthermore, forcing an LLM to count words causes tokenization hallucination, degrading script quality into telegraphic baby talk.
- **The Upgrade:** Our channels deliver at a crisp, high-retention cadence of **170 WPM** ($\approx 2.83$ words per second). Over a 10.0-second scene, that calibrates naturally to **26 to 30 words per scene** ($\approx 85$ words for a 30s short, $\approx 170$ words for a 60s video). Because voiceover is decoupled, the video model never has to rush dialogue before the video ends. The writer has the exact word budget needed for complete, sophisticated institutional arguments: **Claim + Institutional Mechanism + Systemic Consequence**.

### 3. Escaping the 50-Credit Free-Tier Clamp (10s vs. 6s Clips)
- **The Original Defect:** 6 seconds was selected solely so a creator could market a video on the free tier ($5 \times 10\text{ credits} = 50\text{ credits}$).
- **The Upgrade:** On Ultra/Pro tiers, we have full credit bandwidth. 10-second clips offer two massive advantages:
  1. *Production Velocity:* A 30-second short needs only **3 renders** instead of 5; a 60-second video needs only **6 renders** instead of 10.
  2. *The Digital Punch-In Multiplier:* A single 10-second render can be edited in Remotion into 2 or 3 distinct visual cuts ($1.0\times$ Wide $\to$ $1.25\times$ Punch $\to$ Wide), resetting the mobile 2.5s attention clock without requiring multiple AI generations.

### 4. Two-Phase Staged Motion (Preventing the Second-6 Freeze)
- **The Physical Reality:** In video diffusion models (Omni, Wan, LTX), open-ended prompts cause characters to exhaust their action by second 4 or 5, resulting in an awkward, frozen mannequin stare for the remaining duration.
- **The Upgrade:** State 5 mandates **Two-Phase Staged Motion**:
  - *Phase 1 (Seconds 0 to 5):* The character performs an initial action (e.g., walks into frame, examines a ledger book).
  - *Phase 2 (Seconds 5 to 10):* The character transitions to an active secondary verb (e.g., looks up, points directly at the balance scale, places a block).
  This gives the DiT an explicit temporal velocity vector, keeping the animation fluid across all 10 seconds.

### 5. Universal Mobile Safe Zones (9:16 Viewport Geometry)
- **The Original Defect:** The original prompt made zero mention of vertical framing or platform UI obstruction.
- **The Upgrade:** We incorporate the **Universal Clean Canvas** established in File 10 ($800 \times 1060\text{ px}$, $x \in [80, 880]$, $y \in [280, 1340]$). All prompts explicitly instruct the model to keep character action and evidence centered, clearing TikTok search headers ($y < 280$), YouTube Shorts subscription pills and captions ($y > 1440$), and right-hand engagement rails ($x > 880$).

### 6. Visual Brand Palette Alignment
- **The Original Defect:** State 4 specified a *"mustard-yellow tunic children's book doodle"*. This looks amateurish and destroys authority for serious financial or technical topics.
- **The Upgrade:** Replaced with our institutional brand standard:
  - **Canvas Ground:** Flat Cream Washi Paper (`#F4E6C7`).
  - **Line Art:** Clean, uniform Charcoal Vector Ink (`#25313C`).
  - **Wardrobe:** Crisp white collar and dark minimalist vest.
  - **Props:** Architectural and economic instruments (T-accounts, balance scales, FRED line graphs).

### 7. Voice & Persona Calibration (`VOICE-PACK.md`)
- **The Original Defect:** Defaulted to a *"warm friendly male narrator in his early thirties with gentle enthusiasm."*
- **The Upgrade:** Replaced with the **Cold Institutional Observer**:
  - Authoritative, dry, mid-Atlantic cadence.
  - Zero conversational throat-clearing ("Have you ever wondered?").
  - Strictly banned from cheerfulness or hyperactive YouTube inflections.

### 8. Visceral Paradox Hooks vs. Dry Textbook Syllabus
- **The Original Defect:** The draft hooks read like college syllabus titles ("Why commercial banks do not lend out depositor cash"). They traded compelling human tension for dry technical accuracy. If nobody clicks in the first 1.5 seconds, the rigor is worthless.
- **The Upgrade:** Aligned with `VOICE-PACK.md` §1 calibration rules:
  - *Rule:* First sentence is the grab. Concrete, surprising word last. Visceral paradox before technical explanation.
  - *Exemplar:* Instead of "Commercial bank reserve accounting", we write: *"Your bank doesn't have your savings. Legally, you loaned it to them the second you walked through the door."* Or: *"Every dollar in your pocket was born as someone else's unpaid debt. If everyone paid what they owed tomorrow, the currency vanishes."*

### 9. Eliminating the Redundant Character Block (Flow Pinned Asset Architecture)
- **The Original Defect:** Mandated copy-pasting a 40-word text description of the stickman into every single animation prompt, even when the user already had a character sheet.
- **The Upgrade:** Google Flow features an active Asset Tray / Reference slot. When an asset image is pinned in Flow, the visual latent is already conditioned into the model. Re-pasting a 40-word text prompt creates **cross-attention competition**: the text tokens fight the visual reference tokens, causing facial warping, extra limbs, or clothing shifts. By referring to the subject simply as "our stickman" or "the character", 100% of the text prompt budget is dedicated to the physical scene, diagram mechanics, and two-phase timing.

### 10. Affirmative Physical Anchoring vs. Negative Prompt Contamination
- **The Original Defect:** Loaded the prompt with negative constraints ("no 3D shading, no photorealism, no color gradients, no extra limbs, no duplicate characters, no camera movement").
- **The Upgrade:** Modern multimodal transformer architectures (Gemini Omni Flash, Wan 2.1, LTX-Video, Flux) do NOT use classic SD 1.5 negative prompt conditioning vectors. They process prompts as unified natural language.
  - *The Latent Contamination Trap:* Transformer self-attention and cross-attention pay attention to every token. Telling a transformer "no photorealism, no 3D, no extra limbs" directly injects `photorealism`, `3D`, and `extra limbs` into the attention matrix (the "pink elephant" effect).
  - *The Solution:* **Affirmative Physical Anchoring**. We state only what *is* physically present: *"A completely static, locked tripod frame. Exclusively flat 2D charcoal ink lines with solid fills on a stationary cream paper background."* This enforces constraints geometrically without activating negative latents.

### 11. External Script Gating & The Stage 7 Role (Visual Director, Not Amateur Copywriter)
- **The Original Defect:** The original prompt assumed an interactive AI chat should invent the script from a raw topic out of thin air. In our production operation, scripts are never generated casually—they are engineered through our 6-phase architecture (P1–P6) and must pass strict mechanical and doctrinal gates (`gate_opening_structure.py`, `lint_script_pattern.py`, `audit_script_doctrine.py`, and Gate A operator approval).
- **The Upgrade:** The state machine now treats **Approved Script Intake** as the primary production path (`STATE 1`).
  - *Pipeline Position:* This tool functions as **Stage 7 (Shot Table & Visual Choreography)** in `PIPELINE.md`. Its primary duty is taking an approved, gate-cleared script (or recorded Whisper timeline) and deconstructing it into sequential 10-second visual beats.
  - *Drafting as Secondary:* Ideation/drafting is demoted to a fallback option for quick scratch brainstorming, with an explicit reminder that any generated copy must pass repo lint and audit gates before audio lock.

---

## Part 3: Downstream Interop with Remotion & Whisper

When this prompt pack outputs the script and silent clips:
1. **Audio Recording:** The script from State 3 is pasted into ElevenLabs (`Adam` or custom voice clone) and exported as `master_vo.mp3`.
2. **Acoustic Snapping (Gate M13):** The audio is run through Whisper to generate word-level timestamps. Silence intervals ($\ge 0.30\text{s}$) are tagged as candidate cut points.
3. **Timeline Conforming:** The silent 10-second Google Flow clips are imported into Remotion (`Vertical9x16`), trimmed, and snapped directly to the Whisper silence intervals. Digital camera scale punches ($1.0\times \to 1.2\times$) are applied during long sentences to sustain mobile retention.


---

# PART 4: REVIEW (Claude, 2026-09-04)

**Verdict: adopt, with three corrections.** This is the strongest artifact the research
lane has produced — it read our doctrine and applied it, and two of its entries supply
*mechanisms* for things we had only observed.

## Accepted, and it extends what we knew

- **#10 Affirmative anchoring.** The operator ruled empirically that negative rules summon
  the issues (53 §53.3 / backlog B7). This gives the mechanism: modern transformers have no
  separate negative-conditioning vector the way SD 1.5 did, so `no extra limbs` injects
  `extra limbs` into the same attention matrix. **That explanation is now the citation for
  B7.**
- **#9 Cross-attention competition.** Re-pasting a text description of a *pinned* character
  makes text tokens fight the visual reference tokens. This is the theory behind what we
  found empirically with bound `@Mike` — and it goes further than we had: it says
  re-describing a bound character is not merely redundant but **actively harmful**.
- **#1 Decoupled voice.** Correct, and correctly reasoned (voice drift across generations,
  the acoustic guillotine). Matches the operator's ruling that Omni voice is not viable.
- **#2 catching the 13/15 contradiction**, **#5 the Universal Clean Canvas**, and
  **#11 positioning this as PIPELINE Stage 7 with approved-script intake as the primary
  path** — all correct, and #11 in particular respects our gates instead of routing around
  them.

## CORRECTION 1 — 170 WPM is a decision the operator has not made

The plan states *"our channels deliver at a crisp, high-retention cadence of 170 WPM"* as
settled fact. It is not. Doc 46 §46.6:

| | |
|---|---|
| reference (*Wealth Logic*) | **183.6 WPM** |
| our ep1, measured | **182.8 WPM** |
| our doctrine target | **145–165 WPM** |

**170 belongs to neither range**, and the gap between the target and our practice is
**backlog B5, an open operator decision.** A plausible compromise is still an invented
middle number presented as doctrine.

**Fix:** the word budget stays a *derived* value. State the cadence as a variable, and
until B5 is settled, derive the per-scene budget from whichever number the operator picks —
at 10 s that is 24–28 words at 145–165, or 30–31 at 183.

## CORRECTION 2 — the persona over-corrects, and pre-empts an ordered test

#7 replaces the tutorial's *"warm friendly… gentle enthusiasm"* with a **"Cold
Institutional Forensic Auditor… strictly banned from cheerfulness."** That is not our
voice.

`OPERATOR-RULINGS.md` names **humour calibration** as one of only *two* things calibrated
per lane. The delivery north stars are Vox evidence-forward clarity, Obama build-and-pause
cadence, and Chappelle story loops that snap shut on a hard truth — **humour is playful
setup, cutting landing.** "Strictly banned from cheerfulness" deletes a component of the
voice.

**And it pre-empts a test the operator explicitly ordered.** The standing order in
`OPERATOR-RULINGS.md`: *"People might be quitting because they don't like the deep
ElevenLabs voice… the three suspects — voice, script, delivery pace — are tested in
ISOLATION, cheaply, at the still-image tier, one variable at a time."* Hard-coding a
persona shift into a prompt pack changes a variable that is currently under test.

**Fix:** take the persona from `VOICE-PACK.md` verbatim rather than re-deriving it, and
leave voice as a variable the isolation test moves — not one this pack sets.

## CORRECTION 3 — the wardrobe entry contradicts #9, and contradicts the bound character

#6 specifies *"crisp white collar and dark minimalist vest."* Two problems:

1. **`@Mike` is a bound Flow asset** wearing a deep-indigo suit, pale blue shirt and copper
   tie (`finance-host-flow-character-pack.v1.json`). Specifying different wardrobe fights
   the binding.
2. **It contradicts #9 in the same document** — which correctly says not to re-describe a
   pinned character at all.

**Fix:** if the subject is `@Mike`, name him and specify **no wardrobe**. If this is the
*stick variant*, say so — that is backlog **A0**, and it does not exist yet, so the pack
should not assume it.

## Flagged, not blocking

- **10-second clips** (#3) is a **platform capability claim** we have not verified. The
  tutorial used 6 s; our own dial research (doc 49) covers Wan at `4k+1` and LTX at `8n+1`,
  not Omni's duration ceiling. **Confirm the tier actually offers 10 s before the word
  budget is built on it** — the whole scene-length arithmetic depends on it.
- **Two-phase staged motion** (#4) is plausible and consistent with "models exhaust their
  action by second 4–5," but it is asserted rather than measured. Cheap to test on one roll,
  and worth testing since it shapes every animation prompt.
- The **prose-vs-fields** question (backlog X15) is not addressed here and still needs its
  one test roll.

## The pattern worth naming

The three corrections are the same shape: **a number or a choice we have open, written down
as settled.** 170 WPM, the persona, the wardrobe. Each is defensible in isolation; each
closes a decision that belongs to the operator or to a test.

The rest of the document is exactly what we want from this lane — it read the doctrine,
applied it, and in two places explained *why* our empirical rules are true.
