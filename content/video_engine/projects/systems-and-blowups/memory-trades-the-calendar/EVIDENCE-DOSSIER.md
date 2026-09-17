# EVIDENCE DOSSIER - Memory trades the calendar (one-shot #3)

Tiers per `docs/agent-memory/operator/research-gate-tiers.md`: CONFIRMED (a source on disk), FIRST-PARTY (the operator's own record, quoted as written), DERIVED (arithmetic from the above, shown), EDITORIAL.

| figure | spoken as | tier | source on disk |
|---|---|---|---|
| the customs print lands mid-month for the prior month | "Around the fifteenth of every month, Korean customs prints the price of memory chips crossing its border" | CONFIRMED | `evidence/objects/ev-trade-the-calendar-v1.series.json` src: KCS release schedule; HS 8542.32 via the SCML monitor |
| +6.8 % mean in the half-month INTO the print (18 of 25 positive); +2.2 % after | "the stocks average plus six point eight percent. In the half-month after: plus two point two" | FIRST-PARTY | `../EPISODE-SEEDS.md:66-75` (the operator's backtest, 2026-08-30; n = 25, one regime, trend beta in the drift) |
| 3x | the melt on "front-run" | DERIVED | 6.8 / 2.2 = 3.09, written on the row (`build_short.py`, chart_to compare) |
| 14 strong prints; +3.4 % mean after; 8 of 14 up | "After the fourteen strong prints, the next two weeks averaged plus three point four. Eight of fourteen up." | FIRST-PARTY | `../EPISODE-SEEDS.md:71-72` |
| 8 weak prints (m/m <= -3 %) in 25 months; 7 fell; mean -6.9 %; the values per print | "Eight of them in twenty-five months. After seven of the eight, the stocks fell. Average: minus six point nine." | CONFIRMED | `evidence/objects/ev-weak-prints-v1.series.json` (the card `ev-trim-proof-v1` from Steel and Paper, values on disk: -3.9, -12.4, -5.3, -10.5, -11.3, +10.9, -8.7, -13.8) |
| -13.8 % / -14 % after the July '26 print | "the stocks dropped fourteen percent in two weeks" | CONFIRMED | the same card's last bar and LATEST badge |
| the July print -3.7 % m/m; the August print +16.4 % | "One soft print ... Sixteen percent higher a month later" | CONFIRMED | `evidence/objects/ev-print-metronome-v1.series.json` eventbars (Steel and Paper's `ev-june-print-v1`) |
| the chip price +267 % Dec '25 - Jul '26; the stocks -34 % off the June peak | the calendar page's tags | CONFIRMED | `evidence/objects/ev-trade-the-calendar-v1.series.json` (the parked `ev-cycle-anatomy-v1`, Yahoo Finance 000660.KS + MU; KCS via SCML) |
| "Good news is priced before it lands. Bad news is the only surprise left." | the reflection | EDITORIAL | the reading of the three FIRST-PARTY / CONFIRMED rows above |

Not spoken, by decision: the capitulation doctrine (EPISODE-SEEDS:31-49, earmarked for the full memory episode).
