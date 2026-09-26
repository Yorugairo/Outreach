# AMD / XCZU47DR RFSoC / Puzhi - research pack (Money Physics)

Compiled 2026-09-26 by docs_researcher. All snapshots under `sources/`. Tiers: CONFIRMED = primary source captured on disk / quoted verbatim with URL; PLAUSIBLE = reputable secondary (or a primary we could not capture); UNSOURCED-editorial = opinion/anonymous/snippet only; REJECTED = contradicted.

**Defamation frame (read first).** Dylan Patel ALLEGES; AMD DENIES direct sales and blames third-party diversion. Nothing on record establishes that AMD sold to Puzhi, that any law was broken, that any authority is investigating, or that the $1,000 quote exists outside Patel's post. The word is "investigated for treason" (his call for an investigation), never "charged". No charge, investigation or finding was found.

---

## 1. Claims table

| # | Claim | Tier | Source URL | On-disk file | Verbatim (short) |
|---|---|---|---|---|---|
| 1 | Patel posted on X on 2026-09-19 16:41:05 UTC | CONFIRMED | https://x.com/dylan522p/status/2101350877932212621 (via api.fxtwitter.com) | sources/01 | created_at "Sat Sep 19 16:41:05 +0000 2026" |
| 2 | Patel's words: AMD should be investigated for treason (NOT "charged") | CONFIRMED | same | sources/01 | "AMD needs to be investigated for treason." |
| 3 | Patel: AMD is "dumping US military chips for 1/4 of the cost in China" | CONFIRMED (as his claim) | same | sources/01 | "AMD found a business opportunity in dumping US military chips for 1/4 of the cost in China." |
| 4 | Patel's three prices: $36k list, $4-5k US volume, $1k quoted in China | CONFIRMED that he said it; the $4-5k and $1k figures themselves are UNSOURCED (no evidence attached) | same | sources/01 | "US list price is $36k for this chip, with $4-5k to US companies at volume, but it's getting quoted $1k in China to crowdfunding campaigns" |
| 5 | Patel's post does not say AMD sold to Puzhi; it says the chip is "getting quoted" in China - passive, quoter unnamed | CONFIRMED (reading of the text) | same | sources/01 | "it's getting quoted $1k in China" |
| 6 | Patel framed it beyond export law | CONFIRMED | same | sources/01 | "it's not just export violations, but it's literally selling military end use components to an adversary for less than your home country" |
| 7 | Patel's post linked DigiKey XCZU47DR-2FSVG1517I and the Crowd Supply PZSDR P047 page | CONFIRMED | same | sources/01 | (URLs in post JSON) |
| 8 | AMD's statement went to Tom's Hardware via a spokesperson | PLAUSIBLE (recipient's own report; AMD did not publish it on its site as far as found) | Tom's article (body via https://www.tomshardware.com/feeds/tag/amd) | sources/04 | "a spokesperson told Tom's Hardware" |
| 9 | AMD: shipments to restricted regions violate its policy; this instance is unrelated to direct AMD sales | PLAUSIBLE (quoted by recipient) | same | sources/04 | "This recent instance is unrelated to any direct AMD sales or shipments." |
| 10 | AMD: it investigates suspected diversion and will report violations and cut off the company | PLAUSIBLE | same | sources/04 | "We investigate all suspected diversion cases and if we find any violation of law, we will report it to relevant authorities and cease all business with the company." |
| 11 | AMD did not confirm an investigation of this case | PLAUSIBLE | same | sources/04 | "did not explicitly confirm that it had opened an investigation into this particular case" |
| 12 | AMD gave Patel the same answer, per a Patel follow-up post | PLAUSIBLE (Tom's says so); the follow-up post itself NOT FOUND | same | sources/04 | "AMD told Patel the same, according to another X post he made as a follow-up" |
| 13 | Tom's: the $1,000 is Patel's reported figure, not a public offer | PLAUSIBLE | same | sources/04 | "The $1,000 figure, however, is Patel's reported price for the chip rather than a publicly advertised retail offer." |
| 14 | The crowdfunded product is "PZSDR P047 RF-ADC and RF-DAC" by Puzhi, Shanghai, on Crowd Supply | CONFIRMED | https://www.crowdsupply.com/puzhi/pzsdr-p047-rf-adc-and-rf-dac | sources/02 | "An advanced single-chip SDR based on the AMD Zynq UltraScale+ XCZU47DR RFSoC" |
| 15 | The board names the chip as XCZU47DR-2FFVE1156I (1156-ball package) - not the 1517-ball part Patel linked | CONFIRMED | Crowd Supply + Puzhi P047 page | sources/02, sources/05 | "AMD Zynq UltraScale+ XCZU47DR-2FFVE1156I" |
| 16 | Campaign ended 2026-08-27, $57,143 raised on a $1 goal, 5 backers; board price $8,749 now | CONFIRMED (as shown 2026-09-26) | Crowd Supply | sources/02 | "$57,143 raised"; "5 backers"; "$8,749" |
| 17 | Campaign pledge price was $6,699 and live by 2026-06-11; deliveries Nov 2026 | PLAUSIBLE | https://www.cnx-software.com/2026/06/11/pzsdr-p047-rf-adc-and-rf-dac-high-end-sdr-board-is-based-on-amd-zynq-ultrascale-zu47dr-rfsoc/ | sources/08 | pledge "$6,699" |
| 18 | Ship date: Tom's says 2026-11-06; live Crowd Supply page now says 2027-05-06 | CONFIRMED (the live page); PLAUSIBLE (Tom's date) - the date has moved or the pages disagree | Crowd Supply; Tom's | sources/02, sources/04 | "May 06, 2027" |
| 19 | Crowd Supply is a Mouser Electronics company (acquired 2018-10-03), based in Portland, Oregon | CONFIRMED | https://www.crowdsupply.com/announcements/crowd-supply-has-been-acquired | sources/08 | "Crowd Supply will remain in Portland, Oregon" |
| 20 | Puzhi = Puzhi Electronic Technology (Shanghai) Co., Ltd., Pudong | CONFIRMED | https://www.en.puzhi.com/Product/AMD-FPGA-Development-Board/Zynq-UltraScale-plus-RFSoC/P047 | sources/05 | "Puzhi Electronic Technology (Shanghai) Co., Ltd." |
| 21 | Puzhi sells a whole line of XCZU47DR products (P047, P047Pro, PZ-ZU47DR-SOM, PZ-ZU47DR-KFB) via AliExpress/eBay; the SOM page title includes "Satellite Radar" | CONFIRMED | Puzhi pages | sources/05 | "Software Defined Radio Digital Signal Processing Satellite Radar" |
| 22 | DigiKey price, XCZU47DR-2FSVG1517I (Patel's link): $35,979.02 qty 1, 40-week lead time | CONFIRMED | https://www.digikey.com/en/products/detail/amd/XCZU47DR-2FSVG1517I/15908156 | sources/03 | "$35,979.02" |
| 23 | DigiKey price, XCZU47DR-2FFVE1156I (the part on the board): $31,354.40 qty 1, 40 weeks | CONFIRMED | https://www.digikey.com/en/products/detail/amd/XCZU47DR-2FFVE1156I/15908035 | sources/06 | "$31,354.40" |
| 24 | Lead times 40-52 weeks at Avnet and DigiKey | 40 weeks at DigiKey CONFIRMED; "52 weeks"/Avnet PLAUSIBLE (Tom's only; Avnet blocked) | Tom's; DigiKey | sources/03, 04, 06 | "40 to 52 weeks" (Tom's) |
| 25 | A HK reseller sells Puzhi's XCZU47DR SOM board for $4,378.45-$4,475.91 and the KFB dev board for $6,004.08 | CONFIRMED (listing as shown) | https://www.thanksbuyer.com/products/4378-45 ; https://www.thanksbuyer.com/products/104984 | sources/05 | "$4,378.45 - $4,475.91" |
| 26 | AMD's own university RFSoC board (RFSoC 4x2, XCZU48DR-1FFVG1517E) sells at $2,499 academic; that bare chip is $27,686.12 at DigiKey | CONFIRMED | https://www.realdigital.org/hardware/rfsoc-4x2 ; https://github.com/Xilinx/RFSoC-PYNQ/blob/master/docs/rfsoc_4x2_overview.md ; DigiKey | sources/08 | "Academic Price: $2,499.00" |
| 27 | AMD's university board requires an End Use Form | CONFIRMED | realdigital.org | sources/08 | "complete the End Use Form prior to purchase" |
| 28 | XCZU47DR specs: 8 x 14-bit ADC up to 5 GSPS, 8 x 14-bit DAC up to 9.85 GSPS, 930K logic cells, 4,272 DSP | CONFIRMED for ADC/DAC counts and rates (Puzhi + Crowd Supply pages); PLAUSIBLE for DSP count (Tom's) - AMD DS889 not extractable | Crowd Supply, Puzhi, Tom's | sources/02, 04, 05 | "8-channel ADC/ sampling rate 5Gsps, 8-channel DAC/ sampling rate 9.85Gsps" |
| 29 | Gen 3 RFSoC announced 2019-02-20 for 5G, cable, phased-array radar, test, satcom; Gen 3 "available in 2H 2019" | CONFIRMED | https://www.prnewswire.com/news-releases/xilinx-extends-its-breakthrough-zynq-ultrascale-rfsoc-portfolio-to-full-sub-6ghz-spectrum-support-300798481.html | sources/11 | "Advanced phased-array radar" |
| 30 | XCZU47DR reached production in 2020 | PLAUSIBLE (Tom's) | Tom's | sources/04 | "reached production status in 2020" |
| 31 | XCZU47DR is ECCN 3A001.a.14 | PLAUSIBLE (Tom's; no AMD/distributor classification record captured) | Tom's | sources/04, 09 | "a 3A001.a.14 ECCN classification" |
| 32 | 3A001.a.14 was created on 2017-08-15 to control ICs doing the job of 3A002.h digitizer assemblies | CONFIRMED | https://www.govinfo.gov/content/pkg/FR-2017-08-15/html/2017-16904.htm | sources/09 | "Paragraph 3A001.a.14 is added to control integrated circuits that perform the same functionality ... described in paragraph 3A002.h." |
| 33 | BIS expected 3A001.a.14 to add "50 or fewer" licence applications a year | CONFIRMED | same | sources/09 | "an increase of 50 or fewer license application submissions per year" |
| 34 | 3A001.a.14 text: ICs that do high-rate A/D conversion AND store or process the digitized data | PLAUSIBLE (eccnfinder rendering; eCFR confirms the paragraph is live, text not captured from eCFR) | https://eccnfinder.com/eccn/3a001/ | sources/09 | "Integrated circuits that perform or are programmable to perform all of the following" |
| 35 | A licence is needed to ship it to China and would almost certainly be denied | PLAUSIBLE (Tom's; legally likely but not verified against the Country Chart/licence-review policy) | Tom's | sources/04 | "that license will almost certainly be denied" |
| 36 | A licence exception lets it ship to Group B commercial buyers, a leak path | PLAUSIBLE (Tom's; exception unnamed, unverified) | Tom's | sources/04 | "a license exception that allows shipping such items to commercial companies from the Group B countries" |
| 37 | No direct XQ (defense-grade) ZU47DR; ZU48DR has XC and XQ versions | PLAUSIBLE (Tom's; AMD XQ page timed out) | Tom's | sources/04 | "the XCZU47DR does not have a direct XQZU47DR counterpart" |
| 38 | "Military chip": the XCZU47DR is a commercial/industrial XC part with military uses (dual-use), not a defense-grade part | PLAUSIBLE (Tom's) | Tom's | sources/04 | "technically aimed at civil, commercial, and industrial applications" |
| 39 | AMD revenue billed to China (incl. HK): $7,751M of $34,639M in FY2025 (22.4%) | CONFIRMED (figures); % is my arithmetic | https://www.sec.gov/Archives/edgar/data/2488/000000248826000018/R54.htm | sources/07 | table |
| 40 | AMD geography is by customer billing location | CONFIRMED | R12.htm | sources/07 | "based on billing location of the customer" |
| 41 | AMD Embedded segment (FPGAs, adaptive SoCs) revenue: $3,454M FY2025, $3,557M FY2024, $5,321M FY2023 | CONFIRMED | R52.htm / R12.htm | sources/07 | table |
| 42 | 2015-16 DOJ case: three Chinese traders tried to buy rad-tolerant Xilinx ICs and swap in counterfeits bearing fake Xilinx labels; 12-15 month sentences | PLAUSIBLE (DOJ pages empty to fetcher; DOJ/FBI search snippets + 2017 trade blog) | https://www.justice.gov/usao-ct/pr/three-chinese-nationals-arrested-scheme-steal-and-illegally-export-military-grade | sources/10 | "eight counterfeit ICs, each bearing a counterfeit Xilinx brand label" |
| 43 | RUSI 2022: 450+ foreign components in Russian weapons, two-thirds US-made; a Russian importer brought in $1.1M of Xilinx microelectronics | PLAUSIBLE (VOA summary of RUSI) | VOA / RUSI | sources/10 | "$1.1 million worth of microelectronics made by Xilinx" |
| 44 | BIS enforcement 2025: $324M penalties (vs ~$16M 2024); 65 convictions; 162 indictments; 142 Entity List additions | PLAUSIBLE (law-firm summary of the BIS annual report) | https://blog.volkovlaw.com/2026/09/biss-fy2025-annual-report-an-18-fold-enforcement-surge-and-what-it-means-for-export-compliance-programs/ | sources/10 | "$324 million in civil and criminal penalties" |
| 45 | Bare XCZU47DR-2FFVE1156I chips listed on eBay from China at US$400 (169 pcs) and US$2,873.38 | UNSOURCED (search-engine snippets; eBay blocked; nothing captured) | ebay.de/itm/317067774760 ; ebay.com/itm/388723784740 | sources/10 | - |
| 46 | Puzhi eBay storefront listed an XCZU47DR core board at US$3,999 | UNSOURCED (snippet only) | ebay.com/itm/388751147008 | sources/05 | - |
| 46a | Patel's two attached photos are Crowd Supply screenshots (Puzhi header; campaign box "$39,645 raised", "4 backers", "$8,749"), not a $1k quote | CONFIRMED (images read) | pbs.twimg.com/media/HSl_fCIbIAAH4qZ.jpg ; pbs.twimg.com/media/HSl_fMPaIAAwgyc.jpg | sources/01 | "$39,645 raised" |
| 46b | Puzhi describes itself as founded 2017, products "exported to more than 60 countries" | CONFIRMED (Crowd Supply header in Patel's screenshot; text cropped) | same | sources/01 | "was founded in 2017" |
| 46c | Campaign moved from $39,645/4 backers (at the post) to $57,143/5 backers (2026-09-26); +$17,498 = 2 x $8,749 | CONFIRMED figures; the "one backer, two boards" reading is inference | sources/01 + 02 | sources/01, 02 | - |
| 47 | Patel "accused AMD of treason" / AMD "charged" | REJECTED as worded: he called for an investigation; no charge exists | - | sources/01 | - |
| 48 | BigGo's rendering of Patel's post and AMD's statement | REJECTED as verbatim (paraphrased; wording differs from the X JSON and from Tom's) | https://finance.biggo.com/news/fa589bf6-0360-451f-a5ea-c88e06224c84 | sources/01, 04 | - |
| 49 | RTL-SDR blog: "AMD is obviously giving significantly better pricing to Asian manufacturers" | UNSOURCED-editorial (blog inference) | https://www.rtl-sdr.com/pzsdr-new-amd-zync-ultrascale-based-sdr-crowd-funding-on-crowd-supply/ | sources/06 | quote |

---

## 2. Timeline

| Date (UTC) | Event | Tier | Source |
|---|---|---|---|
| 2017-08-15 | BIS adds ECCN 3A001.a.14 (Wassenaar 2016) - "RFSoC-type" ICs controlled | CONFIRMED | FR 2017-16904 (sources/09) |
| 2018-10-03 | Mouser Electronics acquires Crowd Supply | CONFIRMED | sources/08 |
| 2019-02-20 | Xilinx announces Gen 2/Gen 3 RFSoC; Gen 3 "available in 2H 2019" | CONFIRMED | sources/11 |
| 2020 | XCZU47DR reaches production | PLAUSIBLE | Tom's (sources/04) |
| 2020-06-29 | BIS military end-use/end-user rule for China, Russia, Venezuela takes effect (FR 2020-07241, pub. 2020-04-28) | CONFIRMED (FR API metadata) | sources/09 |
| 2022-10-07 | "Oct 7" advanced-computing rule (AI/HPC; not RFSoC) | CONFIRMED | FR 2022-21658 |
| 2023-11-17 | Oct-2023 AC/S rules effective | CONFIRMED | FR 2023-23055 / 23049 |
| 2024-12-02 | FDPR / Entity List package | CONFIRMED | FR 2024-28270 / 28267 |
| ~2025-07 | Puzhi eBay XCZU47DR board listing "last updated" | UNSOURCED | snippet |
| by 2026-06-11 | PZSDR P047 campaign live on Crowd Supply at $6,699 | PLAUSIBLE | CNX (sources/08) |
| 2026-08-18..27 | Four campaign updates; campaign ends 2026-08-27, $57,143, 5 backers | CONFIRMED | sources/02 |
| 2026-09-19 16:41 | Patel's X post calling for a treason investigation | CONFIRMED | sources/01 |
| 2026-09-19..24 | Patel follow-up post saying AMD gave him the same answer | PLAUSIBLE (post not found) | Tom's |
| 2026-09-24 13:00 | Tom's Hardware (Anton Shilov) publishes, with AMD's statement | CONFIRMED (feed pubDate) | sources/04 |
| 2026-09-26 | Crowd Supply page shows est. ship "May 06, 2027" | CONFIRMED | sources/02 |
| 2026-11-06 | Puzhi's ship date as reported by Tom's | PLAUSIBLE | sources/04 |

---

## 3. Chartable numbers

| Value | Unit | Date | What | Source | Tier |
|---|---|---|---|---|---|
| 35,979.02 | USD, qty 1 | 2026-09-26 | DigiKey XCZU47DR-2FSVG1517I (Patel's "$36k") | sources/03 | CONFIRMED |
| 31,354.40 | USD, qty 1 | 2026-09-26 | DigiKey XCZU47DR-2FFVE1156I (the part on Puzhi's board) | sources/06 | CONFIRMED |
| 4,000-5,000 | USD | 2026-09-19 | "US companies at volume" per Patel | sources/01 | UNSOURCED (his claim) |
| 1,000 | USD | 2026-09-19 | "quoted ... in China to crowdfunding campaigns" per Patel | sources/01 | UNSOURCED (his claim; not public per Tom's) |
| 8,749 | USD | 2026-09-26 | PZSDR P047 board price on Crowd Supply | sources/02 | CONFIRMED |
| 6,699 | USD | 2026-06-11 | P047 campaign pledge price | sources/08 | PLAUSIBLE |
| 4,378.45 | USD | 2026-09-26 | HK reseller, Puzhi XCZU47DR SOM board (lowest variant) | sources/05 | CONFIRMED |
| 6,004.08 | USD | 2026-09-26 | HK reseller, Puzhi XCZU47DR KFB dev board | sources/05 | CONFIRMED |
| 2,499 | USD | 2026-09-26 | AMD university RFSoC 4x2 board (ZU48DR), academic | sources/08 | CONFIRMED |
| 27,686.12 | USD, qty 1 | 2026-09-26 | DigiKey XCZU48DR-1FFVG1517E (chip on the RFSoC 4x2) | sources/08 | CONFIRMED |
| 40 | weeks | 2026-09-26 | DigiKey manufacturer lead time (all XCZU47DR/48DR parts checked) | sources/03, 06, 08 | CONFIRMED |
| 40-52 | weeks | 2026-09-24 | Avnet/DigiKey lead-time range | sources/04 | PLAUSIBLE |
| 57,143 / 5 | USD / backers | 2026-08-27 | P047 campaign total | sources/02 | CONFIRMED |
| 392,513 | views | 2026-09-26 | Patel post views (also 1,040 likes, 62 reposts, 35 quotes) | sources/01 | CONFIRMED (snapshot) |
| 7,751 / 34,639 | USD M | FY2025 | AMD revenue billed to China incl. HK / total (22.4%) | sources/07 | CONFIRMED |
| 6,231 / 25,785 | USD M | FY2024 | same (24.2%) | sources/07 | CONFIRMED |
| 3,417 / 22,680 | USD M | FY2023 | same (15.1%) | sources/07 | CONFIRMED |
| 3,454 / 3,557 / 5,321 | USD M | FY25/24/23 | AMD Embedded segment revenue | sources/07 | CONFIRMED |
| 5 / 9.85 | GSPS | - | XCZU47DR ADC / DAC sample rate (8 channels each, 14-bit) | sources/02, 05 | CONFIRMED |
| 50 | licence apps/yr | 2017-08-15 | BIS's estimate of the added licence load from 3A001.a.14 | sources/09 | CONFIRMED |
| 324 vs ~16 | USD M | CY2025 vs CY2024 | BIS civil + criminal export penalties | sources/10 | PLAUSIBLE |
| 65 / 162 | count | FY2025 / 2025 | BIS-driven criminal convictions / indictments (112 in 2024) | sources/10 | PLAUSIBLE |
| 142 | entities | 2025 | Entity List additions | sources/10 | PLAUSIBLE |
| 1.1 | USD M | 2021 | Xilinx microelectronics imported by one Russian firm (RUSI via VOA) | sources/10 | PLAUSIBLE |

Derived ratios (my arithmetic; label as such on screen):
- Patel's own ratio is **1/4** ($1k vs $4-5k volume), not 36x. The "$36,000 ... $1,000" framing is the headline's, using the qty-1 catalogue price.
- $35,979.02 / $1,000 = 36.0x (headline framing). The part actually on the board: $31,354.40 / $1,000 = 31.4x.
- A whole Puzhi SOM board ($4,378.45) = 14% of DigiKey's price for the chip it carries ($31,354.40).
- AMD's own academic board ($2,499) = 9% of DigiKey's price for its chip ($27,686.12).

---

## 4. The mechanism in one paragraph

The $36,000 is not "the price" of the chip; it is DigiKey's quantity-one catalogue price for a part that is not stocked and has a 40-week lead time. That price exists so a lone buyer who wants one pays for the trouble. Big customers negotiate from AMD's price book, and AMD itself sells a whole board with a sibling Gen-3 RFSoC to universities for $2,499, about a tenth of the chip's catalogue price - so a far lower real-world price proves nothing wrong on its own. The export control creates the second wedge. China is walled off by licence (ECCN 3A001.a.14 per Tom's), so in China the part cannot come through the official channel at all; supply comes from whatever leaks. Tom's names the route: licensed or licence-exempt sales to buyers in friendly countries, then onward resale. Other routes in the record are salvaged parts (unconfirmed for this chip) and relabelled counterfeits (the 2015 Xilinx case). A leaked chip's price is set by what that grey pool holds, not by AMD's list. The "is it even real?" branch: Patel's $1,000 is unpublished, and Tom's says it is not a public offer. No expert opinion was found saying whether a genuine new XCZU47DR can be had for $1,000. Unverified eBay snippets show "new" chips from China at $400 in 169-piece lots. A new genuine part does not sell for 1% of list in bulk (inference), so a price like that points to remarked, salvaged or counterfeit stock. The honest on-screen line is the mechanism, not a verdict: the list price is a quantity-one convenience price, the control removes the legitimate seller from the market, and what's left is priced by leakage and trust.

---

## 5. Open questions / not found

1. **Patel's follow-up post** (Tom's says AMD "told Patel the same"): not found. Tried fxtwitter thread API (returned only the root post), xcancel (HTTP 451), web search restricted to x.com.
2. **Who quoted $1,000, to whom, for what**: not found. Patel gives no source, and Tom's says it is not a public offer. His 2 attached photos were retrieved and read, and both are Crowd Supply screenshots, not a quote. The $1k figure has no evidence anywhere on the public record found.
3. **AMD/distributor ECCN record for XCZU47DR**: not captured. Tried DigiKey (field not exposed to the fetcher), Mouser (timeout), Octopart and Avnet (blocked), and AMD (timeouts). So 3A001.a.14 is PLAUSIBLE only.
4. **3A001.a.14 exact regulatory text from eCFR**: not captured. The eCFR renderer truncated and the govinfo FR text did not include the amendatory text. The eccnfinder rendering is secondary.
5. **Licence-exception path ("Group B")**: which exception (GBS?) applies to 3A001.a.14 is unverified. So is whether the China licence-review policy is presumption of denial.
6. **"$4-5k at volume"**: no source found. AMD does not publish volume pricing.
7. **eBay listings** ($400 bare chip x169; $2,873.38 bare chip; $3,999 Puzhi core board): eBay returned 403, so these are snippets only. A browser capture is needed before any on-screen use.
8. **Ship date**: Tom's gives 2026-11-06; the live page says 2027-05-06. The change date is unknown.
9. **Crowd Supply fulfilment and export**: Crowd Supply (Mouser-owned, Portland) sells the board with "Free US Shipping / $18 Worldwide". The record does not show whether the boards are imported into the US and re-exported, or how the board is classified. No statement from Crowd Supply or Mouser was found. Worth asking them for comment.
10. **Production date 2020 and XQ-counterpart claim**: Tom's only. AMD pages timed out.
11. **Ukraine GUR portal listing of Xilinx parts** in Iskander-M / Kh-101: the portal timed out, so this rests on search snippets only.
12. **BIS FY2025 annual report**: the PDF downloaded but no text could be extracted here, so the figures come via the Volkov Law summary.
13. **Whether any authority is investigating**: nothing found.
