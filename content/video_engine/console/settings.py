"""Where the console reads from.

The console owns no data. Every path here points at an artifact the CLI already
produces, so the two surfaces cannot drift apart: change the file on disk and both
see the change.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

#: Environment variable naming the project whose catalogue is served.
PROJECT_ROOT_ENV = "VIDEO_ENGINE_PROJECT_ROOT"
#: Environment variable naming the catalogue file directly, overriding the above.
CATALOG_ENV = "VIDEO_ENGINE_CATALOG"

CATALOG_FILENAME = "asset-catalog.v1.json"


@dataclass(frozen=True)
class ConsoleSettings:
    """Resolved, immutable console configuration."""

    project_root: Path | None
    catalog_path: Path | None

    @property
    def is_configured(self) -> bool:
        return self.catalog_path is not None


def load_settings(
    *,
    project_root: str | Path | None = None,
    catalog_path: str | Path | None = None,
    env: dict[str, str] | None = None,
) -> ConsoleSettings:
    """Resolve settings from explicit arguments, then the environment.

    Returns an unconfigured instance rather than raising. A console that cannot
    find a catalogue should render an empty state explaining how to point it at
    one, not refuse to start.
    """

    source = os.environ if env is None else env

    root = project_root if project_root is not None else source.get(PROJECT_ROOT_ENV)
    explicit = catalog_path if catalog_path is not None else source.get(CATALOG_ENV)

    resolved_root = Path(root).expanduser() if root else None
    if explicit:
        resolved_catalog: Path | None = Path(explicit).expanduser()
    elif resolved_root is not None:
        resolved_catalog = resolved_root / CATALOG_FILENAME
    else:
        resolved_catalog = None

    return ConsoleSettings(project_root=resolved_root, catalog_path=resolved_catalog)
