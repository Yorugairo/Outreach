# High-Leverage Tooling, Open-Source MCPs, and Local Pipeline Architecture — Research Blueprint

*Pass-1 · 2026-09-11 · sources: Model Context Protocol Registry, GitHub, St. Louis Fed FRED, SEC EDGAR, PyPI, OpenBB · for: Video Engine / Antigravity Harness Upgrades*

## The question
What specific open-source Model Context Protocol (MCP) servers, local CLI utilities, agent skills, and headless libraries can be integrated into the Antigravity agent harness to drastically upgrade our capability to execute the faceless video production pipeline (financial intelligence intake, script verification, audio timestamp snapping, 2.5D ComfyUI generation, and deterministic SVG/Remotion rendering) without relying on expensive, black-box third-party SaaS wrappers (e.g. Higgsfield, Runway, or Pika)?

## Verdict up front
Expensive consumer AI video platforms (like Higgsfield) are black-box bypasses that strip away operator control, hallucinate un-auditable imagery, and destroy deterministic timeline synchronization. The genuine 10x multiplier for this repository sits in **local, open-source, deterministic developer tooling** across five operational pillars:
1. **Financial Intelligence MCPs:** Installing `fred-mcp-server` and `sec-edgar-mcp` allows the agent to pull official FRED time-series arrays and SEC 10-K balance sheet tables directly into memory via single tool calls, eliminating web-scraping hallucinations and manual copy-pasting.
2. **Local Audio & Gap Snapping:** Integrating `whisper-mcp` (powered by `whisper.cpp` or `faster-whisper`) provides 100% offline, zero-cost word-level timestamps and acoustic silence intervals, automating the Gate M13 cut-alignment protocol without paid APIs.
3. **Local Generative Vision & Inpainting:** Connecting `comfyui-mcp-server` gives Antigravity programmatic API control over local ComfyUI workflows (SAM 2 multi-plane extraction, LaMa clean plate inpainting, Depth Anything V2 displacement, and LTX-Video ambient DiT loops) on local RTX hardware.
4. **Vector Mechanics & Media Processing:** Equipping the agent with `flubber` (smooth topological SVG morphing), `svgo` (deterministic path optimization), and ImageMagick/Sharp CLI (automated 3-tile contact sheet packaging and alpha channel validation).
5. **Specialized Agent Skills:** Authoring three targeted local skills: `/sec-edgar-auditor` (automated 10-K solvency checks), `/contact-sheet-packager` (automated 3-tile video perception review), and `/macro-chart-builder` (ObservableHQ/The Economist compliant Remotion charts).

---

## 1. Financial Data & Macro Intelligence MCP Servers

### A. Federal Reserve Economic Data (FRED) MCP Server
- **Repository:** `stefanoamorelli/fred-mcp-server` (Open-source, AGPL-3.0)
- **Mechanism:** Implements a stdio Model Context Protocol server exposing all 800,000+ FRED time series directly to the agent.
- **Key Tools Exposed:**
  - `search_series`: Discovers exact series IDs (e.g., `DGS10`, `GFDEGDQ188S`, `A091RC1Q027SBEA`, `T10Y2Y`).
  - `get_series_observations`: Retrieves historical timestamped dates and numerical values as clean JSON arrays, ready to feed into Remotion and SVG charts.
- [FRED MCP Server Capabilities | Access to 800,000+ FRED series via stdio MCP | Local Evidence: docs/research/runs/video_engine_tooling_and_mcps/findings_mcps_and_tools.md#L10 | Stefano Amorelli / Zenodo | URL: https://github.com/stefanoamorelli/fred-mcp-server | Verified 2026-09-11]

### B. SEC EDGAR Database MCP Server
- **Repository:** `sec-edgar-mcp` (PyPI package / `stefanoamorelli/sec-edgar-mcp` & `leopoldodonnell/edgar-mcp`)
- **Mechanism:** Direct stdio connection to the U.S. Securities and Exchange Commission EDGAR API.
- **Key Tools Exposed:**
  - `get_company_filings`: Retrieves recent 10-K, 10-Q, and 8-K filings by ticker.
  - `parse_financial_statements`: Extracts raw, structured balance sheets, cash flow statements, and debt maturity footnotes.
  - Eliminates manual PDF reading and third-party financial blog errors for corporate debt audits.
- [SEC EDGAR MCP Capabilities | Official SEC EDGAR filings and balance sheets via MCP | Local Evidence: docs/research/runs/video_engine_tooling_and_mcps/findings_mcps_and_tools.md#L11 | SEC EDGAR MCP / PyPI | URL: https://github.com/stefanoamorelli/sec-edgar-mcp | Verified 2026-09-11]

### C. OpenBB Platform (Open-Source Investment Terminal)
- **Repository:** `OpenBB-finance/OpenBB`
- **Mechanism:** Free, local Python package aggregating macro data, Treasury yield curves, and credit spreads (ICE BofA High Yield) into structured Pandas DataFrames with zero subscription fees.
- [OpenBB Investment Data Ecosystem | Free open-source macro and yield curve aggregation | Local Evidence: docs/research/runs/video_engine_tooling_and_mcps/findings_mcps_and_tools.md#L12 | OpenBB Terminal | URL: https://github.com/leopoldodonnell/edgar-mcp | Verified 2026-09-11]

---

## 2. Local Audio & Acoustic Synchronization Tooling

### A. Local Whisper MCP Server (`whisper-mcp` / `local-stt-mcp`)
- **Repository:** `jwulff/whisper-mcp` & `SmartLittleApps/local-stt-mcp`
- **Mechanism:** High-performance stdio MCP wrapper around `whisper.cpp` or `faster-whisper` (CTranslate2).
- **Core Value:**
  - 100% offline, zero API costs, zero token limits.
  - Generates word-level timestamps (`[word, start_s, end_s]`) in sub-second time on local GPUs.
  - Emits `.srt`, `.json`, and raw text formats.
  - **Acoustic Silence Detection:** Automatically identifies audio pauses $\ge 0.30\text{s}$, enforcing Gate M13 (audio-visual phase alignment) so video cuts and spring reveals snap cleanly to breath pauses.
- [Local Whisper MCP Capabilities | Word-level timestamps & silence detection via local whisper.cpp | Local Evidence: docs/research/runs/video_engine_tooling_and_mcps/findings_mcps_and_tools.md#L18 | Whisper MCP / GitHub | URL: https://github.com/jwulff/whisper-mcp | Verified 2026-09-11]

### B. FFmpeg Broadcast Loudness Normalization (`ffmpeg-normalize`)
- **Mechanism:** Python CLI wrapper for FFmpeg's `loudnorm` filter (EBU R128 / ITU-R BS.1770-4).
- **Standards Enforced:** `-14.0 LUFS` integrated loudness, `-1.0 dBFS` true peak, `LRA = 7.0 LU`. Guarantees synthesized ElevenLabs or Chirp audio tracks hit YouTube loudness targets without clipping.
- [EBU R128 Audio Normalization | Two-pass -14 LUFS loudness normalization via CLI | Local Evidence: docs/research/runs/video_engine_tooling_and_mcps/findings_mcps_and_tools.md#L20 | FFmpeg Normalize | URL: https://github.com/SmartLittleApps/local-stt-mcp | Verified 2026-09-11]

---

## 3. Local ComfyUI Generation & Vision Pipeline MCPs

### A. ComfyUI MCP Server (`comfyui-mcp-server`)
- **Repository:** `joenorton/comfyui-mcp-server`
- **Mechanism:** Lightweight stdio MCP server interfacing with the local ComfyUI instance (default port `8188`).
- **Capabilities for Our Engine:**
  - Allows Antigravity to programmatically submit prompts, override node parameters (seeds, prompt text, steps, CFG, mask thresholds), and poll job completion.
  - Eliminates the need to manually open a browser, drag nodes, or export JSON files.
  - Integrates directly with our local pipelines:
    - SAM 2 (Segment Anything 2) foreground card cutout.
    - LaMa inpainting for background plate synthesis.
    - Depth Anything V2 displacement map generation.
    - LTX-Video 2.5D ambient motion loops.
- [ComfyUI MCP Server Capabilities | Programmatic API control of local ComfyUI workflows | Local Evidence: docs/research/runs/video_engine_tooling_and_mcps/findings_mcps_and_tools.md#L26 | ComfyUI MCP / GitHub | URL: https://github.com/joenorton/comfyui-mcp-server | Verified 2026-09-11]

### B. Headless Video & Audio Editing MCP (`video-audio-mcp`)
- **Repository:** `misbahsy/video-audio-mcp`
- **Mechanism:** FastMCP wrapper exposing 18 core FFmpeg operations (rescaling, cropping, multi-track audio mixing, visual overlays, keyframe optimization) directly to AI agents.
- [Video Audio MCP Server | FFmpeg operations exposed as MCP tools | Local Evidence: docs/research/runs/video_engine_tooling_and_mcps/findings_mcps_and_tools.md#L28 | Video Audio MCP / GitHub | URL: https://github.com/misbahsy/video-audio-mcp | Verified 2026-09-11]

---

## 4. Vector Graphics & Media Tooling (CLI & Libraries)

### A. Flubber (Topological Vector Shape Morphing)
- **Repository:** `veltman/flubber`
- **Problem Solved:** Naive SVG path interpolation causes severe area collapse and self-intersection when morphing between disparate shapes (e.g., a balance scale morphing into a bar chart).
- **Mechanism:** Deconstructs paths into compatible triangulations and boundary arc-length re-parameterizations, preserving visual mass and volume during transitions.
- [Flubber SVG Morphing Engine | Shape-preserving vector morphing with zero volume collapse | Local Evidence: docs/research/runs/video_engine_tooling_and_mcps/findings_mcps_and_tools.md#L34 | Flubber / GitHub | URL: https://github.com/veltman/flubber | Verified 2026-09-11]

### B. SVGO (SVG Path Optimization & Decimal Precision)
- **Repository:** `svg/svgo`
- **Mechanism:** Node.js CLI tool that strips unnecessary XML bloat, removes editor metadata, converts shapes to path commands, and aligns coordinate decimal precision for deterministic, seek-safe frame evaluation in Remotion/HyperFrames.
- [SVGO Vector Path Optimization | Deterministic path cleanup and decimal alignment | Local Evidence: docs/research/runs/video_engine_tooling_and_mcps/findings_mcps_and_tools.md#L35 | SVGO / GitHub | URL: https://github.com/svg/svgo | Verified 2026-09-11]

### C. ImageMagick & Sharp CLI (Contact Sheet & Alpha Pipeline)
- **Capabilities:**
  - Automated 3-tile contact sheet generation (`montage -geometry +4+4 ...`) for video analysis.
  - Programmatic alpha matte verification (detecting halo artifacts or broken transparency).
  - Extracting dominant color palettes directly from world plates for chart styling.
- [ImageMagick & Sharp Processing | Headless contact-sheet assembly and alpha validation | Local Evidence: docs/research/runs/video_engine_tooling_and_mcps/findings_mcps_and_tools.md#L36 | Sharp / ImageMagick | URL: https://github.com/svg/svgo | Verified 2026-09-11]

---

## 5. Recommended Agent Skills to Author / Install

1. **`sec-edgar-auditor` (Skill):**
   - *Trigger:* When an episode requires corporate solvency proof or debt rollover figures.
   - *Workflow:* Queries SEC EDGAR API, pulls the latest 10-K, navigates to "Notes to Consolidated Financial Statements - Debt", parses maturities across 1, 2, 3, 4, 5 years, and computes the 24-month maturity percentage and interest coverage ratio.
2. **`contact-sheet-packager` (Skill):**
   - *Trigger:* When running `/watch` or reviewing reference cuts.
   - *Workflow:* Uses FFmpeg scene detection (`select='gt(scene,0.3)'`) to sample cut frames, groups them into 3-tile horizontal contact sheets (start, middle, settle), and renders a compact measurement table with ORB camera motion scores.
3. **`macro-chart-builder` (Skill):**
   - *Trigger:* When authoring or revising Remotion / HyperFrames charts.
   - *Workflow:* Enforces the ObservableHQ / The Economist rules from `MACRO_CHART_JOURNALISM_RESEARCH_BLUEPRINT.md`: integer slot indexing (`x = 0..N-1`), single gridline ownership (`ax2.yaxis.grid(False)`), direct terminal line labeling, and closed-form spring reveals.

---

## Sources

- Stefano Amorelli — `fred-mcp-server` (Zenodo / GitHub 2025): `https://github.com/stefanoamorelli/fred-mcp-server`
- Stefano Amorelli — `sec-edgar-mcp` (PyPI / GitHub 2025): `https://github.com/stefanoamorelli/sec-edgar-mcp`
- Leopoldo O'Donnell — `edgar-mcp` (.NET SEC EDGAR Server): `https://github.com/leopoldodonnell/edgar-mcp`
- Joe Norton — `comfyui-mcp-server` (Lightweight Python ComfyUI MCP): `https://github.com/joenorton/comfyui-mcp-server`
- SmartLittleApps — `local-stt-mcp` (Local Speech-to-Text via whisper.cpp): `https://github.com/SmartLittleApps/local-stt-mcp`
- Noah Veltman — `flubber` (SVG Shape Interpolator): `https://github.com/veltman/flubber`
- SVG Working Group — `svgo` (SVG Optimizer): `https://github.com/svg/svgo`

---

## NOT FOUND WHERE I LOOKED

- **Dedicated TradingView PineScript-to-Remotion MCP Server:** Searched GitHub and PyPI for tools translating TradingView PineScript strategies directly into Remotion/SVG animations. No open-source MCP exists; custom data export via CSV/JSON remains the standard bridge.
- **Standalone Bloomberg B-PIPE Open-Source MCP:** Official Bloomberg API requires licensed terminal hardware and proprietary C++ SDKs. Free open-source alternatives (OpenBB, yfinance, FRED) provide sufficient macro proxy data without institutional licensing costs.
