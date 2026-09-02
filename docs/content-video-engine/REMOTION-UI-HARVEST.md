# remotion-ui harvest notes (operator review, 2026-08-31)

Component sources reviewed via the registry MCP. Targets `src/remotion/*`
- i.e. they install into the p29 Remotion editor when it's harvested.
What's worth taking, and where:

## Steal into OUR player template (technique, not React)
- **line-chart-draw: the tip head + deposited dots.** A glowing dot
  rides the drawing line's tip - read off the REAL path via
  `getPointAtLength` (native SVG API, works in our template today), and
  data dots grow in as the tip passes them ("the line depositing them
  rather than a blink"). One gesture instead of overlapping animations.
  Also: the zero gridline reads heavier than the others.
- **comparison-bars: the callout is the conclusion.** The delta chip
  lands only after the second bar stops moving, and slides in from -12px.
  Apply to our badge choreography: badges that state a conclusion should
  land AFTER their evidence finishes drawing, not alongside it.

## Species candidates (future episodes, build in whichever surface)
- **bar-chart-race: the soft fractional rank.** Rank = sum of sigmoids
  against every other series (softness = 2.2% of the leader), so bars
  SLIDE past each other at crossovers instead of teleporting a row.
  Genuinely clever; the mechanism is surface-agnostic. Candidates:
  memory-maker share over years, capex league table, index-weight race.
- **hook-card (block): shorts/opener packaging.** Line-by-line rise from
  per-line masks at spoken cadence, underline DRAWS under the promise
  substring, kicker chip with breathing live-dot, and a drifting
  radial field ("a still frame reads as a slide"). Made for Building
  Money shorts and MP shorts openers. Its `balanceLines` (no orphan
  words) is a general caption utility.

## Doctrine echoes worth absorbing (doc 29 candidates)
- "Exits accelerate away; entrances decelerate in. Never ease-out an
  exit." (motion-tokens discipline - matches our grammar; adopt the
  phrasing.)
- Shared scale across compared rows, always - "per-row scaling is what
  makes a small category look like it beat a large one."
- The numeral inside a bar waits until the bar is wide enough to hold
  it (we already do this; theirs fades on a progress window).

## Install commands (run in the p29 editor after harvest, NOT here)
    npx remotion-ui@latest add bar-chart-race
    npx remotion-ui@latest add comparison-bars
    npx remotion-ui@latest add hook-card
    npx remotion-ui@latest add line-chart-draw
    npx remotion-ui@latest add animated-bar-chart

## Lesson (2026-09-01): harvest the idea, never replace the mechanism

The directional-wipe port (dd9e476) is the counter-example. It swapped
the reviewed hard `inset()` scene wipe for remotion-ui's feathered mask
+ parallax cross-reveal. On review it read as a two-direction fade,
flipped the reveal direction, and mirrored the carried light; it was
retired and the hard front restored (75a0f13). Operator: *"there was
something we were trying to learn from the remotion component, but
definitely over-stepped and ruined what was good about what we had."*

Standing rule for every future steal-now:
- A port that changes what a REVIEWED shot looks like is a proposal, not
  a change. Render candidates side by side; the operator picks.
- Extract the transferable idea and graft it INSIDE our mechanism. The
  ports that survived (badge floor, tip head, deposited dots) are all of
  that kind - additions to a mechanism, never replacements of one.
- When motion regresses, `git log -S<constant>` on the template first.
  Doc 29 s9.15: a reviewed refinement outranks the demo it refined.
