"""V-a - the muted-caption judge (P37 T5). For every scene pair - the prior frame with its
captions (context) and the test frame with captions removed - a judge states the claim the
test frame makes, and CODE returns PASS / FAIL with a diagnosis:

    scenery     - the judge can only describe the picture; the frame carries no claim
    over-dense  - the judge cannot resolve the claim; too much is on the frame
    none        - PASS

Operator, 2026-09-04: "a muted caption test doesn't only have to be human, it can be an LLM
judge. If I'm asking the average viewer to have stronger reasoning than a decent LLM can
manage, the material is probably too complex." And: "you don't API call, you drive Codex
via the CLI like we do for the other judging - and since Codex is judging we don't have
to ship individual pairs, it can do it all at once."

So the judge is the Codex CLI (`viewer_run.py`'s lane, memory `codex-fulfillment-flow`),
ONE headless run per manifest, every frame attached with the variadic `-i`, one JSON array
back. Unwired from any build; cadence is the operator's. Tests replay recorded replies.

    python judge_muted_caption.py manifest.json --out report.json                 # live, one codex run
    python judge_muted_caption.py manifest.json --responses recorded.json         # replay
    python judge_muted_caption.py --prior a.png --test b.png --claim "..." --responses r.json   # one pair

manifest.json: [{"scene": "s03", "prior": "prior.png", "test": "test.png", "claim": "..."}, ...]
recorded.json: {"<test basename>": {"claim_read": str, "confidence": 0..1, "describes_only_scenery": bool}, ...}
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

CONFIDENCE_MIN = 0.6
OVERLAP_MIN = 2
STOP = {"the", "a", "an", "of", "in", "on", "and", "to", "is", "are", "was", "were", "by", "for", "with", "that", "this", "it", "its", "as", "at", "from"}
SRC_V_A = "47 s3 V-a / P36: the viewer reads the frame without the words - if a decent model cannot read the claim, the viewer cannot"
CODEX_TIMEOUT_S = 900.0


@dataclass(frozen=True)
class Verdict:
    scene: str
    verdict: str        # PASS | FAIL
    diagnosis: str      # none | scenery | over-dense
    claim: str
    claim_read: str
    confidence: float
    overlap: int
    rationale: str
    src: str = SRC_V_A


def _stems(text: str) -> set[str]:
    return {w[:6] for w in re.findall(r"[a-z0-9%]+", text.lower()) if w not in STOP and len(w) > 2}


def judge(claim: str, reply: dict, scene: str = "-") -> Verdict:
    """Pure: the judge's structured reply -> a verdict with a diagnosis. The verdict is code, not the model."""
    read = str(reply.get("claim_read") or "").strip()
    conf = float(reply.get("confidence") or 0.0)
    scenery = bool(reply.get("describes_only_scenery"))
    overlap = len(_stems(claim) & _stems(read))
    if scenery or not read:
        return Verdict(scene, "FAIL", "scenery", claim, read, conf, overlap, "the judge could only describe the picture - the frame carries no claim without its words")
    if conf < CONFIDENCE_MIN or overlap < OVERLAP_MIN:
        return Verdict(scene, "FAIL", "over-dense", claim, read, conf, overlap,
                       f"the judge read '{read}' at confidence {conf:.2f} sharing {overlap} term(s) with the claim - it could not resolve the claim")
    return Verdict(scene, "PASS", "none", claim, read, conf, overlap, f"the judge read the claim at confidence {conf:.2f}")


# --- the Codex lane: one run, every pair -------------------------------------------------
def batch_prompt(manifest: list[dict]) -> str:
    lines = ["You are judging frames from a finance explainer. Each TEST frame has had its captions removed;",
             "its PRIOR frame (captions on) is context only. For every test frame, state the single claim a",
             "first-time viewer would read from the TEST frame alone in two seconds. Do NOT use the prior frame's",
             "words as the answer - it is there so you know what the scene is about.",
             "",
             "The attached images are, in order:"]
    for i, item in enumerate(manifest):
        lines.append(f"  {2 * i + 1}. PRIOR for scene {item['scene']}: {Path(item['prior']).name}")
        lines.append(f"  {2 * i + 2}. TEST  for scene {item['scene']}: {Path(item['test']).name}")
    lines += ["",
              "Reply with ONLY a JSON array, one object per scene, in manifest order:",
              '[{"scene": "<scene id>", "claim_read": "<one sentence, or empty string if the test frame only shows scenery>",',
              ' "confidence": <0..1 that a first-time viewer reads that claim in 2 seconds>, "describes_only_scenery": <true|false>}, ...]']
    return "\n".join(lines)


def codex_cmd(bin_: str, cwd: Path, prompt: str, images: list[Path], last_msg: Path, effort: str = "low", model: str | None = None) -> list[str]:
    """viewer_run.codex_cmd's rule, many images: `-i` is VARIADIC and swallows the positional
    prompt, so every image goes first and the non-variadic `-c` closes the list."""
    cmd = [bin_, "exec", "--cd", str(cwd), "--skip-git-repo-check", "--approve-for-me", "-i", *[str(p) for p in images]]
    cmd += ["-c", f'model_reasoning_effort="{effort}"', "-o", str(last_msg)]
    if model:
        cmd += ["-m", model]
    return cmd + [prompt]


def run_codex(manifest: list[dict], run_dir: Path, codex_bin: str | None, effort: str, model: str | None) -> list[dict]:
    from viewer_run import call_codex, find_codex  # the same lane as the viewer (P36)
    bin_ = find_codex(codex_bin)
    run_dir.mkdir(parents=True, exist_ok=True)
    sandbox = run_dir / "sandbox"; sandbox.mkdir(exist_ok=True)
    last_msg = run_dir / "last.txt"
    images = [Path(p).resolve() for item in manifest for p in (item["prior"], item["test"])]
    prompt = batch_prompt(manifest)
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    raw = call_codex(codex_cmd(bin_, sandbox, prompt, images, last_msg, effort, model), run_dir / "codex.log", last_msg, CODEX_TIMEOUT_S)
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        raise ValueError(f"codex returned no JSON array; see {run_dir / 'codex.log'}")
    replies = json.loads(m.group(0))
    if len(replies) != len(manifest):
        raise ValueError(f"codex returned {len(replies)} replies for {len(manifest)} scenes")
    return replies


def replay(manifest: list[dict], responses: dict) -> list[dict]:
    return [responses[Path(item["test"]).name] for item in manifest]


def judge_all(manifest: list[dict], replies: list[dict]) -> list[Verdict]:
    return [judge(item["claim"], reply, item["scene"]) for item, reply in zip(manifest, replies)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", nargs="?", help="JSON list of {scene, prior, test, claim}")
    ap.add_argument("--prior"); ap.add_argument("--test"); ap.add_argument("--claim")
    ap.add_argument("--responses", help="recorded replies keyed by test basename (replay; no codex run)")
    ap.add_argument("--out", help="write the report JSON here")
    ap.add_argument("--run-dir", default="judge-muted-caption-run")
    ap.add_argument("--codex-bin"); ap.add_argument("--effort", default="low"); ap.add_argument("--model")
    args = ap.parse_args()
    if args.manifest:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    elif args.prior and args.test and args.claim:
        manifest = [{"scene": "-", "prior": args.prior, "test": args.test, "claim": args.claim}]
    else:
        ap.error("give a manifest, or --prior/--test/--claim")
    if args.responses:
        replies = replay(manifest, json.loads(Path(args.responses).read_text(encoding="utf-8")))
    else:
        replies = run_codex(manifest, Path(args.run_dir), args.codex_bin, args.effort, args.model)
    verdicts = judge_all(manifest, replies)
    report = {"scenes": [asdict(v) for v in verdicts],
              "counts": {k: sum(1 for v in verdicts if v.verdict == k) for k in ("PASS", "FAIL")},
              "diagnoses": {k: sum(1 for v in verdicts if v.diagnosis == k) for k in ("scenery", "over-dense")}}
    text = json.dumps(report, indent=1)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    return 1 if report["counts"]["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
