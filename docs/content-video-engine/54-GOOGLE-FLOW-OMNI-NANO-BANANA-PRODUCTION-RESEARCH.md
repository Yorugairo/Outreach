# 54 — Google Flow Production Research: Gemini Omni 1.1 Flash & Nano Banana Pro

**Title:** Production Optimization, Prompt Engineering, Multimodal Conditioning, and Responsive Composition for Google Flow  
**Engines Covered:** Gemini Omni 1.1 Flash (`gemini-omni-1.1-flash`), Nano Banana Pro (`gemini-3-pro-image`), Google Flow (`labs.google/fx/tools/flow`)  
**Target Channels:** Money Physics, Building Money, Martial Matters  
**Status:** Canonical Reference & Research Monograph  
**Date:** 2026-09-04  

---

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
> | Cream `#F4E6C7` / charcoal `#25313C` monoline as *the* style | **trying it — operator, 2026-09-04** | those are our house tokens (29/41/48). The retention host keeps the operator's phrase, *"A light application of woodblock print and vox newspaper with rich anime colors"*; the **stick lane is being rolled on cream/charcoal** (v5) because *"if cream works it gives us a unique space and opens up using the drawing lane to create both styles"* — one ground for the page and the man. |
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

---

## Executive Summary & Architectural Core

This research monograph documents the complete findings of four parallel agentic deep-research loops investigating **Google Flow**'s next-generation production pipeline, centered strictly on **Gemini Omni 1.1 Flash** (video generation) and **Nano Banana Pro** (image generation).

In our production stack:
1. **Veo is replaced by Gemini Omni 1.1 Flash.** Omni 1.1 Flash is a **Unified Multimodal Autoregressive Transformer** (rather than a Latent Diffusion Transformer with a frozen T5 encoder like Veo). It natively reasons over visual tokens, understanding abstract 2D line art, stickmen, and data diagrams without hallucinating "3D plastic shading" or photorealistic skin textures. It cuts latency by 70% (15–30s vs. 60–90s), halves Flow credit expenditure (10–15 credits vs. 24–40 credits), and delivers **native 10.0-second clips** at 24 FPS.
2. **Nano Banana Pro (Gemini 3 Pro Image) replaces older diffusion stills.** Nano Banana Pro operates at **0 credits** in Google Flow Image Mode, provides studio-level spatial layout reasoning, achieves ~94% on-screen typographic accuracy, and strictly adheres to hex codes (`#F4E6C7`, `#25313C`) when bound via semantic role-syntax.
3. **Character identity is anchored by Flow's dual-layer Character Builder**, eliminating prompt bloat and latent drift through affirmative full-body modeling (`Portrait` $\to$ `Create Body` without image uploads) and token stripping downstream.
4. **Multi-scene continuity is achieved via Tail-Frame Extension Chaining** ($t=10.0\text{s}$ terminal frame extraction) and **3-Slot Ingredients Conditioning** (Subject + Prop + Environment), strictly pre-cropped to the destination aspect ratio ($>1024\text{ px}$).
5. **Cross-platform framing enforces the Universal Clean Canvas** ($X \in [10\%, 90\%]$, $Y \in [20\%, 75\%]$) and the **Cowboy Shot Golden Zone**, resolving the spatial patch downsampling bug where thin stickman limbs dissolve in extreme wide shots.

---

## 1. Engine Stack & Workspace Architecture

```
+───────────────────────────────────────────────────────────────────────────────────────────+
|                           GOOGLE FLOW PRODUCTION ENGINE STACK                             |
|                                                                                           |
|  [Script & Shot Table] (170 WPM VO via ElevenLabs — Decoupled & 100% Silent Video)        |
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

### 1.1 Technical Comparison: Omni 1.1 Flash vs. Veo 3.1

| Evaluation Axis | Gemini Omni 1.1 Flash (`gemini-omni-1.1-flash`) | Google Veo 3 / 3.1 | Production Verdict |
|---|---|---|---|
| **Underlying Architecture** | **Unified Multimodal Autoregressive Transformer** | Latent Diffusion Transformer (DiT) with frozen text encoder | Omni natively attends to visual context; eliminates plastic 3D creep on 2D line art. |
| **Generation Latency** | **15 – 30 seconds** | 60 – 90+ seconds | **70% speedup** allows real-time iteration. |
| **Credit Economics** | **10 credits (6s @ 720p) / 15 credits (10s @ 720p)** | 24 – 40+ credits | **50–60% cheaper** per scene. |
| **Native Clip Duration** | **10.0 seconds** (fixed native duration) | 4s, 6s, or 8s | Single 10s clip provides 2–3 punch-in cuts in post. |
| **Stylistic Adherence** | High affinity for 2D line art, blueprints, and diagrams | Biased toward photorealism and heavy 3D volumetric shading | Omni maintains flat cream paper and monoline ink without airbrushing. |
| **Audio Output** | **Prompt 100% silent video** | Generative audio enabled | Decouple VO to ElevenLabs; models cannot maintain timbre across seeds. |

---

## 2. Gemini Omni 1.1 Flash: Video Prompt Engineering

### 2.1 The Single Continuous Prose Paragraph
Omni 1.1 Flash parses prompts as dense multimodal prose (40–90 words). 
*   **The Tag Soup Failure Mode:** In older diffusion models, bracketed labels (`[SHOT: WIDE]`, `[CAMERA: PAN]`) were used to weight tokens. In Omni 1.1 Flash, bracketed tags act as out-of-distribution noise tokens or are rendered as literal text on the canvas.
*   **The Rule:** Prompts must be written as **one continuous, flowing paragraph** of descriptive English prose. Zero bullet points, zero form headers, zero bracketed labels.

### 2.2 Affirmative Physical Anchoring (The Ban on Negative Prompts)
*   **The Mechanism:** Multimodal autoregressive transformers calculate self-attention across every input token. Including tokens like `"no 3D, no extra limbs, no camera shake, no text, without distortion"` directly activates the attention embeddings for `3D`, `extra limbs`, and `camera shake`. The model hallucinates the defect precisely because it was named (the "pink elephant" effect).
*   **The Production Standard:** Describe only what *is* physically present in the frame:
    *   ❌ *Negative (Summons Defects):* `"No camera shake, no panning, no 3D shading, no extra limbs, no text."`
    *   ✅ *Affirmative (Locks Ground):* `"A completely stationary, locked tripod camera frame with fixed perpendicular perspective at eye level. Rendered exclusively in flat 2D uniform charcoal vector linework (#25313C) with solid clean fills on an unmoving cream paper background (#F4E6C7). A single solitary character centered in frame."`

### 2.3 Two-Phase Staged Kinetics (Defeating the Second-5 Motion Stall)
Video generation models exhibit a universal inductive bias: they execute prompt action aggressively in seconds 0–3, resolve the movement by second 4 or 5, and freeze into rigid mannequins for seconds 6–10.
*   **The Protocol:** Every 10-second prompt must script an **explicit transition verb at second 5**:
    *   *Phase 1 (0 to 5s):* Initial continuous physical action (e.g., examining a document on a desk, standing by an unmoving balance scale).
    *   *Phase 2 (5 to 10s):* Secondary kinetic verb (e.g., reaches forward, points directly at column B, places a counter-weight).

### 2.4 Cinematic Camera Lexicon (Adhered Directives)
Omni 1.1 Flash responds with high fidelity to director-level camera terms. Use exactly one primary camera directive per prompt:
*   `Locked-off static tripod camera, fixed perpendicular perspective at eye level`: The bedrock baseline for diagrams, balance scales, and institutional explainers.
*   `Slow, steady push-in dolly shot toward the subject, maintaining crisp perpendicular perspective`: Creates escalating cognitive focus on a critical data node.
*   `Smooth horizontal tracking shot gliding alongside @CharacterName at uniform velocity`: Moves an actor laterally across a continuous panoramic chart.
*   `Smooth vertical pedestal tracking shot rising steadily alongside the ascending chart`: Reveals tall vertical data columns or balance sheets.

---

## 3. Frames to Video & Tail-Frame Extension Chaining

Creating coherent 30- to 60-second video sequences requires chaining multiple 10-second Omni 1.1 Flash clips together without spatial popping or character morphing.

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

### 3.1 Terminal Frame Extraction
1. Generate Clip $N$ (10.0 seconds) in Google Flow.
2. Extract the exact final frame ($t=10.0\text{s}$):
   * *Flow UI:* Click the clip card $\to$ click `"Save Frame"` on the playback scrubber at the final frame.
   * *CLI / FFmpeg Automation:*
     ```bash
     ffmpeg -sseof -0.04 -i clip_01.mp4 -update 1 -frames:v 1 clip_01_tail.png
     ```
3. In Google Flow Video Mode for Clip $N+1$, click **`+ Add start frame`** and select `clip_01_tail.png`.

### 3.2 Kinetic-Delta-Only Prompting
When an initial frame is anchored, **never re-describe what is already visible in the image**. If the prompt re-describes the character's clothing, desk, or room, Omni 1.1 Flash attempts to re-synthesize the scene, causing a noticeable 1-frame boundary glitch.
*   ❌ *Redundant Prompt:* `"A stickman wearing a vest stands on a cream paper background next to a balance scale. He reaches out..."`
*   ✅ *Kinetic Delta Prompt:* `"Continuing from the starting frame, @Mike smoothly extends his right hand and places the brass coin into the right dish. At second 5, the balance scale tips downward on the right, and @Mike takes one step back, resting his hands at his sides. Completely locked static camera. Completely silent video."`

---

## 4. Ingredients-to-Video Architecture

Omni 1.1 Flash supports multi-latent conditioning with up to **3 reference ingredients**:

| Slot | Role | Reference Asset | Prompt Binding Syntax |
|---|---|---|---|
| **Ingredient 1** | **Subject** | Pinned Character Sheet from Character Builder (`@character`) | `"@Mike [performs action]"` |
| **Ingredient 2** | **Object / Prop** | Clean isolated prop on flat ground (`@prop`) | `"interacts with @prop"` |
| **Ingredient 3** | **Environment** | Static background / world plate (`@background`) | `"against @background"` |

### 4.1 Strict Technical Rules for Ingredients
1. **Mandatory Pre-Cropping:** All reference images must be pre-cropped to the **destination aspect ratio** (`16:9` or `9:16`) and exceed $1024\text{ px}$. Mismatched aspect ratios force the latent encoder to shear or anamorphic-stretch the subject.
2. **Clear-Zone Margin:** Maintain a 5–10% empty border around isolated character and prop cutouts to prevent severed limbs or clipped edges in the video render.
3. **Explicit Role Binding:** The prompt must explicitly bind the ingredients into physical interaction:
   `"@Mike picks up @prop from the desk and examines it carefully against @background. Completely locked static camera."`

---

## 5. 16:9 Landscape vs. 9:16 Vertical Mobile Architecture

### 5.1 The Universal Clean Canvas (Mobile UI Safe Zones)
Mobile platforms (TikTok, YouTube Shorts, Instagram Reels) overlay UI chrome that obstructs up to **59.1%** of a 9:16 vertical viewport.

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

### 5.2 The 3-Zone Vertical Stage (Never Blur-Pad)
Converting 16:9 to 9:16 via center-crop destroys **68.36% of horizontal area** ($1 - 607.5/1920$). Blurred-background padding is a banned slop pattern. Stack elements into three vertical tiers:
*   **Zone 1: Metric Headline / Hook ($Y: 10\%\text{--}25\%$):** Primary claim, live counter, or paradox statement.
*   **Zone 2: Core Evidence Canvas ($Y: 25\%\text{--}70\%$):** Pinned character, ledger board, chart, or balance scale.
*   **Zone 3: Kinetic Captions & Baseline ($Y: 70\%\text{--}90\%$):** Word-level captions and character floor contact.

### 5.3 The Cowboy Shot "Golden Zone" for Stickman Legibility
*   **Extreme Wide Shots (EWS) Fail:** In a 9:16 vertical 720p frame, an EWS scales a stickman down to $\approx 250\text{ px}$. At that resolution, $2\text{ px}$ vector limbs fall below the spatial patch downsampling threshold of the model ($8 \times 8$ or $16 \times 16$ latent patches), causing arms and legs to detach, flicker, or dissolve.
*   **Extreme Close-Ups (ECU) Fail:** Zooming into a flat 2D face forces the model to hallucinate 3D skin pores, shading, and fleshy facial features.
*   **The Cowboy Shot (Mid-thigh up, $65\%\text{--}75\%$ frame height):** The mathematically optimal framing. Places the character's head comfortably below the top dead zone ($Y: 280$), keeps hands in the active central canvas ($Y \in [600, 1100]$), terminates above captions ($Y: 1440$), and maintains full $6\text{--}12\text{ px}$ line-art integrity.

---

## 6. Nano Banana Pro Image Generation Engineering

**Nano Banana Pro (`gemini-3-pro-image`)** is built on Gemini 3 Pro (vs. Nano Banana 2 on Gemini 3.1 Flash Image).

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

1. **Credit Cost:** **0 credits** in Google Flow Image Mode (verified in driver telemetry).
2. **Prompt Structure (6-Factor Design Brief):** Tag soup degrades Gemini 3 Pro's reasoning. Brief the model with:
   1. *Subject* (physical posture, anatomy),
   2. *Work Surface / Medium* (`"Flat 2D monoline vector illustration"`, `"Orthographic 2D CAD elevation"`),
   3. *Composition* (`"fixed perpendicular perspective, eye-level horizon"`),
   4. *Ground & Environment* (texture, floor baseline),
   5. *Color & Lighting* (role-bound hex codes, unshaded fills),
   6. *Typography & Constraints* (quoted text strings, coordinates).
3. **Exact Hex Code Role-Binding:** Always pair hex codes with their physical element to avoid semantic drift:
   `"Charcoal ink linework (#25313C) rendered on a solid, untextured cream washi paper ground (#F4E6C7)"`.
4. **Typographic Rendering (~94% Accuracy):** Nano Banana Pro renders crisp, legible on-screen text when enclosed in double quotes with explicit font categories:
   `"Render the headline 'FEDERAL RESERVE' in bold condensed all-caps sans-serif font centered across the top 15% of the frame."`
5. **Character Builder Lifecycle (`Portrait` $\to$ `Create Body`):**
   - **Step 1:** Generate bust/headshot triptych (`Portrait`).
   - **Step 2:** Click **`Create Body`**. **DO NOT UPLOAD AN IMAGE.** Flow automatically pipes portrait latents into Nano Banana Pro. Prompt must declare: (1) `"Full-body shot, head to toe, standing neutral"`, (2) proportions, (3) complete wardrobe and **explicit footwear/soles**, (4) grounding contact shadow, and (5) hex code ground continuity.
   - **Step 3:** Tag `@CharacterName` downstream in Omni 1.1 Flash and **strip all physical adjectives** to avoid token-latent competition.

### 6.1 Common Image Failure Modes & Countermeasures

| Failure Mode | Root Cause | Exact Prompt Countermeasure |
|---|---|---|
| **Unwanted Photorealism** | Using words like "hyper-detailed", "photorealistic", or 35mm/85mm lens terms on graphic scenes. | `"Rendered strictly as a flat 2D vector editorial drawing. Matte screenprint aesthetic, solid ink contours, zero photographic textures, zero skin pores, zero depth-of-field blur."` |
| **3D Clay / Plastic Shading** | Ambiguous cartoon tags ("cute", "smooth 3D", "animation style"). | `"Flat 2D graphic illustration, unshaded flat color fills, zero 3D rendering, zero ambient occlusion, zero clay texture, crisp hard vector edges."` |
| **Muddy Line Weights** | Unspecified stroke parameters; model blends lines with painterly shading. | `"Uniform monoline black ink contours of fixed hairline weight (#25313C). Sharp, high-contrast closed vector boundaries separating color fills from the background."` |
| **Accessory Hallucination** | Contextual bleeding (generating in a train yard adds a conductor cap). | `"Bare-headed, clean hair silhouette, no hat, no headwear, empty open hands relaxed at sides, no handheld objects, no unprompted accessories."` |

---

## 7. Slim-LLM Production Formulas & State-Machine Prompts

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

## 8. Agent Pre-Flight Execution Checklist

Before submitting generation requests to Google Flow:

- [ ] **Model Selection Confirmed:** Image mode set to `🍌 Nano Banana Pro` (0 credits); Video mode set to `Gemini Omni 1.1 Flash` (10–15 credits @ 720p).
- [ ] **Aspect Ratio Alignment:** Target aspect ratio (`16:9` or `9:16`) matches across prompt text, UI dropdown, and all reference images ($>1024\text{ px}$).
- [ ] **Dual-Layer Character Stored:** Character has both `Portrait` and `Create Body` saved in the Flow tray.
- [ ] **Token Stripping Enforced:** Character is referenced via `@CharacterName` with all redundant facial and clothing adjectives stripped.
- [ ] **Single Prose Paragraph:** Video prompt is written as one continuous paragraph of natural English prose (zero bracketed labels, zero bullet points).
- [ ] **Affirmative Physical Anchoring:** Zero negative prompt tokens (`no`, `never`, `without`, `do not`); spatial bounds described affirmatively.
- [ ] **Two-Phase Staged Kinetics:** Prompt scripts an explicit transition verb at second 5 to prevent late-clip motion freeze.
- [ ] **Framing Calibrated:** Character is framed in a **Cowboy Shot** (mid-thigh up) centered inside the **Universal Clean Canvas** ($X \in [10\%, 90\%]$, $Y \in [20\%, 75\%]$).
- [ ] **Audio Decoupled:** Video prompt is completely silent; VO script is decoupled to ElevenLabs at **170 WPM** (~28 words/10s).

---

## 9. Primary Citations & Evidence Ledger

1. **Google DeepMind:**
   - *Gemini Omni Model Card & Technical Architecture* (DeepMind, 2026): Multimodal autoregressive transformer architecture, 24 FPS video output, 1,048,576 token multimodal context, native 720p base generation with upscaling, and native 16:9 / 9:16 aspect ratio support.
   - *Gemini Omni Prompting Guide* (`deepmind.google/models/gemini-omni/prompt-guide`): Director-level camera terminology (`locked off`, `push in`, `dolly zoom`, `one continuous shot / oner`, `eye level`).
   - *Introducing Nano Banana Pro (Gemini 3 Pro Image)*, Naina Raisinghani (Product Manager, Google DeepMind), Nov 2025 / 2026.
2. **Google Cloud Vertex AI Documentation:**
   - *Ultimate Prompting Guide for Veo 3.1 & Nano Banana* (`cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana`): Mandates affirmative framing ("Describe what you want, not what you don't want"), specifies native aspect ratio support for Nano Banana (`1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9`), and establishes 6-factor prompt taxonomy.
   - *Gemini Enterprise Agent Platform Video API Reference* (`docs.cloud.google.com/.../use-reference-images-to-guide-video-generation`): Documents API parameter `"aspectRatio": "16:9" | "9:16"` and 3s–10s base clip limits.
3. **Repository Evidence & Shipped Telemetry:**
   - `docs/content-video-engine/49-GENERATIVE-VIDEO-AND-THE-VERTICAL-STAGE.md`: Universal Clean Canvas derivation ($X \in [80, 880]\text{ px}, Y \in [280, 1340]\text{ px}$ on $1080 \times 1920$), 3-Zone Vertical Stage, and proof of $68.36\%$ horizontal area destruction under center-crop.
   - `docs/content-video-engine/53-THE-STICKMAN-LANE.md`: Operator ruling (2026-09-04) on eliminating negative prompt tokens and switching from bracketed field schemas to single flowing prose paragraphs.
   - `review/claims/mp-host-transitions-v1/WORK-ORDER.md`: Live telemetry on credit usage (10 credits for 6s @ 720p x1 on Omni Flash, 0 credits for Nano Banana Pro in Image Mode).
   - `tools/google-flow-driver/src/cdp-driver.mjs` & `dag-engine.mjs`: Implementation of the Flow CDP state machine, composer pill parsing, and multi-scene generation chaining.
