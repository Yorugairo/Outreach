# REWRITE ORDER B - "Memory trades the calendar" (the short)

**Status: the ORDER (E99 s75 Apply (4); BACKLOG R26-193).** An order for the next letter, never a patch of the recorded
one. Letter B is not drafted here; it is drafted from this order when the calendar short is next built.

E99 s75 Apply (4): "the calendar script's ring - "the day the print lands is the day the stocks trade it" - goes to a
REWRITE ORDER for the next letter (the recorded take stands; script changes never patch a recorded letter)". The rule for
an order (`docs/agent-memory/operator/script-changes-go-to-next-letter.md`): "when more than one change is due, write them
into a rewrite order (what changes, why, what is out of scope) and draft the next letter from it; leave the previous letter
and its take byte-identical".

**Letter naming:** the project's script carries no letter (`SCRIPT-SHORT-VO.txt`, `SCRIPT-SHORT-GATES.md`,
`SCRIPT-SHORT-SCREENS.md`). As in `myth-of-historical-normal/REWRITE-ORDER-B.md`, the on-disk `SCRIPT-SHORT-VO.txt` is
**letter A** and this order names **letter B** (`SCRIPT-SHORT-VO-B.txt`).

## 1. Letter A stays as recorded

- `SCRIPT-SHORT-VO.txt` - the script, byte-identical.
- `vo-short/audio/scene_1-tight.words.json` - the recorded take's word timeline: 225 words, the last ending at 71.22 s;
  its closing words are A's ring as written ("the day the print lands is the day the stocks trade it.").
- `SCRIPT-SHORT-GATES.md` - A's gates report (`VERDICT: PASS`; S05 "'calendar' returns at the close sharing ['trade']").
- The served frozen copy `build-p66-cal-frozen-v7/` is never rebuilt (E99 s75 Apply (6)).

## 2. What the operator said, recorded

E99 s75, on `p66-hg1-the-calendar-base-v7`: "this script isn't great, especially the ending \"That's the day the stocks
trade it.\" but the creation itself is better than before." s75's Why: "The script's ring line is the one-shot's script,
not the compiler's".

## 3. What changes in letter B

| # | Change | Why (the record) |
|---|---|---|
| 1 | The ring. A's last sentence, "So you don't have to read the print faster than the market. [ring] You have to know the calendar: the day the print lands is the day the stocks trade it.", is rewritten. | s75: "especially the ending"; s75 Apply (4) names this line. |
| 2 | The letter is re-read whole, not only at its ring. | s75: "this script isn't great"; the next-letter rule: patchwork "leaves a text no one wrote as a whole". |

Letter B runs `docs/runbooks/ONE-SHOT.md` steps 2 and 3 as any letter does: its own gates report and blind viewer, then its
own take (`record_short_take.py`) - A's take is never re-aligned to B's text.

## 4. Out of scope

- The figures. `PRODUCTION-LEDGER.md` "Decisions taken without the operator" item 2 records them (CONFIRMED, or the
  operator's first-party backtest quoted as written). This order changes none; a new figure in B passes the research tiers
  first.
- The visuals of any cut built from A (E99 s75 Apply (1)-(3), s76, s77): those are build work under
  `docs/runbooks/ONE-SHOT.md` "The editing rules", not script changes.

## 5. Gaps - what the record does not say (listed, not filled)

1. **The new ending's words.** The operator named what fails ("isn't great, especially the ending") and never what should
   replace it; no recorded answer gives B's ring. Letter B's author writes it and it goes to the operator on the letter's card.
2. **The quoted ending is not A's text.** The operator quoted "That's the day the stocks trade it."; letter A and its take
   end "the day the print lands is the day the stocks trade it." s75 Apply (4) names A's line, so this order targets that
   line; whether the card's captions or another build carried the quoted wording is not on record.
3. **The rest of the letter.** "this script isn't great" names no other line; which other sentences B changes is the
   author's read (change 2), not a recorded instruction.
4. **When.** No ruling schedules the calendar short's next build; s77 stopped the compiler base it was served from, and
   s77 Apply (7) sends the next short "by hand on the door cut's pattern (E98 s7)". This order waits for that build.
