"""Japan Tariff Trick's review player - a thin wrapper on the SHARED server (P51 T4).

The server itself is `content/video_engine/scripts/serve_player.py` (no-store, Range/seek, .mjs as
text/javascript, and `--watch` for the hot-reload loop). This file keeps the CLI and the port the
project's runbooks and `.claude/launch.json` have always used:

    python serve_player.py [port] [build dir] [--watch] [--no-check]     # default 8731, this dir

The shared file is loaded BY PATH under another name: a plain `import serve_player` from a script
of the same name imports this wrapper a second time, not the server.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED = HERE.parents[2] / "scripts" / "serve_player.py"   # content/video_engine/scripts
sys.path.insert(0, str(SHARED.parent))
_spec = importlib.util.spec_from_file_location("review_server", SHARED)
S = importlib.util.module_from_spec(_spec)
sys.modules["review_server"] = S
_spec.loader.exec_module(S)

if __name__ == "__main__":
    raise SystemExit(S.legacy_main(HERE, 8731, "Japan Tariff Trick"))
