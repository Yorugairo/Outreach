# CHANGE REPORT - tokyo-tea-break/build-short-t6 - 2026-09-11

before: the build re-compiled with no sidecar (the agent's authored rows)
after: the build as it stands (overrides.json, 3 key(s))
timeline: tokyo-short.timeline.json - aspect 9:16 - runtime 88.8 s

## 1. The sidecar, field by field

- s02.camera: {"keys": [], "attention": "landings"} -> null [added]
- s04.dock.dock-k-pledge-record.centre_y: 0.335 -> 0.3 [added]
- s04.species.3.at: 50.3 -> 55.31 ("pledged") [added]

## 2. The instants each key touches, before and after

(the determinism check's own diff of the two compiled timelines names these; instants are deduped to 1/50 s, so one reason stands for every key that moved at the same instant)

### s02.camera - 2 instant(s)

| t | why | before | after | pair |
|---|---|---|---|---|
| 1.99 | s02 scene changed | change-report/s02.camera-1.99-before.png | change-report/s02.camera-1.99-after.png | change-report/s02.camera-1.99-pair.png |
| 38.96 | s02 span end | change-report/s02.camera-38.96-before.png | change-report/s02.camera-38.96-after.png | change-report/s02.camera-38.96-pair.png |

### s04.dock.dock-k-pledge-record - 2 instant(s)

| t | why | before | after | pair |
|---|---|---|---|---|
| 55.31 | s04 dock dock-k-pledge-record enter | change-report/s04.dock.dock-k-pledge-record-55.31-before.png | change-report/s04.dock.dock-k-pledge-record-55.31-after.png | change-report/s04.dock.dock-k-pledge-record-55.31-pair.png |
| 59.57 | s04 dock dock-k-pledge-record exit | change-report/s04.dock.dock-k-pledge-record-59.57-before.png | change-report/s04.dock.dock-k-pledge-record-59.57-after.png | change-report/s04.dock.dock-k-pledge-record-59.57-pair.png |

### s04.species.3 - 1 instant(s)

| t | why | before | after | pair |
|---|---|---|---|---|
| 56.71 | s04 species chart_to | change-report/s04.species.3-56.71-before.png | change-report/s04.species.3-56.71-after.png | change-report/s04.species.3-56.71-pair.png |

## 3. The gate delta (M01-M26, before -> after)

- M23: PASS -> PASS, the reading moved - before: 6 transition(s), each on a built chart and clear of its page's edge: s02 rescale 0:21+1.4s, s02 park 0:36+0.9s, s04 park 0:54+0.9s, s04 recast 0:50+1.4s, s04 recast 0:56+0.5s, s04 park 0:59+0.9s - after: 6 transition(s), each on a built chart and clear of its page's edge: s02 rescale 0:21+1.4s, s02 park 0:36+0.9s, s04 park 0:54+0.9s, s04 recast 0:55+1.4s, s04 recast 0:56+0.5s, s04 park 0:59+0.9s
- M24: PASS -> PASS, the reading moved - before: 3 pointing species on moving-camera scenes, every target in frame when it fires - after: 0 pointing species on moving-camera scenes, every target in frame when it fires
- M25: PASS -> PASS, the reading moved - before: no settled card on the chart's data, on a line of the page's ink or in the caption strip over 61 instants probed; smallest type read 11.6 CSS px on a phone (floor 11) | INFO, listed not scored (CSS px on a phone): sourc... - after: no settled card on the chart's data, on a line of the page's ink or in the caption strip over 59 instants probed; smallest type read 11.6 CSS px on a phone (floor 11) | INFO, listed not scored (CSS px on a phone): sourc...
- M26: PASS -> PASS, the reading moved - before: 41 printed value(s) over 61 instants probed agree with the height drawn on the scale the page prints (band 4% of the top tick + the burst's 5% overshoot); worst 2.9% of the top tick - May at 0:56 - after: 21 printed value(s) over 59 instants probed agree with the height drawn on the scale the page prints (band 4% of the top tick + the burst's 5% overshoot); worst 0.3% of the top tick - 5% at 1:16

20 row(s) unchanged.

## 4. The determinism check on the after build, at the changed instants

| t | why | warm vs cold |
|---|---|---|
| 1.99 | s02 scene changed | ok |
| 38.96 | s02 span end | ok |
| 55.31 | s04 dock dock-k-pledge-record enter | MISMATCH |
| 56.71 | s04 species chart_to | ok |
| 59.57 | s04 dock dock-k-pledge-record exit | MISMATCH |

verdict: mismatch at 55.31, 59.57

## 5. Verdict

3 field(s) changed on 3 row(s); 5 instant(s); gate delta: M23, M24, M25, M26; determinism: mismatch at 55.31, 59.57
