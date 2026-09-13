---
name: caption-energy-lessons
description: "Shorts captions, 2026-09-05, seven rounds by eye: anything that moves word to word pins the eye (a pop AND a box), anything that ignores the voice loses sync, a flash is an event not motion (E21), and the vertical word gate is LINES not words (800 px strip at 64 px = 25-28 chars = 3-6 words, two lines max)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-05T22:22:07.331Z
---

**What happened (2026-09-05, the Tokyo short).** The operator asked for "more dynamic captions ... letting people read the captions on shorts is how we reduce mental friction; right now they're hanging on every word". Seven rounds: (1) the phrase landing whole = readable, dead; (2) a hyperframes-style box per spoken word = energy, but a jumping cursor pins the eye exactly like the popping words did; (3) one smooth red front across the phrase = fluid, off the voice, a flat band; (4) a gold landing flash + keyword pop = "WAY too busy ... a lot of flashes, not a lot of motion - an old lesson we learned the hard way"; (5) back to the golden set's per-word pops on sentence-sized pages; (6) the spoken-word lift and a per-word BOIL restored "the words shifting slightly to stay alive"; (7) toned down (pop 1.10, lift 1.03, rise 6 px, the captions' own boil at half the plates'). What shipped: the golden set's kinetics + the red box on the keyword as it lands (gold text never changes) + a soft shadow for contrast + sentence-sized pages.

**Why:** the eye follows the newest discrete event; energy has to come from continuous motion (settles, lifts, boil) tied to the voice, not from events. Colour: gold is the retention colour; the keyword keeps it whatever sits behind it.

**How to apply:** never put a per-word cursor or flash on a short; keep motion continuous and voice-timed at the word level only where the golden set had it. The vertical word gate is LINES: measure the built page's block height (a 1.2em keyword is not a line) - the 800 px strip at 64 px holds 25-28 chars, so 28 chars / 6 words = 3-6 words on two lines; 46 / 7 wrapped a third of pages to three. A build declares `caption_style: phrase` and its own page budget; long-form is untouched. Judge captions in motion in the player, not from stills. See [screen-never-still](screen-never-still.md), [soak-ink-is-a-plate](soak-ink-is-a-plate.md).
