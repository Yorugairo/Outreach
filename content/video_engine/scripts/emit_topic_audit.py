"""Emit TOPIC-EXIT-AUDIT.md - the E12 enumeration (runs after EVERY
retime: the warp preserves durations while topics move)."""
import importlib.util, json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"

sp = importlib.util.spec_from_file_location("shot", EP / "SHOT-TABLE-F.py")
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
tl = json.loads((EP / "build-f/timeline.json").read_text(encoding="utf-8"))
rows = sorted(m.W, key=lambda r: r[0])
out = ["# TOPIC-EXIT AUDIT (E12 enumeration) - every dock vs its narration", ""]
n = 0
for r in rows:
    for d in r[4]:
        n += 1
        out.append(f"## [{n}] {d[0]}  slot{d[1]}  {d[2]:.1f}-{d[3]:.1f}  "
                   f"(plate {r[2]} {r[0]:.1f}-{r[1]:.1f})")
        for s2 in tl["sentences"]:
            if d[2] - 6 <= s2["start"] <= d[3] + 12:
                mark = ("  IN " if d[2] <= s2["start"] < d[3]
                        else ("  pre" if s2["start"] < d[2] else "  POST"))
                out.append(f"{mark} {s2['start']:6.1f}  {s2['text'][:95]}")
        out.append("")
(EP / "build-f/TOPIC-EXIT-AUDIT.md").write_text("\n".join(out),
                                                encoding="utf-8")
print(f"{n} docks enumerated -> build-f/TOPIC-EXIT-AUDIT.md")
