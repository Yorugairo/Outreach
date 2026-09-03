"""
HyperFrames Causal Braid Engine Showcase
Integrates the full 90-second story arc from hyperframes-opening-v1 with
deterministic evidence docking, causal braid reference rails, and decoupled stat badges.
"""

from pathlib import Path

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HyperFrames Causal Braid Engine Showcase</title>
  <style>
    :root {
      --bg: #081824;
      --charcoal: #25313C;
      --cobalt: #1769C2;
      --teal: #178C83;
      --sunflower: #e8c56f;
      --secondary-teal: #77e1e8;
      --coral: #ED6A4A;
      --cream: #F4E6C7;
      --dark-card: #0c2233;
    }
    body {
      font-family: Inter, system-ui, sans-serif;
      background: var(--bg);
      color: #fff3d2;
      margin: 0;
      padding: 2rem;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    header {
      margin-bottom: 1.5rem;
      border-bottom: 1px solid #1e3a52;
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
    .beat-selector {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
    }
    .beat-btn {
      background: var(--dark-card);
      color: #cbd5e1;
      border: 1px solid #1e3a52;
      padding: 0.6rem 1rem;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.85rem;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .beat-btn.active {
      background: var(--cobalt);
      color: #fff;
      border-color: var(--secondary-teal);
      box-shadow: 0 4px 12px rgba(23, 105, 194, 0.4);
    }
    .beat-btn:hover {
      border-color: var(--sunflower);
    }

    /* 16:9 Master Viewport */
    .viewport-frame {
      width: 100%;
      max-width: 1100px;
      height: 619px;
      margin: 0 auto;
      background: #05131e;
      border: 4px solid var(--charcoal);
      border-radius: 16px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 25px 60px rgba(0,0,0,0.7);
    }

    /* Base World Layer (Elevator World) */
    .world-bg {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      filter: saturate(0.85) brightness(0.8);
      transform-origin: center center;
      transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1), filter 0.8s ease;
    }

    .vignette-scrim {
      position: absolute;
      inset: 0;
      box-shadow: inset 0 0 240px rgba(5,19,30,0.85);
      pointer-events: none;
    }

    /* Causal Reference Rail (Left Side Tabs) */
    .braid-rail {
      position: absolute;
      top: 40px;
      left: 40px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      z-index: 10;
    }
    .braid-tab {
      width: 190px;
      height: 110px;
      background: var(--cream);
      border: 2.5px solid var(--charcoal);
      border-radius: 8px;
      box-shadow: 6px 6px 0px var(--charcoal);
      overflow: hidden;
      position: relative;
      transform: translateX(-240px);
      opacity: 0;
      transition: all 0.45s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .braid-tab.docked {
      transform: translateX(0);
      opacity: 1;
    }
    .braid-tab img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .braid-label {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background: rgba(37, 49, 60, 0.92);
      color: var(--sunflower);
      font-size: 0.65rem;
      font-weight: 800;
      padding: 3px 6px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* Primary Active Evidence Dock (Right / Center) */
    .primary-dock {
      position: absolute;
      top: 35px;
      right: 40px;
      width: 560px;
      height: 525px;
      background: var(--cream);
      border: 3.5px solid var(--charcoal);
      border-radius: 14px;
      box-shadow: 14px 14px 0px var(--charcoal);
      padding: 1.2rem;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      z-index: 20;
      transform-origin: center center;
      transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .primary-dock.hidden {
      transform: scale(0.85) translateX(120px);
      opacity: 0;
      pointer-events: none;
    }

    .dock-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid var(--charcoal);
      padding-bottom: 0.45rem;
      margin-bottom: 0.55rem;
    }
    .dock-title {
      font-weight: 900;
      font-size: 0.95rem;
      color: var(--charcoal);
      text-transform: uppercase;
    }
    .dock-badge {
      background: var(--cobalt);
      color: #fff;
      font-size: 0.72rem;
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 800;
    }

    .dock-img-wrap {
      flex: 1;
      border: 2px solid var(--charcoal);
      border-radius: 8px;
      overflow: hidden;
      background: #000;
      position: relative;
    }
    .dock-img-wrap img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    /* Decoupled Stat Rail */
    .dock-stats {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.6rem;
      margin-top: 0.7rem;
    }
    .stat-pill {
      background: var(--charcoal);
      color: #fff;
      padding: 8px 10px;
      border-radius: 6px;
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }
    .stat-label {
      font-size: 0.68rem;
      font-weight: 800;
      color: #94a3b8;
      text-transform: uppercase;
    }
    .stat-val {
      font-size: 1.15rem;
      font-weight: 900;
      font-family: monospace;
      color: var(--sunflower);
    }

    /* Risk Stamp Stack */
    .risk-stack {
      position: absolute;
      bottom: 25px;
      left: 40px;
      display: flex;
      gap: 10px;
      z-index: 30;
      opacity: 0;
      transform: translateY(15px);
      transition: all 0.35s ease;
    }
    .risk-stack.visible {
      opacity: 1;
      transform: translateY(0);
    }
    .risk-badge {
      padding: 8px 14px;
      border: 2.5px solid var(--coral);
      border-radius: 8px;
      background: rgba(37, 49, 60, 0.95);
      color: var(--coral);
      font-weight: 900;
      font-size: 0.85rem;
      box-shadow: 4px 4px 0px rgba(0,0,0,0.3);
      letter-spacing: 0.05em;
    }

    /* Spoken Narration Caption Bar */
    .caption-banner {
      position: absolute;
      bottom: 25px;
      left: 260px;
      right: 40px;
      background: rgba(5,19,30,0.92);
      border: 2px solid var(--sunflower);
      border-radius: 12px;
      padding: 12px 20px;
      color: #fff7df;
      font-size: 1.05rem;
      font-weight: 600;
      line-height: 1.3;
      z-index: 25;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      transition: all 0.3s ease;
    }
    .caption-banner.full-width {
      left: 120px;
      right: 120px;
      text-align: center;
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
        <h1>🧬 HyperFrames Causal Braid Engine</h1>
        <div class="subtitle">Complete 90s opening choreography: elevator anchor ➔ memory stack ➔ factory braid ➔ index flows ➔ callback.</div>
      </div>
      <div>
        <button class="beat-btn active" style="background: var(--cobalt); color: #fff;" onclick="playFull90s()">▶️ Play Full 90s Sequence</button>
      </div>
    </header>

    <div class="beat-selector">
      <button class="beat-btn active" onclick="setBeat(1)">Beat 1: The Wrong Bubble (0s–2.4s)</button>
      <button class="beat-btn" onclick="setBeat(2)">Beat 2: Memory Product (2.4s–11.6s)</button>
      <button class="beat-btn" onclick="setBeat(3)">Beat 3: Three Supports Braid (11.6s–23.0s)</button>
      <button class="beat-btn" onclick="setBeat(4)">Beat 4: Automatic Inflows (23.0s–45.8s)</button>
      <button class="beat-btn" onclick="setBeat(5)">Beat 5: Physical Bottleneck (45.8s–75.9s)</button>
      <button class="beat-btn" onclick="setBeat(6)">Beat 6: Thesis Callback (75.9s–90s)</button>
    </div>

    <!-- 16:9 Viewport Canvas -->
    <div class="viewport-frame">
      <img class="world-bg" id="world-bg" src="hyperframes_assets/wrong-bubble-elevators-v2.png" alt="World Elevator Mechanism" />
      <div class="vignette-scrim"></div>

      <!-- Causal Braid Rail (Docked Miniature Evidence Tabs) -->
      <div class="braid-rail">
        <div class="braid-tab" id="tab-memory">
          <img src="hyperframes_assets/memory-skepticism-v2.png" alt="Memory Stack" />
          <div class="braid-label">① MEMORY PRODUCT</div>
        </div>
        <div class="braid-tab" id="tab-factory">
          <img src="hyperframes_assets/memory-three-supports-v1.png" alt="Factory Capacity" />
          <div class="braid-label">② 3-SUPPORT BRAID</div>
        </div>
        <div class="braid-tab" id="tab-fund">
          <img src="hyperframes_assets/index-fund-weighted-inflows-v2.png" alt="Index Fund Inflows" />
          <div class="braid-label">③ WEIGHTED INFLOWS</div>
        </div>
      </div>

      <!-- Primary Active Evidence Dock Card -->
      <div class="primary-dock" id="primary-dock">
        <div class="dock-header">
          <span class="dock-title" id="dock-title">MEMORY PRODUCT EVIDENCE</span>
          <span class="dock-badge" id="dock-badge">STAGE 1</span>
        </div>
        <div class="dock-img-wrap">
          <img id="dock-img" src="hyperframes_assets/memory-skepticism-v2.png" alt="Active Evidence" />
        </div>
        <div class="dock-stats">
          <div class="stat-pill">
            <span class="stat-label" id="stat-label-1">PHYSICAL PRODUCT</span>
            <span class="stat-val" id="stat-val-1" style="color: var(--sunflower);">HBM3E</span>
          </div>
          <div class="stat-pill">
            <span class="stat-label" id="stat-label-2">SCARCITY DURATION</span>
            <span class="stat-val" id="stat-val-2" style="color: var(--secondary-teal);">5-YR TAKE</span>
          </div>
        </div>
      </div>

      <!-- Micro-Risk Warning Stamps -->
      <div class="risk-stack" id="risk-stack">
        <div class="risk-badge">⚠️ CORRECTION</div>
        <div class="risk-badge">⚠️ OVERPRICED</div>
        <div class="risk-badge">⚠️ CYCLICAL</div>
      </div>

      <!-- Narration Caption Bar -->
      <div class="caption-banner" id="caption-banner">
        "The market may be labeling the wrong bubble."
      </div>
    </div>

    <div class="timeline-bar">
      <span>0s</span>
      <input type="range" id="scrubber" min="0" max="90" value="0" step="0.5" oninput="seekTime(parseFloat(this.value))">
      <span>90.0s Total Arc</span>
    </div>
  </div>

  <script>
    const beats = {
      1: {
        dockVisible: false,
        dockedTabs: [],
        worldScale: 1.0,
        worldFilter: 'saturate(0.9) brightness(0.85)',
        caption: 'The market may be labeling the wrong bubble. Same chart shape · different mechanism.',
        captionFull: true,
        riskStack: false
      },
      2: {
        dockVisible: true,
        title: 'MEMORY PRODUCT EVIDENCE',
        badge: 'STAGE 1',
        img: 'memory-skepticism-v2.png',
        label1: 'PHYSICAL PRODUCT',
        val1: 'HBM3E',
        label2: 'SCARCITY DURATION',
        val2: '5-YR TAKE',
        dockedTabs: [],
        worldScale: 1.03,
        worldFilter: 'saturate(0.65) brightness(0.65)',
        caption: 'AI memory stocks have gone vertical. That is normally where sensible people step back and say: bubble. Look at the product, not just the price chart.',
        captionFull: false,
        riskStack: false
      },
      3: {
        dockVisible: true,
        title: 'THREE-SUPPORT CAUSAL BRAID',
        badge: 'STAGE 2',
        img: 'memory-three-supports-v1.png',
        label1: 'DEMAND & CAPACITY',
        val1: '3 : 1 RATIO',
        label2: 'CONTRACTED DEPOSITS',
        val2: '$140B+',
        dockedTabs: ['tab-memory'],
        worldScale: 1.05,
        worldFilter: 'saturate(0.55) brightness(0.55)',
        caption: 'Underneath the chart is a product customers cannot get enough of: demand, capacity, and commitment as one braid.',
        captionFull: false,
        riskStack: false
      },
      4: {
        dockVisible: true,
        title: 'AUTOMATIC INDEX INFLOW FEEDBACK',
        badge: 'STAGE 3',
        img: 'index-fund-weighted-inflows-v2.png',
        label1: 'TOP-10 CONCENTRATION',
        val1: '38.4%',
        label2: 'PASSIVE AUTO-FLOW',
        val2: '$4.2B/DAY',
        dockedTabs: ['tab-memory', 'tab-factory'],
        worldScale: 1.06,
        worldFilter: 'saturate(0.5) brightness(0.5)',
        caption: 'Automatic contributions keep buying the biggest holdings because they are already the biggest: weights + flows create systemic concentration.',
        captionFull: false,
        riskStack: false
      },
      5: {
        dockVisible: true,
        title: 'PHYSICAL CAPACITY REPRICING',
        badge: 'STAGE 4',
        img: 'bottleneck-repricing-v1.png',
        label1: 'FAB LEAD TIME',
        val1: '3–5 YRS',
        label2: 'CLEANROOM CAP',
        val2: '100% UTIL',
        dockedTabs: ['tab-memory', 'tab-factory', 'tab-fund'],
        worldScale: 1.07,
        worldFilter: 'saturate(0.45) brightness(0.45)',
        caption: 'What we are seeing is not speculative euphoria—it is a physical bottleneck being repriced at the gate.',
        captionFull: false,
        riskStack: true
      },
      6: {
        dockVisible: false,
        dockedTabs: [],
        worldScale: 1.0,
        worldFilter: 'saturate(1.0) brightness(0.95)',
        caption: 'Same visible move. Different mechanism. The elevator returns only after the support is proven.',
        captionFull: true,
        riskStack: false
      }
    };

    let activeBeat = 1;
    const worldBg = document.getElementById('world-bg');
    const primaryDock = document.getElementById('primary-dock');
    const dockTitle = document.getElementById('dock-title');
    const dockBadge = document.getElementById('dock-badge');
    const dockImg = document.getElementById('dock-img');
    const statLabel1 = document.getElementById('stat-label-1');
    const statVal1 = document.getElementById('stat-val-1');
    const statLabel2 = document.getElementById('stat-label-2');
    const statVal2 = document.getElementById('stat-val-2');
    const riskStack = document.getElementById('risk-stack');
    const captionBanner = document.getElementById('caption-banner');
    const scrubber = document.getElementById('scrubber');

    function applyBeat(bNum) {
      activeBeat = bNum;
      const b = beats[bNum];

      // Update world plate
      worldBg.style.transform = `scale(${b.worldScale})`;
      worldBg.style.filter = b.worldFilter;

      // Update primary dock
      if (b.dockVisible) {
        primaryDock.classList.remove('hidden');
        dockTitle.innerText = b.title;
        dockBadge.innerText = b.badge;
        dockImg.src = `hyperframes_assets/${b.img}`;
        statLabel1.innerText = b.label1;
        statVal1.innerText = b.val1;
        statLabel2.innerText = b.label2;
        statVal2.innerText = b.val2;
      } else {
        primaryDock.classList.add('hidden');
      }

      // Update docked tabs on left rail
      ['tab-memory', 'tab-factory', 'tab-fund'].forEach(tabId => {
        const el = document.getElementById(tabId);
        if (b.dockedTabs.includes(tabId)) {
          el.classList.add('docked');
        } else {
          el.classList.remove('docked');
        }
      });

      // Update risk stack
      if (b.riskStack) {
        riskStack.classList.add('visible');
      } else {
        riskStack.classList.remove('visible');
      }

      // Caption
      captionBanner.innerText = b.caption;
      if (b.captionFull) {
        captionBanner.classList.add('full-width');
      } else {
        captionBanner.classList.remove('full-width');
      }

      // Highlight active button
      document.querySelectorAll('.beat-btn').forEach((btn, idx) => {
        if (idx === bNum) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    function setBeat(num) {
      applyBeat(num);
    }

    function seekTime(seconds) {
      scrubber.value = seconds;
      if (seconds < 2.4) setBeat(1);
      else if (seconds < 11.6) setBeat(2);
      else if (seconds < 23.0) setBeat(3);
      else if (seconds < 45.8) setBeat(4);
      else if (seconds < 75.9) setBeat(5);
      else setBeat(6);
    }

    let isPlaying = false;
    let timer = null;

    function playFull90s() {
      if (isPlaying) clearInterval(timer);
      isPlaying = true;
      let sec = 0;
      timer = setInterval(() => {
        sec += 0.5;
        seekTime(sec);
        if (sec >= 90) {
          clearInterval(timer);
          isPlaying = false;
        }
      }, 250); // fast-forward demo speed
    }

    window.onload = () => {
      applyBeat(1);
    };
  </script>
</body>
</html>
"""

out_p = Path("content/video_engine/review/hyperframes_braid_showcase.html")
out_p.parent.mkdir(parents=True, exist_ok=True)
out_p.write_text(html, encoding="utf-8")
print(f"Generated HyperFrames Braid Showcase at: {out_p.resolve()}")
