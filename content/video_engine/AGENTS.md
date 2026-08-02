# Content Video Engine

- Treat `storyboard.json` as immutable after Gate A; measured timing belongs in artifacts.
- Audio is the render clock. Never stretch or trim narration to fit video.
- Keep provider keys in environment variables and fail before a paid call when configuration
  is incomplete.
- Gate A and Gate B are operator actions. Tests may simulate them; product code may not
  auto-approve them.
- All stages are deterministic and idempotent from persisted inputs. Record failures and
  degraded behavior in stage events.
- Runtime output belongs under `runtime/jobs/` and is never hand-edited.
