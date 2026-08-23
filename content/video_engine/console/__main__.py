"""Console entrypoint.

Binds loopback only. The console has no authentication because it is never
exposed; making that a default rather than a flag keeps it true.
"""

from __future__ import annotations

import argparse

import uvicorn

from content.video_engine.console.app import DEFAULT_HOST, DEFAULT_PORT, create_app
from content.video_engine.console.settings import load_settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m content.video_engine.console")
    parser.add_argument("--project-root", default=None, help="Project directory holding asset-catalog.v1.json")
    parser.add_argument("--catalog", default=None, help="Catalogue file, overriding --project-root")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)

    settings = load_settings(project_root=args.project_root, catalog_path=args.catalog)
    if settings.catalog_path is not None:
        print(f"catalogue: {settings.catalog_path}")
    else:
        print("no catalogue configured; pass --project-root or --catalog")

    print(f"console: http://{DEFAULT_HOST}:{args.port}/catalog")
    uvicorn.run(create_app(settings), host=DEFAULT_HOST, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
