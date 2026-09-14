# Review Brief: "The Myth of Historical Normal" Production Package

Repository Root: `C:/Users/Snipe/Downloads/Outreach Program`
Addressee: Claude (`--lane claude`, profile: `reviewer`, replyShape: `review`)
Context: Faceless YouTube Production Engine (Channel: Money Physics)

## 1. Objective
Conduct an authoritative editorial, architectural, and doctrine compliance review of the complete production package for the upcoming long-form documentary episode:
**"The Myth of Historical Normal: How Small Changes Break Big Markets"** (Project: `content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/`).

## 2. Deliverables Under Review

1. **Spoken Narration (VO Track):**
   - File: `content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/SCRIPT-VO.txt`
   - Scope: Pure spoken text (no stage directions, all numbers written as words, calibrated to ~8:00 runtime).
2. **Production Script & Stage Directions:**
   - File: `content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/SCRIPT-PRODUCTION.md`
   - Scope: SC-01 through SC-11 synchronized 1:1 with audio cues, motion triggers, and visual props.
3. **Script Mechanical Gate Verification:**
   - File: `content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/SCRIPT-GATES.md`
   - Verification Commands:
     - `python content/video_engine/scripts/lint_script_pattern.py` (0 errors)
     - `python content/video_engine/scripts/audit_script_doctrine.py --pivot` (0 FAIL, 0 WARN)
     - `python content/video_engine/scripts/gate_opening_structure.py --ring --counterparty --timeline` (0 FAIL)
4. **Visual Choreography & Cut Schedule:**
   - File: `content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/VISUAL-CHOREOGRAPHY.md`
   - Scope: Scene-by-scene cut table, camera movements, spring physics ($\zeta = 0.82$, $\omega_0 = 14.5\text{ rad/s}$), and lighting states.
5. **Bravos-Style Production Evidence Pack:**
   - File: `content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/BRAVOS-STYLE-EVIDENCE-PACK.md`
   - Scope: Specifications for 6 still head cutouts, 5 diegetic TV-embed news video clips, 5 stacking press card crops, and screen time balance (80% own analysis vs 13% external claims).
6. **Market Intelligence & Provenance Blueprint:**
   - File: `docs/research/markets/TREASURY_YIELD_SPIKE_SEPTEMBER_2026_RESEARCH_BLUEPRINT.md`
   - Scope: Real-time September 2026 Treasury yield spike data (10Y at 4.95%, 30Y at 5.38% 19-year high, auction tail, SPR < 300M barrels).
7. **Video Engine Tooling & Open-Source MCP Blueprint:**
   - File: `docs/research/tech/VIDEO_ENGINE_TOOLING_AND_MCP_BLUEPRINT.md`
   - Scope: Local non-SaaS infrastructure (FRED MCP, SEC EDGAR MCP, ComfyUI MCP, local Whisper STT, Flubber, SVGO).

## 3. Four-Point Audit Mandate for Claude

Please review the package against these core standards:

1. **Doctrine Compliance & Anti-Recycling (Ruling A1):**
   - Confirm that the script is 100% free of recycled "steel or paper", locomotive, or railway metaphors.
   - Verify the 6-phase architecture (P1 Hook, P2 Mechanism, P3 Stress, P4 Pivot, P5 Solvency, P6 Synthesis) and the exact 50.0% structural pivot.
2. **Bravos Style Mechanics & Visual Pacing:**
   - Evaluate the choreographic rhythm: desk TV embed for external claims vs clean dark stage for proprietary balance models.
   - Verify the 1.2–2.5s visual pulse cadence (M16), 12.0s maximum bare plate limit, and dock transition choreography.
3. **Factual Integrity & 4-Tier Provenance:**
   - Verify that the September 2026 yield spike figures (4.95% 10Y, 5.38% 30Y, $1.08T federal net interest, -0.95% ERP) maintain valid primary source anchors without ungrounded extrapolations.
4. **Verification Commands to Execute:**
   - `python content/video_engine/scripts/audit_research_provenance.py`
   - `python content/video_engine/scripts/audit_script_doctrine.py --pivot`
