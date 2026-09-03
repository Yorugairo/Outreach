"""
Polished World Scene & Context-Aware Evidence Compositor
Features authentic slide contexts, real claim ledger metadata, precise bounding box highlighters,
and organic dual-pass ink sketch callouts.
"""

from pathlib import Path

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hero World Plate & Context-Aware Evidence Compositor</title>
  <style>
    :root {
      --bg: #080c14;
      --charcoal: #25313C;
      --cobalt: #1769C2;
      --teal: #178C83;
      --sunflower: #F5B72E;
      --coral: #ED6A4A;
      --cream: #F4E6C7;
      --card-bg: #141c2b;
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
      margin-bottom: 1.5rem;
      border-bottom: 1px solid #334155;
      padding-bottom: 1.25rem;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }
    h1 {
      margin: 0 0 0.4rem 0;
      color: var(--sunflower);
      font-size: 2rem;
      letter-spacing: -0.02em;
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
      padding: 0.65rem 1.4rem;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.9rem;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(23, 105, 194, 0.3);
      transition: all 0.15s ease;
    }
    .btn:hover {
      background: #1e7be6;
      transform: translateY(-1px);
    }
    .btn-secondary {
      background: #334155;
      box-shadow: none;
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

    /* 16:9 Master Video Compositor Frame */
    .viewport-frame {
      width: 100%;
      max-width: 1100px;
      height: 619px; /* 16:9 */
      margin: 0 auto;
      background: #000;
      border: 4px solid var(--charcoal);
      border-radius: 16px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 25px 60px rgba(0,0,0,0.7);
    }

    /* 1. Base Layer: Hero World Plate with subtle Ken Burns drift */
    .world-layer {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      transform-origin: center center;
    }

    /* 2. Middle Layer: Vignette / Evidence Rail Safe Zone */
    .rail-scrim {
      position: absolute;
      top: 0;
      right: 0;
      width: 60%;
      height: 100%;
      background: linear-gradient(to right, rgba(8, 12, 20, 0) 0%, rgba(8, 12, 20, 0.65) 35%, rgba(8, 12, 20, 0.92) 100%);
      pointer-events: none;
    }

    /* 3. Foreground Layer: 2.5D Evidence Card */
    .evidence-dock {
      position: absolute;
      top: 40px;
      right: 45px;
      width: 530px;
      height: 505px;
      background: var(--cream);
      border: 3.5px solid var(--charcoal);
      border-radius: 14px;
      box-shadow: 14px 14px 0px var(--charcoal);
      padding: 1.2rem;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      transform-origin: center center;
    }

    .evidence-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid var(--charcoal);
      padding-bottom: 0.5rem;
      margin-bottom: 0.6rem;
    }
    .evidence-title {
      font-weight: 900;
      font-size: 0.95rem;
      color: var(--charcoal);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .evidence-badge {
      background: var(--cobalt);
      color: #fff;
      font-size: 0.72rem;
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 800;
      letter-spacing: 0.05em;
    }

    .slide-crop-container {
      flex: 1;
      position: relative;
      border: 2px solid var(--charcoal);
      border-radius: 8px;
      overflow: hidden;
      background: #111;
    }
    .slide-crop-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    /* Dynamic SVG Overlay on the Evidence Card */
    .evidence-svg {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
    }

    /* Contextual Spoken Claim Banner */
    .annotation-pill {
      margin-top: 0.75rem;
      background: var(--charcoal);
      color: var(--sunflower);
      padding: 9px 14px;
      border-radius: 6px;
      font-weight: 800;
      font-size: 0.85rem;
      display: flex;
      flex-direction: column;
      gap: 2px;
      opacity: 0;
      transform: translateY(10px);
      transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .annotation-pill.visible {
      opacity: 1;
      transform: translateY(0);
    }
    .annotation-subtext {
      color: #94a3b8;
      font-weight: 500;
      font-size: 0.75rem;
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
        <h1>🎬 Context-Aware Evidence Compositor</h1>
        <div class="subtitle">Contextual slide bindings, organic ink sketch loops, and exact bounding-box highlighters.</div>
      </div>
      <div>
        <button class="btn" onclick="playScene()">▶️ Play Scene Sequence</button>
      </div>
    </header>

    <div class="controls">
      <label><strong>Select Scenario:</strong></label>
      <select id="scenario-select" onchange="changeScenario(this.value)">
        <option value="triopoly_paradox">1. The Great Valuation Paradox (S&P 500 vs Triopoly CAPE)</option>
        <option value="physics_penalty">2. The 3-to-1 Physics Penalty (Wafer Trade Ratio)</option>
        <option value="hourglass_bottleneck">3. The Inescapable Physical Reality (Hourglass Bottleneck)</option>
        <option value="nine_layer_stack">4. Sovereign Nine-Layer Stack (Memory Foundation)</option>
      </select>

      <button class="btn btn-secondary" onclick="resetScene()">⏮️ Reset</button>
      <span id="frame-display" style="margin-left: auto; font-family: monospace; color: var(--sunflower);">Frame: 0/120 (0.00s)</span>
    </div>

    <!-- 16:9 Composited Video Player Canvas -->
    <div class="viewport-frame">
      <!-- 1. Background Hero Scene Plate -->
      <img class="world-layer" id="world-bg" src="scene_assets/hero-sp500-double-failure-v1.png" alt="World Plate" />

      <!-- 2. Evidence Rail Scrim -->
      <div class="rail-scrim"></div>

      <!-- 3. 2.5D Evidence Plate Card -->
      <div class="evidence-dock" id="evidence-dock">
        <div class="evidence-header">
          <span class="evidence-title" id="evidence-title">THE GREAT VALUATION PARADOX</span>
          <span class="evidence-badge" id="evidence-badge">EXHIBIT #01</span>
        </div>

        <div class="slide-crop-container">
          <img class="slide-crop-img" id="slide-crop" src="slides/triopoly-paradox.png" alt="Slide Crop" />
          
          <!-- Animated Ink & Highlighter Vectors -->
          <svg class="evidence-svg" viewBox="0 0 500 320" id="card-svg">
            <defs>
              <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#ED6A4A" />
              </marker>
            </defs>

            <!-- Precise Bounding Box Highlighter Sweep -->
            <rect id="hl-rect" x="140" y="95" width="0" height="34" fill="#F5B72E" opacity="0.45" rx="5" />

            <!-- Organic Vector Ink Arrow -->
            <path id="ink-path" d="M 80,200 Q 125,140 145,115" fill="none" stroke="#ED6A4A" stroke-width="4.5" stroke-linecap="round" marker-end="url(#arrow)" stroke-dasharray="200" stroke-dashoffset="200" />

            <!-- Organic Dual-Pass Sketch Loop (Natural Hand-Drawn Feel) -->
            <path id="sketch-loop" d="M 140,112 C 140,85 360,80 375,108 C 390,135 150,145 138,118 C 132,100 240,88 350,92" fill="none" stroke="#ED6A4A" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="900" stroke-dashoffset="900" />
          </svg>
        </div>

        <!-- Contextual Spoken Claim Banner -->
        <div class="annotation-pill" id="claim-pill">
          <span id="claim-heading">⚖️ S&P 500 MULTIPLE DIVERGENCE</span>
          <span class="annotation-subtext" id="claim-subtext">Extreme forward CAPE multiple divergence versus hardware suppliers.</span>
        </div>
      </div>
    </div>

    <div class="timeline-bar">
      <span>0s</span>
      <input type="range" id="scrubber" min="0" max="120" value="0" oninput="renderFrame(parseInt(this.value))">
      <span>4.0s (120 Frames @ 30fps)</span>
    </div>
  </div>

  <script>
    const scenarios = {
      triopoly_paradox: {
        worldPlate: 'hero-sp500-double-failure-v1.png',
        slideImage: 'triopoly-paradox.png',
        title: 'THE GREAT VALUATION PARADOX',
        badge: 'EXHIBIT #01',
        heading: '⚖️ S&P 500 MULTIPLE DIVERGENCE',
        subtext: 'Contrasting extreme S&P 500 forward CAPE ratios with suppressed memory-triopoly valuations.',
        hl: { x: 130, y: 92, w: 260, h: 36 },
        arrow: 'M 75,200 Q 120,135 135,110',
        loop: 'M 125,110 C 125,82 390,78 405,108 C 420,138 140,148 126,118 C 118,98 230,86 380,90'
      },
      physics_penalty: {
        worldPlate: 'hero-fab-constraint-v1.png',
        slideImage: 'memory-3to1-penalty.png',
        title: 'THE 3-TO-1 PHYSICS PENALTY',
        badge: 'EXHIBIT #02',
        heading: '🔬 3X WAFER CONSUMPTION RATIO',
        subtext: 'HBM multi-die stacking consumes 3x more physical wafer capacity than conventional DRAM.',
        hl: { x: 140, y: 110, w: 270, h: 38 },
        arrow: 'M 85,220 Q 130,155 145,130',
        loop: 'M 135,128 C 135,98 410,95 425,126 C 440,158 150,168 136,136 C 128,114 240,102 400,106'
      },
      hourglass_bottleneck: {
        worldPlate: 'hero-hbm-bandwidth-v1.png',
        slideImage: 'silicon-hourglass-bottleneck.png',
        title: 'THE INESCAPABLE PHYSICAL REALITY',
        badge: 'EXHIBIT #03',
        heading: '⏳ SOFTWARE SCALES TO HARDWARE LIMITS',
        subtext: 'Software valuations bottleneck on physical silicon capacity, memory bandwidth, and power grids.',
        hl: { x: 115, y: 130, w: 290, h: 42 },
        arrow: 'M 70,240 Q 110,175 125,150',
        loop: 'M 110,150 C 110,118 410,114 425,148 C 440,182 125,192 112,158 C 104,134 220,122 395,126'
      },
      nine_layer_stack: {
        worldPlate: 'hero-contract-ovens-v1.png',
        slideImage: 'sovereign-nine-layer-stack.png',
        title: 'NINE-LAYER COMPUTE STACK',
        badge: 'EXHIBIT #04',
        heading: '🧱 MEMORY & INTERCONNECT FOUNDATION',
        subtext: 'Mapping sovereign infrastructure down through silicon packaging and high-bandwidth interconnects.',
        hl: { x: 135, y: 100, w: 260, h: 36 },
        arrow: 'M 80,210 Q 125,145 140,120',
        loop: 'M 130,118 C 130,90 395,86 410,116 C 425,146 145,156 132,126 C 124,104 235,92 385,96'
      }
    };

    let activeKey = 'triopoly_paradox';

    function remotionSpring(progress, damping = 20, stiffness = 85) {
      return 1 - Math.exp(-progress * (damping / 3)) * Math.cos(progress * Math.sqrt(stiffness) * 0.4);
    }

    const worldBg = document.getElementById('world-bg');
    const slideCrop = document.getElementById('slide-crop');
    const evidenceDock = document.getElementById('evidence-dock');
    const evidenceTitle = document.getElementById('evidence-title');
    const evidenceBadge = document.getElementById('evidence-badge');
    const claimHeading = document.getElementById('claim-heading');
    const claimSubtext = document.getElementById('claim-subtext');
    const hlRect = document.getElementById('hl-rect');
    const inkPath = document.getElementById('ink-path');
    const sketchLoop = document.getElementById('sketch-loop');
    const claimPill = document.getElementById('claim-pill');
    const scrubber = document.getElementById('scrubber');
    const frameDisplay = document.getElementById('frame-display');

    function applyScenarioData(key) {
      const s = scenarios[key];
      worldBg.src = `scene_assets/${s.worldPlate}`;
      slideCrop.src = `slides/${s.slideImage}`;
      evidenceTitle.innerText = s.title;
      evidenceBadge.innerText = s.badge;
      claimHeading.innerText = s.heading;
      claimSubtext.innerText = s.subtext;

      hlRect.setAttribute('x', s.hl.x);
      hlRect.setAttribute('y', s.hl.y);
      hlRect.setAttribute('height', s.hl.h);
      inkPath.setAttribute('d', s.arrow);
      sketchLoop.setAttribute('d', s.loop);
    }

    function renderFrame(frame) {
      frameDisplay.innerText = `Frame: ${frame}/120 (${(frame/30).toFixed(2)}s)`;
      scrubber.value = frame;
      const s = scenarios[activeKey];

      // 1. World Plate Subtle Ken Burns Parallax Drift (0 - 120)
      const worldScale = 1.0 + 0.04 * (frame / 120);
      const worldX = -8 * (frame / 120);
      worldBg.style.transform = `scale(${worldScale}) translate(${worldX}px, 0px)`;

      // 2. Evidence Card Entrance Spring (Frames 15 - 45)
      if (frame >= 15) {
        const t = Math.min((frame - 15) / 25, 1);
        const springVal = remotionSpring(t * 4, 18, 90);
        const scale = 0.88 + 0.12 * Math.min(Math.max(springVal, 0), 1);
        const opacity = Math.min((frame - 15) / 8, 1);
        evidenceDock.style.transform = `scale(${scale})`;
        evidenceDock.style.opacity = opacity;
      } else {
        evidenceDock.style.transform = 'scale(0.85)';
        evidenceDock.style.opacity = '0';
      }

      // 3. Highlighter Sweep (Frames 40 - 65)
      if (frame >= 40) {
        const hlT = Math.min((frame - 40) / 20, 1);
        hlRect.setAttribute('width', (s.hl.w * hlT).toString());
      } else {
        hlRect.setAttribute('width', '0');
      }

      // 4. Ink Arrow Trace (Frames 55 - 75)
      if (frame >= 55) {
        const arrowT = Math.min((frame - 55) / 18, 1);
        inkPath.style.strokeDashoffset = (200 * (1 - arrowT)).toString();
      } else {
        inkPath.style.strokeDashoffset = '200';
      }

      // 5. Chalk Sketch Loop & Claim Pill Pop (Frames 70 - 95)
      if (frame >= 70) {
        const loopT = Math.min((frame - 70) / 20, 1);
        sketchLoop.style.strokeDashoffset = (900 * (1 - loopT)).toString();
        claimPill.classList.add('visible');
      } else {
        sketchLoop.style.strokeDashoffset = '900';
        claimPill.classList.remove('visible');
      }
    }

    let isPlaying = false;
    let timer = null;

    function playScene() {
      if (isPlaying) cancelAnimationFrame(timer);
      isPlaying = true;
      let f = 0;
      function loop() {
        renderFrame(f);
        f++;
        if (f <= 120 && isPlaying) {
          timer = setTimeout(() => requestAnimationFrame(loop), 1000 / 30);
        } else {
          isPlaying = false;
        }
      }
      loop();
    }

    function resetScene() {
      isPlaying = false;
      if (timer) clearTimeout(timer);
      renderFrame(0);
    }

    function changeScenario(key) {
      activeKey = key;
      applyScenarioData(key);
      resetScene();
      playScene();
    }

    window.onload = () => {
      applyScenarioData(activeKey);
      renderFrame(0);
      setTimeout(playScene, 400);
    };
  </script>
</body>
</html>
"""

out_p = Path("content/video_engine/review/world_scene_evidence_showcase.html")
out_p.parent.mkdir(parents=True, exist_ok=True)
out_p.write_text(html, encoding="utf-8")
print(f"Updated Context-Aware Showcase at: {out_p.resolve()}")
