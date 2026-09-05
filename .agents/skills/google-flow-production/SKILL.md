---
name: google-flow-production
description: Production best practices, prompt engineering, character persistence, and automated scene choreography for Google Flow using Gemini Omni 1.1 Flash (video) and Nano Banana Pro (image). Tailored for token-efficient, slim-LLM video pipelines.
---

# Google Flow Production Skill: Gemini Omni 1.1 Flash & Nano Banana Pro

> **Reconciliation — 2026-09-04, read in full against the live UI the same day.** The research
> is good and most of it agrees with what we already hold. The rows below are where it does not,
> or where a number arrived without an origin. Where this note and the body disagree, this note
> wins; the body is left as delivered so the disagreement stays visible.
>
> | claim in the body | status | why |
> |---|---|---|
> | VO at **170 WPM** (~28 words / 10 s) | **corrected → ~180** (~30 words / 10 s) | 170 comes from `FLOW-OMNI-EXPLAINER-PROMPT-PLAN.md`, Gemini's own estimate; measured delivery is ep1 **182.8**, reference **183.6** (E34). |
> | "Zero negative tokens (`no`, `never`, `without`)" | **narrowed to E29** | E29 distinguishes **content exclusion** (*no background music*, fine) from **defect naming** (*no extra limbs*, strip). The body's own countermeasure table then writes *no hat, no handheld objects, zero skin pores, zero clay texture* — defect naming by another word. E29 governs. |
> | Whisper gap **≥ 0.30 s** | **still open** | 46 §46.2 and 47 (M13) hold 0.30 s/onset vs 0.45 s/midpoint unsettled; P40 T1 settles it from the data. This doc does not. |
> | `Portrait → Create Body`, "do not upload" | **SOURCES-TO-VERIFY** | not exercised today; verify when `finance-host-stick-v1` is bound. |
> | 15 credits / 10 s clip · 70 % latency cut · **~94 % typographic accuracy** · autoregressive architecture | **SOURCES-TO-VERIFY** | 10 credits/6 s is our telemetry; the rest has no source in the repo. Read the meter on the first 10 s roll. |
> | Cream `#F4E6C7` / charcoal `#25313C` monoline as *the* style | **not the directive** | those are our ledger-page tokens (29/41/48) — right for evidence pages, wrong for the host. The host's directive is the operator's phrase, *"A light application of woodblock print and vox newspaper with rich anime colors"*; the stick lane is brush-line on white (53 §53.10). Formulas take the lane's directive, not a hex monoline. |
> | Two-phase kinetics at second 5 · cowboy shot | **plausible, untested** | backlog X17 / X18 — cheap to test on one roll. |
> | 3 ingredients max, > 1024 px, pre-cropped | consistent | the driver already caps uploads at 3. |
> | prose paragraph · `@Name` with no re-description · 10 s native · silent video · Nano Banana at 0 credits | **confirmed** | X15 closed from our metadata; E29; E34; "Generating will use 0 credits" on every roll today. |
>
> **What the body does not know, because it was written from documentation and the UI moved
> the same morning:** Flow is `flow.google.com`; the `@` picker is a listbox whose search field
> steals focus — a Character is typed-to-filter, selected, then inserted with **Add to prompt**;
> a file reference is reused by filename from project assets or uploaded through the picker's
> file chooser; an uploaded reference **re-renders on the canvas as a new CDN image** that looks
> like a finished generation; x2..x4 rolls land as separate tiles. All of it is in the driver
> (`cdp-driver.mjs`) and CAPABILITIES, proven by the A0 sheets.

This skill governs best practices, prompt engineering, character persistence, frame chaining, ingredients ingestion, and multi-format (16:9 vs. 9:16) composition for **Google Flow** (`labs.google/fx/tools/flow` / `flow.google.com`), powered natively by:
1. **Gemini Omni 1.1 Flash (`gemini-omni-1.1-flash`)** — The video generation engine (native 10.0-second clips, multimodal autoregressive architecture, 70% lower latency, 50% lower credit cost than Veo).
2. **Nano Banana Pro (`gemini-3-pro-image`)** — The image generation engine (built on Gemini 3 Pro, 0 credits in Flow image mode, ~94% typographic accuracy, exact hex code role-binding, 2D vector linework).

It is specifically calibrated for **token-efficient, slim-LLM pipelines** (Claude 3.5 Haiku, Gemini Flash, GPT-4o-mini) to generate production-ready prompts with zero token waste, zero prompt drift, and 100% deterministic visual stability.

---

## 1. Production Engine Architecture & Stack

```
+───────────────────────────────────────────────────────────────────────────────────────────+
|                           GOOGLE FLOW PRODUCTION ENGINE STACK                             |
|                                                                                           |
|  [Script & Shot Table] (~180 WPM VO via ElevenLabs — Decoupled & 100% Silent Video)        |
|                                │                                                          |
|      ┌─────────────────────────┴─────────────────────────┐                                |
|      ▼                                                   ▼                                |
|  [Nano Banana Pro] (Image Mode: 0 Credits)        [Gemini Omni 1.1 Flash] (Video Mode)   |
|  - Gemini 3 Pro Multimodal Engine                 - Autoregressive Multimodal Transformer |
|  - Character Builder (Portrait + Body Sheet)      - Native 10.0s Clips @ 24 FPS (720p/4K) |
|  - Clean Prop & Background Ingredients (≥1024px)  - Two-Phase Staged Kinetics (0-5s / 5-10s) |
|  - Exact Hex Codes & ~94% Typographic Labels     - Affirmative Physical Anchoring (No Negs) |
|      │                                                   │                                |
|      └─────────────────────────┬─────────────────────────┘                                |
|                                ▼                                                          |
|  [Assembly & Post-Production] (Remotion / HyperFrames / CapCut)                           |
|  - 10s Clip Multiplier: 2-3 Digital Punch-Ins (1.0x -> 1.25x -> 1.0x every 3-4s)          |
|  - Universal Clean Canvas: X ∈ [10%, 90%], Y ∈ [20%, 75%] for Mobile UI Safe Zones        |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

### 1.1 Why Gemini Omni 1.1 Flash Over Veo
*   **Architecture:** Omni 1.1 Flash is a **Unified Multimodal Autoregressive Transformer**, not a latent diffusion transformer (DiT) with a frozen T5 text encoder like Veo. It natively reasons over visual tokens, understanding abstract 2D line art, stickmen, and diagrams without trying to turn them into photorealistic 3D humans.
*   **Speed & Latency:** 15–30 seconds per clip (70% faster than Veo’s 60–90s generation time).
*   **Credit Economics:** 10 credits per 6s / 15 credits per 10s clip at 720p x1 (50–60% cheaper than Veo 3.1).
*   **Native Duration:** Generates **10.0-second native clips**. A single 10s clip allows 2–3 digital punch-in cuts ($1.0\times \to 1.25\times \to 1.0\times$) in Remotion/CapCut, resetting viewer attention every 3–4 seconds without burning extra generation credits.
*   **Audio Decoupling Rule:** All video prompts must specify completely silent video. Generative video models hallucinate random voice timbres across seeds. Master voiceover is generated separately via ElevenLabs at **~180 WPM** (measured: ep1 182.8, reference 183.6; ~30 words per 10s clip) and cut on Whisper acoustic gaps (threshold 0.30 s vs 0.45 s still open — P40 T1).

---

## 2. Character Lifecycle & True Persistence

Character drift (facial warping, wardrobe morphing, limb count mutations) occurs when models guess anatomy from text. Flow solves this via its **dual-layer Character Profile architecture**.

```
+───────────────────────────────────────────────────────────────────────────────────────────+
|                             FLOW CHARACTER BUILDER LIFECYCLE                              |
|                                                                                           |
|  [Step 1: Text Prompt] ──> [Nano Banana Pro] ──> [Portrait Triptych] (Face / ID Lock)    |
|                                                          │                                |
|                                              [Click "Create Body"] (DO NOT UPLOAD IMAGE)  |
|                                                          │                                |
|  [Step 2: Full-Body Prompt] ───────────────────> [Nano Banana I2I]                        |
|                                                          │                                |
|                                                [Full-Body Sheet] (Anatomy & Shoes Lock)   |
|                                                          │                                |
|                                             [Save to Character Tray]                      |
|                                                          │                                |
|  [Step 3: Downstream Video] ───────────────────> Tag `@CharacterName` (Strip Adjectives) |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

### Stage 1: The Portrait Lock (`Portrait`)
Generate the initial headshot/bust. Focus exclusively on facial geometry, hair texture, skin tone, glasses, and art style.
- **Formula:**
  ```text
  Front, side, and three-quarter portrait triptych of [Character Description], rendered in [Art Style] on a solid [Background Hex Code] ground. Neutral expression, clean hairline ink boundaries, and sharp facial features.
  ```

### Stage 2: The Full-Body Lock (`Create Body`) — *No Upload Required*
Once the portrait renders, click **`Create Body`**.
> [!IMPORTANT]
> **Do NOT upload a new image.** Flow automatically pipes the latent representation of the approved portrait into Nano Banana Pro's conditioning buffer.

The prompt must fulfill the **5 Mandatory Structural Anchors**:
1. **Vertical Framing Lock:** Must explicitly begin with `"Full-body shot, head to toe, standing neutral"`. Without this, the engine defaults to a waist-up bust.
2. **Build & Proportions:** Explicit proportions (e.g., `"slender minimalist stick limbs, adult proportions, 1:7 head-to-body ratio"`).
3. **Complete Wardrobe & Explicit Footwear:** Top-to-bottom outfit declaration down to shoes and soles (e.g., `"charcoal tailored vest over white collared shirt, slim dark trousers, and matte black oxford shoes with flat soles resting firmly on the floor"`). Omitting shoes causes the model to generate random footwear and colors across video shots.
4. **Grounding & Contact Anchor:** `"Arms relaxed at sides, hands open with separated fingers, feet planted firmly on flat horizontal ground with a soft neutral contact shadow."` Prevents hands fusing into hips or floating feet.
5. **Style & Ground Continuity:** Match exact hex codes (e.g., `"uniform charcoal vector linework #25313C on flat cream washi paper ground #F4E6C7 with zero shading"`).

### Stage 3: Casting in Video Prompts (`@CharacterName`)
Once saved in the Flow project tray:
- Tag the character as `@CharacterName` (e.g., `@Mike`).
- **THE TOKEN STRIPPING PROTOCOL:** **Strip out all redundant physical adjectives.** Do NOT re-describe face, hair, glasses, or clothing in downstream video prompts.
  - ❌ *Wrong (Latent Competition $\to$ Morphing):* `"@Mike, a slender stickman with a charcoal vest and white shirt, walks forward..."`
  - ✅ *Correct (Latent Harmonized):* `"@Mike walks steadily from left to right across the frame, stopping at center to point at the chart."`

---

## 3. Nano Banana Pro Image Engineering

Nano Banana Pro (Gemini 3 Pro Image) provides studio-grade reasoning, native 2K/4K resolution, zero Flow credit cost in Image Mode, and ~94% typographic accuracy.

### 3.1 Prompt Structure: Art Direction Prose vs. Tag Soup
Tag soup degrades Gemini 3 Pro's reasoning engine. Brief the model as a technical art director using the **6-Factor Design Brief**:
1. **Subject:** Exact physical entity, posture, and anatomical constraints.
2. **Work Surface / Medium:** Definition of the physical medium (`"Flat 2D monoline vector illustration"`, `"Orthographic 2D CAD elevation"`).
3. **Composition & Framing:** Perspective (`"fixed perpendicular perspective, eye-level horizon"`), margins, and safe boundaries.
4. **Ground & Environment:** Texture, floor baseline, and exact background color.
5. **Color & Lighting:** Role-bound hex codes and flat unshaded fills.
6. **Typography & Constraints:** Quoted text strings, coordinates, and typography hierarchy.

### 3.2 Exact Color Hex Code Adherence (Role-Binding)
To prevent semantic drift, always bind hex codes to their specific physical role:
*   ❌ *Weak:* `"#F4E6C7 and #25313C, line drawing"`
*   ✅ *Role-Bound:* `"Charcoal ink linework (#25313C) rendered on a solid, untextured cream washi paper ground (#F4E6C7)"`
*   **Palette Transfer (Conversational Edit / Image-to-Image):**
    `"Change the color grading of this image to strictly adhere to this four-color palette: background ground #F4E6C7, line ink #25313C, primary accent #E05A47, secondary neutral #8C969E. Remove all other hues."`

### 3.3 Production Typography & On-Screen Text (~94% Accuracy)
1. **Always Use Double Quotes:** Every text element must be enclosed in quotation marks: `"LIQUIDITY RATIO"`.
2. **Declare Font Style & Case:** Specify font category (e.g., `"bold condensed all-caps sans-serif font"`, `"monospaced ledger typewriter font"`). All-caps is most resistant to kerning defects.
3. **Declare Anchor Coordinates:** State exact placement:
   `"Render the headline 'FEDERAL RESERVE' in bold charcoal sans-serif centered horizontally across the top 15% of the frame."`
4. **Keep Text Atomic:** For diagrams, limit callouts to 1–4 words per node.

### 3.4 Common Image Failure Modes & Countermeasures

| Failure Mode | Root Cause | Exact Prompt Countermeasure |
|---|---|---|
| **Unwanted Photorealism** | Using words like "hyper-detailed", "photorealistic", or 35mm/85mm lens terms on graphic scenes. | `"Rendered strictly as a flat 2D vector editorial drawing. Matte screenprint aesthetic, solid ink contours, zero photographic textures, zero skin pores, zero depth-of-field blur."` |
| **3D Clay / Plastic Shading** | Ambiguous cartoon tags ("cute", "smooth 3D", "animation style"). | `"Flat 2D graphic illustration, unshaded flat color fills, zero 3D rendering, zero ambient occlusion, zero clay texture, crisp hard vector edges."` |
| **Muddy Line Weights** | Unspecified stroke parameters; model blends lines with painterly shading. | `"Uniform monoline black ink contours of fixed hairline weight (#25313C). Sharp, high-contrast closed vector boundaries separating color fills from the background."` |
| **Accessory Hallucination** | Contextual bleeding (generating in a train yard adds a conductor cap). | `"Bare-headed, clean hair silhouette, no hat, no headwear, empty open hands relaxed at sides, no handheld objects, no unprompted accessories."` |

---

## 4. Video Prompt Engineering for Gemini Omni 1.1 Flash

Omni 1.1 Flash parses prompts as continuous multimodal prose paragraphs (40–90 words).

### 4.1 Rule 1: Single Continuous Prose Paragraph Only
Every prompt must be **one single continuous paragraph** of natural English prose.
*   **Strictly ban bracketed tags:** `[SHOT: WIDE]`, `[CAMERA: PAN]`, `[AUDIO: SILENT]` are treated as semantic noise tokens or rendered as literal visual artifacts.

### 4.2 Rule 2: Affirmative Physical Anchoring (Ban on Negative Prompts)
Multimodal transformers activate attention weights on every token. Telling a model *"no 3D, no extra limbs, no camera shake, no text"* activates `3D`, `extra limbs`, `camera shake`, and `text`.
*   ❌ *Negative (Summons Defects):* `"No camera shake, no panning, no 3D shading, no extra limbs, no text."`
*   ✅ *Affirmative (Locks Ground):* `"A completely stationary, locked tripod camera frame with fixed perpendicular perspective at eye level. Rendered exclusively in flat 2D uniform charcoal vector linework (#25313C) with solid clean fills on an unmoving cream paper background (#F4E6C7). A single solitary character centered in frame."`

### 4.3 Rule 3: Two-Phase Staged Kinetics (Defeating the Second-5 Freeze)
In 8s–10s clips, open-ended action prompts cause characters to finish moving by second 4 or 5, leaving them frozen like mannequins for the rest of the clip.
*   **The Protocol:** Every 10-second prompt must script an **explicit transition verb** at second 5:
    *   *Phase 1 (0 to 5s):* Initial continuous action (examining a document, standing by a balance scale).
    *   *Phase 2 (5 to 10s):* Secondary kinetic verb (reaches forward, points directly at column B, places counter-weight).

### 4.4 Rule 4: Cinematic Camera Lexicon
Use exactly one primary camera directive per prompt:
*   `Locked-off static tripod camera, fixed perpendicular perspective at eye level` (Primary anchor for diagrams/explainers).
*   `Slow, steady push-in dolly shot toward the subject, maintaining crisp perpendicular perspective` (Escalating cognitive focus).
*   `Smooth horizontal tracking shot gliding alongside @CharacterName at uniform velocity` (Lateral progression).
*   `Smooth vertical pedestal tracking shot rising steadily alongside the ascending chart` (Vertical data reveal).

---

## 5. Frames to Video & Tail-Frame Extension Chaining

Multi-scene explainers require seamless character and environmental continuity across successive 10-second clips.

```
+───────────────────────────────────────────────────────────────────────────────────────────+
|                         TAIL-FRAME EXTENSION (CHAINING) PIPELINE                          |
|                                                                                           |
|  [Clip N: Seconds 0-10] ──> [Extract Frame at t=10.0s] ──> Save as `clip_N_tail.png`     |
|                                                                     │                     |
|                                                       [Insert into Clip N+1]              |
|                                                       [Slot: "+ Add Start Frame"]         |
|                                                                     │                     |
|  [Prompt Clip N+1]: "KINETIC DELTAS ONLY" ──────────────────────────┴──> [Clip N+1]       |
|  (Never re-describe static elements already present in the start frame)                   |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

### 5.1 Tail-Frame Extraction Protocol
1.  Generate Clip $N$ (10.0 seconds) in Google Flow.
2.  Extract the exact terminal frame ($t=10.0\text{s}$):
    *   *Via Flow UI:* Click the clip card $\to$ click `"Save Frame"` on the playback scrubber at the final frame.
    *   *Via CLI / FFmpeg:*
        ```bash
        ffmpeg -sseof -0.04 -i clip_01.mp4 -update 1 -frames:v 1 clip_01_tail.png
        ```
3.  In Google Flow Video Mode for Clip $N+1$, click **`+ Add start frame`** and select `clip_01_tail.png`.

### 5.2 Kinetic-Delta-Only Prompting Rule
When an initial frame is anchored, **never re-describe what is already visible in the image**.
*   ❌ *Redundant (Causes Boundary Glitches):* `"A stickman wearing a vest stands on a cream paper background next to a balance scale. He reaches out..."` (Model tries to re-draw the scene, causing a 1-frame pop).
*   ✅ *Kinetic Delta Prompt:* `"Continuing from the starting frame, @Mike smoothly extends his right hand and places the brass coin into the right-hand dish. At second 5, the balance scale tips downward on the right, and @Mike takes one step back, resting his hands at his sides. Completely locked static camera. Completely silent video."`

---

## 6. Ingredients-to-Video Production Architecture

Omni 1.1 Flash supports multi-latent conditioning with up to **3 reference ingredients**:

| Slot | Role | Reference Asset | Prompt Binding Syntax |
|---|---|---|---|
| **Ingredient 1** | **Subject** | Pinned Character Sheet from Character Builder (`@character`) | `"@Mike [performs action]"` |
| **Ingredient 2** | **Object / Prop** | Clean isolated prop on flat ground (`@prop`) | `"interacts with @prop"` |
| **Ingredient 3** | **Environment** | Static background / world plate (`@background`) | `"against @background"` |

### 6.1 Strict Technical Pre-Flight for Ingredients
1.  **Mandatory Pre-Cropping:** All reference images must be pre-cropped to the **destination aspect ratio** (`16:9` or `9:16`) and exceed $1024\text{ px}$. Mismatched aspect ratios force the latent encoder to shear or anamorphic-stretch the subject.
2.  **Clear-Zone Margin:** Maintain a 5–10% empty border around isolated character and prop cutouts to prevent severed limbs or clipped edges in the video render.
3.  **Explicit Role Binding:** The prompt must explicitly bind the ingredients into physical interaction:
    `"@Mike picks up @prop from the desk and examines it carefully against @background. Completely locked static camera."`

---

## 7. 16:9 Landscape vs. 9:16 Vertical Mobile Architecture

### 7.1 The Universal Clean Canvas (Mobile UI Safe Zones)
Mobile UI overlays (search headers, subscription pills, description bars, right-hand engagement rails) consume up to **59.1%** of a 9:16 vertical viewport.

```
0 px ───────────────────────────────────────────────────────────── (Top of Frame)
     │  TOP UI DEAD ZONE (Y: 0 to 280 px | 14.6% of height)       │
     │  - Platform search bar, account pills, system notch, audio │
280 px ──────────────────────────────────────────────────────────── (Upper Safe Line)
     │                                                     │      │
     │  UNIVERSAL CLEAN CANVAS                             │ R    │
     │  (X: 80 to 880 px, Y: 280 to 1340 px)               │ I    │
     │  - Usable Canvas: 800 x 1060 px (40.9% frame area)  │ G    │
     │  - All character anatomy, diagrams, charts, props   │ H    │
     │    MUST reside inside this rectangle.               │ T    │
     │                                                     │      │
     │                                                     │ R    │
     │                                                     │ A    │
     │                                                     │ I    │
1340 px ───────────────────────────────────────────────────│ L    │
     │  DYNAMIC KINETIC CAPTION STRIP (Y: 1340 to 1440 px) │      │
1440 px ───────────────────────────────────────────────────┴──────│ (Lower Safe Line)
     │  BOTTOM UI DEAD ZONE (Y: 1440 to 1920 px | 25.0% of height)│ (Right 200px:
     │  - Subscribe pill, caption text, sound title, scrub bar    │  Avatar, Like,
1920 px ────────────────────────────────────────────────────────── (Bottom of Frame)
```

*   **Pixel Budget on $1080 \times 1920$ Master:**
    *   **Universal Clean Canvas:** $X \in [80, 880]\text{ px}$, $Y \in [280, 1340]\text{ px}$ ($800 \times 1060\text{ px}$).
    *   **Top Dead Zone:** $Y \in [0, 280]\text{ px}$ (14.6%).
    *   **Bottom Dead Zone:** $Y \in [1440, 1920]\text{ px}$ (25.0%).
    *   **Right Rail Dead Zone:** $X \in [880, 1080]\text{ px}$ (200px width for engagement icons).
*   **Pixel Budget on $720 \times 1280$ Native Omni 1.1 Flash Output:**
    *   **Active Clean Box:** $X \in [53, 587]\text{ px}$ ($10\% - 90\%$), $Y \in [187, 893]\text{ px}$ ($20\% - 75\%$).

### 7.2 The 3-Zone Vertical Stage
When adapting horizontal concepts to 9:16 vertical, **never use blurred-background padding** (banned slop pattern). Stack elements into three vertical tiers:
*   **Zone 1: Metric Headline / Hook ($Y: 10\%\text{--}25\%$):** Primary claim, live counter, or paradox statement.
*   **Zone 2: Core Evidence Canvas ($Y: 25\%\text{--}70\%$):** Pinned character, ledger board, chart, or balance scale.
*   **Zone 3: Kinetic Captions & Baseline ($Y: 70\%\text{--}90\%$):** Word-level captions and character floor contact.

### 7.3 Camera Distance: The Cowboy Shot "Golden Zone"
*   **Avoid Extreme Wide Shots (EWS):** In a 9:16 vertical 720p frame, an EWS scales a stickman down to $\approx 250\text{ px}$. At that resolution, $2\text{ px}$ vector limbs fall below the spatial patch downsampling threshold of the model, causing arms and legs to detach, flicker, or dissolve.
*   **Avoid Extreme Close-Ups (ECU):** Zooming into a flat 2D face forces the model to hallucinate 3D skin pores, shading, and fleshy facial features.
*   **The Cowboy Shot (Mid-thigh up, $65\%\text{--}75\%$ frame height):** The mathematically optimal framing. Places the character's head comfortably below the top dead zone ($Y: 280$), keeps hands in the active central sweet spot ($Y \in [600, 1100]$), terminates above the bottom caption zone ($Y: 1440$), and maintains full $6\text{--}12\text{ px}$ line-art integrity.

---

## 8. Slim-LLM Production Formulas & State-Machine Prompts

Slim LLMs (Claude 3.5 Haiku, Gemini Flash, GPT-4o-mini) operate best with deterministic, schema-bound generation patterns. Use these production formulas.

### Formula A: Nano Banana Pro Character Builder (`Create Body`)
```text
Full-body head-to-toe shot of our [Style Adjective] character standing in a neutral upright posture, centered horizontally on a [9:16 vertical / 16:9 horizontal] canvas. [Anatomical Build & Head Description], wearing [Upper Body Garment Description], [Lower Body Garment Description], and [Explicit Footwear with Flat Soles] resting firmly on a flat floor baseline. Arms relaxed at sides with open, clearly separated hands. Framed with generous 25% clear headroom above the head and 20% clear baseline margin below the shoes. Rendered in clean flat 2D graphic illustration on a solid [Background Hex Code] ground with uniform [Linework Hex Code] outlines, zero 3D shading, zero gradients, and a soft neutral floor contact shadow.
```

### Formula B: Nano Banana Pro Isolated Prop Ingredient (≥1024px)
```text
An isolated editorial prop plate of a [Prop Description], perfectly centered in frame on a [9:16 vertical / 16:9 horizontal] canvas. Rendered in clean 2D vector linework with [Linework Hex Code] contours and [Accent Hex Code] matte fills. The prop rests on a completely flat, solid [Background Hex Code] background with a subtle, tight contact shadow directly underneath its base. Pure negative space surrounding the object on all four sides. Zero perspective tilt, zero background environment, zero gradients, zero 3D ambient occlusion.
```

### Formula C: Gemini Omni 1.1 Flash 10-Second Scene Prompt
```text
A 10-second 2D minimalist line-art animation on a [9:16 vertical / 16:9 horizontal] canvas, framed by a completely locked static tripod camera with fixed perpendicular perspective at eye level. A stationary [Background Hex Code] background displays a centered [Diagram / Evidence Description]. @CharacterName is positioned in the optical center in a cowboy shot, framed from mid-thigh up with 25% clear headroom above the head and ample negative margins flanking both sides. During the first 5 seconds, @CharacterName [Phase 1 Action Description]. At second 5, @CharacterName [Phase 2 Transition Verb and Secondary Action]. Rendered exclusively in uniform 2D charcoal vector linework (#25313C) with solid flat fills, soft contact shadow, and steady physical motion. All action remains tightly contained within the central vertical sweet spot. Completely silent video.
```

### Formula D: Gemini Omni 1.1 Flash Tail-Frame Chained Scene
```text
Continuing from the starting frame, @CharacterName [Kinetic Delta Action Description during 0-5s]. At second 5, @CharacterName [Phase 2 Transition Verb and Resolving Action]. The camera remains completely locked in a stationary tripod position with fixed perpendicular perspective. Rendered in uniform 2D vector linework (#25313C) with flat clean fills and steady physical motion against the stationary cream ground (#F4E6C7). Completely silent video.
```

---

## 9. Agent Pre-Flight Execution Checklist

Before submitting generation requests to Google Flow:

- [ ] **Model Selection Confirmed:** Image mode set to `🍌 Nano Banana Pro` (0 credits); Video mode set to `Gemini Omni 1.1 Flash` (10–15 credits @ 720p).
- [ ] **Aspect Ratio Alignment:** Target aspect ratio (`16:9` or `9:16`) matches across prompt text, UI dropdown, and all reference images ($>1024\text{ px}$).
- [ ] **Dual-Layer Character Stored:** Character has both `Portrait` and `Create Body` saved in the Flow tray.
- [ ] **Token Stripping Enforced:** Character is referenced via `@CharacterName` with all redundant facial and clothing adjectives stripped.
- [ ] **Single Prose Paragraph:** Video prompt is written as one continuous paragraph of natural English prose (zero bracketed labels, zero bullet points).
- [ ] **Affirmative Physical Anchoring (E29):** no **defect naming** (`no extra limbs`, `no morphing`, `zero skin pores`); **content exclusion** (`no background music`, `no on-screen text`) is fine. Defect detection belongs to the driver on return, not the prompt.
- [ ] **Two-Phase Staged Kinetics:** Prompt scripts an explicit transition verb at second 5 to prevent late-clip motion freeze.
- [ ] **Framing Calibrated:** Character is framed in a **Cowboy Shot** (mid-thigh up) centered inside the **Universal Clean Canvas** ($X \in [10\%, 90\%]$, $Y \in [20\%, 75\%]$).
- [ ] **Audio Decoupled:** Video prompt is completely silent; VO script is decoupled to ElevenLabs at **~180 WPM** (~30 words/10s).


---

## 10. Observed on the live UI (2026-09-04) — this is what the driver actually does

Flow moved to `flow.google.com` and rebuilt its composer on 2026-09-04. Everything above that
describes the UI was written from documentation; this section was written from screenshots and
is implemented in `tools/google-flow-driver/src/cdp-driver.mjs`.

| step | gesture | check that it worked |
|---|---|---|
| bind a Character | type `@`, type the name into the picker's search (it steals focus), click the option, click **Add to prompt** | a `.mention-chip[data-reference-type="entity"]` is in the composer — the driver **throws before submit** if not; literal `@Mike` text binds nothing and the model draws a different man |
| attach a file reference | type `@`, type the filename — if it is already a project asset, click it (media inserts on click); else **Upload media** → native file chooser → **Add to prompt** | a `.mention-chip[data-reference-type="media"]`; re-uploading the same file every run duplicates it in Uploads |
| order | **prompt first, references second** | both are composer chips and `setPrompt` clears the composer |
| collect the output | new `img[src*='flow-content.google/image/']` (or `/asb/`) not in the pre-submit baseline | an uploaded reference **re-renders as a new CDN image, re-encoded** — the driver skips any candidate whose 16×16 average-hash matches a reference file; three downloads were the reference before that existed |
| x2..x4 | count is part of the settings match; outputs saved as `-raw`, `-raw-2`, … | the same src can be handed back twice (dedupe by src); a 45 s quiet cut-off takes what landed |
| Nano Banana Pro stills | `Generating will use 0 credits` on every roll today | read the meter for video; 15 credits / 10 s is not yet observed |

Provenance: `provider-jobs/finance-host-model-sheets-001.google-flow-job.v1.json` `roll_log` (seven attempts, each with what broke and what fixed it).
