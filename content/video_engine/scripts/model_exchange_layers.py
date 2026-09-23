"""CLI for the review-only 24 fps source exchange layer bridge."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content.video_engine.src.modeling.exchange_layers import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
