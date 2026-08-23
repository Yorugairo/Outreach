# Current-bubble editor benchmark

Measured locally against snapshot
`9de69ca8035a0a574c763d392ee89f93a14f68231c0fc2faa6e9ec55d3948242`.

- Episode: 29,425 frames at 30 fps (980.806-second canonical audio; 980.833
  frame-rounded composition duration).
- Snapshot: 8 tracks, 1,182 timeline items, 137 assets (95 approved,
  including 9 context-preserving semantic evidence crops), and 2,445 words.
- Five snapshot compiles: 733.58, 727.67, 725.23, 737.15, and 743.52 ms;
  median 733.58 ms.
- Browser fixture: 1,180 rendered timeline blocks, 5,717 DOM nodes, and 27.5 MB
  used JS heap at rest in headless Chrome.
- Browser proof successfully performed frame seek, scene trim, five inserts,
  inspector edits, keyframes, save, reload, and draft recovery on the complete
  episode.
- `frameupdate` mutates only the playhead position through
  `requestAnimationFrame`; React editor state changes on explicit seek/pause,
  avoiding full-editor rerenders for every playback frame.

These measurements are a local regression baseline, not a cross-device SLA.
