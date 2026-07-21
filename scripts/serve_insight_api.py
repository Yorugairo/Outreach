from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the SEO Insights API and operator dashboard")
    parser.add_argument("--host", default=os.getenv("SEO_INSIGHTS_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("SEO_INSIGHTS_PORT", "8765")))
    parser.add_argument("--reload", action="store_true", help="development only")
    args = parser.parse_args()

    if not os.getenv("SEO_INSIGHTS_API_KEY"):
        parser.error("SEO_INSIGHTS_API_KEY must be set before starting the server")

    uvicorn.run(
        "src.api.app:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload,
        proxy_headers=True,
        forwarded_allow_ips=os.getenv("SEO_INSIGHTS_FORWARDED_ALLOW_IPS", "127.0.0.1"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
