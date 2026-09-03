# The viewer's prompt — v1

The wording of the blind reading test (PRP P36). One version, one file: this
is the only place the questions are written, and `viewer_run.py` sends nothing
but the fenced blocks below.

**Change control.** Any change to the wording of a block is a new version:
copy this file to `viewer_prompt.v2.md` and run with `--prompt`. A run records
`prompt_version` beside its answers so two runs are never compared across
different wording.

**What the reader is allowed to know.** Only the title, the picture, and the
words it has already been given. It is never told what the thing it is reading
is for, who wrote it, how it is put together, or that anything about it is
being measured. If it can work that out from these blocks, the blocks are
wrong.

**Placeholders** are replaced by the runner, verbatim, before the call:
`{{TITLE}}`, `{{SPAN}}`, `{{MEMORY}}`, `{{WINDOW_TEXT}}`, `{{PROMISED}}`.

---

## The package call

Sent once, first, before any of the words. The picture is attached to this call
as an image file; the title is the only text.

<!-- BLOCK: package -->
```text
You are about to watch a video. You have not seen any of it yet.

All you have is what anyone would have before pressing play: its title, and
the picture on it, which is attached to this message as an image. There is no
description, there are no comments, and you cannot look anything up.

TITLE: {{TITLE}}

One question, answered from first impression, the way you would answer a
friend who asked why you were about to watch it:

  What were you promised? What do you expect this video to tell you or show
  you, and what do you expect to walk away knowing?

Answer with JSON only — no greeting, no explanation, nothing before or after
the object:

{"promised": "<one or two plain sentences, in your own words>"}
```
<!-- END BLOCK -->

---

## The per-part call

Sent once per part, in order. `{{MEMORY}}` is the words of the previous two
parts and nothing else; `{{WINDOW_TEXT}}` is the words of this part.

<!-- BLOCK: window -->
```text
You are watching a video, and every so often I stop it and ask you what you
have taken in so far.

You cannot rewind and you cannot skip ahead. You know only what you have
already heard — what is below, and nothing else. Answer from what a person
would actually be holding in their head at this moment, watching once, at
normal speed: not from what you could work out if you sat and thought about
it, and not from anything you happen to know about the subject.

WHAT YOU HEARD JUST BEFORE THIS (already fading; empty if this is the start):
{{MEMORY}}

WHAT YOU ARE HEARING NOW ({{SPAN}}):
{{WINDOW_TEXT}}

Four questions, all of them about WHAT YOU ARE HEARING NOW:

  1. What do you now know that you did not know a moment ago? List the things
     plainly and separately — a number, a name, a thing, a way something
     works, a claim. Say them the way you would say them to someone else, not
     by quoting. If nothing new arrived, return an empty list; do not pad it.

  2. What question are you holding right now — the thing you are waiting to
     have answered? One sentence, in your own words. If you are holding none,
     return "".

  3. What, if anything, were you just asked to do? Only if you were actually
     asked; "" if you were not.

  4. What could you not follow? A word you did not know, a jump you could not
     make, a sentence you would have had to hear twice. List them short.
     Empty list if all of it landed.

Answer with JSON only, with these keys, and nothing before or after the
object:

{"new_things": ["...", "..."], "held_question": "...", "asked_of_me": "...", "could_not_follow": ["..."]}
```
<!-- END BLOCK -->

---

## The first part, additionally

Appended to the per-part call for the first part of the words only, so the
promise the picture and the title made is checked against what actually
arrives.

<!-- BLOCK: window_one_extra -->
```text

ONE MORE THING, ASKED ONLY THIS ONCE. Before you heard any of it you saw only
the title and the picture, and you said you had been promised this:

  "{{PROMISED}}"

  0. Has that promise been answered yet — and if it has, by which sentence?
     Quote the sentence exactly as you heard it. If it has not been answered
     yet, say so plainly, and say what you are still waiting for.

Put the answer in the same JSON object as the other four, as two more keys:

{"promise_answered": "yes | not yet | <what actually happened>", "answered_by": "<the exact sentence, or \"\">"}
```
<!-- END BLOCK -->

---

## The answer, exactly

Every per-part answer is one JSON object and nothing else. No prose around it,
no code fence, no commentary.

| key | type | meaning |
|---|---|---|
| `new_things` | list of short strings | one entry per thing newly known; `[]` if nothing arrived |
| `held_question` | string | the one question being held; `""` if none |
| `asked_of_me` | string | what the listener was just asked to do; `""` if nothing |
| `could_not_follow` | list of short strings | each thing that did not land; `[]` if all of it landed |
| `promise_answered` | string | first part only |
| `answered_by` | string | first part only |

A worked example — deliberately about nothing we make, so it primes nothing.

Heard just before: *"The bakery on Mill Street opened in 1974."*
Hearing now: *"By 2019 it was baking four hundred loaves a day. Then the
landlord tripled the rent. Watch what the owner did next, because it is the
opposite of what you would do."*

```json
{
  "new_things": [
    "the bakery was baking 400 loaves a day by 2019",
    "the landlord tripled its rent",
    "the owner did something surprising in response"
  ],
  "held_question": "What did the owner actually do about the rent?",
  "asked_of_me": "keep watching to see what the owner did",
  "could_not_follow": []
}
```

And the package answer, in the same spirit:

```json
{"promised": "That a small bakery survived something that should have closed it, and that I will find out what its owner did differently."}
```
