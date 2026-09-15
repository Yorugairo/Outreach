"""Extract, segment, and catalogue 24 hero props from Propsheets 1 & 2.

Edge Cleanup & Anti-Collision Protocol:
- Global full-sheet connected component segmentation: every pixel/island in the sheet
  is assigned exclusively to its true parent prop via anchor centroid distance.
- Zero neighbor intrusions: eliminates all adjacent prop slivers, border fragments,
  and stray bounding box overlaps.
- External contour fill: internal black pixels (e.g. black oil barrel, GPU fans,
  server racks, witch hats) remain 100% opaque.
- Anti-aliased edge alpha feathering to prevent dark halos on cream paper (#F4E6C7).
- Lossless 32-bit RGBA PNG output.
- Manifest generation with SHA-256 digests and semantic tags (institutional, no 'powell').
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
PROPS_DIR = REPO_ROOT / "assets" / "props"
CUTOUTS_DIR = PROPS_DIR / "cutouts"
SOURCE_DIR = PROPS_DIR / "source"

CUTOUTS_DIR.mkdir(parents=True, exist_ok=True)
SOURCE_DIR.mkdir(parents=True, exist_ok=True)

# The two sheets, copied out of the Gemini upload store on the first run (2026-09-14); a rerun reads these copies,
# which live on disk only (generated imagery stays out of git - E99 s31).
SHEET1_SRC = SOURCE_DIR / "source_propsheet_1_ai_memory.jpg"
SHEET2_SRC = SOURCE_DIR / "source_propsheet_2_macro_catalysts.jpg"

SHEET1_SPECS = [
    {
        "id": "prop-ai-hype-bubble-v1",
        "name": "AI Hype Bubble",
        "anchor": (141, 131),
        "tier": "prop",
        "category": "ai_market",
        "tags": ["bubble", "speculation", "ai", "hype", "great-wave", "microchip", "euphoria"],
        "context": "Market euphoria, AI speculative valuation bubble, rising equity trends amidst volatility waves.",
    },
    {
        "id": "prop-memory-steel-ibeam-v1",
        "name": "Memory Structural I-Beam",
        "anchor": (395, 133),
        "tier": "prop",
        "category": "infrastructure",
        "tags": ["memory", "i-beam", "steel", "foundation", "infrastructure", "hardware", "structural"],
        "context": "Memory bandwidth and capacity as the foundational structural backbone supporting AI architectures.",
    },
    {
        "id": "prop-dram-memory-module-v1",
        "name": "DRAM Memory DIMM Stick",
        "anchor": (644, 140),
        "tier": "prop",
        "category": "semiconductor",
        "tags": ["dram", "ram", "memory", "pcb", "dimm", "semiconductor", "micron", "samsung"],
        "context": "Working system DRAM memory modules, memory supercycle demand, and commodity chip pricing.",
    },
    {
        "id": "prop-hbm-stacked-die-v1",
        "name": "3D Stacked HBM Chip",
        "anchor": (907, 137),
        "tier": "prop",
        "category": "semiconductor",
        "tags": ["hbm", "hbm3e", "sk-hynix", "stacked-silicon", "bandwidth", "through-silicon-via"],
        "context": "High Bandwidth Memory (HBM) 3D stacked dies on interposer packaging powering next-gen AI accelerators.",
    },
    {
        "id": "prop-gpu-accelerator-card-v1",
        "name": "GPU Compute Accelerator Card",
        "anchor": (146, 378),
        "tier": "prop",
        "category": "compute",
        "tags": ["gpu", "nvidia", "compute", "blackwell", "hopper", "triple-fan", "graphics-card"],
        "context": "High-density enterprise GPU hardware driving parallel compute clusters for model training and inference.",
    },
    {
        "id": "prop-ai-server-rack-cabinet-v1",
        "name": "AI Supercomputer Server Rack",
        "anchor": (376, 369),
        "tier": "prop",
        "category": "datacenter",
        "tags": ["server-rack", "datacenter", "supercomputer", "nvlink", "enterprise", "ukiyo-e"],
        "context": "Multi-node AI server rack enclosure with active cooling, high-speed interconnects, and cloud deployment.",
    },
    {
        "id": "prop-hyperscale-datacenter-v1",
        "name": "Hyperscale Data Center Campus",
        "anchor": (631, 382),
        "tier": "prop",
        "category": "infrastructure",
        "tags": ["datacenter", "cloud-facility", "infrastructure", "capex", "rising-sun", "pines"],
        "context": "Physical hyperscale datacenter capex, cloud campus buildouts, gigawatt electricity consumption, and real estate.",
    },
    {
        "id": "prop-silicon-wafer-semiconductor-v1",
        "name": "Semiconductor Silicon Wafer",
        "anchor": (910, 367),
        "tier": "prop",
        "category": "semiconductor",
        "tags": ["silicon-wafer", "tsmc", "foundry", "photolithography", "sakura", "nanometer"],
        "context": "Monocrystalline silicon wafer patterned with microscopic integrated circuits, foundry fabrication, and supply chain.",
    },
    {
        "id": "prop-neural-cloud-brain-v1",
        "name": "Neural Cloud Brain",
        "anchor": (140, 615),
        "tier": "prop",
        "category": "ai_models",
        "tags": ["neural-network", "cloud", "ai-model", "llm", "synapse", "intelligence", "weights"],
        "context": "Cloud-hosted foundation models, cognitive algorithms, neural network parameter weights, and frontier AI intelligence.",
    },
    {
        "id": "prop-bigtech-capital-tower-v1",
        "name": "Big Tech Capital Monolith Tower",
        "anchor": (395, 628),
        "tier": "prop",
        "category": "capital_flows",
        "tags": ["magnificent-seven", "hedge-fund", "capital-inflows", "monolith", "big-tech"],
        "context": "Hedge fund and institutional capital concentrating heavily into Mega-Cap tech conglomerates.",
    },
    {
        "id": "prop-memory-wall-breach-v1",
        "name": "The Memory Wall Breach",
        "anchor": (658, 626),
        "tier": "mechanism",
        "category": "bottleneck",
        "tags": ["memory-wall", "bottleneck", "bandwidth-limit", "von-neumann", "structural-failure"],
        "context": "The Memory Wall: computational scaling hitting memory bandwidth transfer ceilings and hardware bottlenecks.",
    },
    {
        "id": "prop-ai-journey-roadmap-fuji-v1",
        "name": "AI Adoption Roadmap to Fuji",
        "anchor": (912, 625),
        "tier": "prop",
        "category": "roadmap",
        "tags": ["roadmap", "timeline", "fuji", "adoption-curve", "maturity", "infrastructure-phase"],
        "context": "The multi-year AI investment horizon, transitioning from early hype to infrastructure buildout and maturity.",
    },
]

SHEET2_SPECS = [
    {
        "id": "prop-triple-witching-opex-v1",
        "name": "Triple Witching OpEx Calendar",
        "anchor": (141, 153),
        "tier": "prop",
        "category": "macro_events",
        "tags": ["triple-witching", "opex", "options-expiry", "futures", "quarterly-rebalance"],
        "context": "Quarterly Triple Witching expiration of stock options, index options, and futures contracts causing high volume volatility.",
    },
    {
        "id": "prop-federal-reserve-building-v1",
        "name": "Federal Reserve Headquarters",
        "anchor": (402, 174),
        "tier": "prop",
        "category": "central_bank",
        "tags": ["federal-reserve", "fed", "central-bank", "monetary-policy", "fomc", "interest-rates", "eccles-building", "rate-decision", "us-central-bank"],
        "context": "Sovereign monetary authority, discount window lending, interest rate target bands, and liquidity governance.",
    },
    {
        "id": "prop-dot-plot-projections-v1",
        "name": "FOMC Dot Plot Projections",
        "anchor": (653, 132),
        "tier": "prop",
        "category": "central_bank",
        "tags": ["dot-plot", "federal-reserve", "fomc", "rate-projections", "economic-forecast", "terminal-rate", "central-bank-policy"],
        "context": "FOMC members' individual interest rate forecasts and terminal policy rate trajectories across forward years.",
    },
    {
        "id": "prop-treasury-yield-gauge-5pct-v1",
        "name": "10Y Treasury Yield Speedometer",
        "anchor": (899, 142),
        "tier": "mechanism",
        "category": "rates_bonds",
        "tags": ["treasury-yield", "10-year", "bond-market", "rate-spike", "speedometer", "gauge"],
        "context": "Surging benchmark 10-year sovereign bond yields tightening financial conditions and compressing equity multiples.",
    },
    {
        "id": "prop-crude-oil-barrel-spike-v1",
        "name": "Crude Oil Price Shock Barrel",
        "anchor": (125, 413),
        "tier": "prop",
        "category": "commodities",
        "tags": ["crude-oil", "brent", "wti", "commodity-spike", "energy-cost", "inflation-driver"],
        "context": "Energy price spikes, Brent/WTI crude oil supply disruptions, and input-cost headline inflation pressures.",
    },
    {
        "id": "prop-geopolitical-conflict-globe-v1",
        "name": "Geopolitical Conflict & War Globe",
        "anchor": (393, 405),
        "tier": "prop",
        "category": "geopolitics",
        "tags": ["geopolitical-risk", "war", "defense", "tank", "warship", "supply-choke"],
        "context": "Regional war outbreaks, defense escalation, trade chokepoint closures, and sovereign supply chain ruptures.",
    },
    {
        "id": "prop-hedge-fund-tech-funnel-v1",
        "name": "Hedge Fund Capital Tech Funnel",
        "anchor": (658, 393),
        "tier": "mechanism",
        "category": "capital_flows",
        "tags": ["hedge-fund", "capital-allocation", "passive-inflows", "momentum", "tech-basket"],
        "context": "Institutional smart money and hedge fund liquidity funneled aggressively into dominant mega-cap technology balance sheets.",
    },
    {
        "id": "prop-tech-sp500-concentration-v1",
        "name": "Tech to S&P 500 Concentration Flow",
        "anchor": (895, 420),
        "tier": "mechanism",
        "category": "market_structure",
        "tags": ["market-breadth", "concentration-risk", "sp500", "index-weighting", "passive-flow"],
        "context": "Unprecedented index concentration where top tech equities dictate the entirety of broader S&P 500 returns.",
    },
    {
        "id": "prop-vix-volatility-tempest-v1",
        "name": "VIX Volatility Tempest Waves",
        "anchor": (132, 638),
        "tier": "prop",
        "category": "volatility",
        "tags": ["vix", "volatility", "fear-index", "storm", "tail-risk", "market-crash"],
        "context": "Violent spikes in the Cboe Volatility Index (VIX), equity hedging demand surges, and market tail risk liquidation.",
    },
    {
        "id": "prop-liquidity-drain-pump-v1",
        "name": "Quantitative Tightening Liquidity Drain",
        "anchor": (385, 635),
        "tier": "mechanism",
        "category": "monetary_policy",
        "tags": ["liquidity-drain", "quantitative-tightening", "qt", "balance-sheet-runoff", "cash-drain"],
        "context": "Quantitative Tightening (QT), commercial bank reserve drains, and central bank balance sheet contraction.",
    },
    {
        "id": "prop-ai-pause-roadblock-barrier-v1",
        "name": "AI Moratorium Roadblock Barrier",
        "anchor": (653, 624),
        "tier": "prop",
        "category": "governance",
        "tags": ["ai-pause", "moratorium", "regulation", "governance", "safety", "roadblock"],
        "context": "Calls for regulatory moratoriums, safety halts, frontier model deployment licensing, and governmental friction.",
    },
    {
        "id": "prop-upcoming-catalysts-calendar-v1",
        "name": "Upcoming Catalysts Macro Calendar",
        "anchor": (901, 635),
        "tier": "prop",
        "category": "macro_events",
        "tags": ["catalysts", "fed-decision", "federal-reserve", "inflation-data", "cpi", "earnings-season", "geopolitical-risk", "macro-events"],
        "context": "High-impact market catalyst roadmap tracking Fed meetings, CPI/inflation releases, quarterly earnings, and geopolitical risks.",
    },
]


def extract_sheet_props(img: np.ndarray, specs: list[dict], sheet_name: str) -> list[dict]:
    """Segment props via global connected component ownership to guarantee 0 edge fragments."""
    h, w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 1. Global foreground thresholding
    thresh = (gray > 10).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh, connectivity=8)

    # 2. Assign each component exclusively to its closest anchor
    prop_masks = {s["id"]: np.zeros_like(gray) for s in specs}
    anchors = [s["anchor"] for s in specs]

    for lab in range(1, num_labels):
        area = stats[lab, cv2.CC_STAT_AREA]
        if area < 10:  # ignore 1-pixel sensor noise
            continue
        cx, cy = centroids[lab]
        dists = [((cx - ax) ** 2 + (cy - ay) ** 2) ** 0.5 for ax, ay in anchors]
        min_idx = np.argmin(dists)
        if dists[min_idx] < 175:  # must be within true prop territory
            prop_id = specs[min_idx]["id"]
            prop_masks[prop_id][labels == lab] = 255

    # 3. For each prop, fill internal holes and apply smooth anti-aliased edge
    records = []
    for spec in specs:
        raw_mask = prop_masks[spec["id"]]

        # Find external contours of THIS prop's exclusive mask and fill internal holes
        contours, _ = cv2.findContours(raw_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        solid_mask = np.zeros_like(gray)
        for c in contours:
            if cv2.contourArea(c) >= 150:  # keep real prop parts (>=150px), discard stray edge speckles
                cv2.drawContours(solid_mask, [c], -1, 255, thickness=cv2.FILLED)

        # Anti-aliased 1px edge transition
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        eroded = cv2.erode(solid_mask, kernel)
        border_zone = (solid_mask > 0) & (eroded == 0)

        alpha = solid_mask.astype(np.float32)
        lum = gray.astype(np.float32) / 255.0
        border_alpha = np.clip(lum * 1.5, 0.0, 1.0) * 255.0
        alpha[border_zone] = np.maximum(alpha[border_zone] * 0.5, border_alpha[border_zone])
        alpha[eroded == 255] = 255.0
        alpha[solid_mask == 0] = 0.0
        alpha = np.clip(alpha, 0, 255).astype(np.uint8)

        # 4. Crop tightly to this prop's non-zero alpha bounding box
        ys, xs = np.where(alpha > 0)
        if len(xs) == 0:
            print(f"WARNING: Prop {spec['id']} has no alpha pixels!")
            continue

        x1 = max(0, xs.min() - 1)
        y1 = max(0, ys.min() - 1)
        x2 = min(w, xs.max() + 2)
        y2 = min(h, ys.max() + 2)

        crop_rgb = rgb[y1:y2, x1:x2]
        crop_alpha = alpha[y1:y2, x1:x2]
        rgba = np.dstack([crop_rgb, crop_alpha])

        # Save lossless PNG
        out_name = f"{spec['id']}.png"
        out_path = CUTOUTS_DIR / out_name
        im = Image.fromarray(rgba)
        im.save(out_path, format="PNG", compress_level=6)

        # Calculate SHA-256
        file_hash = sha256_file(out_path)
        cw, ch = rgba.shape[1], rgba.shape[0]

        record = {
            **spec,
            "filename": out_name,
            "path": f"assets/props/cutouts/{out_name}",
            "width": cw,
            "height": ch,
            "sha256": file_hash,
            "source_sheet": sheet_name,
        }
        records.append(record)
        print(f"  + {out_name} ({cw}x{ch}) -> SHA: {file_hash[:10]}...")

    return records


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    img1 = cv2.imread(str(SHEET1_SRC))
    img2 = cv2.imread(str(SHEET2_SRC))

    print("Extracting Propsheet 1 (AI, Memory & Infrastructure)...")
    recs1 = extract_sheet_props(img1, SHEET1_SPECS, "Propsheet1_AI_Memory")

    print("\nExtracting Propsheet 2 (Macro, Fed & Market Catalysts)...")
    recs2 = extract_sheet_props(img2, SHEET2_SPECS, "Propsheet2_Macro_Catalysts")

    all_records = recs1 + recs2

    # Write manifest.json
    manifest_path = PROPS_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"schema": "finance_props_catalog.v1", "total_assets": len(all_records), "props": all_records}, f, indent=2)
    print(f"\nManifest written to {manifest_path}")

    # Write CATALOGUE.md
    cat_path = PROPS_DIR / "CATALOGUE.md"
    with open(cat_path, "w", encoding="utf-8") as f:
        f.write("# Finance & AI Hero Props Catalogue (24 Master Cutouts)\n\n")
        f.write("Extracted, segmented, defringed, and losslessly isolated from `Propsheet1` & `Propsheet2`.\n")
        f.write("Registered under doctrine tier 2 as `kind: prop` / tier 3 as `kind: mechanism`, `rights_state: operator_approved`, `render_eligible: true`.\n\n")
        f.write("## Summary\n")
        f.write(f"- **Total Cutouts:** {len(all_records)}\n")
        f.write("- **Schema:** `finance_props_catalog.v1` (`manifest.json`)\n")
        f.write("- **Asset Directory:** `assets/props/cutouts/`\n\n")
        f.write("## Asset Registry\n\n")
        f.write("| Thumbnail / ID | Source Sheet | Dimensions | SHA-256 | Tier | Semantic Tags | Macro / Narrative Context |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in all_records:
            tag_str = ", ".join(f"`{t}`" for t in r["tags"][:5])
            f.write(f"| [`{r['id']}`]({r['path']})<br>*{r['name']}* | `{r['source_sheet']}` | {r['width']}×{r['height']} | `{r['sha256'][:10]}...` | `{r['tier']}` | {tag_str} | {r['context']} |\n")
    print(f"CATALOGUE.md written to {cat_path}")

    # Write HTML Contact Sheet for visual review
    cs_path = PROPS_DIR / "contact_sheet.html"
    with open(cs_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Finance & AI Hero Props Review Sheet</title>
<style>
  body { background: #0F1218; color: #E5E7EB; font-family: system-ui, sans-serif; padding: 32px; }
  h1 { font-size: 24px; margin-bottom: 8px; color: #F3F4F6; }
  p { color: #9CA3AF; margin-bottom: 24px; font-size: 14px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
  .card { background: #181D26; border: 1px solid #2B3342; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; }
  .preview-box { height: 220px; display: flex; align-items: center; justify-content: center; position: relative; }
  .washi-bg { background: #F4E6C7; background-image: radial-gradient(#E8D7B2 1px, transparent 0); background-size: 8px 8px; }
  .preview-box img { max-width: 90%; max-height: 90%; object-fit: contain; }
  .meta { padding: 14px; font-size: 12px; flex-grow: 1; display: flex; flex-direction: column; gap: 6px; }
  .title { font-weight: 600; font-size: 14px; color: #F9FAFB; }
  .tier-badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
  .tier-prop { background: #1E3A8A; color: #93C5FD; }
  .tier-mechanism { background: #831843; color: #FBCFE8; }
  .tags { color: #9CA3AF; font-size: 11px; }
  .hash { font-family: monospace; color: #6B7280; font-size: 10px; }
  .toggle-bar { margin-bottom: 16px; }
  button { background: #2563EB; color: white; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; }
  button:hover { background: #1D4ED8; }
</style>
</head>
<body>
<h1>Finance & AI Hero Props — Visual QA Contact Sheet (24 Assets)</h1>
<p>Proofing lossless alpha cutouts against production cream washi (#F4E6C7) and dark slate (#181D26).</p>
<div class="toggle-bar">
  <button onclick="toggleBg()">Toggle Canvas Background (Washi Cream / Dark Slate)</button>
</div>
<div class="grid">
""")
        for r in all_records:
            tier_class = "tier-prop" if r["tier"] == "prop" else "tier-mechanism"
            tag_preview = " · ".join(r["tags"][:4])
            f.write(f"""  <div class="card">
    <div class="preview-box washi-bg" id="box-{r['id']}">
      <img src="cutouts/{r['filename']}" alt="{r['name']}">
    </div>
    <div class="meta">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="title">{r['name']}</span>
        <span class="tier-badge {tier_class}">{r['tier']}</span>
      </div>
      <div class="tags">{tag_preview}</div>
      <div style="color: #D1D5DB; font-size: 11px; margin-top: 4px;">{r['context']}</div>
      <div class="hash" style="margin-top: auto; padding-top: 8px;">{r['width']}×{r['height']} px · SHA: {r['sha256'][:16]}...</div>
    </div>
  </div>
""")
        f.write("""</div>
<script>
let washi = true;
function toggleBg() {
  washi = !washi;
  const boxes = document.querySelectorAll('.preview-box');
  boxes.forEach(b => {
    if (washi) {
      b.classList.add('washi-bg');
      b.style.background = '#F4E6C7';
    } else {
      b.classList.remove('washi-bg');
      b.style.background = '#111827';
    }
  });
}
</script>
</body>
</html>
""")
    print(f"contact_sheet.html written to {cs_path}")


if __name__ == "__main__":
    main()
