# Export-control classification and rule timeline

Retrieved 2026-09-26.

## ECCN 3A001.a.14 - when it was created (PRIMARY, Federal Register)
- Rule: "Wassenaar Arrangement 2016 Plenary Agreements Implementation", FR Doc 2017-16904, published and effective 2017-08-15.
  Text: https://www.govinfo.gov/content/pkg/FR-2017-08-15/html/2017-16904.htm
- Preamble, verbatim: "Paragraph 3A001.a.14 is added to control integrated circuits that perform the same functionality of electronic assemblies, modules, or equipment described in paragraph 3A002.h. This addition of control will result in an increase of 50 or fewer license application submissions per year."
- Later FR rules touching the term "3A001.a.14" (federalregister.gov API search): 2018-22163 (2018-10-24), 2019-10778 (2019-05-23), 2020-16286 (2020-09-11), 2023-03683 (2023-02-24), 2023-22299 (2023-10-18), 2023-23055 (2023-10-25), 2024-07004 (2024-04-04), 2024-19633 (2024-09-06).

## ECCN 3A001.a.14 - current text (SECONDARY rendering; eCFR confirms the paragraph is live)
- eCFR full-text search (https://www.ecfr.gov/api/search/v1/results?query=%223A001.a.14%22) returns Supplement No. 1 to Part 774 (the CCL) excerpts naming "3A001.a.12 to 3A001.a.14" - i.e. the paragraph exists in the current CCL.
- Text as rendered by eccnfinder.com/eccn/3a001/ (secondary): "Integrated circuits that perform or are programmable to perform all of the following:" (a) analog-to-digital conversions above resolution/sample-rate thresholds (e.g. 12-14 bit at >1.0 GSPS; 14-16 bit at >400 MSPS), and (b) "Storage of digitized data" or "Processing of digitized data". [NOT verified word-for-word against eCFR - the eCFR renderer truncated before Category 3.]
- Why the XCZU47DR fits (inference): 14-bit ADCs at 5 GSPS on the same die as FPGA fabric that processes the samples.
- 3A001 reasons for control per eccnfinder (secondary): NS, RS, MT, NP, AT. Paragraph-level applicability for a.14 not verified.

## ECCN of the XCZU47DR specifically
- Tom's Hardware (secondary, 2026-09-24) states it is 3A001.a.14. NO primary AMD or distributor classification record retrieved (DigiKey pages did not expose the ECCN field to the fetcher; Mouser timed out; Octopart/Avnet blocked). Tier: PLAUSIBLE.

## Licence requirement for China
- Tom's (secondary): a licence is required for China and "will almost certainly be denied"; mentions a licence exception for "Group B" countries (not named; possibly GBS - UNVERIFIED).
- Separate primary layer: the 2020 military end-use/end-user rule - "Expansion of Export, Reexport, and Transfer (in-Country) Controls for Military End Use or Military End Users in the People's Republic of China, Russia, or Venezuela", FR Doc 2020-07241, published 2020-04-28, effective 2020-06-29 (federalregister.gov API).
- AMD's own university RFSoC board requires an End Use Form before purchase (realdigital.org) - shows AMD's channel gates RFSoC sales on end-use.

## The China "advanced computing" rule timeline (PRIMARY, federalregister.gov API) - context only; these rules target AI/HPC chips and chip-making tools, NOT RFSoCs
| Published | Effective | FR Doc | Title (short) |
|---|---|---|---|
| 2022-10-13 | 2022-10-07 | 2022-21658 | Advanced Computing and Semiconductor Manufacturing Items (the "Oct 7" rule) |
| 2023-01-18 | 2023-01-17 | 2023-00888 | Updates ... to add Macau |
| 2023-10-25 | 2023-11-17 | 2023-23055 | Advanced Computing Items; Updates and Corrections (the "Oct 17, 2023" AC/S rule) |
| 2023-10-25 | 2023-11-17 | 2023-23049 | Export Controls on Semiconductor Manufacturing Items |
| 2024-04-04 | 2024-04-04 | 2024-07004 | Corrections and Clarifications |
| 2024-12-05 | 2024-12-02 | 2024-28270 | Foreign-Produced Direct Product Rule additions (the "Dec 2, 2024" rule) |
| 2024-12-05 | 2024-12-02 | 2024-28267 | Entity List additions; VEU removals |
| 2025-01-15 | 2025-01-13 | 2025-00636 | Framework for AI Diffusion |
| 2025-09-16 | 2025-09-12 | 2025-17893 | Additions and Revisions to the Entity List |
| 2026-01-15 | 2026-01-15 | 2026-00789 | Revision to License Review Policy for Advanced Computing Commodities |

Key point for the script: the RFSoC's control predates the famous AI-chip rules - it is a Wassenaar (multilateral) dual-use control from 2017, not part of the Oct-2022 China package.
