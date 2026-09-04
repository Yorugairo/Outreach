# Is Wealth Logic composited or generated? — checked against the frames, 2026-09-04

Gemini's read: "100% composited, not AI-generated into the scene." **Agreed, and it
matters.** But its stated evidence is wrong, and the real tell is the opposite of what
it describes.

## Agreed — this is composited vector assets, not diffusion

Looking at `frame_0020`, `frame_0026`, `frame_0080`:

- **Pure white ground with nothing on it.** No horizon, no floor plane, no shadow under
  any figure. Characters stand on nothing. Diffusion does not reliably produce an empty
  white field; compositing produces nothing else.
- **A persistent character with swapped poses.** The lab-coat analyst appears in `0020`
  and `0080` — same face construction, same coat, same tie, hand pose changed.
- **Independent kinetic layers.** The `NOT YET` stamp in `0080` sits over the ground
  beside the host. In `0026` the floating calendars are scattered at different scales
  and rotations around a central pile — each one a separate placed object.
- **Captions with a per-word highlight and no background pill** (`BECAUSE YOUR OWN
  MONEY`, one word lit green).

## Disagreed — the "multi-style collision" is not there

> *"On the left a sleek thin-line corporate executive… in the center the host in bold
> retro-ink 1950s cartoon… on the right a blond kid in completely different line weight
> and pastel colouring. Three completely distinct illustration styles."*

**No.** In `frame_0020` all three figures share one outline weight, one flat-fill
treatment, one face-construction grammar (dot-and-line eyes, same nose, same hand
shapes). They are three different **characters** from one consistent library — the look
is a stock 2D character system (Vyond/Powtoon family), not three sources collided.

Gemini read *different characters* as *different styles* and built the argument on it.
The actual forensic tell is the **opposite**: the consistency is unnaturally perfect,
including across the vault, the desk and the props. Diffusion drifts; a library does
not. Same conclusion, sounder reason.

## The thing neither of us named, and it is the useful one

**They do not build worlds. They compose props on white.**

`frame_0026` — the claim is "your own money is tied up." The frame is: one character,
one pile of coloured pens, one cash bundle, five floating calendars. **Four asset types
on an empty ground.** That is the abstract-to-concrete rule executed for the price of a
prop, not a plate.

Compare our revised Tokyo table: six *new world plates* to carry six metaphors. Theirs
would be six *new props* against a ground they already have — and every prop is reusable
forever, while a world plate is spent on one shot.

> **Props compose. Worlds don't.**

That is the cheaper and better road to the same place, and it changes what our
generation claims should be asking for: a transparent prop library (toll gate, empty
chair + cold cup + bill, crate stamped with a future year, tipping scale) rather than a
fully-dressed scene per beat. Our asset registry already separates `world` / `actor` /
`prop` / `mechanism`; we have simply been generating at the `world` tier by habit.

## Two claims Gemini makes about US that are false

1. > *"Our pipeline… automatically detects acoustic breath pauses (Gap ≥ 0.45 s) and
   > programmatically sets scene boundaries so cuts land in silence."*

   **We do not do this.** Measured today on ep1: **68% of our scene cuts land MID-WORD**,
   32% in a gap of any size, 13% in a gap ≥0.45 s. This is the aspiration described as
   though it were implemented — the exact defect the whole gap investigation exists to
   fix. Gate M13 is proposed and **not built**.

2. > *"78% of plates hold for 8–20 seconds."*

   Measured from the shot ledger: **55%**. The 78% figure came from Gemini's own earlier
   report and was carried forward without recheck.

Both are the same failure mode: a plausible number reused instead of measured. Worth
naming because this dossier is otherwise the most useful reference work we have.

## Where Gemini's recommendation is right

- **Do not downgrade to prompt-per-timestamp diffusion slideshows.** Correct.
- **Keep the composited renderer of record.** Correct.
- **Adopt abstract-to-concrete into storyboarding.** Already done —
  `RULE-abstract-to-concrete.md`.

To which the frames add: **execute it at the prop tier, not the world tier.**
