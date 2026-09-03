"""
HTML Review Sheet Generator for Candidate Footage Harvests.
Discovers multiple candidates per scene query and renders an interactive HTML review doc.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.footage_harvester import FootageHarvesterService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("generate_harvest_review")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Footage Harvest Review Sheet</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0284c7;
      --success: #10b981;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 2rem;
    }
    .header {
      max-width: 1200px;
      margin: 0 auto 2rem auto;
      border-bottom: 1px solid var(--border);
      padding-bottom: 1rem;
    }
    h1 {
      margin: 0 0 0.5rem 0;
      color: var(--accent);
    }
    .subtitle {
      color: var(--text-muted);
      font-size: 0.95rem;
    }
    .scene-section {
      max-width: 1200px;
      margin: 0 auto 3rem auto;
    }
    .scene-title {
      font-size: 1.25rem;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .scene-badge {
      background: var(--accent);
      color: #0f172a;
      font-size: 0.75rem;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-weight: bold;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 1.5rem;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .card:hover {
      border-color: var(--accent);
      transform: translateY(-2px);
    }
    .preview-container {
      position: relative;
      width: 100%;
      padding-top: 56.25%; /* 16:9 */
      background: #000;
    }
    .preview-container iframe, .preview-container img {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      border: none;
    }
    .card-body {
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      flex-grow: 1;
    }
    .card-title {
      font-weight: 600;
      font-size: 1rem;
      margin-bottom: 0.5rem;
      line-height: 1.4;
    }
    .meta-row {
      display: flex;
      justify-content: space-between;
      color: var(--text-muted);
      font-size: 0.85rem;
      margin-bottom: 0.75rem;
    }
    .snippet-box {
      background: #0f172a;
      border-left: 3px solid var(--accent);
      padding: 0.6rem 0.8rem;
      font-size: 0.85rem;
      color: #cbd5e1;
      margin-bottom: 1rem;
      font-style: italic;
      border-radius: 0 4px 4px 0;
    }
    .timecode-tag {
      display: inline-block;
      background: #334155;
      padding: 0.2rem 0.6rem;
      border-radius: 4px;
      font-family: monospace;
      font-size: 0.85rem;
      margin-bottom: 1rem;
    }
    .btn-row {
      margin-top: auto;
      display: flex;
      gap: 0.5rem;
    }
    .btn {
      flex: 1;
      padding: 0.6rem;
      border-radius: 6px;
      border: none;
      font-weight: 600;
      font-size: 0.85rem;
      cursor: pointer;
      text-align: center;
      text-decoration: none;
      transition: background 0.15s ease;
    }
    .btn-primary {
      background: var(--accent);
      color: #0f172a;
    }
    .btn-primary:hover {
      background: var(--accent-hover);
    }
    .btn-secondary {
      background: #334155;
      color: var(--text);
    }
    .btn-secondary:hover {
      background: #475569;
    }
    .export-panel {
      position: sticky;
      bottom: 1rem;
      max-width: 1200px;
      margin: 2rem auto 0 auto;
      background: #1e293b;
      border: 1px solid var(--accent);
      border-radius: 8px;
      padding: 1rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>🎬 Footage Harvest Review Sheet</h1>
    <div class="subtitle">Generated review session. Inspect candidates and timecodes before approving harvest commands.</div>
  </div>

  <div id="scenes-container">
    <!-- SCENES_INJECTION_POINT -->
  </div>

  <div class="export-panel">
    <div>
      <strong>Approval Status:</strong> <span id="selected-count">0</span> clips selected for final render.
    </div>
    <div>
      <button class="btn btn-primary" onclick="copyHarvestScript()">📋 Copy Batch Harvest CLI Command</button>
    </div>
  </div>

  <script>
    const selections = {};

    function selectCandidate(sceneId, candidateData) {
      selections[sceneId] = candidateData;
      document.getElementById('selected-count').innerText = Object.keys(selections).length;
      alert(`Selected candidate for ${sceneId}: "${candidateData.title}" (Start: ${candidateData.start}s)`);
    }

    function copyHarvestScript() {
      const commands = Object.entries(selections).map(([scene, item]) => {
        return `python content/video_engine/scripts/harvest_footage.py --url "${item.url}" --start ${item.start} --duration 5.0 --output "content/video_engine/assets/clips/${scene}.mp4"`;
      });
      if (commands.length === 0) {
        alert("Please select at least one candidate first.");
        return;
      }
      navigator.clipboard.writeText(commands.join("\\n"));
      alert("Copied batch harvest commands to clipboard!");
    }
  </script>
</body>
</html>
"""


def generate_review_html(
    scenes: list[dict[str, Any]],
    output_html_path: str | Path,
) -> str:
    """Generate the full standalone HTML review doc."""
    service = FootageHarvesterService()
    scenes_html = []

    for idx, scene in enumerate(scenes):
        scene_id = scene.get("id", f"scene_{idx+1}")
        query = scene.get("query", "")
        keywords = scene.get("keywords", query.split())
        target_dur = scene.get("duration", 5.0)

        logger.info(f"Finding review candidates for [{scene_id}]: '{query}'...")
        candidates = service.search_candidates(query, max_results=3)

        cards_html = []
        for c in candidates:
            video_id = c.get("id")
            url = c.get("url")
            title = c.get("title", "Unknown Title")
            uploader = c.get("uploader", "Web Video")
            
            # Retrieve subtitles if available to determine optimal timestamp
            subs = service.fetch_subtitles(url) if url else []
            start_t, end_t = service.find_best_timecode(subs, keywords, target_dur)

            snippet_text = "Standard opening segment"
            if subs:
                matching_subs = [s["text"] for s in subs if start_t <= s["start"] <= end_t]
                if matching_subs:
                    snippet_text = " ".join(matching_subs[:2])

            embed_src = f"https://www.youtube.com/embed/{video_id}?start={int(start_t)}&autoplay=0" if video_id else ""
            thumb_src = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else ""

            candidate_payload = json.dumps({
                "scene_id": scene_id,
                "url": url,
                "title": title,
                "start": start_t,
                "duration": target_dur,
            }).replace('"', '&quot;')

            card = f"""
            <div class="card">
              <div class="preview-container">
                <iframe src="{embed_src}" allowfullscreen loading="lazy"></iframe>
              </div>
              <div class="card-body">
                <div class="card-title">{title}</div>
                <div class="meta-row">
                  <span>👤 {uploader}</span>
                </div>
                <div class="snippet-box">
                  "{snippet_text}"
                </div>
                <div>
                  <span class="timecode-tag">⏱️ Clip: {start_t:.1f}s - {start_t + target_dur:.1f}s ({target_dur}s)</span>
                </div>
                <div class="btn-row">
                  <a href="{url}" target="_blank" class="btn btn-secondary">🔗 Open Source</a>
                  <button class="btn btn-primary" onclick="selectCandidate('{scene_id}', {candidate_payload})">✅ Approve Candidate</button>
                </div>
              </div>
            </div>
            """
            cards_html.append(card)

        scene_block = f"""
        <div class="scene-section">
          <div class="scene-title">
            <span class="scene-badge">{scene_id.upper()}</span>
            <span>Query: <em>"{query}"</em></span>
          </div>
          <div class="grid">
            {''.join(cards_html) if cards_html else '<p style="color:#94a3b8;">No candidates found for this query.</p>'}
          </div>
        </div>
        """
        scenes_html.append(scene_block)

    final_html = HTML_TEMPLATE.replace("<!-- SCENES_INJECTION_POINT -->", "\n".join(scenes_html))
    
    out_p = Path(output_html_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(final_html, encoding="utf-8")
    logger.info(f"Successfully generated HTML review doc: {out_p.resolve()}")
    return str(out_p.resolve())


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an interactive HTML review sheet for potential footage harvests.")
    parser.add_argument("--queries", "-q", nargs="+", help="One or more scene queries to discover candidates for")
    parser.add_argument("--scenes-json", "-s", type=str, help="Path to JSON file with scene queries and keyword configurations")
    parser.add_argument("--output", "-o", type=str, default="content/video_engine/review/harvest_review.html", help="Output HTML file path")

    args = parser.parse_args()

    scenes = []
    if args.scenes_json:
        scenes = json.loads(Path(args.scenes_json).read_text(encoding="utf-8"))
    elif args.queries:
        for idx, q in enumerate(args.queries):
            scenes.append({
                "id": f"scene_{idx+1}",
                "query": q,
                "duration": 5.0,
            })
    else:
        # Default sample showcase
        scenes = [
            {"id": "scene_1_trading_floor", "query": "1980s wall street trading floor archival", "duration": 5.0},
            {"id": "scene_2_server_room", "query": "modern supercomputer server room data center", "duration": 4.5},
            {"id": "scene_3_news_broadcast", "query": "vintage breaking news broadcast television studio", "duration": 5.0},
        ]

    generate_review_html(scenes, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
