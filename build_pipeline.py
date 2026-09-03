from pathlib import Path

html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Modular Scene Evidence Pipeline (1-2 Pieces per Plate)</title>
  <style>
    :root {
      --bg: #060e17;
      --charcoal: #25313C;
      --cobalt: #1769C2;
      --teal: #178C83;
      --sunflower: #e8c56f;
      --secondary-teal: #77e1e8;
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

    /* Base World Layer Plate */
    .world-bg {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      filter: saturate(0.95) brightness(0.9);
      transform-origin: center center;
      transition: opacity 0.5s ease, transform 0.1s linear;
    }

    /* Right Evidence Rail Scrim */
    .rail-scrim {
      position: absolute;
      top: 0;
      right: 0;
      width: 60%;
      height: 100%;
      background: linear-gradient(to right, rgba(6, 14, 23, 0) 0%, rgba(6, 14, 23, 0.65) 35%, rgba(6, 14, 23, 0.94) 100%);
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.4s ease;
    }
    .rail-scrim.active {
      opacity: 1;
    }

    /* Single 2.5D Evidence Dock Card */
    .evidence-dock {
      position: absolute;
      top: 35px;
      right: 40px;
      width: 550px;
      height: 525px;
      background: var(--cream);
      border: 3.5px solid var(--charcoal);
      border-radius: 14px;
      box-shadow: 14px 14px 0px var(--charcoal);
      padding: 1.25rem;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      z-index: 20;
      transform-origin: center center;
      opacity: 0;
      transform: scale(0.86) translateX(120px);
      transition: all 0.45s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .evidence-dock.active {
      opacity: 1;
      transform: scale(1) translateX(0);
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

    /* 100% Intact Slide Viewport */
    .slide-view-container {
      flex: 1;
      border: 2px solid var(--charcoal);
      border-radius: 8px;
      overflow: hidden;
      background: #000;
      position: relative;
    }
    .slide-view-img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
      transition: opacity 0.3s ease;
    }

    /* Decoupled Live Stat Rail */
    .badges-rail {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.6rem;
      margin-top: 0.7rem;
    }
    .stat-card {
      background: var(--charcoal);
      color: #fff;
      padding: 8px 12px;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      opacity: 0;
      transform: translateY(10px);
      transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stat-card.visible {
      opacity: 1;
      transform: translateY(0);
    }
    .stat-label {
      font-size: 0.68rem;
      font-weight: 800;
      color: #94a3b8;
      text-transform: uppercase;
    }
    .stat-val-row {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-top: 2px;
    }
    .stat-num {
      font-size: 1.25rem;
      font-weight: 900;
      font-family: monospace;
      color: var(--sunflower);
    }
    .stat-tag {
      font-size: 0.7rem;
      font-weight: 800;
      padding: 1px 5px;
      border-radius: 3px;
    }

    /* Citation Footer */
    .citation-footer {
      margin-top: 0.55rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.72rem;
      color: var(--charcoal);
      font-weight: 700;
      opacity: 0.75;
      border-top: 1px dashed var(--charcoal);
      padding-top: 0.35rem;
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
      transition: all 0.3s ease;
    }

    /* Scene Wipe Curtain Transition */
    .scene-wipe-curtain {
      position: absolute;
      inset: 0;
      background: var(--bg);
      z-index: 50;
      transform: scaleX(0);
      transform-origin: right center;
      transition: transform 0.45s cubic-bezier(0.77, 0, 0.175, 1);
    }
    .scene-wipe-curtain.wipe-in {
      transform: scaleX(1);
      transform-origin: left center;
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
        <h1>Modular Scene Evidence Pipeline Engine</h1>
        <div class="subtitle">World Plate (Narrative) -> Supporting Evidence 1 + Stats -> Supporting Evidence 2 + Stats -> Clean Board Wipe.</div>
      </div>
      <div>
        <button class="btn" onclick="startPlayback()">Play 22s Sequence</button>
      </div>
    </header>

    <div class="controls">
      <button class="btn btn-secondary" onclick="pauseToggle()" id="play-pause-btn">Pause</button>
      <button class="btn btn-secondary" onclick="restart()">Restart</button>
      <span id="time-display" style="margin-left: auto; font-family: monospace; font-size: 1.15rem; color: var(--sunflower); font-weight: 800;">00:00.0 / 00:22.0</span>
    </div>

    <!-- 16:9 Master Viewport -->
    <div class="viewport-frame">
      <!-- 1. Background World Plate -->
      <img class="world-bg" id="world-bg" src="scene_assets/hero-fab-constraint-v1.png" alt="World Scene Plate" />

      <!-- 2. Dark Scrim on Evidence Rail -->
      <div class="rail-scrim" id="rail-scrim"></div>

      <!-- 3. Single 2.5D Evidence Dock Card -->
      <div class="evidence-dock" id="evidence-dock">
        <div class="dock-header">
          <span class="dock-title" id="dock-title">THE 3-TO-1 PHYSICS PENALTY</span>
          <span class="dock-badge" id="dock-badge">EVIDENCE 1/2</span>
        </div>

        <div class="slide-view-container">
          <img class="slide-view-img" id="slide-img" src="slides/memory-3to1-penalty.png" alt="Slide Evidence" />
        </div>

        <!-- Decoupled Live Stat Badges -->
        <div class="badges-rail">
          <div class="stat-card" id="stat-card-1">
            <span class="stat-label" id="stat-lbl-1">HBM TRADE RATIO</span>
            <div class="stat-val-row">
              <span class="stat-num" id="stat-val-1" style="color: var(--sunflower);">3.0 : 1</span>
              <span class="stat-tag" id="stat-tag-1" style="background: rgba(245, 183, 46, 0.2); color: var(--sunflower);">PHYSICAL CAP</span>
            </div>
          </div>

          <div class="stat-card" id="stat-card-2">
            <span class="stat-label" id="stat-lbl-2">DDR5 SQUEEZE</span>
            <div class="stat-val-row">
              <span class="stat-num" id="stat-val-2" style="color: var(--coral);">-66%</span>
              <span class="stat-tag" id="stat-tag-2" style="background: rgba(237, 106, 74, 0.2); color: var(--coral);">SHORTAGE</span>
            </div>
          </div>
        </div>

        <!-- Citation Footer Rail -->
        <div class="citation-footer">
          <span id="citation-src">SOURCE: Micron Fiscal Q3 Prepared Remarks & TrendForce</span>
          <span style="color: var(--cobalt);">VERIFIED FILING</span>
        </div>
      </div>

      <!-- 4. Narration Caption Bar -->
      <div class="caption-banner" id="caption-banner">
        "Underneath the price chart is a severe physical factory bottleneck."
      </div>

      <!-- 5. Scene Wipe Curtain -->
      <div class="scene-wipe-curtain" id="wipe-curtain"></div>
    </div>

    <div class="timeline-bar">
      <span>0.0s</span>
      <input type="range" id="scrubber" min="0" max="22" value="0" step="0.05" oninput="seekTo(parseFloat(this.value))">
      <span>22.0s Total</span>
    </div>
  </div>

  <script>
    const pipeline = [
      // === SCENE 1: FAB CAPACITY WORLD PLATE ===
      {
        start: 0.0,
        end: 2.5,
        scene: 1,
        worldPlate: 'hero-fab-constraint-v1.png',
        worldScale: 1.0,
        scrim: false,
        dock: false,
        caption: 'Underneath the price chart is a severe physical factory bottleneck.'
      },
      // Evidence 1 on Scene 1
      {
        start: 2.5,
        end: 6.8,
        scene: 1,
        worldPlate: 'hero-fab-constraint-v1.png',
        worldScale: 1.03,
        scrim: true,
        dock: true,
        title: 'THE 3-TO-1 PHYSICS PENALTY',
        badge: 'EVIDENCE 1/2',
        slide: 'memory-3to1-penalty.png',
        lbl1: 'HBM TRADE RATIO',
        val1: '3.0 : 1',
        val1Col: 'var(--sunflower)',
        tag1: 'PHYSICAL CAP',
        tag1Col: 'var(--sunflower)',
        tag1Bg: 'rgba(245, 183, 46, 0.2)',
        lbl2: 'DDR5 SQUEEZE',
        val2: '-66%',
        val2Col: 'var(--coral)',
        tag2: 'SHORTAGE',
        tag2Col: 'var(--coral)',
        tag2Bg: 'rgba(237, 106, 74, 0.2)',
        citation: 'SOURCE: Micron Q3 Remarks & TrendForce',
        caption: 'Evidence 1: HBM packaging consumes 3x more physical wafer capacity than conventional DRAM.'
      },
      // Evidence 2 on Scene 1 (Same Background Plate!)
      {
        start: 6.8,
        end: 11.0,
        scene: 1,
        worldPlate: 'hero-fab-constraint-v1.png',
        worldScale: 1.06,
        scrim: true,
        dock: true,
        title: 'FOUNDRY CONTRACT COMMITMENTS',
        badge: 'EVIDENCE 2/2',
        slide: 'sovereign-nine-layer-stack.png',
        lbl1: 'CONTRACTED DEPOSITS',
        val1: '+',
        val1Col: 'var(--emerald)',
        tag1: '5-YR TAKE',
        tag1Col: 'var(--emerald)',
        tag1Bg: 'rgba(16, 185, 129, 0.2)',
        lbl2: 'CLEANROOM CAPEX',
        val2: '100% UTIL',
        val2Col: 'var(--secondary-teal)',
        tag2: 'NO IDLE CAP',
        tag2Col: 'var(--secondary-teal)',
        tag2Bg: 'rgba(119, 225, 232, 0.2)',
        citation: 'SOURCE: Company 10-K Filings & Supply Agreements',
        caption: 'Evidence 2: Hyperscaler deposits lock in 100% of high-bandwidth memory capacity through 2028.'
      },
      // === BOARD WIPE (11.0s - 11.8s) ===
      {
        start: 11.0,
        end: 11.8,
        scene: 1,
        wipe: true,
        scrim: false,
        dock: false,
        caption: 'Board wipes clean. Transitioning to the market valuation reflex.'
      },
      // === SCENE 2: S&P 500 REFLEX WORLD PLATE ===
      {
        start: 11.8,
        end: 14.5,
        scene: 2,
        worldPlate: 'hero-sp500-double-failure-v1.png',
        worldScale: 1.0,
        scrim: false,
        dock: false,
        caption: 'Meanwhile, passive index funds are buying software multiples at historic peaks.'
      },
      // Evidence 1 on Scene 2
      {
        start: 14.5,
        end: 19.5,
        scene: 2,
        worldPlate: 'hero-sp500-double-failure-v1.png',
        worldScale: 1.04,
        scrim: true,
        dock: true,
        title: 'THE GREAT VALUATION PARADOX',
        badge: 'EVIDENCE 1/1',
        slide: 'triopoly-paradox.png',
        lbl1: 'S&P 500 FORWARD CAPE',
        val1: '38.4x',
        val1Col: 'var(--coral)',
        tag1: '+92% HIST.',
        tag1Col: 'var(--coral)',
        tag1Bg: 'rgba(237, 106, 74, 0.2)',
        lbl2: 'TRIOPOLY FORWARD P/E',
        val2: '11.2x',
        val2Col: 'var(--emerald)',
        tag2: '-70% DISCOUNT',
        tag2Col: 'var(--emerald)',
        tag2Bg: 'rgba(16, 185, 129, 0.2)',
        citation: 'SOURCE: FactSet & MacroMicro Market Valuations',
        caption: 'Evidence 1: Extreme forward multiple divergence between software leaders and memory suppliers.'
      },
      // === SCENE RESOLUTION (19.5s - 22.0s) ===
      {
        start: 19.5,
        end: 22.0,
        scene: 2,
        worldPlate: 'hero-sp500-double-failure-v1.png',
        worldScale: 1.0,
        scrim: false,
        dock: false,
        caption: 'Same visible chart move. Completely different underlying mechanism.'
      }
    ];

    const worldBg = document.getElementById('world-bg');
    const railScrim = document.getElementById('rail-scrim');
    const evidenceDock = document.getElementById('evidence-dock');
    const dockTitle = document.getElementById('dock-title');
    const dockBadge = document.getElementById('dock-badge');
    const slideImg = document.getElementById('slide-img');
    const statLbl1 = document.getElementById('stat-lbl-1');
    const statVal1 = document.getElementById('stat-val-1');
    const statTag1 = document.getElementById('stat-tag-1');
    const statLbl2 = document.getElementById('stat-lbl-2');
    const statVal2 = document.getElementById('stat-val-2');
    const statTag2 = document.getElementById('stat-tag-2');
    const citationSrc = document.getElementById('citation-src');
    const statCard1 = document.getElementById('stat-card-1');
    const statCard2 = document.getElementById('stat-card-2');
    const captionBanner = document.getElementById('caption-banner');
    const wipeCurtain = document.getElementById('wipe-curtain');
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
      timeDisplay.innerText =  0: / 00:22.0;

      const b = pipeline.find(item => t >= item.start && t < item.end) || pipeline[pipeline.length - 1];

      // Scene wipe curtain
      if (b.wipe) {
        wipeCurtain.classList.add('wipe-in');
      } else {
        wipeCurtain.classList.remove('wipe-in');
      }

      // World Plate
      if (b.worldPlate) {
        worldBg.src = scene_assets/;
        worldBg.style.transform = scale();
      }

      // Scrim
      if (b.scrim) railScrim.classList.add('active');
      else railScrim.classList.remove('active');

      // Evidence Dock & Decoupled Stat Badges
      if (b.dock) {
        evidenceDock.classList.add('active');
        dockTitle.innerText = b.title;
        dockBadge.innerText = b.badge;
        slideImg.src = slides/;
        
        statLbl1.innerText = b.lbl1;
        statVal1.innerText = b.val1;
        statVal1.style.color = b.val1Col;
        statTag1.innerText = b.tag1;
        statTag1.style.color = b.tag1Col;
        statTag1.style.background = b.tag1Bg;

        statLbl2.innerText = b.lbl2;
        statVal2.innerText = b.val2;
        statVal2.style.color = b.val2Col;
        statTag2.innerText = b.tag2;
        statTag2.style.color = b.tag2Col;
        statTag2.style.background = b.tag2Bg;

        citationSrc.innerText = b.citation;

        // Animate stat cards into view
        setTimeout(() => statCard1.classList.add('visible'), 200);
        setTimeout(() => statCard2.classList.add('visible'), 400);
      } else {
        evidenceDock.classList.remove('active');
        statCard1.classList.remove('visible');
        statCard2.classList.remove('visible');
      }

      captionBanner.innerText = "";
    }

    function tick(timestamp) {
      if (!isRunning) return;
      if (!lastTimestamp) lastTimestamp = timestamp;
      const delta = (timestamp - lastTimestamp) / 1000;
      lastTimestamp = timestamp;

      currentTime += delta;
      if (currentTime >= 22.0) {
        currentTime = 22.0;
        renderTime(22.0);
        isRunning = false;
        playPauseBtn.innerText = 'Play';
        return;
      }

      renderTime(currentTime);
      animHandle = requestAnimationFrame(tick);
    }

    function startPlayback() {
      currentTime = 0;
      isRunning = true;
      lastTimestamp = null;
      playPauseBtn.innerText = 'Pause';
      if (animHandle) cancelAnimationFrame(animHandle);
      animHandle = requestAnimationFrame(tick);
    }

    function pauseToggle() {
      if (isRunning) {
        isRunning = false;
        playPauseBtn.innerText = 'Play';
        if (animHandle) cancelAnimationFrame(animHandle);
      } else {
        if (currentTime >= 22.0) currentTime = 0;
        isRunning = true;
        lastTimestamp = null;
        playPauseBtn.innerText = 'Pause';
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
'''

out_p = Path('content/video_engine/review/scene_evidence_pipeline_showcase.html')
out_p.parent.mkdir(parents=True, exist_ok=True)
out_p.write_text(html, encoding='utf-8')
print('SUCCESS_SAVED:', out_p.resolve())
