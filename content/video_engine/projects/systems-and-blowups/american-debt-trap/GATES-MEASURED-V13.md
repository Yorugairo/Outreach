# Measured V13 scratch opening gate

Scratch voice only; frozen V13. Original estimated report remains unchanged.

```text
Traceback (most recent call last):
  File "C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\scripts\gate_opening_structure.py", line 1082, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\scripts\gate_opening_structure.py", line 1065, in main
    gates, stats = run(text, tl, args.counterparty, args.ring, args.opening_s, args.cycle_s,
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\scripts\gate_opening_structure.py", line 645, in run
    sents = _sentences_timed(text, timeline)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\scripts\gate_opening_structure.py", line 313, in _sentences_timed
    out.append((seg[0]["start"], seg[-1]["end"], s, off))
                ~~~~~~^^^^^^^^^
KeyError: 'start'

```

