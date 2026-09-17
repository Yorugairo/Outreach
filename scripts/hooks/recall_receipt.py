"""The RECALL RECEIPT (operator, 2026-09-08): a commit that changes a MECHANISM must cite the record it integrates.

    "how come you just now found all of that research/doc information? the whole point of making this information
     retrieval cheap and easy was to get you to use it. How do we gate for that or make it part of your standardized
     processes?"

The gate is a receipt, not a reminder. When a commit touches the player template, the kinetics, the timeline compiler or
a short's shot table, its message must carry at least one `Recall:` line naming a path in the record (a docs/ file, a
research blueprint, a ruling) that EXISTS - the docs_find hit the change was designed from - or the explicit
`Recall: docs_find 0 hits for <term>` when the record truly has nothing. A commit with neither is refused.

P67 T3 (2026-09-16) widened it three ways, backward compatibly:
  * the mechanism list gained the caption builder and the authoring kit - the caption fix of that morning changed how
    every caption page is built and this hook printed "no mechanism touched";
  * a line may be staged, `Recall(<stage>): ...`, the grammar the BUILD receipt uses (`recall_verify.py`), so a commit
    citing in P67's own form is not refused by the hook that ships it;
  * a line that carries a QUOTED SPAN - `<path>:<line> "<verbatim span>"` - is re-read off disk through
    `recall_verify` (citation is not grounding: a path:line proves nothing). A line with NO span keeps the
    path-exists check and passes; spans are mandatory in the BUILD receipt, not here. If `recall_verify` cannot be
    imported the hook says so on one line and falls back - it never blocks a commit on its own plumbing.

Install (the operator's call - a standing process change):
    commit-msg hook:  python scripts/hooks/recall_receipt.py "$1"        (the message file)
    or by hand:       python scripts/hooks/recall_receipt.py --message "<msg>" --staged

Exit 0 = pass, 1 = refused (the reason is printed), 2 = usage.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

#: The checkout this hook lives in. `.git/hooks` is shared by every worktree, so `commit-msg` resolves the MAIN
#: checkout and runs THIS file from it; `recall_verify` is loaded the same way, off the same root.
HOOK_ROOT = Path(__file__).resolve().parents[2]
REPO = HOOK_ROOT
VERIFY_REL = "content/video_engine/scripts/recall_verify.py"
MECHANISM_PATHS = (
    "docs/content-video-engine/samples/scene-evidence-player.template.html",
    "content/video_engine/scripts/kinetics/",
    "content/video_engine/scripts/build_scene_timeline_f.py",
    "content/video_engine/scripts/gate_motion_density.py",
    "content/video_engine/scripts/build_caption_pages.py",
    "content/video_engine/scripts/authoring/",
)
MECHANISM_GLOBS = ("build_short.py", "build_scene_timeline")
#: Both forms: the 2026-09-08 `Recall: ...` and the staged `Recall(<stage>): ...`. The body is what follows the colon.
RECALL_RE = re.compile(r"^\s*Recall(?:\(\s*(?P<stage>[A-Za-z_]+)\s*\))?\s*:\s*(?P<body>.+?)\s*$", re.M)
ZERO_RE = re.compile(r"docs_find\s+0\s+hits?\s+for\s+\S+", re.I)


def staged_paths() -> list[str]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=REPO, capture_output=True, text=True)
    return [p.strip() for p in out.stdout.splitlines() if p.strip()]


def touches_mechanism(paths: list[str]) -> list[str]:
    hit = []
    for p in paths:
        q = p.replace("\\", "/")
        if any(q.startswith(m) or q == m for m in MECHANISM_PATHS) or any(g in q for g in MECHANISM_GLOBS):
            hit.append(q)
    return hit


def _load_verifier():
    """`recall_verify` off the checkout this hook was run from. Raises - the caller turns that into a notice."""
    path = Path(REPO) / VERIFY_REL
    if not path.is_file():
        path = HOOK_ROOT / VERIFY_REL
    spec = importlib.util.spec_from_file_location("recall_verify_for_hook", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"no import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # the verifier's dataclasses look their own module up while it executes
    spec.loader.exec_module(module)
    return module


def span_verdict(body: str) -> tuple[str, str]:
    """One `Recall` body against the record. Returns (verdict, text).

    "ok" the quoted span is on the cited line; "refused" it is not (the text names the line, and where the span
    actually is); "nospan" the line quotes no span - the caller keeps the path-exists check; "unavailable"
    `recall_verify` did not load - the text is the one notice line and the caller falls back.
    """
    try:
        verifier = _load_verifier()
    except Exception as exc:  # plumbing, never the author's fault: named once, never a refusal
        return "unavailable", f"note: span check skipped - {VERIFY_REL} did not load ({exc}); path-exists check only"
    citation = verifier._parse_line(None, body, body, 0)
    if citation.kind != "cite" or citation.span is None:
        return "nospan", ""
    why = verifier._check_citation(Path(REPO), citation)
    return ("refused", why) if why else ("ok", "")


def check(message: str, paths: list[str]) -> tuple[bool, str]:
    mech = touches_mechanism(paths)
    if not mech:
        return True, "no mechanism touched"
    recalls = [(m.group("stage"), m.group("body")) for m in RECALL_RE.finditer(message)]
    if not recalls:
        return False, ("REFUSED: this commit changes a mechanism (" + ", ".join(mech[:3]) + (", ..." if len(mech) > 3 else "")
                       + ") and carries no `Recall:` line. Run docs_find on the mechanism's nouns first and cite the hit "
                         "(`Recall: <path>:<line>`), or state `Recall: docs_find 0 hits for <term>`.")
    notices: list[str] = []

    def said(text: str) -> str:
        """The refusal or the pass, under any plumbing notice this run had to print."""
        return "".join(n + "\n" for n in notices) + text

    verified = 0
    for stage, r in recalls:
        label = f"Recall({stage}): {r}" if stage else f"Recall: {r}"
        if ZERO_RE.search(r):
            continue
        if '"' in r:
            verdict, text = span_verdict(r)
            if verdict == "refused":
                return False, said(f"REFUSED: `{label}` - {text}")
            if verdict == "ok":
                verified += 1
                continue
            if verdict == "unavailable" and text not in notices:
                notices.append(text)
        path = r.split(":")[0].strip().strip("`")
        if (Path(REPO) / path).exists():
            continue
        return False, said(f"REFUSED: `{label}` names a path that does not exist in the record: {path}")
    span = f", {verified} span(s) re-read off disk" if verified else ""
    return True, said(f"receipt ok: {len(recalls)} recall line(s) for {len(mech)} mechanism path(s){span}")


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--message":
        message = argv[1]
        paths = staged_paths() if "--staged" in argv else [a for a in argv[2:] if a != "--staged"]
    else:
        message = Path(argv[0]).read_text(encoding="utf-8")
        paths = staged_paths()
    ok, why = check(message, paths)
    print(why)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
