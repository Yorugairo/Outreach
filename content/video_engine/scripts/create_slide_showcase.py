"""
Interactive Slide Evidence-Lock & Tracing Showcase
Demonstrates incorporating teacher-stamped slide PNGs into Remotion with spring entrances,
animated SVG ink tracing, highlighter wipes, and annotation stickers.
"""

from pathlib import Path

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Slide Evidence Layer & Tracing Showcase</title>
  <style>
    :root {
      --bg: #0b0f17;
      --panel-bg: #F4E6C7; /* Washi Cream */
      --charcoal: #25313C;
      --cobalt: #1769C2;
      --teal: #178C83;
      --sunflower: #F5B72E;
      --coral: #ED6A4A;
      --card-bg: #161f2e;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: #f8fafc;
      margin: 0;
      padding: 2rem;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    header {
      margin-bottom: 2rem;
      border-bottom: 1px solid #334155;
      padding-bottom: 1.25rem;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }
    h1 {
      margin: 0 0 0.5rem 0;
      color: var(--sunflower);
      font-size: 2rem;
    }
    .subtitle {
      color: #94a3b8;
      font-size: 0.95rem;
    }
    .controls {
      display: flex;
      gap: 1rem;
      align-items: center;
      margin-bottom: 1.5rem;
      background: var(--card-bg);
      padding: 1rem 1.5rem;
      border-radius: 12px;
      border: 1px solid #334155;
    }
    .btn {
      background: var(--cobalt);
      color: #fff;
      border: none;
      padding: 0.6rem 1.25rem;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .btn:hover {
      background: #1e7be6;
      transform: translateY(-1px);
    }
    .btn-secondary {
      background: #334155;
    }
    .btn-secondary:hover {
      background: #475569;
    }
    select {
      background: #0f172a;
      color: #f8fafc;
      border: 1px solid #475569;
      padding: 0.6rem 1rem;
      border-radius: 6px;
      font-size: 0.9rem;
    }

    /* Video Player Mock Viewport */
    .viewport-frame {
      width: 100%;
      max-width: 1080px;
      height: 608px; /* 16:9 */
      margin: 0 auto;
      background: #1a2230;
      border: 4px solid var(--charcoal);
      border-radius: 16px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 20px 50px rgba(0,0,0,0.6);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* 2.5D Evidence Plate Container */
    .evidence-plate {
      width: 900px;
      height: 502px;
      background: var(--panel-bg);
      border: 3px solid var(--charcoal);
      border-radius: 12px;
      box-shadow: 12px 12px 0px var(--charcoal);
      position: relative;
      overflow: hidden;
      transform-origin: center center;
    }

    .slide-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    /* SVG Overlay Layer */
    .svg-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
    }

    /* Floating Callout Tag */
    .callout-tag {
      position: absolute;
      top: 60px;
      right: 60px;
      background: var(--charcoal);
      color: var(--sunflower);
      border: 2px solid var(--sunflower);
      padding: 10px 16px;
      border-radius: 8px;
      box-shadow: 4px 4px 0px rgba(0,0,0,0.3);
      font-weight: 800;
      font-size: 0.95rem;
      opacity: 0;
      transform: scale(0.8) translateY(-10px);
      transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .callout-tag.visible {
      opacity: 1;
      transform: scale(1) translateY(0);
    }

    .timeline-bar {
      margin-top: 1rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      color: #94a3b8;
      font-size: 0.9rem;
    }
    .timeline-bar input[type="range"] {
      flex: 1;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>📑 Slide Evidence-Lock & Tracing Showcase</h1>
        <div class="subtitle">Teacher-Stamped Slide PNG layered with Remotion spring entrance, ink arrows, and highlighter wipe.</div>
      </div>
      <div>
        <button class="btn" onclick="playSequence()">▶️ Play Evidence-Lock Sequence</button>
      </div>
    </header>

    <div class="controls">
      <label><strong>Select Deck Slide:</strong></label>
      <select id="slide-select" onchange="changeSlide(this.value)">
        <option value="silicon-silent-triopoly-slide-002.png">Silicon's Silent Triopoly — Slide 2</option>
        <option value="memory-supercycle-slide-002.png">The Memory Supercycle — Slide 2</option>
        <option value="silicon-value-software-bubble-slide-002.png">Silicon Value in a Software Bubble — Slide 2</option>
      </select>

      <button class="btn btn-secondary" onclick="resetPlate()">⏮️ Reset</button>
      <span id="status-label" style="margin-left: auto; font-family: monospace; color: var(--sunflower);">Frame: 0/90 (0.0s)</span>
    </div>

    <!-- 16:9 Video Canvas -->
    <div class="viewport-frame">
      <!-- 2.5D Evidence Plate Card -->
      <div class="evidence-plate" id="plate">
        <img class="slide-img" id="slide-img" src="slides/silicon-silent-triopoly-slide-002.png" alt="Slide Evidence" />
        
        <!-- Animated SVG Overlay -->
        <svg class="svg-overlay" viewBox="0 0 900 502" id="svg-layer">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#ED6A4A" />
            </marker>
          </defs>

          <!-- 1. Animated Highlighter Rect -->
          <rect id="highlighter-rect" x="380" y="140" width="0" height="42" fill="#F5B72E" opacity="0.4" rx="4" />

          <!-- 2. Animated Ink Pointer Arrow -->
          <path id="ink-arrow" d="M 260,260 Q 320,200 370,170" fill="none" stroke="#ED6A4A" stroke-width="4.5" stroke-linecap="round" marker-end="url(#arrow)" stroke-dasharray="250" stroke-dashoffset="250" />

          <!-- 3. Chalk Callout Ring -->
          <ellipse id="chalk-ring" cx="540" cy="162" rx="160" ry="32" fill="none" stroke="#ED6A4A" stroke-width="3" stroke-dasharray="1000" stroke-dashoffset="1000" />
        </svg>

        <!-- Dynamic Sticker Callout -->
        <div class="callout-tag" id="callout-tag">
          ⚡ 96% GLOBAL TRIOPOLY CHOKEPOINT
        </div>
      </div>
    </div>

    <div class="timeline-bar">
      <span>0s</span>
      <input type="range" id="scrubber" min="0" max="90" value="0" oninput="renderFrame(parseInt(this.value))">
      <span>3.0s (90 Frames @ 30fps)</span>
    </div>
  </div>

  <script>
    function remotionSpring(progress, damping = 20, stiffness = 80) {
      return 1 - Math.exp(-progress * (damping / 3)) * Math.cos(progress * Math.sqrt(stiffness) * 0.4);
    }

    const plate = document.getElementById('plate');
    const highlighter = document.getElementById('highlighter-rect');
    const inkArrow = document.getElementById('ink-arrow');
    const chalkRing = document.getElementById('chalk-ring');
    const calloutTag = document.getElementById('callout-tag');
    const scrubber = document.getElementById('scrubber');
    const statusLabel = document.getElementById('status-label');

    function renderFrame(frame) {
      statusLabel.innerText = `Frame: ${frame}/90 (${(frame/30).toFixed(2)}s)`;
      scrubber.value = frame;

      // Phase 1: Card Entrance (Frames 0 - 25)
      const entranceT = Math.min(frame / 25, 1);
      const entranceSpring = remotionSpring(entranceT * 4, 18, 90);
      const scale = 0.85 + 0.15 * Math.min(Math.max(entranceSpring, 0), 1);
      const opacity = Math.min(frame / 10, 1);
      plate.style.transform = `scale(${scale})`;
      plate.style.opacity = opacity;

      // Phase 2: Highlighter Sweep (Frames 25 - 45)
      if (frame >= 25) {
        const hlT = Math.min((frame - 25) / 20, 1);
        highlighter.setAttribute('width', (320 * hlT).toString());
      } else {
        highlighter.setAttribute('width', '0');
      }

      // Phase 3: Ink Arrow Drawing (Frames 35 - 55)
      if (frame >= 35) {
        const arrowT = Math.min((frame - 35) / 20, 1);
        inkArrow.style.strokeDashoffset = (250 * (1 - arrowT)).toString();
      } else {
        inkArrow.style.strokeDashoffset = '250';
      }

      // Phase 4: Chalk Ring Draw & Sticker Reveal (Frames 50 - 75)
      if (frame >= 50) {
        const ringT = Math.min((frame - 50) / 20, 1);
        chalkRing.style.strokeDashoffset = (1000 * (1 - ringT)).toString();
        calloutTag.classList.add('visible');
      } else {
        chalkRing.style.strokeDashoffset = '1000';
        calloutTag.classList.remove('visible');
      }
    }

    let isPlaying = false;
    let animId = null;

    function playSequence() {
      if (isPlaying) cancelAnimationFrame(animId);
      isPlaying = true;
      let currentF = 0;

      function loop() {
        renderFrame(currentF);
        currentF++;
        if (currentF <= 90 && isPlaying) {
          animId = setTimeout(() => requestAnimationFrame(loop), 1000 / 30);
        } else {
          isPlaying = false;
        }
      }
      loop();
    }

    function resetPlate() {
      isPlaying = false;
      if (animId) clearTimeout(animId);
      renderFrame(0);
    }

    function changeSlide(filename) {
      document.getElementById('slide-img').src = `slides/${filename}`;
      resetPlate();
      playSequence();
    }

    window.onload = () => {
      renderFrame(0);
      setTimeout(playSequence, 500);
    };
  </script>
</body>
</html>
"""

out_p = Path("content/video_engine/review/slide_evidence_showcase.html")
out_p.parent.mkdir(parents=True, exist_ok=True)
out_p.write_text(html, encoding="utf-8")
print(f"Generated Slide Evidence Showcase at: {out_p.resolve()}")
