# Dossier: Claude Code (Free Plan) + YouTube Deconstruction
**Source Video:** https://www.youtube.com/watch?v=WVT2FCjhDDY  
**Creator:** zapiwala ai  
**Duration:** 12m 26s (747s) | 100 Cuts (8.03 CPM) | 103 Generated Scenes  

---

## 1. The Core Architectural Learning: Audio Gaps as Scene Breaks

The single most valuable technical takeaway from this deconstruction:

> **Do not compress narration silences or rebuild artificial timelines. Use the natural acoustic breath pauses in the voiceover as the absolute scene boundaries.**

### The Mechanism
1. **The Flawed Status Quo**:
   - Creators write a script, estimate scene lengths (e.g. 5s, 8s), generate visuals first, record audio second, or compress out silences to make speech rapid-fire.
   - Result: Visual transitions collide mid-word or mid-phrase, producing cognitive dissonance and retention drops.
2. **The Correct Principle**:
   - Audio is the master clock. 
   - When a speaker finishes a thought, physiological breathing creates a natural pause of 0.4s - 1.2s.
   - **The visual transition (cut, dock rise, ink bleed, camera move) must occur during that acoustic pause.**
   - When the next sentence begins, the new visual plate is already established.
3. **Programmatic Pipeline Implementation**:
   - Given word-level timestamps (words.json / Whisper):
     Gap = word[i+1].start - word[i].end
   - Any Gap >= 0.45s triggers a scene cut in storyboard.json.
   - The scene slice inherits t_start and t_end directly from speech boundaries.

---

## 2. Dossier Files in This Directory

| File | Description |
|---|---|
| REPORT.md | Executive metrics: CPM (8.03), mean shot duration (7.47s), speech cadence (147.1 WPM), and 6-phase retention mapping. |
| SHOT_LEDGER.md | Cut-by-cut table: Start/end timestamps, durations, spoken lines, and thumbnail links. |
| CLEAN_TRANSCRIPT.txt | Complete, deduplicated, clean text transcript of the entire 12-minute tutorial. |
| video.en.vtt | Raw WebVTT subtitle stream with millisecond-level cue timings. |
| video.info.json | Complete YouTube metadata (tags, chapters, URLs, description). |
| frames/ | Directory containing 100 extracted reference keyframes (frame_0001.jpg to frame_0215.jpg). |

---

## 3. Notable Keyframe References

- frames/frame_0001.jpg: Opening hook image ('2 AM stick figure scrolling YouTube').
- frames/frame_0014.jpg: Reference channel showcase ('What Did Ancient Humans Do at Night?' - 7.5M views).
- frames/frame_0086.jpg: The 'WRONG vs. RIGHT' workflow slide explicitly showing why scene generation must be subordinate to voiceover timing.
- frames/frame_0126.jpg: Pause timestamp extraction interface (FoziScribe / Whisper pause detection).
- frames/frame_0142.jpg: Google Flow interface with batch prompt queue and model settings (Nano Banana 2).
- frames/frame_0178.jpg: NLE timeline alignment on timestamp boundaries.

---

## 4. Operational Context & MCP Server Role

- **The Video Approach**: Built a custom Chrome extension (ZAPI FLOW) to inject a queue loop into flow.google with 5-15s jitter delays.
- **Our Repository Standard**: We do NOT use browser extensions or ad-hoc Playwright scripts. We have a dedicated MCP server:
  - google-flow MCP Server (tools/google-flow-driver/mcp/server.mjs)
  - Direct agent tool calls: create_flow_batch, create_flow_image, create_flow_video, and create_comfy_parallax_video.
  - Configured in ~/.gemini/config/mcp_config.json.
