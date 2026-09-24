# R26-306 VERIFY — the Gemini reply, checked (2026-09-24)

Tiers: CONFIRMED = the primary page retrieved, the number is on it, and it is on disk. PLAUSIBLE = a reputable secondary on disk, primary not retrieved. UNSOURCED = nothing retrievable states it. REJECTED = contradicted, or the citation is fabricated. The run copy matches the original byte for byte (sha256).

## 1. URLs
| URL in the reply | Result | Verdict |
|---|---|---|
| trendforce …/20241018-12345.html | 404; live site uses the same pattern (20251030-12762 resolves) | FABRICATED |
| trendforce …/20240612-12180.html | 404 | FABRICATED |
| techinsights …/data-center-server-processor-market-share-and-forecast | 404 | unresolvable |
| iot-analytics.com/data-center-ai-chip-market/ | 404 | unresolvable |
| idc prUS51944324 | redirects to my.idc.com, then 403 | not retrievable |
| omdia …/omdia-ai-processors-market | 403 | not retrievable |
| delloro …/data-center-it-capex-growth/ | 404 | unresolvable |
| goldmansachs …/ai-investment-and-macro-outlook.html | 403 | not retrievable |
| sec.gov NVDA 10-K FY2025 (nvda-20250126.htm) | resolves | real; saved |
| coreweave …/coreweave-series-c; lambdalabs → lambda.ai …; blogs.nvidia.com …/sakana-ai-collaboration/ | 404 | unresolvable |
| wsj / ft / reuters | fetch tool blocked | not retrievable |
| sec.gov Recursion 000160183023000073/rxrx-20230712.htm | 404; the real 8-K is 0001601830-23-000050 `rxrx-20230711.htm` | FABRICATED path, real fact |
| DOI 10.1017/S002205070006041X | not registered (real Mitchell 1964 is 10.1017/S0022050700060873) | FABRICATED |
| DOI 10.1007/978-1-349-02685-2 | not registered | FABRICATED |
| DOI 10.1017/CBO9780511561085 | resolves to *Durham Priory 1400–1450* | MISATTRIBUTED |
| DOI 10.4159/harvard.9780674498877 | resolves to *Washington Irving and the Storrows* | MISATTRIBUTED |
| OUP / CUP / HSUS / JHU / NBER / BEA / Census landing pages | generic pages, no per-year numbers | no support |

## 2. NVIDIA

**(a) Market share**
| Claim | Retrieved | Tier |
|---|---|---|
| 98% of DC GPUs, 2023 (TechInsights) | DCD, June 2024, citing TechInsights: "Nvidia retained a 98 percent market share of the data center GPU market last year" | PLAUSIBLE |
| ~90% of AI servers; ~64% of all accelerators (TrendForce) | fabricated URLs | REJECTED |
| 92% of DC GPUs (IoT Analytics) | IoT Analytics, 2025-03-04: "In 2024 … NVIDIA vastly led the data center GPU market, holding 92% of the market share"; AMD 4%, Huawei 2%, market $125B; GPUs only | CONFIRMED (the year is 2024, not May 2024) |
| 75–80% of AI processors | not on the retrieved page | UNSOURCED |
| IDC 87% / 75–81%; Omdia $123B / $207B | login walls | UNSOURCED |
| Found: ~70% of AI chips in 2025, ASICs included | TrendForce 2025-10-30: "TrendForce estimates that NVIDIA will maintain approximately 70% of the AI chip market share in 2025." | CONFIRMED (estimate) |
| Found: 65% of DC AI chips, 2023 ($17.7B; Intel 22%, AMD 11%) | TechInsights Q1 2024 update | CONFIRMED (estimate) |

**(b) Investments**
| Claim | Retrieved (filing on disk) | Tier |
|---|---|---|
| Private (non-marketable) stakes: $3,387M, $1,321M, $288M; net additions 1,309 / 859 | 10-K FY2025 carrying-value table | CONFIRMED |
| Public stakes: $381M | 10-K FY2025 fair value table | CONFIRMED |
| New: private stakes $22,251M (Jan 2026), net additions 17,444 | 10-K FY2026 | CONFIRMED |
| New: private stakes $47,898M (Jul 2026), H1 net additions 31,005 | 10-Q Q2 FY2027 | CONFIRMED |
| New: public stakes 36,934 (Level 1) + 10,806 (Level 2) = $47,740M | 10-Q, Note 5 | CONFIRMED (sum derived) |
| New: $3.3B equity-method stakes; $25B equity commitments; guarantees capped at $105B for OpenAI-affiliate leases | 10-Q; CFO commentary | CONFIRMED (not summed) |
| New: Groq $13,000M | 10-K FY2026 cash flow | CONFIRMED; a licence, not a stake |
| Recursion $50M | real 8-K: "gross proceeds … approximately $50 million", 7,706,363 shares | CONFIRMED (fact); URL REJECTED |
| CoreWeave, Lambda, OpenAI $100M, Mistral, Cohere, Sakana | dead or blocked links | UNSOURCED |

**(c) Customer spending**
| Claim | Retrieved | Tier |
|---|---|---|
| Direct customers A/B/C = 12% / 11% / 11% (FY2025) | 10-K FY2025 | CONFIRMED |
| Their dollar amounts ($15,660M etc.) | not in the filing | derived only |
| "Customer A 19% in FY2024" | the filing shows A under 10%, B 13% | REJECTED |
| 35–40% of hyperscaler capex; >50–75% of compute capex | dead or blocked links | UNSOURCED |
| New: Hyperscale $48,710M of $89,023M Data Center revenue = 54.7% (H1: 55.9%) | 10-Q Q2 FY2027 | CONFIRMED |
| New: one AI company contributes "a meaningful amount" of revenue through the clouds | 10-Q | CONFIRMED (no number) |

**Financial core:** Data Center revenue FY2025 is **$115,186M** (the reply's $115,173M is REJECTED), and FY2024 is $47,525M (not $47,516M). Revenue of $130,497M, operating cash flow of $64,089M and capex of $3,236M are CONFIRMED. Free cash flow of $60,853M and $60,724M are derived and hold. New in FY2026: revenue $215,938M, Data Center $193,737M, operating cash flow $102,718M.

## 3. Railways
**UK, all 31 rows REJECTED:**
- The DOIs are fabricated or point to other books. The Kenwood (1965) reference is real (10.2307/2552228) but paywalled.
- The Bank of England's 1847 GDP is £628.3M at market prices (£574.2M at factor cost), against the reply's £465M. The reply's 1830 figure of £412M matches no column.
- Odlyzko gives about £44M of railway investment in 1847, and his Table 2 implies £37.8M, £41.0M and £37.1M added in 1846–48. The reply says 21.0, 31.1 and 26.5.
- "Over 60% of all investment": total investment in 1847 was £88M, so the reply's own figure is 35%. The on-disk figures give about 50%.
- The Bank of England dataset has no railway-investment series.

**What survives (PLAUSIBLE, `ev-railway-gdp-series-v1`):** each year's increase in cumulative railway capital (Odlyzko Table 2, from Mitchell 1988), divided by Bank of England GDP at market prices.

| Year | 1836 | 1838 | 1840 | 1843 | 1845 | 1846 | **1847** | 1848 | 1849 | 1850 | 1852 | 1855 | 1860 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| £M added | 5.6 | 9.8 | 10.6 | 5.1 | 11.0 | 37.8 | **41.0** | 37.1 | 30.0 | 11.4 | 15.7 | 11.5 | 13.8 |
| % of GDP | 1.07 | 1.83 | 1.98 | 1.04 | 1.94 | 6.36 | **6.53** | 6.30 | 5.09 | 2.09 | 2.70 | 1.61 | 1.76 |

On the other measure, £44M is 7.0% of GDP; Odlyzko's own text says 7.3% of £600M. Railways took 47–55% of all UK investment in 1846–49.

**US, all 20 rows REJECTED as cited:**
- The citations point to the wrong books.
- The NBER Fishlow chapter gives only decade totals in constant 1909 dollars: $926.9M (variant I) or $761.2M (variant II) for 1849–58. Fishlow's Table B-1 is in 1860 dollars.
- The reply's 1849–58 sum of $522.9M does not reconcile with about $703M in 1860 dollars.

## 4. Modern comparator
- The BEA figures cite a landing page, and the FRED check timed out, so they were not re-verified.
- The 2025 and 2026 values are labelled "projected" but marked CONFIRMED; BEA publishes no projections, so as stated they are REJECTED.
- The "dedicated AI capex" row is UNSOURCED.
- For the modern side of the broken axis, use `ev-equip-ipp-gdp-v2` or the railway yardstick (28.2% of GPDI). The two use different denominators.

## 5. Retrieval notes
- EDGAR was fetched with curl; the first request carried the operator's email in the User-Agent.
- The 27.5 MB Bank of England workbook is not copied. Its 1828–1862 GDP and investment extract, the URL and the sha256 are.
- WSJ, FT and Reuters were not tried any other way.
