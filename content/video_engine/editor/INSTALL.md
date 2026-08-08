# Editor Install Contract (Remotion)

*Verified 2026-08-08 on Windows 11, Node v24.16.0.*

- All Remotion packages pinned **exactly** at `4.0.502` (`remotion`, `@remotion/cli`,
  `@remotion/media`, `@remotion/transitions`). Every `@remotion/*` package MUST share one exact
  version — mixed versions fail cryptically.
- TypeScript `5.7.3`, React `18.3.1`.

## Commands

```bash
npm ci                 # 256 packages, ~6s
npm run typecheck      # tsc --noEmit — 0 errors required
npm run render:smoke   # Documentary comp, frames 0-30 -> out/smoke.mp4
```

Smoke verification (2026-08-08): `out/smoke.mp4` — duration 1.088s, 70,685 bytes, exit 0.
First render downloads Chrome Headless Shell into the local cache; later renders are fast.

Compositions (`src/Root.tsx`): `Editorial` (default manifest is 1 frame — not a smoke target),
`Documentary` (60-frame default treatment — the smoke target), `EditorialMotion`.

CLI verification wrapper: `python content/video_engine/cli.py verify-editor [--smoke]`.
