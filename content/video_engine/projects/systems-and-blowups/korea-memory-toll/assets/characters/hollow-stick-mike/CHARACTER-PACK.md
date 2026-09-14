# @HollowStickMike — Character Asset Dossier & Prompt Architecture

**Registered Asset:** `content/video_engine/projects/systems-and-blowups/korea-memory-toll/assets/characters/hollow-stick-mike/portrait_reference.png`  
**Flow Project Slot Name:** `@HollowStickMike`  
**Archetype:** Senior Risk Analyst / Institutional Host (Money Physics)

---

## 1. Physical Anatomy & Visual Identity

The character design has a major architectural advantage for AI video generation: **a hollow face with floating geometric glasses**. By eliminating internal facial anatomy (eyes, nose, mouth, lips), Omni 1.1 Flash and Nano Banana Pro are physically prevented from hallucinating lip-sync melting, mouth morphing, or facial asymmetry.

| Anatomical Zone | Visual Trait | Color Token | Mechanics in Flow Video |
|---|---|---|---|
| **Head Contour** | Clean black monoline circular ring stroke. Hollow interior showing background ground. | `#141414` | Completely immune to facial distortion or uncanny valley. |
| **Eyewear** | Chunky rectangular frames floating centered inside the circular ring. Hollow clear lenses. | Deep Purple / Indigo `#4A3E6D` | Anchors gaze direction without needing pupils or blinks. |
| **Hairstyle** | Voluminous, chunky textured dreadlocks / locs swept up and to the left. Matte vector silhouette. | Deep Charcoal / Black `#111111` | Provides high-contrast silhouette recognition across all angles. |
| **Neck & Limbs** | Crisp black solid stick-line stroke with fixed uniform line weight. | `#141414` | Stable kinematic joint pivots. |
| **Suit Jacket** | Tailored single-breasted suit jacket with notched lapels and tactile embossed seam contours. | Slate Navy `#2E4A73` | Rich color block separating character from background. |
| **Shirt** | Crisp stiff collared dress shirt. | Off-White `#F7F7F7` | Sharp contrast behind tie. |
| **Necktie** | Classic straight necktie tucked into buttoned jacket. | Crimson / Burgundy `#8C1D24` | Primary warm accent token. |

---

## 2. The Flow Prompting Contract

### Rule 1: The Token Stripping Protocol
Once `@HollowStickMike` is saved to your project character tray in Google Flow:
* ❌ **BANNED (Latent Interference):**  
  `"@HollowStickMike, a stickman with black locs and purple glasses wearing a navy suit and red tie, stands at a desk..."`  
  *(Re-describing features forces the model to synthesize them anew, fighting the image embeddings and causing wardrobe drift).*
* ✅ **MANDATORY (Harmonized Embedding):**  
  `"@HollowStickMike stands at the trading desk and smoothly extends his right hand toward the monitor. Locked tripod camera. Completely silent video."`

### Rule 2: Two-Phase Kinetic Staging
Every 10-second clip driven by `@HollowStickMike` must execute an explicit transition verb at second 5:
* **Phase 1 (0–5s):** Posture / subtle motion (e.g. examining a document, hands resting at sides, leaning over a desk).
* **Phase 2 (5–10s):** Deliberate physical action (e.g. points at the chart, takes one step forward, turns head to camera).

---

## 3. Production Test Prompts for "The Trillion Dollar Toll Booth"

### Test 1: The Opening Desk & Steam (Shot 01)
**Step A: Generate Start Frame Keyframe (Nano Banana Pro / Image Mode)**
```text
A wide 9:16 vertical studio plate with fixed perpendicular perspective at eye level. In the lower-center of the frame stands @HollowStickMike in his tailored slate navy suit and crimson tie, standing behind a dark oak analyst desk. Resting on the desk to the right is a clean ceramic coffee cup. In the background behind the desk, visible through a large industrial steel-framed window, are the towering container cranes of the port of Busan under a twilight sky. Rendered in clean flat 2D graphic illustration with tactile embossed contours on a solid cream paper ground (#F4E6C7). High contrast, sharp vector silhouettes, generous headroom.
```

**Step B: Animate Video (Omni 1.1 Flash / `Frames to Video` / `+ Add start frame`)**
```text
Continuing from the starting frame, @HollowStickMike stands composed behind the desk, arms resting loosely at his sides. Delicate wisps of steam curl gently upward from the rim of the coffee cup into the air. At second 5, @HollowStickMike smoothly lifts his right hand and gestures toward the window with an open palm, holding the pose calmly. The desk, coffee cup, and background cranes remain completely motionless. Locked-off static tripod camera, fixed eye-level perspective. Completely silent video.
```

---

### Test 2: The Cleanroom & Silicon Monolith (Shot 04)
**Step A: Generate Start Frame Keyframe (Nano Banana Pro / Image Mode)**
```text
A 9:16 vertical composition with fixed eye-level framing. On the left side of the frame stands @HollowStickMike in his signature slate navy suit, crimson tie, and purple glasses, turned slightly inward. On the right side of the frame looms an illuminated semiconductor cleanroom vacuum chamber with a massive circular silicon wafer mounted vertically like a monolith. Clean industrial piping, soft amber and cool white cleanroom lighting. Rendered in flat 2D graphic editorial vector linework on a solid cream ground (#F4E6C7), zero 3D rendering, crisp graphic edges.
```

**Step B: Animate Video (Omni 1.1 Flash / `Frames to Video` / `+ Add start frame`)**
```text
Continuing seamlessly from the starting frame, @HollowStickMike takes one deliberate step closer to the glowing silicon monolith on the right, keeping his posture upright and analytical. At second 5, he points his right index finger directly at the center of the wafer pattern, holding the analytical gesture steadily. The cleanroom chamber and background machinery remain completely stationary. Completely locked tripod camera. Completely silent video.
```

---

### Test 3: The Outro at the Port Baseline (Shot 13)
**Step A: Generate Start Frame Keyframe (Nano Banana Pro / Image Mode)**
```text
A 9:16 vertical full shot. @HollowStickMike stands centered on a flat horizontal shipping dock baseline, framed cowboy shot from mid-thigh up with 25% clear headroom. Behind him are stacked shipping containers and maritime port cranes silhouetted against a calm sunset. Rendered in clean 2D tactile graphic art, slate navy suit (#2E4A73), crimson tie (#8C1D24), purple rectangular glasses (#4A3E6D), solid flat fills, subtle floor contact shadow.
```

**Step B: Animate Video (Omni 1.1 Flash / `Frames to Video` / `+ Add start frame`)**
```text
Continuing from the starting frame, @HollowStickMike looks directly forward toward the camera with his hands resting calmly at his sides. At second 5, he brings both hands together in front of him, resting them in a composed executive posture as the scene holds steady. Locked-off static camera, fixed perpendicular perspective. Completely silent video.
```
