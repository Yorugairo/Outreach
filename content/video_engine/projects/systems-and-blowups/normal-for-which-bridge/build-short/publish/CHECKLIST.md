# Publish checklist - Normal For Which Bridge (Money Physics) - `build-short`

9:16 - 1:10 - every step below is a HUMAN's. The package is written from the build's own artifacts; scheduling and API posting are out of scope (R26-8).

**The master:** NOT RENDERED YET - `RENDER_ASPECT=9:16 python content/video_engine/scripts/render_episode.py` (the existing path; one master, no second size) - ONE file serves YouTube, Facebook and Instagram (R26-8: the platform assigns the better codec at 1440p+ and the same upload travels). Never render a per-platform size.

- [ ] 1. Upload the master to the channel: the title from `DESCRIPTION-YOUTUBE.md` (`## Title`), the description from its paste block.
- [ ] 2. Upload the thumbnail (`thumbnail.png` here when the build carries one). `first-frame.png` is what the platform would pick on its own - it is evidence, not a thumbnail.
- [ ] 3. Set the keywords from `TAGS.txt`, the playlist, the audience ('not made for kids') and the language.
- [ ] 4. Publish, or set the schedule yourself - this tool never schedules and never posts (R26-8 draws the line there).
- [ ] 5. Post `PINNED-COMMENT.md` as a comment and pin it. A Short's links are not clickable, so the URL rides as text.
- [ ] 6. Facebook and Instagram: the SAME master file, the caption from `DESCRIPTION-FACEBOOK.md`, and the link as the FIRST COMMENT (`## First comment`).
- [ ] 7. Read the description once against the episode's hand-written one, if it has one, and against the dossier: this package copies figures, it does not check them.

**In this folder:** `DESCRIPTION-YOUTUBE.md`, `DESCRIPTION-FACEBOOK.md`, `PINNED-COMMENT.md`, `SOURCES.md`, `TAGS.txt`, `MANIFEST.json`, `first-frame.png`.

**Not on disk when this was written** (the package is thinner for it):
- the evidence dossier (EVIDENCE-DOSSIER.md)
- the fetched sources' links (evidence/sources/*)
- the 1440p master (render/)
- the thumbnail (*thumb*.png)
