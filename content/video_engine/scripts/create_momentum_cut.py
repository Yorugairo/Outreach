"""
High-Momentum 20-Second Dynamic Evidence Cut
Features single clean evidence dock, animated causal connector beams (mechanism links),
elevator car motion, and pure cinematic momentum without clutter.
"""

from pathlib import Path

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>High-Momentum 20-Second Dynamic Cut</title>
  <style>
    :root {
      --bg: #060e17;
      --charcoal: #25313C;
      --cobalt: #1769C2;
      --teal: #178C83;
      --sunflower: #e8c56f;
      --cyan: #77e1e8;
      --coral: #ED6A4A;
      --cream: #F4E6C7;
      --emerald: #10B981;
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
    .controls {
      display: flex;
      gap: 1rem;
      align-items: center;
      margin-bottom: 1.5rem;
      background: var(--dark-card);
      padding: 1rem 1.5rem;
      border-radius: 12px;
      border: 1px solid #1e3a52;
    }
    .btn {
      background: var(--cobalt);
      color: #fff;
      border: none;
      padding: 0.7rem 1.6rem;
      border-radius: 8px;
      font-weight: 800;
      font-size: 0.95rem;
      cursor: pointer;
      box-shadow: 0 4px 14px rgba(23, 105, 194, 0.4);
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
      box-shadow: 0 25px 60px rgba(0,0,0,0.8);
    }

    /* Base World Layer (Elevator World with Living Mechanical Motion) */
    .world-bg {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      filter: saturate(0.95) brightness(0.9);
      transform-origin: center center;
      transition: transform 0.05s linear;
    }

    /* Left Narrative Stage Scrim */
    .narrative-scrim {
      position: absolute;
      top: 0;
      right: 0;
      width: 58%;
      height: 100%;
      background: linear-gradient(to right, rgba(6, 14, 23, 0) 0%, rgba(6, 14, 23, 0.6) 30%, rgba(6, 14, 23, 0.94) 100%);
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.4s ease;
    }
    .narrative-scrim.active {
      opacity: 1;
    }

    /* Dynamic SVG Mechanism Connector Beam */
    .mechanism-svg {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 15;
    }

    /* Single Focused 2.5D Evidence Dock */
    .evidence-dock {
      position: absolute;
      top: 35px;
      right: 45px;
      width: 540px;
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
      opacity: 0;
      transform: scale(0.85) translateX(120px) rotate(2deg);
      transition: all 0.45s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .evidence-dock.active {
      opacity: 1;
      transform: scale(1) translateX(0) rotate(0deg);
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
      letter-spacing: 0.04em;
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

    /* Decoupled Live Stat Rail */
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
      font-size: 1.2rem;
      font-weight: 900;
      font-family: monospace;
      color: var(--sunflower);
    }

    /* Opening / Closing Hero Banner */
    .hero-banner {
      position: absolute;
      top: 45px;
      left: 60px;
      background: rgba(5,19,30,0.94);
      border: 3px solid var(--sunflower);
      border-radius: 12px;
      padding: 14px 24px;
      color: #fff;
      font-weight: 900;
      font-size: 1.3rem;
      box-shadow: 0 10px 30px rgba(0,0,0,0.6);
      opacity: 0;
      transform: translateY(-20px);
      transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
      z-index: 30;
    }
    .hero-banner.visible {
      opacity: 1;
      transform: translateY(0);
    }
    .hero-banner small {
      display: block;
      color: var(--cyan);
      font-size: 0.85rem;
      font-weight: 500;
      margin-top: 4px;
    }

    /* Narration Caption Bar */
    .caption-banner {
      position: absolute;
      bottom: 25px;
      left: 60px;
      right: 60px;
      background: rgba(5,19,30,0.92);
      border: 2px solid var(--sunflower);
      border-radius: 12px;
      padding: 12px 22px;
      color: #fff7df;
      font-size: 1.05rem;
      font-weight: 600;
      line-height: 1.3;
      text-align: center;
      z-index: 25;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      transition: all 0.25s ease;
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
        <h1>⚡ High-Momentum 20-Second Dynamic Cut</h1>
        <div class="subtitle">Single evidence focus + dynamic mechanism connector beams + living elevator parallax.</div>
      </div>
      <div>
        <button class="btn" onclick="startPlayback()">▶️ Play 20-Second Sequence</button>
      </div>
    </header>

    <div class="controls">
      <button class="btn btn-secondary" onclick="pauseToggle()" id="play-pause-btn">⏸️ Pause</button>
      <button class="btn btn-secondary" onclick="restart()">⏮️ Restart</button>
      <span id="time-display" style="margin-left: auto; font-family: monospace; font-size: 1.15rem; color: var(--sunflower); font-weight: 800;">00:00.0 / 00:20.0</span>
    </div>

    <!-- 16:9 Master Viewport -->
    <div class="viewport-frame">
      <!-- 1. Background Elevator World Plate -->
      <img class="world-bg" id="world-bg" src="hyperframes_assets/wrong-bubble-elevators-v2.png" alt="World Elevator Mechanism" />
      
      <!-- 2. Dark Scrim for Evidence Mode -->
      <div class="narrative-scrim" id="scrim"></div>

      <!-- 3. Dynamic Causal Connector Beam (Mechanism Link) -->
      <svg class="mechanism-svg" viewBox="0 0 1100 619">
        <defs>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>
        <!-- Causal energy connector line extending from the left elevator mechanism to the evidence dock -->
        <path id="connector-beam" d="M 280,310 Q 420,290 560,295" fill="none" stroke="#e8c56f" stroke-width="5" stroke-linecap="round" filter="url(#glow)" stroke-dasharray="400" stroke-dashoffset="400" opacity="0" />
        <circle id="connector-pulse" cx="280" cy="310" r="7" fill="#77e1e8" stroke="#e8c56f" stroke-width="3" opacity="0" />
      </svg>

      <!-- 4. Single Focused 2.5D Evidence Dock Card -->
      <div class="evidence-dock" id="evidence-dock">
        <div class="dock-header">
          <span class="dock-title" id="dock-title">MEMORY PRODUCT EVIDENCE</span>
          <span class="dock-badge" id="dock-badge">EXHIBIT #01</span>
        </div>
        <div class="dock-img-wrap">
          <img id="dock-img" src="hyperframes_assets/memory-skepticism-v2.png" alt="Active Evidence" />
        </div>
        <div class="dock-stats">
          <div class="stat-pill">
            <span class="stat-label" id="stat-label-1">PHYSICAL PRODUCT</span>
            <span class="stat-val" id="stat-val-1">HBM3E</span>
          </div>
          <div class="stat-pill">
            <span class="stat-label" id="stat-label-2">CONTRACT VALUE</span>
            <span class="stat-val" id="stat-val-2" style="color: var(--cyan);">$140B+</span>
          </div>
        </div>
      </div>

      <!-- 5. Opening / Callback Thesis Banner -->
      <div class="hero-banner" id="hero-banner">
        THE WRONG BUBBLE
        <small>same chart shape · different mechanism</small>
      </div>

      <!-- 6. Narration Caption Bar -->
      <div class="caption-banner" id="caption-banner">
        "The market may be labeling the wrong bubble."
      </div>
    </div>

    <div class="timeline-bar">
      <span>0.0s</span>
      <input type="range" id="scrubber" min="0" max="20" value="0" step="0.05" oninput="seekTo(parseFloat(this.value))">
      <span>20.0s Total</span>
    </div>
  </div>

  <script>
    const timeline = [
      {
        start: 0.0,
        end: 3.5,
        type: 'intro',
        worldY: 0,
        worldScale: 1.0,
        scrim: false,
        dock: false,
        beam: false,
        bannerText: 'THE WRONG BUBBLE',
        bannerSub: 'same chart shape · different mechanism',
        banner: true,
        caption: 'The market may be labeling the wrong bubble. Same visible chart move—different underlying mechanism.'
      },
      {
        start: 3.5,
        end: 9.5,
        type: 'evidence_1',
        title: 'MEMORY PRODUCT EVIDENCE',
        badge: 'EXHIBIT #01',
        img: 'memory-skepticism-v2.png',
        label1: 'PHYSICAL PRODUCT',
        val1: 'HBM3E',
        label2: '5-YEAR COMMITMENTS',
        val2: '$140B+',
        val2Color: '#77e1e8',
        worldY: -12,
        worldScale: 1.04,
        scrim: true,
        dock: true,
        beam: true,
        beamPath: 'M 260,330 Q 410,290 560,290',
        pulsePos: [260, 330],
        banner: false,
        caption: 'AI memory stocks went vertical. Sensible people say: bubble. But look at the product, not just the price chart.'
      },
      {
        start: 9.5,
        end: 15.5,
        type: 'evidence_2',
        title: 'PHYSICAL CAPACITY BOTTLENECK',
        badge: 'EXHIBIT #02',
        img: 'memory-three-supports-v1.png',
        label1: 'WAFER TRADE RATIO',
        val1: '3 : 1 PENALTY',
        label2: 'GLOBAL SUPPLY CHOKE',
        val2: '96% TRIOPOLY',
        val2Color: '#e8c56f',
        worldY: -22,
        worldScale: 1.06,
        scrim: true,
        dock: true,
        beam: true,
        beamPath: 'M 240,280 Q 400,290 560,290',
        pulsePos: [240, 280],
        banner: false,
        caption: 'Underneath is a physical supply constraint: 3-to-1 wafer penalties and contracted capacity across three manufacturers.'
      },
      {
        start: 15.5,
        end: 20.0,
        type: 'callback',
        worldY: 0,
        worldScale: 1.0,
        scrim: false,
        dock: false,
        beam: false,
        bannerText: 'SAME MOVE. DIFFERENT MECHANISM.',
        bannerSub: 'the elevator returns only after the support is proven',
        banner: true,
        caption: 'Same visible move. Different mechanism. The elevator returns only after the support is proven.'
      }
    ];

    const worldBg = document.getElementById('world-bg');
    const scrim = document.getElementById('scrim');
    const evidenceDock = document.getElementById('evidence-dock');
    const dockTitle = document.getElementById('dock-title');
    const dockBadge = document.getElementById('dock-badge');
    const dockImg = document.getElementById('dock-img');
    const statLabel1 = document.getElementById('stat-label-1');
    const statVal1 = document.getElementById('stat-val-1');
    const statLabel2 = document.getElementById('stat-label-2');
    const statVal2 = document.getElementById('stat-val-2');
    const connectorBeam = document.getElementById('connector-beam');
    const connectorPulse = document.getElementById('connector-pulse');
    const heroBanner = document.getElementById('hero-banner');
    const captionBanner = document.getElementById('caption-banner');
    const scrubber = document.getElementById('scrubber');
    const timeDisplay = document.getElementById('time-display');
    const playPauseBtn = document.getElementById('play-pause-btn');

    let currentTime = 0;
    let isRunning = false;
    let animHandle = null;
    let lastTimestamp = null;

    function renderTime(t) {
      currentTime = t;
      scrubber.value = t;
      timeDisplay.innerText = `00:${t.toFixed(1).padStart(4, '0')} / 00:20.0`;

      const b = timeline.find(item => t >= item.start && t < item.end) || timeline[timeline.length - 1];

      // 1. Continuous Parallax Camera Drift
      worldBg.style.transform = `scale(${b.worldScale}) translateY(${b.worldY}px)`;

      // 2. Scrim
      if (b.scrim) scrim.classList.add('active');
      else scrim.classList.remove('active');

      // 3. Single Evidence Dock
      if (b.dock) {
        evidenceDock.classList.add('active');
        dockTitle.innerText = b.title;
        dockBadge.innerText = b.badge;
        dockImg.src = `hyperframes_assets/${b.img}`;
        statLabel1.innerText = b.label1;
        statVal1.innerText = b.val1;
        statLabel2.innerText = b.label2;
        statVal2.innerText = b.val2;
        statVal2.style.color = b.val2Color || 'var(--sunflower)';
      } else {
        evidenceDock.classList.remove('active');
      }

      // 4. Dynamic Causal Connector Beam (Mechanism Link)
      if (b.beam) {
        connectorBeam.setAttribute('d', b.beamPath);
        connectorBeam.style.opacity = '1';
        connectorBeam.style.strokeDashoffset = '0';
        connectorBeam.style.transition = 'stroke-dashoffset 0.5s ease-out, opacity 0.3s ease';
        connectorPulse.setAttribute('cx', b.pulsePos[0]);
        connectorPulse.setAttribute('cy', b.pulsePos[1]);
        connectorPulse.style.opacity = '1';
      } else {
        connectorBeam.style.opacity = '0';
        connectorBeam.style.strokeDashoffset = '400';
        connectorPulse.style.opacity = '0';
      }

      // 5. Hero Banner
      if (b.banner) {
        heroBanner.innerHTML = `${b.bannerText}<small>${b.bannerSub}</small>`;
        heroBanner.classList.add('visible');
      } else {
        heroBanner.classList.remove('visible');
      }

      // 6. Caption
      captionBanner.innerText = `"${b.caption}"`;
    }

    function tick(timestamp) {
      if (!isRunning) return;
      if (!lastTimestamp) lastTimestamp = timestamp;
      const delta = (timestamp - lastTimestamp) / 1000;
      lastTimestamp = timestamp;

      currentTime += delta;
      if (currentTime >= 20.0) {
        currentTime = 20.0;
        renderTime(20.0);
        isRunning = false;
        playPauseBtn.innerText = '▶️ Play';
        return;
      }

      renderTime(currentTime);
      animHandle = requestAnimationFrame(tick);
    }

    function startPlayback() {
      currentTime = 0;
      isRunning = true;
      lastTimestamp = null;
      playPauseBtn.innerText = '⏸️ Pause';
      if (animHandle) cancelAnimationFrame(animHandle);
      animHandle = requestAnimationFrame(tick);
    }

    function pauseToggle() {
      if (isRunning) {
        isRunning = false;
        playPauseBtn.innerText = '▶️ Play';
        if (animHandle) cancelAnimationFrame(animHandle);
      } else {
        if (currentTime >= 20.0) currentTime = 0;
        isRunning = true;
        lastTimestamp = null;
        playPauseBtn.innerText = '⏸️ Pause';
        animHandle = requestAnimationFrame(tick);
      }
    }

    function restart() {
      currentTime = 0;
      renderTime(0);
      if (isRunning) lastTimestamp = null;
    }

    function seekTo(val) {
      renderTime(val);
      lastTimestamp = null;
    }

    window.onload = () => {
      startPlayback();
    };
  </script>
</body>
</html>
"""

out_p = Path("content/video_engine/review/momentum_20s_cut.html")
out_p.parent.mkdir(parents=True, exist_ok=True)
out_p.write_text(html, encoding="utf-8")
print(f"Generated High-Momentum 20-Second Cut at: {out_p.resolve()}")
