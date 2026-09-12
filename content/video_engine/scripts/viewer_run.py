"""The viewer's runner: one blind call per window, through Codex headless (P36 T2).

The viewer is the third role beside the gates and the judge - an agent that
knows NOTHING. This module is the thing that keeps it that way. It reads the
windows `viewer_windows.py` cut, and for each one it makes a single headless
call that can see only four things: the wording in
`content/video_engine/configs/viewer_prompt.v2.md`, the memory text of the
previous two windows, the words of this window, and the `[screen]` lines the
windower folded in for what is on screen while they are spoken (R26-0, ruling
E43 - the prompt says a `[screen]` line is what you can see). No doctrine, no
tags, no ledger, no dossier, no other window. If the viewer can see any of
those the test is void (P36 "Not Building").

WINDOW 0 IS THE PACKAGE (ruling E27: the package answered is the first thing
that matters). Before a single word of the script, the viewer is shown the
title and the thumbnail (`--thumb-file`, attached to the call as an image) and
asked one question - what were you promised? The first window of words then
additionally answers whether that promise was answered and by which sentence.
Without `--title` there is no package window; the run records the skip rather
than pretending (AGENTS.md s8: no silent skips).

The viewer is NEVER asked when it would drop off. An LLM's patience is not a
person's; it is asked only for perception reports it can give stably, and
`viewer_score.py` does the judging.

    python viewer_run.py <script.txt> [--lane codex] [--model <m>] [--effort high]
                         [--thumb-file <png>] [--title "<t>"] [--limit N]
                         [--dry-run] [--out <path>]

Writes `<script>-VIEWER-REPORTS.json` (`viewer_reports.v1`) beside the script,
in the shape `viewer_score.py` binds to. `--dry-run` renders every prompt into
the run directory and makes no call at all.

Isolation note: the headless calls run with `--cd` pointed at an EMPTY
directory outside this repository, so the agent cannot discover `AGENTS.md`,
the doctrine tree, or the rest of the script. Prompts and logs are kept beside
that sandbox, not inside it.

`render_prompt` and `parse_response` are pure and importable - they touch no
network and no disk, so the fixtures in T3 can exercise them offline.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# --- constants, cited ---------------------------------------------------------
SCHEMA_VERSION = "viewer_reports.v1"
WINDOWS_SCHEMA_VERSION = "viewer_windows.v1"
# v2 = v1 + the `[screen]` lines (P52 T14 / R26-0, ruling E43). The wording of a
# version is frozen; a change is a new file, and a run records which it sent.
PROMPT_VERSION = "v2"
DEFAULT_PROMPT = Path(__file__).resolve().parents[1] / "configs" / f"viewer_prompt.{PROMPT_VERSION}.md"
DEFAULT_LANE = "codex"
# P36 click 2026-09-03: the plates ran low effort because orchestration is
# mechanical; READING is not - the viewer runs high.
DEFAULT_EFFORT = "high"
# One malformed answer is a hiccup, two is the model. Retry once, then record
# the window as an error and carry on rather than losing the run (P36 T2).
MAX_ATTEMPTS = 2
CALL_TIMEOUT_S = 600.0
VO_SUFFIX = "-VO"
WINDOWS_SUFFIX = "-VIEWER-WINDOWS.json"
REPORTS_SUFFIX = "-VIEWER-REPORTS.json"
NO_MEMORY = "(nothing yet - this is the very start)"
BLOCK_RE = re.compile(r"<!--\s*BLOCK:\s*([a-z_]+)\s*-->\s*```[a-z]*\n(.*?)```", re.DOTALL)
REQUIRED_BLOCKS = ("package", "window", "window_one_extra")
WINDOW_KEYS = ("new_things", "held_question", "asked_of_me", "could_not_follow")


@dataclass(frozen=True)
class PromptCfg:
    """The wording of one prompt version, plus what the package call carries."""
    package: str
    window: str
    window_one_extra: str
    title: str = ""
    promised: str = ""
    version: str = PROMPT_VERSION


# --- pure: wording ------------------------------------------------------------
def load_prompt_blocks(path: Path) -> dict[str, str]:
    """Extract the fenced blocks the runner is allowed to send."""
    blocks = {name: body for name, body in BLOCK_RE.findall(path.read_text(encoding="utf-8"))}
    missing = [b for b in REQUIRED_BLOCKS if b not in blocks]
    if missing:
        raise ValueError(f"{path.name}: missing prompt block(s) {missing}")
    return blocks


def render_package_prompt(cfg: PromptCfg) -> str:
    """The WINDOW 0 call: the title and the thumbnail, one question (E27)."""
    return cfg.package.replace("{{TITLE}}", cfg.title).strip() + "\n"


def render_prompt(window: dict, memory: str | None, cfg: PromptCfg) -> str:
    """The per-window call. Pure: only this window's words and the memory text."""
    mem = (window.get("memory", "") if memory is None else memory).strip()
    text = (cfg.window
            .replace("{{SPAN}}", str(window.get("span", "")))
            .replace("{{MEMORY}}", mem or NO_MEMORY)
            .replace("{{WINDOW_TEXT}}", str(window.get("text", "")).strip()))
    if int(window.get("i", -1)) == 0 and cfg.promised:
        text = text.rstrip() + "\n" + cfg.window_one_extra.replace("{{PROMISED}}", cfg.promised)
    return text.strip() + "\n"


# --- pure: answers ------------------------------------------------------------
def _first_json_object(text: str) -> dict:
    dec = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = dec.raw_decode(text[i:])
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj
    raise ValueError("no JSON object in the response")


def parse_response(text: str, kind: str = "window") -> dict:
    """Strict-ish read of one answer. Raises ValueError so the caller can retry."""
    obj = _first_json_object(text or "")
    if kind == "package":
        promised = obj.get("promised")
        if not isinstance(promised, str) or not promised.strip():
            raise ValueError("package answer has no 'promised' string")
        return {"promised": promised.strip()}
    missing = [k for k in WINDOW_KEYS if k not in obj]
    if missing:
        raise ValueError(f"answer is missing key(s) {missing}")
    for k in ("new_things", "could_not_follow"):
        if not isinstance(obj[k], list) or any(not isinstance(v, str) for v in obj[k]):
            raise ValueError(f"'{k}' must be a list of strings")
    for k in ("held_question", "asked_of_me"):
        if not isinstance(obj[k], str):
            raise ValueError(f"'{k}' must be a string")
    out = {
        "new_things": [v.strip() for v in obj["new_things"] if v.strip()],
        "held_question": obj["held_question"].strip(),
        "asked_of_me": obj["asked_of_me"].strip(),
        "could_not_follow": [v.strip() for v in obj["could_not_follow"] if v.strip()],
    }
    for k in ("promise_answered", "answered_by"):
        if isinstance(obj.get(k), str):
            out[k] = obj[k].strip()
    return out


# --- the headless lane --------------------------------------------------------
def find_codex(explicit: str | None) -> str:
    """The CLI hides inside the ChatGPT Store app; memory `codex-fulfillment-flow`."""
    for cand in (explicit, os.environ.get("VIDEO_ENGINE_CODEX_BIN"), shutil.which("codex")):
        if cand and (Path(cand).exists() or shutil.which(cand)):
            return cand
    raise FileNotFoundError(
        "codex CLI not found. Pass --codex-bin, or set VIDEO_ENGINE_CODEX_BIN. "
        "It ships inside the ChatGPT desktop app: copy codex.exe, "
        "codex-code-mode-host.exe, codex-command-runner.exe and "
        "codex-windows-sandbox-setup.exe together out of "
        r"'C:\Program Files\WindowsApps\OpenAI.Codex_*_x64__*\app\resources'. "
        "See docs/runbooks/HEADLESS_CLAIM_RESUME.md.")


def codex_cmd(bin_: str, cwd: Path, prompt: str, model: str | None, effort: str,
              last_msg: Path, image: Path | None) -> list[str]:
    """The runbook's invocation: never interactive, approvals routed, cwd isolated."""
    cmd = [bin_, "exec", "--cd", str(cwd), "--skip-git-repo-check", "--approve-for-me"]
    # `-i/--image <FILE>...` is VARIADIC: anything after it is swallowed as another
    # file, including the positional PROMPT (caught live 2026-09-03: "No prompt
    # provided via stdin"). Emit it FIRST so the non-variadic `-c` closes the list.
    if image:
        cmd += ["-i", str(image)]
    cmd += ["-c", f'model_reasoning_effort="{effort}"', "-o", str(last_msg)]
    if model:
        cmd += ["-m", model]
    return cmd + [prompt]


def call_codex(cmd: list[str], log: Path, last_msg: Path, timeout: float) -> str:
    """One call. stdin from the null device, stdout+stderr to the window's log."""
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(os.devnull, "rb") as devnull, log.open("ab") as fh:
        fh.write(f"\n$ {' '.join(cmd[:-1])} <prompt>\n".encode("utf-8", "replace"))
        fh.flush()
        proc = subprocess.run(cmd, stdin=devnull, stdout=fh, stderr=subprocess.STDOUT,
                              timeout=timeout, check=False)
    if last_msg.exists() and last_msg.read_text(encoding="utf-8", errors="replace").strip():
        return last_msg.read_text(encoding="utf-8", errors="replace")
    tail = log.read_text(encoding="utf-8", errors="replace")[-8000:]
    if proc.returncode != 0:
        raise RuntimeError(f"codex exited {proc.returncode}; log {log}")
    return tail


def ask(prompt: str, kind: str, slug: str, rd: "RunDirs", opts: argparse.Namespace,
        bin_: str, image: Path | None) -> tuple[dict, str]:
    """Ask once, retry once on a malformed answer, then give up on this window."""
    (rd.prompts / f"{slug}.txt").write_text(prompt, encoding="utf-8")
    last_error, raw = "", ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        sandbox = rd.sandbox / f"{slug}-{attempt}"
        sandbox.mkdir(parents=True, exist_ok=True)
        last_msg = rd.last / f"{slug}-{attempt}.txt"
        last_msg.parent.mkdir(parents=True, exist_ok=True)
        cmd = codex_cmd(bin_, sandbox, prompt, opts.model, opts.effort, last_msg, image)
        try:
            raw = call_codex(cmd, rd.logs / f"{slug}.log", last_msg, opts.timeout)
            return parse_response(raw, kind), raw
        except (ValueError, RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            print(f"    attempt {attempt}/{MAX_ATTEMPTS} failed - {last_error}", file=sys.stderr)
    return {"error": last_error, "raw": raw[-2000:]}, raw


# --- io -----------------------------------------------------------------------
@dataclass(frozen=True)
class RunDirs:
    root: Path
    prompts: Path
    logs: Path
    last: Path
    sandbox: Path


def make_run_dirs(root: Path) -> RunDirs:
    rd = RunDirs(root, root / "prompts", root / "logs", root / "last", root / "sandbox")
    for p in (rd.root, rd.prompts, rd.logs, rd.last, rd.sandbox):
        p.mkdir(parents=True, exist_ok=True)
    return rd


def artifact_stem(script: Path) -> str:
    """`SCRIPT-G-VO.txt` -> `SCRIPT-G`, as viewer_windows/viewer_score name it."""
    # `-VO` may sit before an author marker (`SCRIPT-90S-VO.claude.txt`): strip it wherever it is, as
    # viewer_windows.py and run_script_gates.py do, or the gate runner folds in a stale report.
    return script.stem.replace(VO_SUFFIX, "")


def windows_path(script: Path) -> Path:
    stem = artifact_stem(script)
    for cand in (script.with_name(stem + WINDOWS_SUFFIX),
                 script.with_name(script.stem + WINDOWS_SUFFIX)):
        if cand.exists():
            return cand
    return script.with_name(stem + WINDOWS_SUFFIX)


def load_windows(script: Path, explicit: Path | None) -> dict:
    path = explicit or windows_path(script)
    if not path.exists():
        raise SystemExit(
            f"viewer_run: {path.name} not found beside the script.\n"
            f"  Create it first:\n"
            f"    python content/video_engine/scripts/viewer_windows.py {script} "
            f"[--timeline <build>/timeline.json]")
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema_version") != WINDOWS_SCHEMA_VERSION:
        raise SystemExit(f"viewer_run: {path.name} is not {WINDOWS_SCHEMA_VERSION}")
    return doc


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_reports(out: Path, doc: dict) -> None:
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --- the run ------------------------------------------------------------------
def run(opts: argparse.Namespace) -> int:
    doc = load_windows(opts.script, opts.windows)
    windows = list(doc.get("windows") or [])[: opts.limit] if opts.limit else list(doc.get("windows") or [])
    blocks = load_prompt_blocks(opts.prompt)
    cfg = PromptCfg(blocks["package"], blocks["window"], blocks["window_one_extra"],
                    title=opts.title or "", version=opts.prompt.stem.split(".")[-1])
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    rd = make_run_dirs(opts.run_dir or Path(tempfile.gettempdir()) / "viewer-runs"
                       / f"{artifact_stem(opts.script)}-{stamp}")
    out = opts.out or opts.script.with_name(artifact_stem(opts.script) + REPORTS_SUFFIX)
    thumb = Path(opts.thumb_file) if opts.thumb_file else None
    print(f"=== VIEWER RUN: {opts.script.name} ===")
    print(f"  windows : {len(windows)} of {len(doc.get('windows') or [])} "
          f"({doc.get('timing_source', '?')} timings, {doc.get('window_s')}s)")
    print(f"  prompt  : {opts.prompt.name} ({cfg.version})   lane {opts.lane}"
          f"   model {opts.model or '(codex default)'}   effort {opts.effort}")
    print(f"  run dir : {rd.root}")

    package = package_note(opts, thumb)
    report = {"schema_version": SCHEMA_VERSION, "prompt_version": cfg.version,
              "script": opts.script.name, "windows_file": (opts.windows or windows_path(opts.script)).name,
              "model": opts.model or "(codex default)", "effort": opts.effort, "lane": opts.lane,
              "started_at": now_iso(), "finished_at": "", "windows_run": 0,
              "package": package, "reports": []}

    if opts.dry_run:
        return dry_run(windows, cfg, rd, opts, package)
    bin_ = find_codex(opts.codex_bin)
    if cfg.title:
        print("  [package] title + thumbnail -> what were you promised?")
        ans, _ = ask(render_package_prompt(cfg), "package", "package", rd, opts, bin_, thumb)
        package.update(ans)
        package["status"] = "error" if "error" in ans else "asked"
        cfg = PromptCfg(cfg.package, cfg.window, cfg.window_one_extra, cfg.title,
                        ans.get("promised", ""), cfg.version)
    for w in windows:
        i = int(w.get("i", 0))
        print(f"  [{i:>3}] {w.get('span', '')}")
        ans, _ = ask(render_prompt(w, None, cfg), "window", f"w{i:03d}", rd, opts, bin_, None)
        report["reports"].append({"i": i, "span": w.get("span", ""), **ans})
        report["windows_run"] = len(report["reports"])
        report["finished_at"] = now_iso()
        write_reports(out, report)
    errs = sum(1 for r in report["reports"] if "error" in r)
    print(f"\nRESULT: {report['windows_run']} windows run / {errs} errored -> {out}")
    return 1 if errs else 0


def package_note(opts: argparse.Namespace, thumb: Path | None) -> dict:
    """What the package window carries - or why there wasn't one (no silent skips)."""
    if not opts.title:
        return {"status": "skipped", "reason": "no --title supplied; E27 package window not run"}
    note = {"status": "pending", "title": opts.title,
            "thumb_file": str(thumb) if thumb else "", "promised": ""}
    if thumb and not thumb.exists():
        note["reason"] = f"thumbnail {thumb} not found - the package call was title-only"
    return note


def dry_run(windows: list[dict], cfg: PromptCfg, rd: RunDirs, opts: argparse.Namespace,
            package: dict) -> int:
    """Render every prompt, call nothing, write no reports file."""
    n = 0
    if cfg.title:
        (rd.prompts / "package.txt").write_text(render_package_prompt(cfg), encoding="utf-8")
        n += 1
    shown = PromptCfg(cfg.package, cfg.window, cfg.window_one_extra, cfg.title,
                      "<the viewer's own answer to the package question>", cfg.version)
    for w in windows:
        (rd.prompts / f"w{int(w.get('i', 0)):03d}.txt").write_text(
            render_prompt(w, None, shown), encoding="utf-8")
        n += 1
    print(f"  package : {package['status']}"
          + (f" ({package.get('reason', '')})" if package.get("reason") else ""))
    print(f"\nRESULT: dry run - {n} prompts written to {rd.prompts}, 0 calls, no reports file")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="run the blind viewer over a script's windows (P36)")
    ap.add_argument("script", type=Path)
    ap.add_argument("--lane", default=DEFAULT_LANE, choices=["codex"])
    ap.add_argument("--model", default=None, help="the strongest model available to the lane")
    ap.add_argument("--effort", default=DEFAULT_EFFORT, help="model_reasoning_effort (default high)")
    ap.add_argument("--thumb-file", default=None, help="the FINAL thumbnail, attached to window 0 (E27)")
    ap.add_argument("--title", default=None, help="the locked title shown in window 0 (E27)")
    ap.add_argument("--limit", type=int, default=None, help="run only the first N windows")
    ap.add_argument("--dry-run", action="store_true", help="render the prompts, call nothing")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--windows", type=Path, default=None, help="the viewer_windows.v1 JSON")
    ap.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT)
    ap.add_argument("--run-dir", type=Path, default=None, help="prompts, logs and the empty call cwd")
    ap.add_argument("--codex-bin", default=None)
    ap.add_argument("--timeout", type=float, default=CALL_TIMEOUT_S)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        return run(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"viewer_run: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
