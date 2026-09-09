# Intake — the ink bloom transition (operator, 2026-09-08)

The operator brought a MotionKit preset by hand: *"here's an ink bloom transition that is not the swirl; our swirl is
really built to stay on the same world, this allows us to transition to other worlds better maybe?"*

**Recall** (the receipt):
- `docs/portable/OPERATOR-RULINGS.md` E47 — the world-change kit is cut / dip / blur-zoom; the wipe is retired as a default;
  *mechanisms port, code does not*. E48 — a short declares ONE primary, one or two ACCENTS for topic changes and the
  climax, ONE hero (the spiral, a return move that stays on its world — the operator's own read).
- `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md:1764` — the motion menu already lists a **radial reveal** (a
  `clip-path: circle()` from a named point) as unbuilt; the ink bloom is that reveal with an organic edge.
- `docs/content-video-engine/44-INK-AND-SURFACE.md` — the ink physics we hold and the preset lacks: Kubelka-Munk (alpha
  blending is the wrong operator), the dark rim (Deegan 1997), the halo (Chu & Tai 2005). `kinetics/ink.mjs` implements
  K-M behind the `km_ink` flag; the memory `soak-ink-is-a-plate` records six K-M filter rounds lost to alpha pooling.
- The research brief C4 — Chromium seek envelope: SVG paths ≤ 450, ≤ 2 filter primitives; Canvas 2D for high-frequency
  dynamic drawing. C6 — every frame a pure function of t (the preset is frame-driven and seeded: it qualifies).
- `docs_find "ink bloom"` — 0 hits: the record holds the physics and the reveal, not this composite.

## What the preset is (the source, kept verbatim below)

A Canvas 2D bloom from the frame centre: a 40-segment blob whose radius carries two-harmonic noise
(`sin(3a + 2t)·0.10 + sin(7a + t)·0.05`), grown by an ease-out cubic to 0.6 of the diagonal; twelve tapered
quadratic tendrils reaching past the blob; `splatterCount` seeded droplets (a sine-hash PRNG) with three satellites each,
fading as the bloom grows; an inner radial gradient composited `source-atop`; an optional italic label.

## The mechanism to port (not the code)

1. **An organic mask from a NAMED point** — the radial reveal (29:1764) with the two-harmonic edge noise, seeded by
   `lpHash` so it is a pure function of t and byte-identical on seek; as an SVG `clip-path` polygon on the incoming
   world (40 points, well inside C4), never a canvas.
2. **Tendrils and droplets** as stroked/filled paths on the species layer, seeded the same way; droplet count a dial.
3. **The edge is ours, not a gradient**: the dark rim and the halo from doc 44 on the bloom's boundary; the K-M ink
   behind `km_ink` if the surface is paper (E22's page soak already blooms charcoal to the deckle — the same mechanism,
   on-page).
4. **Placement law**: a world change, so it lands like a cut in the caption gap (M13) and, like the dip, centred on the
   next word's onset (TR-2).

## Where it fits E48

The tariff short's vocabulary is declared: primary the dip, accent the card-then-snap, hero the spiral. An ink bloom
would be the **second accent — the topic change**: the one seam that qualifies is the second lever
(`cut("And that's where Tokyo")`, 47.78 s, the vault plate), where the argument turns from parts to Treasuries. Nowhere
else; a fourth kind on any other seam is a defect of the plan.

## Status

Not built. Backlog TR-14. The operator's source is below so the harvest survives the session; the port is a species /
exit name (`bloom:<x>,<y>`) in the player behind an opt-in, goldens byte-identical, judged on frames at the second-lever
seam before it is declared.

## Source (MotionKit "Ink Bloom Transition", pasted by the operator 2026-09-08)

```tsx
import React, { useRef, useEffect } from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";

const InkBloomTransition: React.FC<{ inkColor: string; backgroundColor: string; splatterColor: string; spreadSpeed: number; splatterCount: number; label: string; fontSize: number; }> =
({ inkColor, backgroundColor, splatterColor, spreadSpeed, splatterCount, label, fontSize }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const labelOpacity = interpolate(frame, [15, 30, durationInFrames - 20, durationInFrames - 5], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  useEffect(() => {
    const canvas = canvasRef.current; if (!canvas) return;
    const ctx = canvas.getContext("2d"); if (!ctx) return;
    canvas.width = width; canvas.height = height; ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = backgroundColor; ctx.fillRect(0, 0, width, height);
    const cx = width / 2, cy = height / 2, t = frame / 30 * spreadSpeed;
    const maxRadius = Math.sqrt(width * width + height * height) * 0.6, bloomRadius = progress * maxRadius;
    ctx.fillStyle = inkColor; const blobSegments = 40; ctx.beginPath();
    for (let i = 0; i <= blobSegments; i++) {
      const angle = (i / blobSegments) * Math.PI * 2;
      const noise = Math.sin(angle * 3 + t * 2) * 0.1 + Math.sin(angle * 7 + t) * 0.05;
      const r = bloomRadius * (1 + noise), x = cx + Math.cos(angle) * r, y = cy + Math.sin(angle) * r;
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.closePath(); ctx.fill();
    const tendrilCount = 12;
    for (let i = 0; i < tendrilCount; i++) {
      const angle = (i / tendrilCount) * Math.PI * 2 + t * 0.1, tendrilLen = bloomRadius * (0.3 + Math.sin(i * 1.7 + t) * 0.2);
      const tx = cx + Math.cos(angle) * (bloomRadius + tendrilLen), ty = cy + Math.sin(angle) * (bloomRadius + tendrilLen);
      ctx.strokeStyle = inkColor; ctx.lineWidth = 8 * (1 - progress * 0.5); ctx.lineCap = "round"; ctx.beginPath();
      ctx.moveTo(cx + Math.cos(angle) * bloomRadius * 0.8, cy + Math.sin(angle) * bloomRadius * 0.8);
      const midX = cx + Math.cos(angle) * bloomRadius * 1.1 + Math.sin(angle + 1.5) * 30, midY = cy + Math.sin(angle) * bloomRadius * 1.1 + Math.cos(angle + 1.5) * 30;
      ctx.quadraticCurveTo(midX, midY, tx, ty); ctx.stroke();
    }
    ctx.fillStyle = splatterColor;
    for (let i = 0; i < splatterCount; i++) {
      const seed = i * 1.7, angle = seeded(seed) * Math.PI * 2, dist = bloomRadius * (0.8 + seeded(seed * 3.3) * 0.6);
      const sx = cx + Math.cos(angle) * dist, sy = cy + Math.sin(angle) * dist, sSize = (2 + seeded(seed * 5.1) * 8) * progress;
      if (progress > 0.2) {
        ctx.globalAlpha = (1 - progress * 0.5) * (0.3 + seeded(seed * 7.7) * 0.5);
        ctx.beginPath(); ctx.arc(sx, sy, sSize, 0, Math.PI * 2); ctx.fill();
        for (let j = 0; j < 3; j++) { const dx = sx + (seeded(seed * 11 + j) - 0.5) * 20, dy = sy + (seeded(seed * 13 + j) - 0.5) * 20; ctx.beginPath(); ctx.arc(dx, dy, sSize * 0.3, 0, Math.PI * 2); ctx.fill(); }
      }
    }
    ctx.globalAlpha = 1;
    if (bloomRadius > 10) {
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, bloomRadius);
      grad.addColorStop(0, inkColor); grad.addColorStop(0.7, inkColor); grad.addColorStop(1, splatterColor + "00");
      ctx.fillStyle = grad; ctx.globalCompositeOperation = "source-atop"; ctx.fillRect(0, 0, width, height); ctx.globalCompositeOperation = "source-over";
    }
  }, [frame, width, height, inkColor, backgroundColor, splatterColor, splatterCount, spreadSpeed, progress]);
  return (
    <AbsoluteFill style={{ backgroundColor }}>
      <canvas ref={canvasRef} style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }} />
      {label && (<AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ fontSize, fontWeight: 800, fontFamily: "'Georgia', serif", color: "#ffffff", letterSpacing: "0.05em", fontStyle: "italic" as const, opacity: labelOpacity, textShadow: "0 0 20px rgba(0,0,0,0.5)" }}>{label}</div>
      </AbsoluteFill>)}
    </AbsoluteFill>
  );
};
const seeded = (seed: number) => { const x = Math.sin(seed * 7890.123) * 43758.5453; return x - Math.floor(x); };
// schema: inkColor #1a1a2e, backgroundColor #f0ebe0, splatterColor #1a1a2e, spreadSpeed 1 (0.3-3), splatterCount 60 (10-150), label "", fontSize 80
// meta: "Ink Bloom Transition" - Canvas 2D organic ink bloom; category transition; 30 fps, 1920x1080, 75 frames; author MotionKit
```
