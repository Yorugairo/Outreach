"""
Extract, segment, antialias, and catalogue 44 finance icons from Icons1.png - Icons4.png.

Adheres strictly to content video engine doctrine:
- kind: 'prop' (tier 2)
- rights_state: 'original_review_only'
- review_state: 'review_only'
- render_eligible: False
- sha256 checksums on all outputs
- Schema-compliant catalogue: finance_icons_catalog.v1.json
"""

import hashlib
import json
import os
from pathlib import Path
import cv2
import numpy as np


BASE_DIR = Path(r"C:\Users\Snipe\Downloads\Outreach Program\content\video_engine")
ICONS_DIR = BASE_DIR / "assets" / "icons"
CUTOUTS_DIR = ICONS_DIR / "cutouts"


# -------------------------------------------------------------------------
# Metadata definitions for all 44 icons
# -------------------------------------------------------------------------

ICONS1_META = [
    # Row 1
    {
        "row": 1, "col": 1,
        "asset_id": "prop-icon-bull-market-v1",
        "title": "Bull Market Rally",
        "visual": "Charging bull silhouetted in dark charcoal with cream and gold horns before a glowing red sun with an ascending trendline.",
        "macro": "Equities bull market, expansion phase, risk-on capital sentiment, and market rally.",
        "tags": ["bull-market", "equities-rally", "expansion", "risk-on", "wall-street"],
        "lenses": ["market-sentiment", "macro-cycles", "equities"],
        "factual_text": False,
    },
    {
        "row": 1, "col": 2,
        "asset_id": "prop-icon-bear-market-v1",
        "title": "Bear Market Contraction",
        "visual": "Imposing grizzly bear silhouetted against a setting red sun, with a descending trendline and defensive stance.",
        "macro": "Bear market drawdown, recessionary pressure, risk-off capital flight, and equity valuation contraction.",
        "tags": ["bear-market", "drawdown", "recession", "risk-off", "market-correction"],
        "lenses": ["market-sentiment", "macro-cycles", "risk-management"],
        "factual_text": False,
    },
    {
        "row": 1, "col": 3,
        "asset_id": "prop-icon-semiconductor-silicon-v1",
        "title": "Semiconductor Silicon Die",
        "visual": "Square microchip processor die with golden circuit pins and PCB trace lines radiating outward on a radiant red sun.",
        "macro": "Foundational semiconductor compute, fabless chip design, microarchitecture, and silicon supply chains.",
        "tags": ["semiconductor", "microchip", "silicon-die", "hardware", "integrated-circuit"],
        "lenses": ["technology-infrastructure", "semiconductors", "supply-chains"],
        "factual_text": False,
    },
    {
        "row": 1, "col": 4,
        "asset_id": "prop-icon-global-macro-growth-v1",
        "title": "Global Macro Growth",
        "visual": "Earth globe with latitudinal grid lines overlaid with a surging upward gold bar chart and arrow across the continents.",
        "macro": "Global economic expansion, worldwide GDP acceleration, cross-border capital flows, and international commerce.",
        "tags": ["global-macro", "world-gdp", "economic-growth", "international-trade", "cross-border-flows"],
        "lenses": ["global-macro", "trade", "gdp"],
        "factual_text": False,
    },
    {
        "row": 1, "col": 5,
        "asset_id": "prop-icon-central-bank-fx-v1",
        "title": "Central Bank Colonnade & Reserve",
        "visual": "Neoclassical Greco-Roman central bank colonnade with a large gold dollar emblem centered in the triangular pediment.",
        "macro": "Central banking authority, Federal Reserve monetary policy, discount window, and institutional currency reserves.",
        "tags": ["central-bank", "federal-reserve", "monetary-authority", "dollar-clearing", "banking-system"],
        "lenses": ["central-banking", "monetary-policy", "sovereign-debt"],
        "factual_text": False,
    },
    # Row 2
    {
        "row": 2, "col": 1,
        "asset_id": "prop-icon-crude-oil-energy-v1",
        "title": "Crude Oil & Petroleum Reserve",
        "visual": "Industrial oil derrick drilling rig flanked by stacked steel crude oil barrels and rising smoke under a red sun.",
        "macro": "Energy commodities, Brent/WTI crude pricing, petrochemical refining, and OPEC+ supply decisions.",
        "tags": ["crude-oil", "petroleum", "brent-wti", "energy-commodities", "opec-supply"],
        "lenses": ["commodities", "energy", "inflation-drivers"],
        "factual_text": False,
    },
    {
        "row": 2, "col": 2,
        "asset_id": "prop-icon-critical-minerals-mining-v1",
        "title": "Critical Minerals & Mining",
        "visual": "Minecart laden with raw mineral ores and crystals, crossed with a miner pickaxe against a mountain silhouette and red sun.",
        "macro": "Critical minerals extraction, rare earth elements, copper/lithium feedstock for electrification, and geopolitical mineral bottlenecks.",
        "tags": ["critical-minerals", "rare-earths", "mining-ores", "lithium-copper", "extractive-industry"],
        "lenses": ["commodities", "supply-chains", "electrification"],
        "factual_text": False,
    },
    {
        "row": 2, "col": 3,
        "asset_id": "prop-icon-maritime-shipping-logistics-v1",
        "title": "Maritime Shipping Logistics",
        "visual": "Ocean container vessel laden with cargo containers navigating rolling stylized waves under a red sun.",
        "macro": "Global maritime freight, supply chain bottlenecks, container shipping rates, and international trade routes.",
        "tags": ["maritime-shipping", "container-freight", "global-supply-chain", "logistics", "trade-routes"],
        "lenses": ["trade", "logistics", "supply-chains"],
        "factual_text": False,
    },
    {
        "row": 2, "col": 4,
        "asset_id": "prop-icon-geopolitical-strategy-v1",
        "title": "Geopolitical Strategy Chess",
        "visual": "Carved chess knight piece positioned on a perspective chessboard, flanked by a rising trendline and sun.",
        "macro": "Geopolitical game theory, economic statecraft, sanctions, strategic defense posture, and sovereign capital positioning.",
        "tags": ["geopolitics", "strategic-game-theory", "macro-positioning", "capital-chess", "foreign-policy"],
        "lenses": ["geopolitics", "game-theory", "macro-strategy"],
        "factual_text": False,
    },
    {
        "row": 2, "col": 5,
        "asset_id": "prop-icon-japan-macro-equities-v1",
        "title": "Japan Macro Equities",
        "visual": "Mount Fuji with a stylized red sun and rising gold bar chart depicting Japanese equity revaluation.",
        "macro": "Bank of Japan policy normalization, Tokyo Stock Exchange corporate governance reform, and Nikkei equity re-rating.",
        "tags": ["japan-macro", "nikkei-index", "bank-of-japan", "tokyo-markets", "yen-assets"],
        "lenses": ["international-macro", "japan", "equities"],
        "factual_text": False,
    },
    # Row 3
    {
        "row": 3, "col": 1,
        "asset_id": "prop-icon-money-printing-liquidity-v1",
        "title": "Intaglio Printing Press & Liquidity",
        "visual": "Vintage intaglio mechanical printing press churning out sheets of banknotes with dollar marks under a red sun.",
        "macro": "Quantitative easing (QE), central bank balance sheet expansion, fiat debasement, and M2 money supply growth.",
        "tags": ["money-printing", "quantitative-easing", "liquidity-injection", "m2-expansion", "fiat-debasement"],
        "lenses": ["monetary-policy", "central-banking", "liquidity"],
        "factual_text": False,
    },
    {
        "row": 3, "col": 2,
        "asset_id": "prop-icon-interest-rates-monetary-policy-v1",
        "title": "Interest Rates & Monetary Policy",
        "visual": "Percentage symbol on a disc with an arrow illustrating interest rate cuts and policy shifts.",
        "macro": "Federal funds rate, central bank policy pivots, rate cuts/hikes, and the cost of debt capital.",
        "tags": ["interest-rates", "federal-funds-rate", "central-bank-policy", "rate-cuts", "monetary-easing"],
        "lenses": ["monetary-policy", "fixed-income", "interest-rates"],
        "factual_text": False,
    },
    {
        "row": 3, "col": 3,
        "asset_id": "prop-icon-innovation-ip-capital-v1",
        "title": "Innovation & IP Capital",
        "visual": "Glowing incandescent lightbulb filament with an upward-surging diagonal vector arrow symbolizing intellectual property.",
        "macro": "Patents and technological moats, corporate R&D capex, disruptive innovation, and commercialized IP value.",
        "tags": ["innovation", "intellectual-property", "rd-capital", "patents", "disruptive-tech"],
        "lenses": ["technology", "intangible-assets", "corporate-finance"],
        "factual_text": False,
    },
    {
        "row": 3, "col": 4,
        "asset_id": "prop-icon-ai-neural-compute-v1",
        "title": "AI Neural Compute Architecture",
        "visual": "Profile of a human mind integrated with neural network nodes, synaptic circuits, and an illuminated core.",
        "macro": "Frontier AI models, neural network scaling laws, cognitive labor automation, and deep learning compute.",
        "tags": ["ai-compute", "neural-networks", "machine-learning", "cognitive-infrastructure", "frontier-models"],
        "lenses": ["artificial-intelligence", "compute", "labor-productivity"],
        "factual_text": False,
    },
    {
        "row": 3, "col": 5,
        "asset_id": "prop-icon-seed-capital-growth-v1",
        "title": "Seed Capital & Venture Growth",
        "visual": "Hand tenderly planting a gold coin sprout into rich soil, with emerging green leaves under a red sun.",
        "macro": "Venture capital, early-stage equity financing, capital formation, and compound investment growth.",
        "tags": ["seed-capital", "venture-capital", "early-stage-investment", "compound-growth", "angel-funding"],
        "lenses": ["venture-capital", "capital-formation", "private-equity"],
        "factual_text": False,
    },
]


ICONS2_META = [
    # Row 1
    {
        "row": 1, "col": 1,
        "asset_id": "prop-icon-global-macro-expansion-v2",
        "title": "Global Macro Expansion",
        "visual": "Planet Earth with ascending 5-bar gold chart and sweeping white arrow piercing upward into the red sun.",
        "macro": "Synchronized global expansion, cross-border trade acceleration, and rising international equity markets.",
        "tags": ["global-macro-expansion", "world-gdp", "economic-expansion", "trade-flows", "equity-rally"],
        "lenses": ["global-macro", "gdp", "trade"],
        "factual_text": False,
    },
    {
        "row": 1, "col": 2,
        "asset_id": "prop-icon-cpi-inflation-basket-v1",
        "title": "CPI Inflation Basket",
        "visual": "Woven wicker basket containing a suburban house, debt contracts, gold bars, oil drum, and wheat stalks under a red sun.",
        "macro": "Consumer Price Index basket of goods, cost-of-living tracking, real asset purchasing power, and commodity hedging.",
        "tags": ["cpi-basket", "inflation-index", "cost-of-living", "real-assets", "commodity-hedge"],
        "lenses": ["inflation", "commodities", "consumer-prices"],
        "factual_text": False,
    },
    {
        "row": 1, "col": 3,
        "asset_id": "prop-icon-us-dollar-reserve-v1",
        "title": "King Dollar Reserve Currency",
        "visual": "Heavy minted gold coin with bold dollar sign radiating sunbeams on a vibrant vermilion ground.",
        "macro": "US Dollar hegemony, global reserve currency status, foreign exchange settlement, and DXY strength.",
        "tags": ["us-dollar", "king-dollar", "reserve-currency", "fiat-hegemony", "dollar-index-dxy"],
        "lenses": ["currencies", "central-banking", "sovereignty"],
        "factual_text": False,
    },
    {
        "row": 1, "col": 4,
        "asset_id": "prop-icon-cash-liquidity-stack-v1",
        "title": "Cash Liquidity & Dry Powder",
        "visual": "Thick strapped bundle of US $100 Federal Reserve banknotes on a red circular disc.",
        "macro": "Balance sheet liquidity, corporate dry powder, risk-off money market flight, and immediate capital deployment.",
        "tags": ["cash-liquidity", "dry-powder", "cash-reserves", "money-market", "safe-haven-cash"],
        "lenses": ["liquidity", "balance-sheet", "treasury-management"],
        "factual_text": False,
    },
    # Row 2
    {
        "row": 2, "col": 1,
        "asset_id": "prop-icon-japan-nikkei-expansion-v1",
        "title": "Nikkei 225 Bull Expansion",
        "visual": "Snow-capped Mount Fuji before a red sun with an ascending 5-bar gold chart and a jagged trendline arrow climbing past the summit.",
        "macro": "Japanese equity bull market, Nikkei index highs, Bank of Japan reflation policy, and corporate Tokyo restructuring.",
        "tags": ["japan-macro", "nikkei-225", "boj-reflation", "tokyo-equities", "japan-bull-market"],
        "lenses": ["international-macro", "japan", "equities"],
        "factual_text": False,
    },
    {
        "row": 2, "col": 2,
        "asset_id": "prop-icon-candlestick-price-action-v1",
        "title": "Candlestick Price Action",
        "visual": "Five Japanese financial candlesticks with wicks (alternating bullish cream/gold and bearish red) against a midnight sky and red sun.",
        "macro": "Market microstructure, technical trading price action, order flow imbalances, and intraday volatility.",
        "tags": ["candlestick-chart", "price-action", "technical-analysis", "order-flow", "volatility"],
        "lenses": ["market-microstructure", "trading", "technical-analysis"],
        "factual_text": False,
    },
    {
        "row": 2, "col": 3,
        "asset_id": "prop-icon-earnings-beat-bullish-filing-v1",
        "title": "Bullish 10-Q Earnings Beat",
        "visual": "White financial report page with upward green trendline arrow and 4-bar green chart on a radiant red sun.",
        "macro": "Quarterly earnings beat, corporate revenue acceleration, operating margin expansion, and raised guidance.",
        "tags": ["earnings-beat", "10-q-filing", "revenue-growth", "margin-expansion", "guidance-raise"],
        "lenses": ["corporate-finance", "earnings", "fundamental-analysis"],
        "factual_text": False,
    },
    {
        "row": 2, "col": 4,
        "asset_id": "prop-icon-earnings-miss-bearish-filing-v1",
        "title": "Bearish 10-Q Earnings Miss",
        "visual": "Financial report page with collapsing red 5-bar chart and sharp downward red trendline arrow on a red sun.",
        "macro": "Corporate earnings miss, guidance cut, margin degradation, asset write-downs, and financial distress.",
        "tags": ["earnings-miss", "guidance-downgrade", "margin-compression", "impairment", "revenue-decline"],
        "lenses": ["corporate-finance", "earnings", "fundamental-analysis"],
        "factual_text": False,
    },
    # Row 3
    {
        "row": 3, "col": 1,
        "asset_id": "prop-icon-us-sovereign-markets-v1",
        "title": "US Sovereign Markets & Wall St",
        "visual": "Statue of Liberty holding torch high, backed by the US Stars and Stripes flag and a radiant red rising sun.",
        "macro": "American economic exceptionalism, US Treasury debt markets, Wall Street institutional equity dominance, and dollar assets.",
        "tags": ["us-sovereignty", "wall-street", "us-treasuries", "american-markets", "statue-of-liberty"],
        "lenses": ["sovereign-debt", "us-economy", "equities"],
        "factual_text": False,
    },
    {
        "row": 3, "col": 2,
        "asset_id": "prop-icon-four-pillar-asset-allocation-v1",
        "title": "Four-Pillar Asset Allocation",
        "visual": "Circular 4-quadrant asset allocation pie: Equities (stocks chart), Real Estate (house), Commodities (gold bars), ESG/Agri (seedling).",
        "macro": "Modern Portfolio Theory (MPT), balanced multi-asset allocation, All-Weather risk parity, and asset diversification.",
        "tags": ["asset-allocation", "modern-portfolio-theory", "all-weather-portfolio", "risk-parity", "diversification"],
        "lenses": ["portfolio-construction", "risk-management", "wealth-preservation"],
        "factual_text": False,
    },
    {
        "row": 3, "col": 3,
        "asset_id": "prop-icon-fuji-structural-growth-v1",
        "title": "Mount Fuji Structural Growth",
        "visual": "Mount Fuji with a stepped ascending gold bar chart and an upward curving vector surging into the red sun.",
        "macro": "Long-term Asian capital cycles, Yen revaluation dynamics, industrial capex, and structural economic compounding.",
        "tags": ["japan-structural-growth", "asian-equities", "yen-revaluation", "industrial-capex", "fuji-growth"],
        "lenses": ["international-macro", "japan", "industrial-cycles"],
        "factual_text": False,
    },
    {
        "row": 3, "col": 4,
        "asset_id": "prop-icon-market-tsunami-crash-v1",
        "title": "Financial Tsunami & Market Crash",
        "visual": "Hokusai-style Great Wave crashing violently across a plunging jagged red trendline breaking falling white bars.",
        "macro": "Liquidity black swan, systemic market collapse, cascading margin liquidations, debt defaults, and crisis panic.",
        "tags": ["market-crash", "liquidity-tsunami", "black-swan", "margin-call-wave", "systemic-collapse"],
        "lenses": ["crisis-mechanics", "liquidity-shocks", "risk-management"],
        "factual_text": False,
    },
]


ICONS3_META = [
    # Row 1
    {
        "row": 1, "col": 1,
        "asset_id": "prop-icon-datacenter-hyperscaler-clusters-v1",
        "title": "Datacenter Hyperscaler Clusters",
        "visual": "Server racks with status LEDs receding in perspective across a grid floor against a red sun.",
        "macro": "Enterprise AI cluster buildouts, cloud hyperscaler capex (AWS, Azure, GCP), and high-density compute infrastructure.",
        "tags": ["datacenter", "hyperscaler", "cloud-clusters", "ai-infrastructure", "server-capex"],
        "lenses": ["cloud-infrastructure", "datacenter-capex", "ai-hardware"],
        "factual_text": False,
    },
    {
        "row": 1, "col": 2,
        "asset_id": "prop-icon-microprocessor-silicon-die-v1",
        "title": "Microprocessor Silicon Core",
        "visual": "Square microchip silicon processor die with golden PCB circuit traces radiating symmetrically to the perimeter.",
        "macro": "Silicon microprocessor architecture, central processing units (CPUs), ASICs, and fabless chip engineering.",
        "tags": ["semiconductor", "microprocessor", "cpu-asic", "silicon-die", "chip-design"],
        "lenses": ["semiconductors", "chip-design", "technology-infrastructure"],
        "factual_text": False,
    },
    {
        "row": 1, "col": 3,
        "asset_id": "prop-icon-dram-hbm-memory-modules-v1",
        "title": "DRAM & HBM Memory Modules",
        "visual": "Two angled dual-in-line memory modules (DIMM RAM sticks) with visible memory chips and gold connector pins.",
        "macro": "High Bandwidth Memory (HBM), DRAM memory pricing supercycle, Micron / SK Hynix / Samsung memory duopoly.",
        "tags": ["dram-memory", "hbm-memory", "dimm-modules", "memory-supercycle", "micron-samsung-hynix"],
        "lenses": ["semiconductors", "memory-hardware", "hardware-cycles"],
        "factual_text": False,
    },
    {
        "row": 1, "col": 4,
        "asset_id": "prop-icon-micron-memory-orbit-v1",
        "title": "Micron Technology Pure-Play",
        "visual": "DRAM memory stick in foreground with a planetary orbital ring encircling an 'M' emblem over mountain ridges and red sun.",
        "macro": "Micron Technology (MU), pure-play memory manufacturing, semiconductor storage capex, and institutional tech positioning.",
        "tags": ["micron-technology", "mu-stock", "memory-pure-play", "semiconductor-memory", "storage-cycle"],
        "lenses": ["equities", "semiconductors", "memory-hardware"],
        "factual_text": False,
    },
    # Row 2
    {
        "row": 2, "col": 1,
        "asset_id": "prop-icon-wafer-foundry-advanced-packaging-v1",
        "title": "Wafer Foundry & CoWoS Packaging",
        "visual": "Photolithography silicon wafer grid disc in foreground with an abstract geometric red/gold ribbon motif hovering over mountains.",
        "macro": "TSMC pure-play foundry fabrication, advanced 2.5D/3D packaging (CoWoS), extreme ultraviolet (EUV) lithography.",
        "tags": ["silicon-wafer", "foundry-fabrication", "advanced-packaging", "tsmc-cowos", "photolithography"],
        "lenses": ["semiconductors", "foundry-economics", "supply-chains"],
        "factual_text": False,
    },
    {
        "row": 2, "col": 2,
        "asset_id": "prop-icon-chiplet-bga-package-v1",
        "title": "Chiplet Heterogeneous Integration",
        "visual": "High-density multi-chip semiconductor package (BGA socketed chiplet) with blue elliptical badge motif over mountain terrain.",
        "macro": "Heterogeneous chiplet architecture, System-in-Package (SiP), modular silicon yield optimization, and enterprise packaging.",
        "tags": ["chiplet-architecture", "bga-package", "system-in-package", "heterogeneous-compute", "semiconductor-packaging"],
        "lenses": ["semiconductors", "chip-design", "hardware-engineering"],
        "factual_text": False,
    },
    {
        "row": 2, "col": 3,
        "asset_id": "prop-icon-hardware-display-workstation-v1",
        "title": "Enterprise Workstation & Hardware",
        "visual": "Dual-display desktop setup (desktop monitor and open laptop) with Mount Fuji wallpapers, backed by mountains and a red sun.",
        "macro": "Enterprise IT hardware refresh cycles, workstation productivity capex, personal computing demand, and developer tooling.",
        "tags": ["workstation-hardware", "enterprise-it", "hardware-refresh", "dual-monitors", "developer-tooling"],
        "lenses": ["enterprise-tech", "hardware-cycles", "productivity"],
        "factual_text": False,
    },
    {
        "row": 2, "col": 4,
        "asset_id": "prop-icon-ai-neural-processor-mind-v1",
        "title": "AI Neural Processor Mind",
        "visual": "Human head profile silhouette enclosing a dense circuit neural network connected to a central glowing microprocessor die.",
        "macro": "Artificial general intelligence (AGI) roadmap, cognitive capital substitution, frontier neural architectures, and software eating labor.",
        "tags": ["artificial-intelligence", "neural-processor", "cognitive-compute", "frontier-ai", "human-ai-capital"],
        "lenses": ["artificial-intelligence", "labor-markets", "productivity"],
        "factual_text": False,
    },
    # Row 3
    {
        "row": 3, "col": 1,
        "asset_id": "prop-icon-gpu-ai-accelerator-v1",
        "title": "AI GPU Accelerator",
        "visual": "Massive high-end triple-fan graphics card (GPU AI accelerator) rendered in gold and dark charcoal linework over mountain ridges.",
        "macro": "Parallel compute hardware, Nvidia GPU monopoly (Hopper/Blackwell), tensor core accelerators, and AI training clusters.",
        "tags": ["gpu-accelerator", "nvidia-h100-blackwell", "parallel-compute", "ai-hardware", "graphics-silicon"],
        "lenses": ["semiconductors", "ai-hardware", "hardware-cycles"],
        "factual_text": False,
    },
    {
        "row": 3, "col": 2,
        "asset_id": "prop-icon-electrical-grid-transmission-v1",
        "title": "Electric Power Grid Transmission",
        "visual": "High-voltage steel transmission tower pylon with power cables stretching across mountain valleys under a red sun.",
        "macro": "Electrical grid capacity constraints, utility interconnect queues, transmission infrastructure, and power bottlenecks for AI.",
        "tags": ["electric-grid", "transmission-lines", "utility-infrastructure", "power-bottlenecks", "electrification"],
        "lenses": ["utilities", "energy-infrastructure", "grid-capacity"],
        "factual_text": False,
    },
    {
        "row": 3, "col": 3,
        "asset_id": "prop-icon-energy-demand-surge-v1",
        "title": "Electricity Demand Surge",
        "visual": "Radiant gold circular gear/sun badge enclosing a bold lightning bolt, driving an ascending 4-bar chart with an upward vector arrow.",
        "macro": "Datacenter power demand explosion, utility sector earnings growth, rising kilowatt-hour electricity costs, and power generation capex.",
        "tags": ["energy-demand-surge", "datacenter-power", "utility-growth", "clean-power-capex", "electricity-spike"],
        "lenses": ["energy", "utilities", "datacenter-power"],
        "factual_text": False,
    },
    {
        "row": 3, "col": 4,
        "asset_id": "prop-icon-nuclear-energy-smr-v1",
        "title": "Nuclear Energy & SMR Baseload",
        "visual": "Nuclear power plant cooling towers releasing steam plumes, stamped with trefoil radiation symbol, situated by water reservoir.",
        "macro": "24/7 carbon-free baseload power, small modular reactors (SMRs), uranium commodity bull market, and tech power purchase agreements.",
        "tags": ["nuclear-power", "smr-reactors", "baseload-clean-energy", "uranium-renaissance", "datacenter-power-contract"],
        "lenses": ["energy", "nuclear-power", "clean-tech"],
        "factual_text": False,
    },
]


ICONS4_META = [
    {
        "slot": 0,
        "x_range": (10, 345),
        "asset_id": "prop-badge-sp500-us-index-v1",
        "title": "S&P 500 Benchmark Index",
        "visual": "American flag, ascending 5-bar gold chart, surging arrow, with typographic label 'S&P 500' and three gold stars.",
        "macro": "The definitive benchmark for US large-cap equities, passive ETF inflows (SPY/VOO), index concentration, and core portfolio returns.",
        "tags": ["sp500-index", "us-equities-benchmark", "passive-investing", "large-cap-stocks", "wall-street-core"],
        "lenses": ["equities", "benchmarks", "passive-investing"],
        "factual_text": True,
    },
    {
        "slot": 1,
        "x_range": (345, 670),
        "asset_id": "prop-badge-soxx-semiconductor-etf-v1",
        "title": "SOXX Semiconductor ETF",
        "visual": "Semiconductor microchip enclosing 4-bar chart and upward trendline, with typographic label 'SOXX' bracketed by horizontal bars.",
        "macro": "iShares Semiconductor ETF (SOXX), benchmark tracking cyclical chipmakers, fabless designers, and semiconductor capital equipment.",
        "tags": ["soxx-etf", "semiconductor-index", "chipmakers-basket", "hardware-beta", "ishares-semiconductor"],
        "lenses": ["semiconductors", "etfs", "hardware-cycles"],
        "factual_text": True,
    },
    {
        "slot": 2,
        "x_range": (670, 998),
        "asset_id": "prop-badge-dram-memory-etf-v1",
        "title": "DRAM Memory Sector ETF",
        "visual": "Dual DRAM memory sticks tilted in front of Mount Fuji and red sun, with typographic label 'DRAM ETF' and mini ascending chart.",
        "macro": "Thematic memory sector basket tracking cyclical memory manufacturers, DRAM supply-demand cycles, and high-bandwidth memory exposure.",
        "tags": ["dram-etf", "memory-chip-basket", "micron-samsung-hynix", "cyclical-memory", "storage-etf"],
        "lenses": ["semiconductors", "memory-hardware", "etfs"],
        "factual_text": True,
    },
    {
        "slot": 3,
        "x_range": (998, 1330),
        "asset_id": "prop-badge-pe-ratio-valuation-v1",
        "title": "P/E Ratio Valuation Multiple",
        "visual": "Formal financial statement with bold typography 'P/E', ascending 4-bar chart, and desktop accounting calculator.",
        "macro": "Price-to-Earnings fundamental valuation, multiple expansion vs compression, earnings yield, and valuation multiples.",
        "tags": ["pe-ratio", "valuation-multiple", "equity-valuation", "fundamental-analysis", "accounting-calculator"],
        "lenses": ["valuation", "fundamental-analysis", "accounting"],
        "factual_text": True,
    },
    {
        "slot": 4,
        "x_range": (1330, 1665),
        "asset_id": "prop-badge-fundamental-financial-audit-v1",
        "title": "Fundamental Financial Audit",
        "visual": "Stacked 10-K / balance sheet filings inspected under brass magnifying glass on '$' dollar mark, backed by city skyscrapers.",
        "macro": "Forensic balance sheet audits, cash flow due diligence, earnings quality verification, SEC 10-K review, and institutional accounting.",
        "tags": ["financial-audit", "forensic-accounting", "sec-10k-filings", "balance-sheet-audit", "due-diligence"],
        "lenses": ["accounting", "auditing", "fundamental-analysis"],
        "factual_text": False,
    },
]


# -------------------------------------------------------------------------
# Segmentation & Cutout Engine
# -------------------------------------------------------------------------

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def segment_and_save_cutout(crop: np.ndarray, dark_thresh: int, output_path: Path, pad_final: int = 4) -> tuple[int, int, str]:
    """
    Takes an RGB crop of an icon, identifies the background via external border
    connected components (preserving dark interior ink lines), performs anti-aliasing
    and color defringing, tight-crops, and saves as a broadcast-grade transparent RGBA PNG.
    """
    ch, cw = crop.shape[:2]
    crop_f = crop.astype(np.float32)

    # 1. Background detection: sample dark border color
    border_pixels = np.concatenate([
        crop[:5, :, :3], crop[-5:, :, :3],
        crop[:, :5, :3], crop[:, -5:, :3]
    ], axis=None).reshape(-1, 3)
    bg_col = np.median(border_pixels, axis=0)

    # 2. Binary dark pixel map
    is_dark = (np.max(crop[:, :, :3], axis=2) < dark_thresh).astype(np.uint8)

    # 3. Connected components on dark pixels
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(is_dark)

    # Find labels touching the crop border
    border_labels = set(np.unique(labels[0, :])).union(
        np.unique(labels[-1, :]),
        np.unique(labels[:, 0]),
        np.unique(labels[:, -1])
    )

    # Background = dark pixels connected to the outer border
    bg_mask = np.isin(labels, list(border_labels)) & (is_dark == 1)
    fg_mask = (~bg_mask).astype(np.uint8) * 255

    # 4. Antialiasing via Gaussian Blur on the mask boundary
    fg_blur = cv2.GaussianBlur(fg_mask, (3, 3), 0.75).astype(np.float32) / 255.0
    alpha_3 = np.repeat(fg_blur[:, :, np.newaxis], 3, axis=2)

    # 5. Defringe: unblend background color in the semi-transparent border zone
    unblended = (crop_f[:, :, :3] - (1.0 - alpha_3) * bg_col.reshape(1, 1, 3)) / np.maximum(alpha_3, 0.01)
    clean_rgb = np.clip(unblended, 0, 255).astype(np.uint8)

    # 6. Find tight bounding box of foreground
    nz_y, nz_x = np.where(fg_mask > 0)
    y_min, y_max = max(0, nz_y.min() - pad_final), min(ch - 1, nz_y.max() + pad_final)
    x_min, x_max = max(0, nz_x.min() - pad_final), min(cw - 1, nz_x.max() + pad_final)

    tight_rgb = clean_rgb[y_min:y_max+1, x_min:x_max+1]
    tight_alpha = (fg_blur * 255)[y_min:y_max+1, x_min:x_max+1].astype(np.uint8)

    rgba = np.dstack([tight_rgb, tight_alpha])

    # 7. Write transparent PNG
    cv2.imwrite(str(output_path), rgba)

    height, width = rgba.shape[:2]
    digest = compute_sha256(output_path)
    return width, height, digest


def process_grid_sheet(sheet_name: str, num_rows: int, num_cols: int, dark_thresh: int, meta_list: list[dict], pad: int = 14) -> list[dict]:
    sheet_path = ICONS_DIR / sheet_name
    img = cv2.imread(str(sheet_path))
    if img is None:
        raise FileNotFoundError(f"Could not load {sheet_path}")

    # Detect components using morphological closing
    bg_mask_full = (np.max(img[:, :, :3], axis=2) < dark_thresh)
    fg_full = (~bg_mask_full).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    fg_closed = cv2.morphologyEx(fg_full, cv2.MORPH_CLOSE, kernel)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(fg_closed)

    comps = []
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] > 8000:
            comps.append((stats[i], centroids[i]))

    # Sort into rows by y centroid
    comps.sort(key=lambda c: c[1][1])
    expected_total = num_rows * num_cols
    if len(comps) != expected_total:
        raise ValueError(f"{sheet_name}: Expected {expected_total} components, found {len(comps)}")

    rows = []
    for r in range(num_rows):
        start = r * num_cols
        row_slice = comps[start:start + num_cols]
        row_slice.sort(key=lambda c: c[1][0]) # sort by x
        rows.append(row_slice)

    results = []
    for r_idx, row in enumerate(rows):
        for c_idx, (stat, cent) in enumerate(row):
            meta = next(m for m in meta_list if m["row"] == r_idx + 1 and m["col"] == c_idx + 1)
            x, y, w, h, area = stat

            x1, y1 = max(0, x - pad), max(0, y - pad)
            x2, y2 = min(img.shape[1], x + w + pad), min(img.shape[0], y + h + pad)
            crop = img[y1:y2, x1:x2]

            out_file = CUTOUTS_DIR / f"{meta['asset_id']}.png"
            width, height, digest = segment_and_save_cutout(crop, dark_thresh, out_file)

            results.append({
                "meta": meta,
                "sheet": sheet_name,
                "path": f"assets/icons/cutouts/{meta['asset_id']}.png",
                "width": width,
                "height": height,
                "sha256": digest,
                "file_size": out_file.stat().st_size,
            })
            print(f"  [{sheet_name}] R{r_idx+1}C{c_idx+1} -> {meta['asset_id']}.png ({width}x{height}, {digest[:8]}...)")

    return results


def process_icons4_sheet() -> list[dict]:
    sheet_name = "Icons4.png"
    sheet_path = ICONS_DIR / sheet_name
    img = cv2.imread(str(sheet_path))
    if img is None:
        raise FileNotFoundError(f"Could not load {sheet_path}")

    results = []
    for meta in ICONS4_META:
        x1, x2 = meta["x_range"]
        crop = img[:, x1:x2]

        out_file = CUTOUTS_DIR / f"{meta['asset_id']}.png"
        width, height, digest = segment_and_save_cutout(crop, dark_thresh=48, output_path=out_file)

        results.append({
            "meta": meta,
            "sheet": sheet_name,
            "path": f"assets/icons/cutouts/{meta['asset_id']}.png",
            "width": width,
            "height": height,
            "sha256": digest,
            "file_size": out_file.stat().st_size,
        })
        print(f"  [{sheet_name}] Slot {meta['slot']+1} -> {meta['asset_id']}.png ({width}x{height}, {digest[:8]}...)")

    return results


# -------------------------------------------------------------------------
# Main Orchestrator
# -------------------------------------------------------------------------

def main():
    CUTOUTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Target Cutouts Directory: {CUTOUTS_DIR}")

    all_assets = []

    print("\n--- Processing Sheet 1: Icons1.png (15 icons, 3x5) ---")
    all_assets.extend(process_grid_sheet("Icons1.png", num_rows=3, num_cols=5, dark_thresh=55, meta_list=ICONS1_META))

    print("\n--- Processing Sheet 2: Icons2.png (12 icons, 3x4) ---")
    all_assets.extend(process_grid_sheet("Icons2.png", num_rows=3, num_cols=4, dark_thresh=48, meta_list=ICONS2_META))

    print("\n--- Processing Sheet 3: Icons3.png (12 icons, 3x4) ---")
    all_assets.extend(process_grid_sheet("Icons3.png", num_rows=3, num_cols=4, dark_thresh=48, meta_list=ICONS3_META))

    print("\n--- Processing Sheet 4: Icons4.png (5 badges, 1x5) ---")
    all_assets.extend(process_icons4_sheet())

    print(f"\nTotal Segmented Icons: {len(all_assets)} / 44")

    # ---------------------------------------------------------------------
    # Generate JSON Asset Catalogue (conforming to finance_asset_catalog.schema.json)
    # ---------------------------------------------------------------------
    catalog_entries = []
    for item in all_assets:
        meta = item["meta"]
        catalog_entries.append({
            "asset_id": meta["asset_id"],
            "path": item["path"],
            "sha256": item["sha256"],
            "kind": "prop",
            "visual_worlds": ["mechanism", "evidence", "story"],
            "semantic_tags": meta["tags"],
            "identity_lenses": meta["lenses"],
            "resolution_tier": 2,
            "generated": True,
            "contains_factual_text": meta["factual_text"],
            "rights_state": "original_review_only",
            "review_state": "review_only",
            "render_eligible": False,
        })

    # Sort deterministically by asset_id
    catalog_entries.sort(key=lambda a: a["asset_id"])

    # Compute deterministic artifact hash
    serialized_assets = json.dumps(catalog_entries, sort_keys=True)
    catalog_artifact_hash = hashlib.sha256(serialized_assets.encode("utf-8")).hexdigest()

    catalog_data = {
        "schema_version": "finance_asset_catalog.v1",
        "channel_id": "money-physics",
        "project_root": "content/video_engine",
        "resolution_order": [
            "exact_semantic_match",
            "reusable_component_composition",
            "deterministic_evidence_or_mechanism",
            "bespoke_plate",
        ],
        "assets": catalog_entries,
        "artifact_hash": catalog_artifact_hash,
    }

    catalog_json_path = ICONS_DIR / "finance_icons_catalog.v1.json"
    with open(catalog_json_path, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, indent=2)
    print(f"Successfully generated catalog: {catalog_json_path} ({len(catalog_entries)} entries)")

    # ---------------------------------------------------------------------
    # Generate CATALOGUE.md
    # ---------------------------------------------------------------------
    md_lines = [
        "# Finance & Macro Icons Catalogue (44 Cutouts)",
        "",
        "Extracted, segmented, and defringed from `Icons1.png` - `Icons4.png`.",
        "Registered under doctrine tier 2 as `kind: prop`, `rights_state: original_review_only`, `review_state: review_only`, `render_eligible: false`.",
        "",
        "## Summary",
        f"- **Total Cutouts:** {len(all_assets)}",
        f"- **Catalogue Schema:** `finance_asset_catalog.v1` (`{catalog_json_path.name}`)",
        f"- **Artifact SHA-256:** `{catalog_artifact_hash}`",
        f"- **Asset Directory:** [`assets/icons/cutouts/`](file:///C:/Users/Snipe/Downloads/Outreach%20Program/content/video_engine/assets/icons/cutouts/)",
        "",
        "## Asset Registry",
        "",
        "| Thumbnail / ID | Source Sheet | Dimensions | SHA-256 | Factual Text | Semantic Tags | Macro Context |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for item in all_assets:
        meta = item["meta"]
        tags_str = ", ".join(f"`{t}`" for t in meta["tags"][:3])
        md_lines.append(
            f"| [`{meta['asset_id']}`](file:///C:/Users/Snipe/Downloads/Outreach%20Program/content/video_engine/{item['path']})<br>*{meta['title']}* | "
            f"`{item['sheet']}` | {item['width']}×{item['height']} | `{item['sha256'][:10]}...` | "
            f"{'Yes' if meta['factual_text'] else 'No'} | {tags_str} | {meta['macro']} |"
        )

    md_path = ICONS_DIR / "CATALOGUE.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"Successfully generated Markdown catalogue: {md_path}")

    # ---------------------------------------------------------------------
    # Generate Visual Contact Sheet (HTML / Image Preview)
    # ---------------------------------------------------------------------
    html_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<title>Finance Icons Contact Sheet (44 Cutouts)</title>",
        "<style>",
        "  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #161b22; color: #f0f6fc; margin: 0; padding: 24px; }",
        "  h1 { margin-top: 0; font-size: 24px; color: #e5a93c; }",
        "  p.sub { color: #8b949e; font-size: 14px; margin-bottom: 24px; }",
        "  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }",
        "  .card { background: #21262d; border: 1px solid #30363d; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; align-items: center; }",
        "  .thumb-container { width: 200px; height: 200px; display: flex; align-items: center; justify-content: center; background: #0d1117; border-radius: 6px; margin-bottom: 12px; background-image: radial-gradient(#30363d 1px, transparent 0); background-size: 10px 10px; }",
        "  .thumb-container img { max-width: 180px; max-height: 180px; object-fit: contain; }",
        "  .title { font-weight: 600; font-size: 14px; color: #f0f6fc; text-align: center; margin-bottom: 4px; }",
        "  .slug { font-family: monospace; font-size: 11px; color: #58a6ff; margin-bottom: 8px; text-align: center; word-break: break-all; }",
        "  .dim { font-size: 11px; color: #8b949e; margin-bottom: 8px; }",
        "  .tags { display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; }",
        "  .tag { background: #2f363d; color: #c9d1d9; font-size: 10px; padding: 2px 6px; border-radius: 4px; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Finance & Macro Icons Contact Sheet (44 Cutouts)</h1>",
        f"<p class='sub'>Channels: <strong>Money Physics</strong> & <strong>Building Money</strong> | Theme: Woodcut Vermilion & Cream Washi (#F4E6C7)</p>",
        "<div class='grid'>",
    ]

    for item in all_assets:
        meta = item["meta"]
        rel_img_path = f"cutouts/{meta['asset_id']}.png"
        tags_html = "".join(f"<span class='tag'>{t}</span>" for t in meta["tags"])
        html_lines.append(f"""
        <div class='card'>
            <div class='thumb-container'>
                <img src='{rel_img_path}' alt='{meta['asset_id']}' loading='lazy' />
            </div>
            <div class='title'>{meta['title']}</div>
            <div class='slug'>{meta['asset_id']}</div>
            <div class='dim'>{item['width']} × {item['height']} px | {item['sheet']}</div>
            <div class='tags'>{tags_html}</div>
        </div>
        """)

    html_lines.extend([
        "</div>",
        "</body>",
        "</html>"
    ])

    contact_sheet_path = ICONS_DIR / "contact_sheet.html"
    with open(contact_sheet_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines) + "\n")
    print(f"Successfully generated contact sheet HTML: {contact_sheet_path}")


if __name__ == "__main__":
    main()
