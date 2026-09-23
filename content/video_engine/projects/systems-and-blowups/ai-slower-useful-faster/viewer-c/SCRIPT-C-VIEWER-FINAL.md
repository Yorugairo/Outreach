# VIEWER — SCRIPT-C-VO.txt

A blind reader, 7 windows, two-window memory, 7 reported (estimated timings, model (codex default), prompt v2).
It was never asked when it would leave. The judging is this file's, and it is deterministic.

```text
  [FAIL ] V01 7/9 declared beats perceived (78%); unperceived: [ring] w0, [stakes] w2
          P36 beat recall (rule R2 laundering, measured from the outside)
  [PASS ] V02 no run of 2+ windows without a concrete new thing
          doc 31 retention clock: something genuinely new every 15-30s
  [PASS ] V03 open loop live in 6/7 windows (86%)
          open-loop coverage floor 50% (doc 31)
  [INFO ] V04 nothing the reader could not follow
          comprehension outranks structure (STRENGTH-LOOP precedence); window-cut artifacts excluded
  [INFO ] V05 gain per window: median 3, 0 dead of 7 reported
          a new thing is CONCRETE when it carries a numeral, or a capitalised name, or a word this window introduced that the memory did not already hold - crude on purpose, and constant-cited

RESULT: 1 FAIL / 0 WARN / 2 PASS / 2 INFO
```

## Beat recall — did the blind reader feel what the writer declared?

| beat | window | perceived | the reader's line |
|---|---|---|---|
| `[ring]` | w0 | **NO** | — |
| `[rehook]` | w2 | yes | A missed handoff makes someone inspect the output, repair it, and run … |
| `[stakes]` | w2 | **NO** | — |
| `[new]` | w2 | yes | Each step is assumed to succeed independently 95 percent of the time. |
| `[new]` | w2 | yes | The example allows no retries or recovery. |
| `[rehook]` | w3 | yes | The example job has twenty required steps. |
| `[catalyst]` | w4 | yes | A small improvement at each step can let many more jobs finish cleanly… |
| `[rehook]` | w5 | yes | A stronger frontier model might reduce the need for human supervision … |
| `[reflect]` | w5 | yes | If reliability matters most, a slower frontier model could still make … |

## Per window

| w | span | gain | holding a question | could not follow |
|---|---|---|---|---|
| 0 | 0:00-0:15 | 4 | Why would slowing the AI frontier create that economic… | — |
| 1 | 0:15-0:30 | 3 | Will the handoff actually finish the work, or just lea… | — |
| 2 | 0:30-0:45 | 4 | How likely is the whole twenty-step job to finish succ… | — |
| 3 | 0:45-1:00 | 3 | — | — |
| 4 | 1:00-1:15 | 3 | How do memory and tools fit into improving this proces… | — |
| 5 | 1:15-1:30 | 3 | Can a stronger frontier model save the same human hour… | — |
| 6 | 1:30-1:45 | 3 | How should AI be judged if not by how clever its demos… | — |

Concreteness rule: a new thing is CONCRETE when it carries a numeral, or a capitalised name, or a word this window introduced that the memory did not already hold - crude on purpose, and constant-cited.
