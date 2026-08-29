"""Create a compact still/contact-sheet review packet from the P33 render."""

from __future__ import annotations

import html
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
VIDEO = PROJECT / "six-minute-p32-evidence-demo-v1/render/current-bubble-six-minute-p33-first-five-review.mp4"
OBLIGATIONS = PROJECT / "edit/evidence-coverage-v1/p33-first-five-minute-evidence-obligation.v1.json"
OUTPUT = PROJECT / "edit/evidence-coverage-v1/p33-gate-b-review"
STILLS = (
    ("opening-wrong-bubble", 1.0, "Opening replacement: wrong bubble"),
    ("safe-index-card", 56.0, "#07: safe-index feedback + Paper Bubble Mechanics"),
    ("next-buyer-card", 67.0, "#08: next-buyer belief + Diagnostic Matrix"),
    ("two-elevator-card", 76.0, "#09: cable versus jumpers + Valuation Paradox"),
    ("strategic-agreements-card", 233.0, "#23: changed buyer behavior + contracted-memory evidence"),
)


def _extract(name: str, seconds: float) -> Path:
    destination = OUTPUT / f"{name}.png"
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{seconds:.3f}", "-i", str(VIDEO), "-frames:v", "1", str(destination)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return destination


def main() -> None:
    if not VIDEO.is_file():
        raise FileNotFoundError(VIDEO)
    if not OBLIGATIONS.is_file():
        raise FileNotFoundError(OBLIGATIONS)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    images = [(title, _extract(name, seconds).name) for name, seconds, title in STILLS]
    obligations = json.loads(OBLIGATIONS.read_text(encoding="utf-8"))["records"]
    cards = "".join(
        f'<article><img src="{html.escape(filename)}" alt="{html.escape(title)}"><h2>{html.escape(title)}</h2></article>'
        for title, filename in images
    )
    table_rows = "".join(
        f'<tr><td>{html.escape(record["asset_id"])}</td><td>{record["start_s"]:.1f}–{record["end_s"]:.1f}s</td><td>{html.escape(record["status"])}</td><td>{html.escape(", ".join(record["evidence_asset_ids"]) or "—")}</td></tr>'
        for record in obligations
    )
    (OUTPUT / "p33-first-five-minute-review.html").write_text(
        f'''<!doctype html><html><head><meta charset="utf-8"><title>P33 Gate B review</title><style>
body{{margin:0;background:#101318;color:#f4eee5;font:15px/1.45 system-ui,sans-serif}}main{{max-width:1440px;margin:auto;padding:28px}}h1{{margin:0}}p{{color:#c8d1d9}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px}}article{{background:#1b222b;border:1px solid #34404b;border-radius:10px;overflow:hidden}}img{{display:block;width:100%;aspect-ratio:16/9;object-fit:cover}}h2{{font-size:15px;padding:0 14px;margin:12px 0 16px}}table{{width:100%;border-collapse:collapse;margin-top:28px;background:#1b222b}}th,td{{padding:9px;border:1px solid #35414d;text-align:left;vertical-align:top;overflow-wrap:anywhere}}th{{background:#27323e}}.covered{{color:#a9e6b2}}.exempt{{color:#ffd792}}</style></head><body><main>
<h1>P33 · First-five-minute Gate B review</h1><p>World plate remains the hero. Each source is a complete teacher-stamped slide, enters one at a time for up to five seconds, and shares an eye-line with word-timed captions.</p><section class="grid">{cards}</section><h2>0–300s evidence obligation</h2><table><tr><th>World plate</th><th>Time</th><th>Status</th><th>Evidence</th></tr>{table_rows}</table></main></body></html>''',
        encoding="utf-8",
    )
    print(OUTPUT / "p33-first-five-minute-review.html")


if __name__ == "__main__":
    main()
