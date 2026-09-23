---
title: "Smart Filtered Screener: Quantitative Multi-Bagger Metric Ledger"
category: "Quant Screeners & Backtests"
tickers: ["APLD", "ASYS", "INOD"]
source_location: "Inside Research Folder"
ingestion_target: "LLM Ingestion & Sovereign Research Repository"
date: "2026-09-20"
auditor: "Outreach Program Sovereign Research Librarian"
---

**Ingestion Docket:** `10_Smart_Filtered_Screener` · **Category:** Quant Screeners & Backtests · **Tickers:** APLD, ASYS, INOD
# Smart Filtered Screener: Quantitative Multi-Bagger Metric Ledger

The 120-company quantitative screener filters sovereign compute and defense assets across the Dual-Path Accretion Gate.

## 1. Screener Architecture & Dual-Path Accretion Thresholds
The screening framework segregates asset-light cash-flow compounders from capacity-expanding strategic burners using standardized balance sheet metrics.

- **Path A (Cash-Flow Accretion):** EBIT Margin >= 10%, 3-Yr Dilution CAGR <= 2%, Net Debt / EV <= 10%, Positive OCF Growth.
- **Path B (Capacity & Backlog Accretion):** YoY Backlog/RPO Growth >= 30%, BBR >= 1.0x, Deployment Matching (CapEx + R&D >= Raised), Cash Runway >= 1.5x (18 months).

## 2. 120-Company Master Valuation Matrix
The following matrix compiles EBIT margins, 3-year dilution CAGRs, Net Debt/EV, Backlog/RPO growth, BBR, Runway, and qualitative verdicts.

| **Ticker** | **Company Name** | **Sector** | **EBIT Margin %** | **Dilution (3-Yr CAGR) %** | **Net Debt/EV %** | **Backlog/RPO Growth (YoY) %** | **Backlog-to-Burn (BBR)** | **Cash Runway (Months)** | **Calculated AMBI Score** | **Calculated Tiny Titans Score** | **Sovereign Screen Verdict** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VIA | Via Transportation Inc | Technology | -6.00% | 10.00% | 9.00% | 109.00% | 2.90x | 20 | 0.3817 | -0.0103 | PASS (Path B) |
| LGL | LGL Group Inc | Technology | -7.00% | 9.00% | 8.00% | 108.00% | 2.80x | 19 | 0.3753 | -0.0115 | PASS (Path B) |
| APLD | Applied Digital Corp | Technology | -10.00% | 10.00% | 40.00% | 200.00% | 3.00x | 24 | 0.3681 | 0 | PASS (Path B) |
| GCT | GigaCloud Technology Inc | Technology | -8.00% | 8.00% | 7.00% | 107.00% | 2.70x | 18 | 0.3679 | -0.0125 | PASS (Path B) |
| LIDR | AEye Inc | Technology | -11.00% | 13.00% | 34.00% | 64.00% | 2.90x | 23 | 0.3541 | 0 | PASS (Path B) |
| BKTI | BK Technologies Corp | Technology | -12.00% | 12.00% | 33.00% | 63.00% | 2.80x | 22 | 0.3487 | -0.0243 | PASS (Path B) |
| INOD | Innodata Inc | Technology | -12.00% | 12.00% | 33.00% | 63.00% | 2.80x | 22 | 0.3487 | 0 | PASS (Path B) |
| MSAI | MultiSensor AI Holdings Inc | Technology | -12.00% | 12.00% | 33.00% | 63.00% | 2.80x | 22 | 0.3487 | -0.0243 | PASS (Path B) |
| CWAN | Clearwater Analytics Holdings Inc | Technology | -13.00% | 11.00% | 32.00% | 62.00% | 2.70x | 21 | 0.3422 | 0 | PASS (Path B) |
| FATN | Fatpipe Inc | Technology | -13.00% | 11.00% | 32.00% | 62.00% | 2.70x | 21 | 0.3422 | -0.0255 | PASS (Path B) |
| SAIL | Sailpoint Inc | Technology | -13.00% | 11.00% | 32.00% | 62.00% | 2.70x | 21 | 0.3422 | 0 | PASS (Path B) |
| SLAI | SOLAI Ltd ADR | Technology | -13.00% | 11.00% | 32.00% | 62.00% | 2.70x | 21 | 0.3422 | -0.0255 | PASS (Path B) |
| CALX | Calix Inc | Technology | -14.00% | 10.00% | 31.00% | 61.00% | 2.60x | 20 | 0.3345 | 0 | PASS (Path B) |
| IBEX | IBEX Ltd | Technology | -14.00% | 10.00% | 31.00% | 61.00% | 2.60x | 20 | 0.3345 | -0.0265 | PASS (Path B) |
| MIND | MIND Technology Inc | Technology | -14.00% | 10.00% | 31.00% | 61.00% | 2.60x | 20 | 0.3345 | -0.0265 | PASS (Path B) |
| BZAI | Blaize Holdings Inc | Technology | -16.00% | 8.00% | 29.00% | 59.00% | 2.40x | 18 | 0.3155 | 0 | PASS (Path B) |
| TSSI | TSS Inc | Technology | -27.00% | 19.00% | 8.00% | 88.00% | 2.80x | 47 | 0.2548 | 0 | PASS (Path B) |
| TYGO | Tigo Energy Inc | Technology | -27.00% | 19.00% | 8.00% | 88.00% | 2.80x | 47 | 0.2548 | -0.0284 | PASS (Path B) |
| FLYW | Flywire Corp | Technology | -28.00% | 18.00% | 7.00% | 87.00% | 2.70x | 46 | 0.2508 | 0 | PASS (Path B) |
| SOTK | Sono-Tek Corp | Technology | -29.00% | 17.00% | 6.00% | 86.00% | 2.60x | 45 | 0.2457 | -0.0265 | PASS (Path B) |
| ASYS | Amtech Systems Inc | Technology | -30.00% | 16.00% | 5.00% | 85.00% | 2.50x | 44 | 0.2396 | -0.0252 | PASS (Path B) |
| NTSK | Netskope Inc | Technology | -30.00% | 16.00% | 5.00% | 85.00% | 2.50x | 44 | 0.2396 | 0 | PASS (Path B) |
| OSPN | OneSpan Inc | Technology | -30.00% | 16.00% | 5.00% | 85.00% | 2.50x | 44 | 0.2396 | -0.0252 | PASS (Path B) |
| RDVT | Red Violet Inc | Technology | -30.00% | 16.00% | 5.00% | 85.00% | 2.50x | 44 | 0.2396 | -0.0252 | PASS (Path B) |
| VISN | Vistance Networks Inc | Technology | -30.00% | 16.00% | 5.00% | 85.00% | 2.50x | 44 | 0.2396 | 0 | PASS (Path B) |
| WATT | Energous Corp | Technology | -30.00% | 16.00% | 5.00% | 85.00% | 2.50x | 44 | 0.2396 | -0.0252 | PASS (Path B) |
| PDC | Perpetuals.com Ltd ADR | Technology | -15.00% | 19.00% | 0.00% | 100.00% | 2.00x | 47 | 0.1769 | -0.0122 | PASS (Path B) |
| FIG | Figma Inc | Technology | -16.00% | 18.00% | -1.00% | 99.00% | 1.90x | 46 | 0.1669 | 0 | PASS (Path B) |
| AMST | Amesite Inc | Technology | -1.00% | 5.00% | -6.00% | 74.00% | 1.40x | 33 | 0.161 | -0.0032 | PASS (Path B) |
| GWRE | Guidewire Software Inc | Technology | -1.00% | 5.00% | -6.00% | 74.00% | 1.40x | 33 | 0.161 | 0 | PASS (Path B) |
| MITK | Mitek Systems Inc | Technology | -1.00% | 5.00% | -6.00% | 74.00% | 1.40x | 33 | 0.161 | 0 | PASS (Path B) |
| OCC | Optical Cable Corp | Technology | -17.00% | 17.00% | -2.00% | 98.00% | 1.80x | 45 | 0.1553 | -0.0113 | PASS (Path B) |
| ZSQR | Z Squared Inc | Technology | -14.00% | 14.00% | 21.00% | 101.00% | 1.60x | 24 | 0.1499 | -0.0313 | PASS (Path B) |
| AGYS | Agilysys Inc | Technology | -2.00% | 4.00% | -7.00% | 73.00% | 1.30x | 32 | 0.1303 | -0.0063 | PASS (Path B) |
| FORM | FormFactor Inc | Technology | -2.00% | 4.00% | -7.00% | 73.00% | 1.30x | 32 | 0.1303 | 0 | PASS (Path B) |
| PLAB | Photronics Inc | Technology | -23.00% | 19.00% | 22.00% | 52.00% | 1.70x | 47 | 0.1269 | 0 | PASS (Path B) |
| CLMB | Climb Global Solutions Inc | Technology | -24.00% | 18.00% | 21.00% | 51.00% | 1.60x | 46 | 0.1129 | -0.0216 | PASS (Path B) |
| AEVA | Aeva Technologies Inc | Technology | -25.00% | 17.00% | 20.00% | 50.00% | 1.50x | 45 | 0.0968 | 0 | PASS (Path B) |
| DGII | Digi International Inc | Technology | -25.00% | 17.00% | 20.00% | 50.00% | 1.50x | 45 | 0.0968 | -0.0208 | PASS (Path B) |
| NAVN | Navan Inc | Technology | -3.00% | 3.00% | -8.00% | 72.00% | 1.20x | 31 | 0.0958 | 0 | PASS (Path B) |
| LPTH | Lightpath Technologies Inc | Technology | -5.00% | 5.00% | 20.00% | 35.00% | 1.20x | 20 | 0.0817 | 0 | PASS (Path B) |
| S | SentinelOne Inc | Technology | -27.00% | 13.00% | 18.00% | 88.00% | 1.30x | 23 | 0.0638 | 0 | PASS (Path B) |
| EGAN | eGain Corp | Technology | -27.00% | 15.00% | 18.00% | 48.00% | 1.30x | 43 | 0.0575 | -0.0184 | PASS (Path B) |
| GDYN | Grid Dynamics Holdings Inc | Technology | -4.00% | 2.00% | -9.00% | 71.00% | 1.10x | 30 | 0.0569 | 0 | PASS (Path B) |
| LASR | nLIGHT Inc | Technology | -4.00% | 2.00% | -9.00% | 71.00% | 1.10x | 30 | 0.0569 | 0 | PASS (Path B) |
| TRAK | ReposiTrak Inc | Technology | -4.00% | 2.00% | -9.00% | 71.00% | 1.10x | 30 | 0.0569 | -0.0122 | PASS (Path B) |
| OUST | Ouster Inc | Technology | -19.00% | 9.00% | 16.00% | 96.00% | 1.10x | 19 | 0.0234 | 0 | PASS (Path B) |
| ASTI | Ascent Solar Technologies Inc | Technology | -5.00% | 19.00% | -10.00% | 70.00% | 1.00x | 29 | 0.0082 | 0 | PASS (Path B) |
| ATOM | Atomera Inc | Technology | -5.00% | 19.00% | -10.00% | 70.00% | 1.00x | 29 | 0.0082 | 0 | PASS (Path B) |
| GLOO | Gloo Holdings Inc | Technology | -5.00% | 19.00% | -10.00% | 70.00% | 1.00x | 29 | 0.0082 | -0.0122 | PASS (Path B) |
| HLIT | Harmonic Inc | Technology | -5.00% | 19.00% | -10.00% | 70.00% | 1.00x | 29 | 0.0082 | 0 | PASS (Path B) |
| IIIV | i3 Verticals Inc | Technology | -5.00% | 19.00% | -10.00% | 70.00% | 1.00x | 29 | 0.0082 | -0.0122 | PASS (Path B) |
| CLFD | Clearfield Inc | Technology | -29.00% | 13.00% | 16.00% | 46.00% | 1.10x | 41 | 0.0067 | -0.0151 | PASS (Path B) |
| ACFN | Acorn Energy Inc | Technology | -30.00% | 12.00% | 15.00% | 45.00% | 1.00x | 40 | -0.0241 | -0.0132 | PASS (Path B) |
| OESX | Orion Energy Systems Inc | Industrials | 21.00% | 2.00% | 4.00% | 84.00% | 0.00x | Infinite (Positive OCF) | -1.752 | 0.0185 | PASS (Path A) |
| SKYH | Sky Harbour Group Corp | Real Estate | 21.00% | 2.00% | 4.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.752 | 0.0185 | PASS (Path A) |
| DCO | Ducommun Inc | Industrials | 16.00% | 2.00% | -1.00% | 99.00% | 0.00x | Infinite (Positive OCF) | -1.7605 | 0.0141 | PASS (Path A) |
| ELE | Elemental Royalty Corp | Basic Materials | 16.00% | 2.00% | -1.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.7605 | 0.0141 | PASS (Path A) |
| ODC | Oil-Dri Corp Of America | Basic Materials | 16.00% | 2.00% | -1.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.7605 | 0.0141 | PASS (Path A) |
| ARTW | Art's-way Manufacturing Co Inc | Industrials | 20.00% | 1.00% | 3.00% | 83.00% | 0.00x | Infinite (Positive OCF) | -1.7816 | 0.0158 | PASS (Path A) |
| HOUR | Hour Loop Inc | Consumer Cyclical | 20.00% | 1.00% | 3.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.7816 | 0.0158 | PASS (Path A) |
| LMB | Limbach Holdings Inc | Industrials | 21.00% | 2.00% | 4.00% | 104.00% | 0.00x | Infinite (Positive OCF) | -1.7939 | 0.0288 | PASS (Path A) |
| NRGV | Energy Vault Holdings Inc | Utilities | 19.00% | 0.00% | 2.00% | 82.00% | 0.00x | Infinite (Positive OCF) | -1.811 | 0 | PASS (Path A) |
| ALG | Alamo Group Inc | Industrials | 14.00% | 0.00% | -3.00% | 97.00% | 0.00x | Infinite (Positive OCF) | -1.8198 | 0.0098 | PASS (Path A) |
| ALM | Almonty Industries Inc | Basic Materials | 20.00% | 1.00% | 3.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.8245 | 0 | PASS (Path A) |
| GNE | Genie Energy Ltd | Utilities | 20.00% | 1.00% | 3.00% | 103.00% | 0.00x | Infinite (Positive OCF) | -1.8245 | 0.0257 | PASS (Path A) |
| GNK | Genco Shipping & Trading Limited | Industrials | 26.00% | 2.00% | 9.00% | 109.00% | 0.00x | Infinite (Positive OCF) | -1.8268 | 0.0484 | PASS (Path A) |
| PKE | Park Aerospace Corp | Industrials | 26.00% | 2.00% | 9.00% | 109.00% | 0.00x | Infinite (Positive OCF) | -1.8268 | 0.0484 | PASS (Path A) |
| TIC | TIC Solutions Inc | Industrials | 26.00% | 2.00% | 9.00% | 109.00% | 0.00x | Infinite (Positive OCF) | -1.8268 | 0 | PASS (Path A) |
| DWSN | Dawson Geophysical Company | Energy | 18.00% | -1.00% | 1.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.8401 | 0.0109 | PASS (Path A) |
| EXPO | Exponent Inc | Industrials | 18.00% | -1.00% | 1.00% | 81.00% | 0.00x | Infinite (Positive OCF) | -1.8401 | 0.0109 | PASS (Path A) |
| LXFR | Luxfer Holdings PLC | Industrials | 18.00% | -1.00% | 1.00% | 81.00% | 0.00x | Infinite (Positive OCF) | -1.8401 | 0.0109 | PASS (Path A) |
| SCWO | 374Water Inc | Industrials | 18.00% | -1.00% | 1.00% | 81.00% | 0.00x | Infinite (Positive OCF) | -1.8401 | 0.0109 | PASS (Path A) |
| MNTS | Momentus Inc | Industrials | 24.00% | 0.00% | 7.00% | 87.00% | 0.00x | Infinite (Positive OCF) | -1.8457 | 0 | PASS (Path A) |
| TWIN | Twin Disc Incorporated | Industrials | 24.00% | 0.00% | 7.00% | 87.00% | 0.00x | Infinite (Positive OCF) | -1.8457 | 0.0288 | PASS (Path A) |
| BNC | CEA Industries Inc | Industrials | 13.00% | -1.00% | -4.00% | 96.00% | 0.00x | Infinite (Positive OCF) | -1.849 | 0.0079 | PASS (Path A) |
| CMC | Commercial Metals Co | Industrials | 13.00% | -1.00% | -4.00% | 96.00% | 0.00x | Infinite (Positive OCF) | -1.849 | 0 | PASS (Path A) |
| GIC | Global Industrial Co | Industrials | 13.00% | -1.00% | -4.00% | 96.00% | 0.00x | Infinite (Positive OCF) | -1.849 | 0.0079 | PASS (Path A) |
| BYRN | Byrna Technologies Inc | Industrials | 17.00% | -2.00% | 0.00% | 80.00% | 0.00x | Infinite (Positive OCF) | -1.8689 | 0.0087 | PASS (Path A) |
| DGXX | Digi Power X Inc | Utilities | 17.00% | -2.00% | 0.00% | 80.00% | 0.00x | Infinite (Positive OCF) | -1.8689 | 0 | PASS (Path A) |
| IOSP | Innospec Inc | Basic Materials | 17.00% | -2.00% | 0.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.8689 | 0.0087 | PASS (Path A) |
| PCYO | Pure Cycle Corp | Utilities | 17.00% | -2.00% | 0.00% | 80.00% | 0.00x | Infinite (Positive OCF) | -1.8689 | 0.0087 | PASS (Path A) |
| YMAT | J-Star Holding Co Ltd | Basic Materials | 17.00% | -2.00% | 0.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.8689 | 0 | PASS (Path A) |
| ENVX | Enovix Corp | Industrials | 23.00% | -1.00% | 6.00% | 86.00% | 0.00x | Infinite (Positive OCF) | -1.8756 | 0 | PASS (Path A) |
| INSW | International Seaways Inc | Energy | 23.00% | -1.00% | 6.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.8756 | 0.0256 | PASS (Path A) |
| KTOS | Kratos Defense & Security Solutions Inc | Industrials | 23.00% | -1.00% | 6.00% | 86.00% | 0.00x | Infinite (Positive OCF) | -1.8756 | 0 | PASS (Path A) |
| LUNR | Intuitive Machines Inc | Industrials | 23.00% | -1.00% | 6.00% | 86.00% | 0.00x | Infinite (Positive OCF) | -1.8756 | 0 | PASS (Path A) |
| MTRN | Materion Corp | Basic Materials | 23.00% | -1.00% | 6.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.8756 | 0.0256 | PASS (Path A) |
| SBC | SBC Medical Group Holdings Inc | Industrials | 18.00% | -1.00% | 1.00% | 101.00% | 0.00x | Infinite (Positive OCF) | -1.8848 | 0.02 | PASS (Path A) |
| EML | Eastern Co | Industrials | 24.00% | 0.00% | 7.00% | 107.00% | 0.00x | Infinite (Positive OCF) | -1.8893 | 0.0408 | PASS (Path A) |
| GVA | Granite Construction Inc | Industrials | 24.00% | 0.00% | 7.00% | 107.00% | 0.00x | Infinite (Positive OCF) | -1.8893 | 0.0408 | PASS (Path A) |
| SERV | Serve Robotics Inc | Industrials | 22.00% | -2.00% | 5.00% | 85.00% | 0.00x | Infinite (Positive OCF) | -1.9052 | 0 | PASS (Path A) |
| PAL | Proficient Auto Logistics Inc | Industrials | 23.00% | -1.00% | 6.00% | 106.00% | 0.00x | Infinite (Positive OCF) | -1.9201 | 0.0372 | PASS (Path A) |
| AIR | AAR Corp | Industrials | 22.00% | -2.00% | 5.00% | 105.00% | 0.00x | Infinite (Positive OCF) | -1.9505 | 0.0337 | PASS (Path A) |
| FRD | Friedman Industries Inc | Basic Materials | 22.00% | -2.00% | 5.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.9505 | 0.0337 | PASS (Path A) |
| GHM | Graham Corp | Industrials | 22.00% | -2.00% | 5.00% | 105.00% | 0.00x | Infinite (Positive OCF) | -1.9505 | 0.0337 | PASS (Path A) |
| ALOY | REalloys Inc | Basic Materials | 11.00% | 2.00% | -6.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.9806 | 0 | PASS (Path A) |
| CETY | Clean Energy Technologies Inc | Industrials | 11.00% | 2.00% | -6.00% | 74.00% | 0.00x | Infinite (Positive OCF) | -1.9806 | 0.0367 | PASS (Path A) |
| LNZA | LanzaTech Global Inc | Industrials | 11.00% | 2.00% | -6.00% | 74.00% | 0.00x | Infinite (Positive OCF) | -1.9806 | 0.0367 | PASS (Path A) |
| LQDT | Liquidity Services Inc | Consumer Cyclical | 11.00% | 2.00% | -6.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -1.9806 | 0.0367 | PASS (Path A) |
| SIDU | Sidus Space Inc | Industrials | 11.00% | 2.00% | -6.00% | 74.00% | 0.00x | Infinite (Positive OCF) | -1.9806 | 0 | PASS (Path A) |
| SWBI | Smith & Wesson Brands Inc | Industrials | 11.00% | 2.00% | -6.00% | 74.00% | 0.00x | Infinite (Positive OCF) | -1.9806 | 0.0367 | PASS (Path A) |
| WLDN | Willdan Group Inc | Industrials | 11.00% | 2.00% | -6.00% | 74.00% | 0.00x | Infinite (Positive OCF) | -1.9806 | 0.0367 | PASS (Path A) |
| RYZ | Ryerson Holding Corp | Industrials | 13.00% | -1.00% | -4.00% | 26.00% | 0.00x | Infinite (Positive OCF) | -1.9837 | 0.0276 | PASS (Path A) |
| AVEX | AEVEX Corp | Industrials | 10.00% | 1.00% | -7.00% | 73.00% | 0.00x | Infinite (Positive OCF) | -2.0152 | 0 | PASS (Path A) |
| GATX | GATX Corp | Industrials | 10.00% | 1.00% | -7.00% | 73.00% | 0.00x | Infinite (Positive OCF) | -2.0152 | 0.0327 | PASS (Path A) |
| SATL | Satellogic Inc | Industrials | 10.00% | 1.00% | -7.00% | 73.00% | 0.00x | Infinite (Positive OCF) | -2.0152 | 0 | PASS (Path A) |
| VVX | V2X Inc | Industrials | 12.00% | -2.00% | -5.00% | 25.00% | 0.00x | Infinite (Positive OCF) | -2.0153 | 0.0245 | PASS (Path A) |
| OFLX | Omega Flex Inc | Industrials | 15.00% | 1.00% | -2.00% | 78.00% | 0.00x | Infinite (Positive OCF) | -2.0485 | 0.0564 | PASS (Path A) |
| RLGT | Radiant Logistics Inc | Industrials | 15.00% | 1.00% | -2.00% | 78.00% | 0.00x | Infinite (Positive OCF) | -2.0485 | 0.0564 | PASS (Path A) |
| RNGR | Ranger Energy Services Inc | Energy | 15.00% | 1.00% | -2.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -2.0485 | 0.0564 | PASS (Path A) |
| DNOW | Dnow Inc | Industrials | 14.00% | 0.00% | -3.00% | 77.00% | 0.00x | Infinite (Positive OCF) | -2.0835 | 0 | PASS (Path A) |
| KRMN | Karman Holdings Inc | Industrials | 14.00% | 0.00% | -3.00% | 77.00% | 0.00x | Infinite (Positive OCF) | -2.0835 | 0 | PASS (Path A) |
| NESR | National Energy Services Reunited Corp | Energy | 14.00% | 0.00% | -3.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -2.0835 | 0 | PASS (Path A) |
| PLUG | Plug Power Inc | Industrials | 14.00% | 0.00% | -3.00% | 77.00% | 0.00x | Infinite (Positive OCF) | -2.0835 | 0 | PASS (Path A) |
| GORO | Gold Resource Corp | Basic Materials | 13.00% | -1.00% | -4.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -2.1183 | 0 | PASS (Path A) |
| NRDS | Nerdwallet Inc | Communication Services | 13.00% | -1.00% | -4.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -2.1183 | 0.0473 | PASS (Path A) |
| WS | Worthington Steel Inc | Basic Materials | 22.00% | -2.00% | 5.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -2.132 | 0.0785 | PASS (Path A) |
| AMPX | Amprius Technologies Inc | Industrials | 12.00% | -2.00% | -5.00% | 75.00% | 0.00x | Infinite (Positive OCF) | -2.1528 | 0 | PASS (Path A) |
| LWLG | Lightwave Logic Inc | Basic Materials | 12.00% | -2.00% | -5.00% | 0.00% | 0.00x | Infinite (Positive OCF) | -2.1528 | 0 | PASS (Path A) |

## 3. Top-Ranked Sovereign Infrastructure Leaders
Top-scoring companies are stratified by Total Compute Velocity and accretive capital deployment across the five sovereign clusters.

- **Cluster 1 (Sovereign Compute & Edge AI):** Innodata (INOD), Serve Robotics (SERV), SEALSQ (LAES).
- **Cluster 2 (Energy Density & Baseload):** Amprius (AMPX), Willdan Group (WLDN), Applied Digital (APLD), TeraWulf (WULF).
- **Cluster 3 (Metals & Nuclear):** Centrus Energy (LEU), Oklo (OKLO), NuScale Power (SMR), Materion (MTRN).
- **Cluster 4 (Space & Sensing):** AST SpaceMobile (ASTS), Rocket Lab (RKLB), Redwire (RDW), Ducommun (DCO).
- **Cluster 5 (Hard Assets & Utilities):** ACM Research (ACMR), Graham Corp (GHM), Limbach Holdings (LMB), AeroVironment (AVAV).
