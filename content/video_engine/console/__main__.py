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
    parser.add_argument(
        "--with-editor", action="store_true",
        help="start Remotion Studio alongside the console and stop it on exit",
    )
    args = parser.parse_args(argv)

    settings = load_settings(project_root=args.project_root, catalog_path=args.catalog)
    if settings.catalog_path is not None:
        print(f"catalogue: {settings.catalog_path}")
    else:
        print("no catalogue configured; pass --project-root or --catalog")

    # Studio rides along only when asked; a dead editor never takes the review
    # surface down with it, so its startup failure is reported and we serve on.
    studio_started = False
    if args.with_editor:
        from content.video_engine.src.services import editor_studio
        from content.video_engine.src.services.editor_studio import EditorStudioError

        try:
            state = editor_studio.start()
            studio_started = True
            print(f"studio: {state.get('state')} (pid {state.get('pid')}, port {state.get('port')})")
        except EditorStudioError as exc:
            for error in exc.errors:
                print(f"studio failed to start: {error}")

    print(f"console: http://{DEFAULT_HOST}:{args.port}/catalog")
    try:
        uvicorn.run(create_app(settings), host=DEFAULT_HOST, port=args.port, log_level="warning")
    except KeyboardInterrupt:
        pass
    finally:
        if studio_started:
            from content.video_engine.src.services import editor_studio

            try:
                editor_studio.stop()
                print("studio: stopped")
            except Exception as exc:  # a survivor is reported, never swallowed
                print(f"studio stop failed: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
