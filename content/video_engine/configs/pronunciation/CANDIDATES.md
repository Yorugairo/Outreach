# Pronunciation Candidates — probe before ruling

Method (the doc 22 lesson): the "obvious" rule was dead on the real script,
and unscoped aliases misfire. So no rule enters a dictionary on a guess.
The loop is:

1. Candidate terms come from **actual corpora** (claim vocabulary, registered
   slides, project scripts) — not brainstormed lists.
2. One short **probe script per domain** (below, `probe-*.txt`) is synthesized
   as a single cheap TTS job through the normal paid gate (~$0.05 each at the
   estimate rate).
3. **Listen.** Only terms the model actually fails become alias rules, scoped
   per doc 22, with `note` + `added_episode` recording the probe.
4. Dead candidates are recorded here as *verified-fine* so nobody re-probes
   them.

Dictionary layout (locator cap is 3 per request):

- **finance-core** — investment + datacenter/silicon terms share the lane and
  the dictionary. Already shipped with observed/structural rules (won
  homographs, AVAV, TSMC, KOSPI, SK hynix).
- **bjj-core** — separate channel, separate dictionary. Created only when the
  BJJ probe returns failures.

## Finance / investment candidates

| Term | Expected speech | Risk class |
| --- | --- | --- |
| S&P 500 | "S and P five hundred" | ampersand handling |
| ROIC | letters, "R O I C" | may attempt "roik" |
| capex | "cap-ex" | may read "kay-pex" |
| IonQ | "ion cue" | may merge into one syllable |
| LASE | letters (ticker convention) | may read "laze" |
| APLD | letters | likely fine |
| FHFA / EBRI | letters | likely fine |
| Braavos | "BRAH-vohs" | may read "BRAY-vohs" (cited channel, doc 35) |
| Nvidia / Micron / Broadcom | natural | verify only |

## Datacenter / silicon candidates (memory thesis vocabulary)

| Term | Expected speech | Risk class |
| --- | --- | --- |
| DRAM | "DEE-ram" | **high** — likely "dram" |
| NAND | "nand" (word) | likely fine |
| ASIC | "AY-sick" | may spell letters or "a-sick" |
| HBM / HBM4 | "H B M (four)" | digit join |
| Tier III | "tier three" | **roman numeral** — may spell "I I I" |
| greenfield / hyperscaler / wafer / fab | natural | verify only |

Writer-side note: units like "MW" or "GW" never reach TTS — written out per
doc 37 §4. Roman numerals outside proper names should also be written out
("Tier three") rather than ruled around.

## BJJ candidates (from the history-of-bjj corpus, by frequency)

| Term | Expected speech | Risk class |
| --- | --- | --- |
| Maeda | "mah-EH-dah" | **high** — likely "MAY-duh" |
| Mitsuyo | "mit-SOO-yoh" | Japanese given name |
| Jigoro | "jee-GOH-roh" | Japanese given name |
| Kano | "KAH-noh" | **high** — likely "KAY-noh" |
| Kodokan | "KOH-doh-kahn" | moderate |
| Helio / Hélio | "EH-lee-oh" | **high** — likely "HEE-lee-oh" (Portuguese) |
| jiu-jitsu | "joo JIT-soo" | verify only |
| vale tudo | "VAH-lee TOO-doh" | Portuguese phrase |
| kimura | "kee-MOO-rah" | may read "kim-YER-ah" |
| americana / judo / Gracie | natural | verify only |

Multilingual v2 is language-aware, so some Japanese/Portuguese names may
come out right without help — that is exactly what the probe determines
before any rule is written.

## Status

- [ ] finance/datacenter probe synthesized and eared (`probe-finance-datacenter.txt`)
- [ ] BJJ probe synthesized and eared (`probe-bjj.txt`)
- [ ] failures promoted to rules; verified-fine terms recorded above
- [ ] finance-core re-synced after any additions
