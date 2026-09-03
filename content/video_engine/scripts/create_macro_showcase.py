"""
Showcase of 5 Coordinate-Independent Evidence Animations.
These techniques do not rely on fragile pixel-level bounding boxes on raw PNG slides.
"""

from pathlib import Path

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Robust Coordinate-Independent Evidence Animations</title>
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
    .mode-tabs {
      display: flex;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
    }
    .tab-btn {
      background: var(--card-bg);
      color: #cbd5e1;
      border: 1px solid #334155;
      padding: 0.75rem 1.25rem;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .tab-btn.active {
      background: var(--cobalt);
      color: #fff;
      border-color: var(--cobalt);
      box-shadow: 0 4px 12px rgba(23, 105, 194, 0.35);
    }
    .tab-btn:hover {
      border-color: var(--sunflower);
    }

    /* 16:9 Master Viewport */
    .viewport-frame {
      width: 100%;
      max-width: 1100px;
      height: 619px;
      margin: 0 auto;
      background: #000;
      border: 4px solid var(--charcoal);
      border-radius: 16px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 25px 60px rgba(0,0,0,0.7);
    }

    .world-layer {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      transform-origin: center center;
    }

    .rail-scrim {
      position: absolute;
      top: 0;
      right: 0;
      width: 60%;
      height: 100%;
      background: linear-gradient(to right, rgba(8, 12, 20, 0) 0%, rgba(8, 12, 20, 0.65) 35%, rgba(8, 12, 20, 0.92) 100%);
      pointer-events: none;
    }

    /* Evidence Dock */
    .evidence-dock {
      position: absolute;
      top: 40px;
      right: 45px;
      width: 540px;
      height: 510px;
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
    }
    .evidence-badge {
      background: var(--cobalt);
      color: #fff;
      font-size: 0.72rem;
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 800;
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
      transform-origin: center center;
      transition: transform 0.05s linear;
    }

    /* Technique Overlays */
    /* 1. Dynamic Focal Spotlight Mask */
    .spotlight-mask {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: radial-gradient(circle at 60% 45%, rgba(0,0,0,0) 25%, rgba(15,23,42,0.7) 75%);
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.4s ease;
    }
    .spotlight-mask.active {
      opacity: 1;
    }

    /* 2. Split Comparison Half-Scrim */
    .half-scrim {
      position: absolute;
      top: 0;
      left: 0;
      width: 50%;
      height: 100%;
      background: rgba(15, 23, 42, 0.7);
      backdrop-filter: blur(2px);
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.4s ease;
    }
    .half-scrim.active {
      opacity: 1;
    }

    /* 3. Corner Evidence Stamp */
    .evidence-stamp {
      position: absolute;
      top: 15px;
      right: 15px;
      border: 3px dashed var(--coral);
      color: var(--coral);
      padding: 6px 12px;
      font-weight: 900;
      font-size: 0.85rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      border-radius: 6px;
      transform: rotate(-8deg) scale(1.4);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .evidence-stamp.active {
      opacity: 1;
      transform: rotate(-8deg) scale(1);
    }

    /* 4. Decoupled Stat Badges (In the Card Margin) */
    .decoupled-metrics {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.5rem;
      margin-top: 0.75rem;
    }
    .metric-pill {
      background: var(--charcoal);
      color: var(--sunflower);
      padding: 8px 10px;
      border-radius: 6px;
      font-weight: 800;
      font-size: 0.8rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      opacity: 0;
      transform: translateY(8px);
      transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .metric-pill.active {
      opacity: 1;
      transform: translateY(0);
    }

    .description-box {
      margin-top: 1.5rem;
      background: var(--card-bg);
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
    }
    .desc-title {
      font-weight: 800;
      color: var(--sunflower);
      font-size: 1.1rem;
      margin-bottom: 0.4rem;
    }
    .desc-text {
      color: #94a3b8;
      font-size: 0.95rem;
      line-height: 1.5;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>🎯 5 Coordinate-Independent Evidence Animations</h1>
        <div class="subtitle">Robust motion techniques that look premium without requiring fragile pixel-level bounding boxes.</div>
      </div>
      <div>
        <button class="tab-btn active" style="background: var(--cobalt); color: #fff;" onclick="playSequence()">▶️ Replay Active Mode</button>
      </div>
    </header>

    <div class="mode-tabs">
      <button class="tab-btn active" onclick="setMode('push_in')">1. Ken Burns Macro Push-In</button>
      <button class="tab-btn" onclick="setMode('spotlight')">2. Radial Vignette Spotlight</button>
      <button class="tab-btn" onclick="setMode('split_focus')">3. Left/Right Split Scrim</button>
      <button class="tab-btn" onclick="setMode('evidence_stamp')">4. Tactile Evidence Stamp</button>
      <button class="tab-btn" onclick="setMode('decoupled_stats')">5. Decoupled Stat Badges</button>
    </div>

    <!-- 16:9 Composited Canvas -->
    <div class="viewport-frame">
      <img class="world-layer" id="world-bg" src="scene_assets/hero-fab-constraint-v1.png" alt="World Plate" />
      <div class="rail-scrim"></div>

      <div class="evidence-dock" id="evidence-dock">
        <div class="evidence-header">
          <span class="evidence-title" id="evidence-title">PHYSICAL CAPACITY CONSTRAINT</span>
          <span class="evidence-badge">EXHIBIT #01</span>
        </div>

        <div class="slide-crop-container">
          <img class="slide-crop-img" id="slide-img" src="slides/triopoly-paradox.png" alt="Slide Image" />
          
          <!-- Technique Overlays -->
          <div class="spotlight-mask" id="spotlight-mask"></div>
          <div class="half-scrim" id="half-scrim"></div>
          <div class="evidence-stamp" id="evidence-stamp">VERIFIED FILING</div>
        </div>

        <!-- Decoupled Live Code Badges (Never touch raw pixels) -->
        <div class="decoupled-metrics" id="metrics-container">
          <div class="metric-pill" id="pill-1">
            <span>FORWARD CAPE</span>
            <span style="color: #ED6A4A;">38.4x</span>
          </div>
          <div class="metric-pill" id="pill-2">
            <span>TRIOPOLY P/E</span>
            <span style="color: #10B981;">11.2x</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Explanatory Box -->
    <div class="description-box">
      <div class="desc-title" id="desc-title">1. Ken Burns Macro Push-In</div>
      <div class="desc-text" id="desc-text">
        The whole slide enters at 100% size, then smoothly glides and scales up 1.18x into the central diagram. Zero pixel coordinates required—works flawlessly on any slide design.
      </div>
    </div>
  </div>

  <script>
    let activeMode = 'push_in';

    const descriptions = {
      push_in: {
        title: '1. Ken Burns Macro Push-In (Smooth Lens Glide)',
        text: 'The whole slide enters at 100% scale, then smoothly glides and scales to 1.18x into the central diagram area. 100% reliable across any slide format without guessing coordinates.'
      },
      spotlight: {
        title: '2. Radial Vignette Spotlight (Subtle Ambient Focus)',
        text: 'A soft, feathered vignette darkens the outer 30% of the slide while casting a soft warm spotlight over the primary graphic. Naturally draws viewer attention without drawn lines.'
      },
      split_focus: {
        title: '3. Left/Right Split Comparison Scrim',
        text: 'Dulls one half of the slide with a subtle frosted slate overlay when the narrator discusses the contrast between the left and right charts (e.g. S&P 500 vs Hardware Triopoly).'
      },
      evidence_stamp: {
        title: '4. Tactile Evidence Stamp ("VERIFIED FILING / CONTRACTED")',
        text: 'Snaps a woodblock/ink verified stamp into the top-right corner with a crisp spring. Adds physical authenticity to filings and earnings transcripts.'
      },
      decoupled_stats: {
        title: '5. Decoupled Code Badges (Rendered Outside the Slide)',
        text: 'Instead of searching for where the number is inside the picture, we render crisp Remotion HTML badges directly below the slide inside the washi card. 100% legible and accurate.'
      }
    };

    function resetOverlays() {
      document.getElementById('spotlight-mask').classList.remove('active');
      document.getElementById('half-scrim').classList.remove('active');
      document.getElementById('evidence-stamp').classList.remove('active');
      document.getElementById('pill-1').classList.remove('active');
      document.getElementById('pill-2').classList.remove('active');
      document.getElementById('slide-img').style.transform = 'scale(1) translate(0px, 0px)';
    }

    function setMode(mode) {
      activeMode = mode;
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      event.target.classList.add('active');

      document.getElementById('desc-title').innerText = descriptions[mode].title;
      document.getElementById('desc-text').innerText = descriptions[mode].text;

      resetOverlays();
      playSequence();
    }

    function playSequence() {
      resetOverlays();
      const slide = document.getElementById('slide-img');

      if (activeMode === 'push_in') {
        setTimeout(() => {
          slide.style.transition = 'transform 2.2s cubic-bezier(0.16, 1, 0.3, 1)';
          slide.style.transform = 'scale(1.22) translate(-15px, -10px)';
        }, 300);
      } else if (activeMode === 'spotlight') {
        setTimeout(() => {
          document.getElementById('spotlight-mask').classList.add('active');
          slide.style.transition = 'transform 2s ease-out';
          slide.style.transform = 'scale(1.06)';
        }, 300);
      } else if (activeMode === 'split_focus') {
        setTimeout(() => {
          document.getElementById('half-scrim').classList.add('active');
        }, 400);
      } else if (activeMode === 'evidence_stamp') {
        setTimeout(() => {
          document.getElementById('evidence-stamp').classList.add('active');
        }, 400);
      } else if (activeMode === 'decoupled_stats') {
        setTimeout(() => {
          document.getElementById('pill-1').classList.add('active');
        }, 300);
        setTimeout(() => {
          document.getElementById('pill-2').classList.add('active');
        }, 600);
      }
    }

    window.onload = () => {
      playSequence();
    };
  </script>
</body>
</html>
"""

out_p = Path("content/video_engine/review/macro_motion_showcase.html")
out_p.parent.mkdir(parents=True, exist_ok=True)
out_p.write_text(html, encoding="utf-8")
print(f"Generated Macro Motion Showcase at: {out_p.resolve()}")
