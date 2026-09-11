"""The AUTHORING KIT (P51 T0) - one door both formats write their shot table through.

An episode's build script owns every episode fact: its rows, its anchors, its crops, its cue
files, its ids. The kit owns the *mechanism* those facts are poured into - the take's clock, the
dock registrations, the audio stitch and bed envelope, the shot-table hand-off to the compiler.

    from authoring import Project
    from authoring import words as W, docks as D, audio as A, table as T

`scripts/` is already on `sys.path` in every build script, so the bare package import works.

THE RULE: nothing in this package names an episode. No episode id, no crop, no quote, no file
name, no absolute path. If a value belongs to one short, it belongs in that short's build script
and arrives here as an argument.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import audio, docks, table, words

__all__ = ["Project", "audio", "docks", "table", "words"]


@dataclass(frozen=True)
class Project:
    """The paths and names every build script already had at the top of its file.

    here         the episode directory (the build script's own parent)
    build        the build directory (an env var picks a side build; the episode reads it)
    take         the take's audio directory, holding ``<take_stem>.words.json`` / ``<take_stem>.mp3``
    take_stem    the take file stem - one take may have several candidate cuts
    script_name  the script file's name, written into ``timeline.json``
    episode_id   the episode id, written into ``timeline.json`` and the compiled timeline
    take_name    the take's name as the timeline records it (the take directory, not the file)
    """

    here: Path
    build: Path
    take: Path
    take_stem: str
    script_name: str
    episode_id: str
    take_name: str = "vo-short"

    @property
    def audio_master(self) -> Path:
        """The build's own copy of the take - the stream every clock is measured against."""
        return self.build / "audio/episode.mp3"

    def mkdirs(self) -> None:
        self.build.mkdir(exist_ok=True)
        (self.build / "audio").mkdir(exist_ok=True)
