# R26-311 VERIFY - US railway investment / GDP and the modern comparator, under the claims gate (2026-09-27)

The Gemini reply to packet `cbf13c74` (conversation `c233db4e`), re-verified with OUR verifier (`verify_research_claims.v2`,
lane B `3a3ca56`, its tamper check live) and with our own fetch of every source. P72 T33. The rules:
`docs/runbooks/RESEARCH-REPLY-CONTRACT.md`; the tiers: `docs/agent-memory/operator/research-gate-tiers.md`; the earlier
reply this one repairs: `docs/research/markets/r26-306-nvda-share-railway-gdp-VERIFY-2026-09-24.md` (section 3, US).

Run folder (gitignored): `docs/research/runs/r26-311-railway-us-and-modern-comparator/`. Promoted claims file sha256
`50e4bc874be7c3f44f46f6307ff6f40108e82afdcf844ff89525f5582473d10e`: the lane's 270 claims, byte for byte, plus the 3 added
in section 4. `verify_research_claims.py <run> --require-pass` exits 0 against it.

## 1. The gate, twice

| Pass | Mode | Verdict | Earned tiers | Capped |
|---|---|---|---|---|
| The lane's reply as sent (claims sha256 `73cdfb65...cfb5`) | online, not trusted | PASS, 0 failures | CONFIRMED 137, PLAUSIBLE 132, UNSOURCED 1, REJECTED 0 | 132: every FRED claim, "saved by the lane, not independently fetched" (timeout / connection closed) |
| The promoted run (claims sha256 `50e4bc87...d10e`) | online, `--trusted-run` | PASS, 0 failures | CONFIRMED 272, UNSOURCED 1, REJECTED 0 | 0 |

Why the second pass may be trusted: every file in the promoted run's `sources/` is OUR fetch (curl, a generic User-Agent,
2026-09-27 11:31-11:39 UTC), and each is byte-identical (sha256) to the copy the lane saved (section 2), so the lane's copies
are no longer the only witness. The run's 2026-09-24 `VERIFY.json` (verifier v1, 269 CONFIRMED) predates the v2 rule and is
kept as `VERIFY-2026-09-24-superseded.*`; the untrusted pass is kept as `VERIFY-lane-reply-2026-09-27.*`.

## 2. Sources - our fetch against the lane's copy

| Source | URL | sha256 (ours = the lane's) | As of |
|---|---|---|---|
| FRED `GDPA` (BEA NIPA Table 1.1.5) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDPA | `ca5518d1df8c` | FRED Last-Modified 2026-04-09 |
| FRED `Y033RC1A027NBEA` (equipment) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=Y033RC1A027NBEA | `03ec1045788f` | 2026-04-09 |
| FRED `Y001RC1A027NBEA` (intellectual property products) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=Y001RC1A027NBEA | `14318650c474` | 2026-04-09 |
| FRED `Y034RC1A027NBEA` (information processing equipment) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=Y034RC1A027NBEA | `3fd8fa7af90f` | 2026-04-09 |
| FRED `B935RC1A027NBEA` (computers and peripheral equipment) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=B935RC1A027NBEA | `a0c6ffda2dc0` | 2026-04-09 |
| MeasuringWorth, Johnston and Williamson, "What Was the U.S. GDP Then?", nominal GDP 1830-1900 | https://www.measuringworth.com/datasets/usgdp/result.php?year_source=1830&year_result=1900&use%5B%5D=NOMINALGDP | `c89975cd8f58` | no printed vintage (the page's citation year is script-generated); read 2026-09-24 and 2026-09-27, identical |
| Ulmer (1960), *Capital in Transportation, Communication, and Public Utilities*, Table C-1 | https://www.nber.org/system/files/chapters/c1498/c1498.pdf | `542b4d915dad` | the 1960 publication |
| Fishlow (1966), "Productivity and Technological Change in the Railroad Sector, 1840-1910", Table 7 | https://www.nber.org/system/files/chapters/c1578/c1578.pdf | `d42ef420bcf9` | the 1966 publication |
| Gallman (1966), "Gross National Product in the United States, 1834-1909", Table A-1 | https://www.nber.org/system/files/chapters/c1565/c1565.pdf | `d1988d1c6153` | the 1966 publication |

Beyond the gate, which checks an elided quote such as `1870 ... 380` only for order, the tables were read row by row: the three
NBER tables on the rendered pages (Ulmer Table C-1, printed p. 256, column (3), gross capital expenditures in current dollars;
Fishlow Table 7, p. 611, column (2), Variant II; Gallman Table A-1, p. 26, column (2), 1860 prices - the claim's note says p. 27,
the PDF page), MeasuringWorth's 71 year/value pairs parsed in order, and the 80 FRED claims matched to their CSV rows. No mismatch.

## 3. US railway investment as a share of GDP, 1870-1900 - CONFIRMED

Ulmer's gross capital expenditures by steam railroads (current dollars) over Johnston and Williamson's nominal GDP (current
dollars). Two authors' series joined by the lane; each input and each ratio passed the gate. Claim ids:
`ulmer-railway-inv-<year>`, `mw-gdp-<year>`, `railway-share-gdp-<year>`.

| Year | Railroad gross capital expenditures ($M) | Nominal GDP ($M) | Share of GDP (%) |
|---|---|---|---|
| 1870 | 380 | 7,899 | 4.811 |
| 1871 | 420 | 7,751 | 5.419 |
| 1872 | 379 | 8,402 | 4.511 |
| 1873 | 262 | 8,936 | 2.932 |
| 1874 | 148 | 8,659 | 1.709 |
| 1875 | 105 | 8,331 | 1.26 |
| 1876 | 104 | 8,482 | 1.226 |
| 1877 | 117 | 8,700 | 1.345 |
| 1878 | 114 | 8,555 | 1.333 |
| 1879 | 125 | 9,555 | 1.308 |
| 1880 | 282 | 10,592 | 2.662 |
| 1881 | 440 | 11,902 | 3.697 |
| 1882 | 398 | 12,519 | 3.179 |
| 1883 | 283 | 12,640 | 2.239 |
| 1884 | 199 | 12,107 | 1.644 |
| 1885 | 150 | 11,925 | 1.258 |
| 1886 | 206 | 12,549 | 1.642 |
| 1887 | 275 | 13,565 | 2.027 |
| 1888 | 251 | 14,332 | 1.751 |
| 1889 | 227 | 14,338 | 1.583 |
| 1890 | 231 | 15,607 | 1.48 |
| 1891 | 237 | 15,944 | 1.486 |
| 1892 | 407 | 16,920 | 2.405 |
| 1893 | 433 | 15,934 | 2.717 |
| 1894 | 190 | 14,606 | 1.301 |
| 1895 | 69 | 16,114 | 0.428 |
| 1896 | 48 | 15,990 | 0.3 |
| 1897 | 48 | 16,666 | 0.288 |
| 1898 | 82 | 18,663 | 0.439 |
| 1899 | 175 | 20,119 | 0.87 |
| 1900 | 205 | 21,197 | 0.967 |

The peak is 1871 (5.419 %), the second boom 1881 (3.697 %), the trough 1897 (0.288 %). Ulmer's annual series starts in 1870.
Fishlow (Table 7's text) argues that Ulmer understates gross investment before 1910, so read these shares as a floor.

## 4. Before 1870 - one decade benchmark, CONFIRMED

No annual national series exists before 1870 (the reply's "not found where I looked", consistent with R26-306). Fishlow's
Table 7 gives decade totals in 1909 dollars, Variant II: 1828-38 88.8, 1839-48 172.5, 1849-58 761.2 ($M), the claims
`fishlow-railroad-inv-*-1909d`. Gallman's Table A-1 gives 1849-58 GNP as a decade average of 3.30 ($bn a year, 1860 prices),
`gallman-gnp-1849-1858-1860d`.

Added in this pass. The report stated the last two with no claim id; each is now a claim the gate recomputed:

| Claim id | Value | How |
|---|---|---|
| `fishlow-1909-per-1860-price-factor` | 108.23 | Table 7's source note: "1828-58: Gross investment in 1860 dollars ... times 108.23" |
| `fishlow-railroad-inv-1849-1858-1860d` | 703.3 ($M, 1860 dollars) | 761.2 / 108.23 x 100 |
| `railway-share-gnp-1849-1858-1860d` | 2.131 (%) | 703.3 / (3.30 x 10 x 1000) x 100 |

Constant prices over constant prices: the decade's investment total over ten times the decade's average annual GNP.
Variant I (926.9) is not restated, because Fishlow's 108.23 converts only his 1860-dollar series.

## 5. The modern comparator, 2000-2025 - CONFIRMED (BEA via FRED, vintage 2026-04-09)

Private fixed investment, nonresidential: equipment (`Y033RC1A027NBEA`) and intellectual property products (`Y001RC1A027NBEA`),
over GDP (`GDPA`). All in current dollars, billions. Claim ids `gdp-`, `equipment-`, `ipp-`, `equipment-share-gdp-` and
`ipp-share-gdp-<year>`. BEA's annual update after 2026-04-09 will revise these; re-fetch before a render.

| Year | GDP ($B) | Equipment ($B) | IPP ($B) | Equipment % GDP | IPP % GDP |
|---|---|---|---|---|---|
| 2000 | 10,250.952 | 766.088 | 411.339 | 7.473 | 4.013 |
| 2001 | 10,581.929 | 711.517 | 415.04 | 6.724 | 3.922 |
| 2002 | 10,929.108 | 659.64 | 406.222 | 6.036 | 3.717 |
| 2003 | 11,456.45 | 670.618 | 418.656 | 5.854 | 3.654 |
| 2004 | 12,217.196 | 721.896 | 437.819 | 5.909 | 3.584 |
| 2005 | 13,039.197 | 794.894 | 473.134 | 6.096 | 3.629 |
| 2006 | 13,815.583 | 862.283 | 506.332 | 6.241 | 3.665 |
| 2007 | 14,474.228 | 893.432 | 544.828 | 6.173 | 3.764 |
| 2008 | 14,769.862 | 845.381 | 574.384 | 5.724 | 3.889 |
| 2009 | 14,478.067 | 670.261 | 564.354 | 4.629 | 3.898 |
| 2010 | 15,048.971 | 777.027 | 578.17 | 5.163 | 3.842 |
| 2011 | 15,599.732 | 881.274 | 621.733 | 5.649 | 3.986 |
| 2012 | 16,253.97 | 983.401 | 655.691 | 6.05 | 4.034 |
| 2013 | 16,880.683 | 1,035.25 | 694.599 | 6.133 | 4.115 |
| 2014 | 17,608.138 | 1,109.086 | 741.461 | 6.299 | 4.211 |
| 2015 | 18,295.019 | 1,144.101 | 778.879 | 6.254 | 4.257 |
| 2016 | 18,804.913 | 1,119.782 | 843.007 | 5.955 | 4.483 |
| 2017 | 19,612.102 | 1,159.953 | 906.246 | 5.914 | 4.621 |
| 2018 | 20,656.516 | 1,227.62 | 992.217 | 5.943 | 4.803 |
| 2019 | 21,539.982 | 1,240.901 | 1,074.887 | 5.761 | 4.99 |
| 2020 | 21,375.281 | 1,112.497 | 1,136.206 | 5.205 | 5.316 |
| 2021 | 23,725.645 | 1,196.318 | 1,263.051 | 5.042 | 5.324 |
| 2022 | 26,054.614 | 1,305.765 | 1,423.69 | 5.012 | 5.464 |
| 2023 | 27,811.517 | 1,404.659 | 1,524.507 | 5.051 | 5.482 |
| 2024 | 29,298.013 | 1,484.254 | 1,603.882 | 5.066 | 5.474 |
| 2025 | 30,762.099 | 1,643.718 | 1,713.656 | 5.343 | 5.571 |

Also CONFIRMED for 2025: information processing equipment 626.606 and computers and peripheral equipment 270.729 ($B;
`info-processing-equip-2025`, `computers-peripherals-2025`). UNSOURCED, declared honestly: a dedicated AI / data-centre capex
share of GDP (`data-centre-ai-gdp-share-2025`). BEA publishes no such line.

## 6. REJECTED - the report's prose where it disagrees with its own claims

Rule 1 of the contract: a figure in the report with no claim id is not a finding. None of these is promoted.

| Report text | Why |
|---|---|
| Section 3's table, 2001-2024 (24 of its 26 rows) | matches neither FRED nor the reply's own claims (2009 equipment 708.238 against FRED's 670.261; 2024 equipment 1,600.323 against 1,484.254) |
| "troughed at 4.902% in 2009 ($708.2B / $14,448.9B)" | taken from that table; the claims give 4.629 (670.261 / 14,478.067) |
| "averaged 1.767% of GDP" across 1870-1900 | does not recompute from the 31 claimed shares |
| "5.420% of GDP in 1871" | the claim is 5.419; the prose mis-rounds |
| "surpassing equipment for the first time in 2020"; the equipment + IPP totals; computers at "0.880% of GDP" | no claim carries them; add a derived claim and re-run the gate before use |

## 7. Retrieval notes

- FRED does not answer the verifier's own User-Agent (`MoneyPhysics-research-verifier (research@localhost)`). With it, urllib
  and curl both time out; with a generic contact User-Agent the same URL returns 200 in under a second. That, not the network,
  is why every FRED claim was capped. The verifier is not changed here (its tamper check); a backlog row carries it.
- Every request in this pass used a generic User-Agent, with no personal address.
- These are the US half of R26-306's railway case; no evidence object is written in this pass.
