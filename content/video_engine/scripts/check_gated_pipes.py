"""A gated step piped into tail/head must not lose its exit code (P54 G2 follow-up, 2026-09-13).

Why: twice the pipe ate the verdict. A join's drift gate FAILED behind `| tail` and the chain ran once on drifted
audio (C05-R016, exchange 4c335f4d4502); a test run piped through tail let a test file that did not parse reach
origin and showed only 3 of 59 failures (C09-R012, exchanges 2b90a363abd2, 97d50f8dae01). A pipeline's status is
its LAST stage's, so `pytest -q | tail -3 && git push` pushes on red.

    python check_gated_pipes.py [--root REPO]

Prints `path:line: <command>` per finding and exits 1 on any; prints `check_gated_pipes: PASS` and exits 0 otherwise.

The rule. A *chain* is one logical command line (continuations joined: a trailing backslash, a PowerShell backtick,
or a trailing `|`, `&&`, `||`), split on `&&`, `||`, `;` into commands and each command on `|` / `|&` into stages.
A *masked pipe* is a command in which a GATED stage (pytest, python -m pytest, npm test / npm run test, any
gate_*.py, verify_*.py, run_script_gates.py, or any `--check` flag, which covers build_docs_layers.py --check) is
followed by a later `tail`, `head`, or `Select-Object`/`select` with -Last/-First stage. It is a FINDING when its
exit code matters, which depends on where it lives:

- scripts - `*.sh`, `*.ps1`, `.githooks/*`, `package.json` scripts, and Python `subprocess.*` / `os.system` /
  `os.popen` string commands (list arguments are checked element by element): ALWAYS, because the script, npm or
  the Python caller reads the status.
- examples - fenced ```bash / sh / shell / zsh / powershell / pwsh / ps1 blocks in `docs/**/*.md`,
  `.agents/skills/**/SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`: only when `&&` follows the masked pipe in
  the same chain, or the fence runs `set -e` (then the fence is a script). The last command of a one-off example
  with no `&&` after it is allowed: a reader looks at its output and nothing runs on its status.

Exempt everywhere: `pipefail` is set (in a file or fence, on that chain or any earlier line; in a Python string or a
package.json script, in the same command text), or `PIPESTATUS` / `$LASTEXITCODE` is read in the chain or the next
two lines. A Python file that does not parse is skipped (parsing is another gate's job).
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GATED = re.compile(r"(?<![\w-])pytest(?![\w-])|\bnpm\s+(?:run\s+)?test\b|\bgate_\w*\.py\b|\bverify_\w*\.py\b"
                   r"|\brun_script_gates\.py\b|(?<!\S)--check\b")
SINK = re.compile(r"^\s*(?:tail|head)(?:\s|$)|^\s*(?:Select-Object|select)\b.*\s-(?:Last|First)\b", re.I)
PIPEFAIL = re.compile(r"\bpipefail\b")
EXEMPT = re.compile(r"PIPESTATUS|\$LASTEXITCODE", re.I)
SET_E = re.compile(r"^\s*set\s+-[a-z]*e")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*([\w-]*)")
SHELL_LANGS = {"bash", "sh", "shell", "zsh", "powershell", "pwsh", "ps1"}
PROMPT = re.compile(r"^\s*(?:\$|PS[^>]*>)\s+")
ROOT_DOCS = {"AGENTS.md", "CLAUDE.md", "GEMINI.md"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "worktrees"}
SUBPROCESS_FUNCS = {"run", "call", "check_call", "check_output", "Popen", "getoutput", "getstatusoutput"}


def logical_lines(lines: list[str], ps: bool = False):
    """Yield (start, end, text) per logical command line, 1-based, continuations joined."""
    buf: list[str] = []
    start = 0
    for n, raw in enumerate(lines, 1):
        s = PROMPT.sub("", raw.rstrip()) if not buf else raw.rstrip()
        if not buf and s.lstrip().startswith("#"):
            continue
        start = start or n
        cont = s.endswith("\\") or (ps and s.endswith("`"))
        buf.append(s[:-1] if cont else s)
        if cont or re.search(r"(?:\|\||&&|\|)\s*$", s):
            continue
        yield start, n, " ".join(buf)
        buf, start = [], 0
    if buf:
        yield start, len(lines), " ".join(buf)


def masked(chain: str) -> tuple[bool, bool]:
    """(a command pipes a gated stage into tail/head, `&&` follows that command)."""
    parts = re.split(r"(&&|\|\||;)", chain)
    for i in range(0, len(parts), 2):
        stages = re.split(r"\|&?", parts[i])
        gated = next((k for k, st in enumerate(stages) if GATED.search(st)), None)
        if gated is not None and any(SINK.search(st) for st in stages[gated + 1:]):
            return True, "&&" in parts[i + 1::2]
    return False, False


def scan_lines(lines: list[str], *, script: bool, ps: bool = False, base: int = 0) -> list[tuple[int, str]]:
    """Findings in a run of shell lines; `script` means the status always matters, else only before `&&`."""
    out: list[tuple[int, str]] = []
    pipefail = False
    for start, end, chain in logical_lines(lines, ps):
        pipefail = pipefail or bool(PIPEFAIL.search(chain))
        script = script or bool(SET_E.search(chain))
        hit, follows = masked(chain)
        if not hit or pipefail or EXEMPT.search(chain + " " + " ".join(lines[end:end + 2])):
            continue
        if script or follows:
            out.append((base + start, chain.strip()))
    return out


def scan_markdown(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        mark, lang = m.group(1), m.group(2).lower()
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith(mark):
            j += 1
        if lang in SHELL_LANGS:
            out += scan_lines(lines[i + 1:j], script=False, ps=lang in {"powershell", "pwsh", "ps1"}, base=i + 1)
        i = j + 1
    return out


def _call_strings(node: ast.Call) -> list[str]:
    func = node.func
    if not isinstance(func, ast.Attribute) or not isinstance(func.value, ast.Name):
        return []
    owner, name = func.value.id, func.attr
    if not ((owner in {"subprocess", "sp"} and name in SUBPROCESS_FUNCS) or (owner == "os" and name in {"system", "popen"})):
        return []
    args = list(node.args[:1]) + [k.value for k in node.keywords if k.arg == "args"]
    items = [e for a in args for e in (a.elts if isinstance(a, (ast.List, ast.Tuple)) else [a])]
    strings = []
    for e in items:
        if isinstance(e, ast.Constant) and isinstance(e.value, str):
            strings.append(e.value)
        elif isinstance(e, ast.JoinedStr):
            strings.append("".join(v.value if isinstance(v, ast.Constant) else "{}" for v in e.values))
    return strings


def scan_python(text: str) -> list[tuple[int, str]]:
    if "|" not in text or not re.search(r"\bsubprocess\b|\bos\.(?:system|popen)\b", text):
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for s in _call_strings(node):
                out += [(node.lineno, c) for _, c in scan_lines([s.replace("\n", " ")], script=True)]
    return out


def scan_package_json(text: str) -> list[tuple[int, str]]:
    try:
        scripts = json.loads(text).get("scripts") or {}
    except (json.JSONDecodeError, AttributeError):
        return []
    lines = text.splitlines()
    out = []
    for name, cmd in scripts.items():
        if not isinstance(cmd, str):
            continue
        line = next((n for n, ln in enumerate(lines, 1) if f'"{name}"' in ln), 1)
        out += [(line, c) for _, c in scan_lines([cmd], script=True)]
    return out


def classify(rel: str) -> str:
    name = rel.rsplit("/", 1)[-1]
    if rel.endswith(".sh") or rel.startswith(".githooks/"):
        return "sh"
    if rel.endswith(".ps1"):
        return "ps1"
    if name == "package.json":
        return "package"
    if rel.endswith(".py"):
        return "py"
    if rel in ROOT_DOCS or (rel.startswith("docs/") and rel.endswith(".md")) or \
            (rel.startswith(".agents/skills/") and name == "SKILL.md"):
        return "md"
    return ""


def repo_files(root: Path) -> list[str]:
    if (root / ".git").exists():
        r = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode == 0:
            return sorted({ln.strip() for ln in r.stdout.splitlines() if ln.strip()})
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*")
                  if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(root).parts))


SCANNERS = {
    "sh": lambda t: scan_lines(t.splitlines(), script=True),
    "ps1": lambda t: scan_lines(t.splitlines(), script=True, ps=True),
    "package": scan_package_json,
    "py": scan_python,
    "md": scan_markdown,
}


def check(root: Path) -> list[str]:
    findings = []
    for rel in repo_files(root):
        kind = classify(rel)
        path = root / rel
        if not kind or not path.is_file() or "node_modules" in rel.split("/"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        findings += [f"{rel}:{line}: {cmd}" for line, cmd in SCANNERS[kind](text)]
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    findings = check(args.root.resolve())
    for f in findings:
        print(f)
    if findings:
        print(f"check_gated_pipes: FAIL ({len(findings)} masked gated pipe(s))")
        return 1
    print("check_gated_pipes: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
