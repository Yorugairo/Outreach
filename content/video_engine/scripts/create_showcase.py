"""
Interactive Browser Showcase for Remotion Editorial Motion Components
Renders live interactive spring physics, charts, market share bars, and headline reveals.
"""

from pathlib import Path

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Editorial Motion Graphics Showcase</title>
  <style>
    :root {
      --bg: #0b0f17;
      --panel-bg: #F4E6C7; /* Editorial Cream */
      --charcoal: #25313C;
      --cobalt: #1769C2;
      --teal: #178C83;
      --sunflower: #F5B72E;
      --coral: #ED6A4A;
      --dark-card: #161f2e;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: #f8fafc;
      margin: 0;
      padding: 2.5rem;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    header {
      margin-bottom: 2.5rem;
      border-bottom: 1px solid #334155;
      padding-bottom: 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }
    h1 {
      margin: 0 0 0.5rem 0;
      color: var(--sunflower);
      font-size: 2.2rem;
      letter-spacing: -0.02em;
    }
    .subtitle {
      color: #94a3b8;
      font-size: 1rem;
    }
    .controls-bar {
      display: flex;
      gap: 1rem;
      margin-bottom: 2rem;
    }
    .btn {
      background: var(--cobalt);
      color: #fff;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.95rem;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(23, 105, 194, 0.3);
      transition: all 0.15s ease;
    }
    .btn:hover {
      background: #1e7be6;
      transform: translateY(-2px);
    }
    .btn-secondary {
      background: #334155;
      box-shadow: none;
    }
    .btn-secondary:hover {
      background: #475569;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(540px, 1fr));
      gap: 2rem;
    }
    .showcase-card {
      background: var(--dark-card);
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 1.75rem;
      box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
    }
    .card-title {
      font-size: 1.2rem;
      font-weight: 700;
      color: #f1f5f9;
    }
    .badge {
      background: #334155;
      color: var(--sunflower);
      font-size: 0.75rem;
      padding: 0.25rem 0.6rem;
      border-radius: 4px;
      font-family: monospace;
      font-weight: 700;
    }

    /* 1. Animated Stock Chart Component */
    .chart-box {
      background: var(--panel-bg);
      border: 3px solid var(--charcoal);
      border-radius: 12px;
      box-shadow: 8px 8px 0px var(--charcoal);
      padding: 1.5rem;
      color: var(--charcoal);
      position: relative;
    }
    .chart-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }
    .ticker-tag {
      background: var(--cobalt);
      color: #fff;
      padding: 3px 8px;
      border-radius: 4px;
      font-weight: 800;
      font-size: 0.8rem;
    }
    .live-badge {
      background: var(--charcoal);
      color: var(--sunflower);
      padding: 6px 14px;
      border-radius: 8px;
      font-family: monospace;
      font-size: 1.3rem;
      font-weight: 900;
      text-align: right;
    }
    svg.stock-svg {
      width: 100%;
      height: 240px;
      overflow: visible;
    }

    /* 2. Market Share Bar Race Component */
    .bars-container {
      background: var(--panel-bg);
      border: 3px solid var(--charcoal);
      border-radius: 12px;
      box-shadow: 8px 8px 0px var(--charcoal);
      padding: 1.5rem;
      color: var(--charcoal);
    }
    .bar-row {
      margin-bottom: 1.25rem;
    }
    .bar-label-row {
      display: flex;
      justify-content: space-between;
      font-weight: 800;
      font-size: 0.95rem;
      margin-bottom: 0.4rem;
    }
    .bar-track {
      height: 28px;
      background: rgba(37, 49, 60, 0.12);
      border: 2px solid var(--charcoal);
      border-radius: 6px;
      overflow: hidden;
      position: relative;
    }
    .bar-fill {
      height: 100%;
      width: 0%;
      border-radius: 4px;
      transition: width 0.05s linear;
    }

    /* 3. Editorial Headline Reveal */
    .headline-box {
      background: #FFFDF7;
      border: 3px solid var(--charcoal);
      border-radius: 12px;
      box-shadow: 8px 8px 0px var(--charcoal);
      padding: 2rem;
      color: var(--charcoal);
      position: relative;
      overflow: hidden;
    }
    .newspaper-header {
      border-bottom: 2px solid var(--charcoal);
      padding-bottom: 0.5rem;
      margin-bottom: 1.25rem;
      display: flex;
      justify-content: space-between;
      font-family: "Georgia", serif;
      font-size: 0.85rem;
      font-weight: bold;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
    .newspaper-headline {
      font-family: "Georgia", serif;
      font-size: 1.75rem;
      font-weight: 900;
      line-height: 1.2;
      margin: 0 0 1rem 0;
    }
    .highlighter {
      background: rgba(245, 183, 46, 0.45);
      padding: 2px 4px;
      border-radius: 2px;
      display: inline;
    }

    /* 4. 2.5D Brand Cards */
    .logo-cards-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
    }
    .logo-card {
      background: var(--panel-bg);
      border: 2px solid var(--charcoal);
      border-radius: 10px;
      box-shadow: 5px 5px 0px var(--charcoal);
      padding: 1.25rem 0.75rem;
      text-align: center;
      color: var(--charcoal);
      transform: translateY(0);
      transition: transform 0.2s ease;
    }
    .logo-card:hover {
      transform: translateY(-4px);
    }
    .logo-icon {
      font-size: 2rem;
      margin-bottom: 0.5rem;
    }
    .logo-name {
      font-weight: 900;
      font-size: 1rem;
    }
    .logo-sub {
      font-size: 0.75rem;
      color: #64748b;
      margin-top: 0.25rem;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>🎨 Editorial Motion Showcase</h1>
        <div class="subtitle">Live Remotion spring physics, dynamic stock charts, market share races & headline reveals.</div>
      </div>
      <div>
        <button class="btn" onclick="replayAll()">🔄 Replay All Animations</button>
      </div>
    </header>

    <div class="controls-bar">
      <button class="btn btn-secondary" onclick="setChartData('supercycle')">📈 Memory Supercycle (+340%)</button>
      <button class="btn btn-secondary" onclick="setChartData('crash')">📉 Dot-Com Bubble Crash (-78%)</button>
      <button class="btn btn-secondary" onclick="triggerMarketShareRace()">🏎️ Market Share Race</button>
      <button class="btn btn-secondary" onclick="triggerHeadlineSlam()">📰 Trigger Headline Slam</button>
    </div>

    <div class="grid">
      <!-- 1. Animated Stock Chart -->
      <div class="showcase-card">
        <div class="card-header">
          <div class="card-title">1. Remotion Spring Stock Curve</div>
          <span class="badge">AnimatedStockChart.tsx</span>
        </div>
        <div class="chart-box" id="chart-card">
          <div class="chart-meta">
            <div>
              <span class="ticker-tag" id="chart-ticker">MU (MICRON)</span>
              <div style="font-weight: 800; font-size: 1.15rem; margin-top: 4px;" id="chart-headline">
                HBM AI Memory Supercycle
              </div>
            </div>
            <div class="live-badge" id="chart-live-val">$142.50</div>
          </div>

          <svg class="stock-svg" viewBox="0 0 500 240" id="stock-svg">
            <defs>
              <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#1769C2" stop-opacity="0.3" />
                <stop offset="100%" stop-color="#1769C2" stop-opacity="0.0" />
              </linearGradient>
            </defs>
            <!-- Grid Lines -->
            <line x1="30" y1="40" x2="470" y2="40" stroke="#25313C" stroke-dasharray="4 4" stroke-opacity="0.15"/>
            <line x1="30" y1="100" x2="470" y2="100" stroke="#25313C" stroke-dasharray="4 4" stroke-opacity="0.15"/>
            <line x1="30" y1="160" x2="470" y2="160" stroke="#25313C" stroke-dasharray="4 4" stroke-opacity="0.15"/>
            <line x1="30" y1="210" x2="470" y2="210" stroke="#25313C" stroke-dasharray="4 4" stroke-opacity="0.15"/>
            
            <path id="chart-area" d="" fill="url(#areaGrad)" opacity="0" />
            <path id="chart-line" d="" fill="none" stroke="#1769C2" stroke-width="4.5" stroke-linecap="round" />
            <circle id="chart-dot" r="6" fill="#25313C" stroke="#F5B72E" stroke-width="3" opacity="0" />
          </svg>
        </div>
      </div>

      <!-- 2. Market Share Bar Race -->
      <div class="showcase-card">
        <div class="card-header">
          <div class="card-title">2. DRAM/HBM Market Concentration</div>
          <span class="badge">AnimatedMarketShare.tsx</span>
        </div>
        <div class="bars-container">
          <div class="bar-row">
            <div class="bar-label-row">
              <span>Samsung Electronics</span>
              <span id="pct-samsung" style="color: #1769C2; font-family: monospace;">0.0%</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill" id="bar-samsung" style="background: #1769C2;"></div>
            </div>
          </div>

          <div class="bar-row">
            <div class="bar-label-row">
              <span>SK Hynix</span>
              <span id="pct-skhynix" style="color: #178C83; font-family: monospace;">0.0%</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill" id="bar-skhynix" style="background: #178C83;"></div>
            </div>
          </div>

          <div class="bar-row">
            <div class="bar-label-row">
              <span>Micron Technology</span>
              <span id="pct-micron" style="color: #ED6A4A; font-family: monospace;">0.0%</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill" id="bar-micron" style="background: #ED6A4A;"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Headline Slam & Highlighter Reveal -->
      <div class="showcase-card">
        <div class="card-header">
          <div class="card-title">3. Editorial Newspaper Clipping</div>
          <span class="badge">HeadlineReveal.tsx</span>
        </div>
        <div class="headline-box" id="headline-box">
          <div class="newspaper-header">
            <span>The Financial Chronicle</span>
            <span>Market Special Edition</span>
          </div>
          <div class="newspaper-headline" id="news-headline">
            AI Chip Giants Face Historic <span class="highlighter" id="hl-text">HBM Supply Shortage</span> as Wall Street Re-Rates Memory Valuations.
          </div>
          <div style="font-size: 0.85rem; color: #64748b; line-height: 1.4;">
            Surging demand from hyperscalers creates unprecedented pricing power across the top three DRAM manufacturers.
          </div>
        </div>
      </div>

      <!-- 4. 2.5D Brand Cards -->
      <div class="showcase-card">
        <div class="card-header">
          <div class="card-title">4. 2.5D Paper-Cut Brand Plates</div>
          <span class="badge">BrandCardPlate.tsx</span>
        </div>
        <div class="logo-cards-grid">
          <div class="logo-card" id="card-mu">
            <div class="logo-icon">⚡</div>
            <div class="logo-name">Micron</div>
            <div class="logo-sub">Nasdaq: MU</div>
          </div>
          <div class="logo-card" id="card-sec">
            <div class="logo-icon">🔷</div>
            <div class="logo-name">Samsung</div>
            <div class="logo-sub">KRX: 005930</div>
          </div>
          <div class="logo-card" id="card-sk">
            <div class="logo-icon">🔴</div>
            <div class="logo-name">SK Hynix</div>
            <div class="logo-sub">KRX: 000660</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Remotion Spring Simulation Function
    function remotionSpring(progress, damping = 22, stiffness = 80) {
      // Simplified damped harmonic spring equation
      return 1 - Math.exp(-progress * (damping / 3)) * Math.cos(progress * Math.sqrt(stiffness) * 0.4);
    }

    let currentMode = 'supercycle';
    const datasets = {
      supercycle: {
        ticker: 'MU (MICRON)',
        headline: 'HBM AI Memory Supercycle',
        startVal: 34.50,
        endVal: 142.50,
        pts: [[30, 200], [120, 180], [210, 160], [300, 110], [390, 70], [460, 45]]
      },
      crash: {
        ticker: 'DOTCOM INDEX',
        headline: 'Speculative Tech Bubble Collapse',
        startVal: 5048.00,
        endVal: 1114.00,
        pts: [[30, 50], [120, 45], [210, 80], [300, 140], [390, 190], [460, 210]]
      }
    };

    function buildSmoothPath(pts) {
      return pts.reduce((acc, pt, i, arr) => {
        if (i === 0) return `M ${pt[0]},${pt[1]}`;
        const prev = arr[i - 1];
        const cx = prev[0] + (pt[0] - prev[0]) / 2;
        return `${acc} C ${cx},${prev[1]} ${cx},${pt[1]} ${pt[0]},${pt[1]}`;
      }, '');
    }

    function animateChart(data) {
      const line = document.getElementById('chart-line');
      const area = document.getElementById('chart-area');
      const dot = document.getElementById('chart-dot');
      const liveVal = document.getElementById('chart-live-val');
      const tickerEl = document.getElementById('chart-ticker');
      const headlineEl = document.getElementById('chart-headline');

      tickerEl.innerText = data.ticker;
      headlineEl.innerText = data.headline;

      const pathD = buildSmoothPath(data.pts);
      line.setAttribute('d', pathD);
      
      const areaD = `${pathD} L ${data.pts[data.pts.length-1][0]},220 L ${data.pts[0][0]},220 Z`;
      area.setAttribute('d', areaD);

      const length = 550;
      line.style.strokeDasharray = length;
      line.style.strokeDashoffset = length;

      let start = null;
      function step(ts) {
        if (!start) start = ts;
        const elapsed = (ts - start) / 1000;
        const t = Math.min(elapsed / 1.5, 1);
        const springT = Math.max(0, Math.min(remotionSpring(t * 5), 1));

        line.style.strokeDashoffset = length * (1 - springT);
        area.style.opacity = springT * 0.4;

        // Current val
        const currentV = data.startVal + (data.endVal - data.startVal) * springT;
        liveVal.innerText = `$${currentV.toFixed(2)}`;

        // Dot position
        const ptIdx = Math.min(Math.floor(springT * (data.pts.length - 1)), data.pts.length - 1);
        const currentPt = data.pts[ptIdx];
        dot.setAttribute('cx', currentPt[0]);
        dot.setAttribute('cy', currentPt[1]);
        dot.setAttribute('opacity', springT > 0.05 ? '1' : '0');

        if (t < 1) {
          requestAnimationFrame(step);
        }
      }
      requestAnimationFrame(step);
    }

    function triggerMarketShareRace() {
      const shares = { samsung: 41.5, skhynix: 34.0, micron: 21.5 };
      let start = null;

      function step(ts) {
        if (!start) start = ts;
        const elapsed = (ts - start) / 1000;

        Object.keys(shares).forEach((key, idx) => {
          const delay = idx * 0.15;
          const t = Math.max(0, Math.min((elapsed - delay) / 1.2, 1));
          const springT = Math.max(0, Math.min(remotionSpring(t * 5), 1));
          const target = shares[key];
          const cur = target * springT;

          document.getElementById(`bar-${key}`).style.width = `${cur}%`;
          document.getElementById(`pct-${key}`).innerText = `${cur.toFixed(1)}%`;
        });

        if (elapsed < 2.0) {
          requestAnimationFrame(step);
        }
      }
      requestAnimationFrame(step);
    }

    function triggerHeadlineSlam() {
      const box = document.getElementById('headline-box');
      box.style.transform = 'scale(0.92) rotate(-1deg)';
      box.style.opacity = '0';
      box.style.transition = 'none';

      setTimeout(() => {
        box.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        box.style.transform = 'scale(1) rotate(0deg)';
        box.style.opacity = '1';
      }, 50);
    }

    function setChartData(type) {
      currentMode = type;
      animateChart(datasets[type]);
    }

    function replayAll() {
      animateChart(datasets[currentMode]);
      triggerMarketShareRace();
      triggerHeadlineSlam();
    }

    window.onload = () => {
      replayAll();
    };
  </script>
</body>
</html>
"""

out_p = Path("content/video_engine/review/motion_showcase.html")
out_p.parent.mkdir(parents=True, exist_ok=True)
out_p.write_text(html_content, encoding="utf-8")
print(f"Generated live showcase at {out_p.resolve()}")
