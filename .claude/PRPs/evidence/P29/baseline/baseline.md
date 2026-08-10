# P29 Remotion Baseline

Recorded: 2026-08-10

## Environment

- Git base: `f70a502ef8260a6f64535ba5559fe724d2096722`
- Branch: `codex/p29-remotion-production-console`
- OS: Windows (`win32`)
- Host: CyberPowerPC GamingPC
- CPU: 13th Gen Intel Core i9-13900KF, 24 cores / 32 logical processors
- Memory: 68,523,470,848 bytes
- Node: `v24.16.0`
- npm: `11.13.0`
- Python: `3.11.15`
- Remotion: exact package parity at `4.0.502`

## Dependency and composition checks

- `npm ci`: passed; 256 packages installed.
- npm audit summary: three existing high-severity advisories. No automatic
  dependency upgrade was performed because P29 pins Remotion and disallows an
  unplanned upgrade.
- `npm run typecheck`: passed.
- `npx remotion versions`: all Remotion packages have the correct version.
- `npx remotion compositions src/index.tsx`: passed; six compositions listed.
- Baseline defect confirmed: `EditorialMotion` is registered to
  `DocumentaryMotionComposition` despite the dedicated component export.

## Fixed render

Command:

```powershell
npx remotion render src/index.tsx EditorialMotion `
  .claude/PRPs/evidence/P29/baseline/editorial-motion-baseline.mp4 `
  --frames=0-59 --scale=0.25 --codec=h264 --log=verbose
```

- Output: `editorial-motion-baseline.mp4`
- Output size: 87.2 kB
- Resolution: 480x270
- Frames: 60 at 30 fps
- Concurrency: 8
- Measured shell wall time: 3.480 seconds
- Remotion frame-render phase: 0.766 seconds
- Slowest frame: frame 3 at 263 ms; next slowest 17 ms

## Concurrency benchmark

Command:

```powershell
npx remotion benchmark src/index.tsx EditorialMotion `
  --runs=1 --concurrencies=1,4,8 --frames=0-59 --scale=0.25 `
  --codec=h264 --log=info
```

Results for the fixed 60-frame low-resolution baseline:

| Concurrency | Time |
| ---: | ---: |
| 1 | 3.82121 s |
| 4 | 1.19331 s |
| 8 | 0.83799 s |

These one-run measurements establish inputs and an initial direction only.
P29 T10 requires at least three comparable before/after runs before claiming a
performance improvement.
