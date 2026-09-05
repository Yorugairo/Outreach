"""V-a - the muted-caption judge (P37 T5). Given a prior frame (captions on) and a test frame
(captions off) plus the claim the scene is supposed to make, ask a model what the test frame
claims, and return PASS / FAIL with a DIAGNOSIS:

    scenery     - the model can only describe the picture; the frame carries no claim
    over-dense  - the model cannot resolve the claim at all; too much is on the frame
    none        - PASS

Operator, 2026-09-04: "a muted caption test doesn't only have to be human, it can be an LLM
judge. If I'm asking the average viewer to have stronger reasoning than a decent LLM can
manage, the material is probably too complex."

Ships as a CLI, NOT wired to any build (human gate: cost and cadence are the operator's).
Tests replay recorded responses; no live call is ever made from a test.

    python judge_muted_caption.py --prior a.png --test b.png --claim "memory makers rose 613%" --responses recorded.json
    python judge_muted_caption.py --prior a.png --test b.png --claim "..." --model gpt-4o        # live (OPENAI_API_KEY)
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIDENCE_MIN = 0.6
OVERLAP_MIN = 2
STOP = {"the", "a", "an", "of", "in", "on", "and", "to", "is", "are", "was", "were", "by", "for", "with", "that", "this", "it", "its", "as", "at", "from"}
SRC_V_A = "47 s3 V-a / P36: the viewer reads the frame without the words - if a decent model cannot read the claim, the viewer cannot"

PROMPT = (
    "You are looking at one frame of a finance explainer with its captions removed. "
    "Answer with JSON only: {\"claim_read\": <the single claim this frame makes, one sentence, or an empty string if it only shows scenery>, "
    "\"confidence\": <0..1 that a first-time viewer would read that claim in 2 seconds>, "
    "\"describes_only_scenery\": <true if the frame shows a picture with no readable claim>}"
)


@dataclass(frozen=True)
class Verdict:
    verdict: str        # PASS | FAIL
    diagnosis: str      # none | scenery | over-dense
    claim_read: str
    confidence: float
    overlap: int
    rationale: str
    src: str = SRC_V_A


def _stems(text: str) -> set[str]:
    return {w[:6] for w in re.findall(r"[a-z0-9%]+", text.lower()) if w not in STOP and len(w) > 2}


def judge(claim: str, reply: dict) -> Verdict:
    """Pure: the model's structured reply -> a verdict with a diagnosis."""
    read = str(reply.get("claim_read") or "").strip()
    conf = float(reply.get("confidence") or 0.0)
    scenery = bool(reply.get("describes_only_scenery"))
    overlap = len(_stems(claim) & _stems(read))
    if scenery or not read:
        return Verdict("FAIL", "scenery", read, conf, overlap, "the model could only describe the picture - the frame carries no claim without its words")
    if conf < CONFIDENCE_MIN or overlap < OVERLAP_MIN:
        return Verdict("FAIL", "over-dense", read, conf, overlap,
                       f"the model read '{read}' at confidence {conf:.2f} sharing {overlap} term(s) with the claim - it could not resolve the claim")
    return Verdict("PASS", "none", read, conf, overlap, f"the model read the claim at confidence {conf:.2f}")


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def call_model(prior: Path, test: Path, claim: str, model: str) -> dict:
    """Live call through the OpenAI-compatible client (the only SDK on this host). The prior
    frame is context; the question is about the test frame. Never called from tests."""
    from openai import OpenAI  # local import: the SDK is optional
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    content = [
        {"type": "text", "text": "Prior frame, with captions (context only):"},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{_b64(prior)}"}},
        {"type": "text", "text": "Test frame, captions removed - answer about THIS frame:"},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{_b64(test)}"}},
        {"type": "text", "text": PROMPT},
    ]
    r = client.chat.completions.create(model=model, messages=[{"role": "user", "content": content}], temperature=0)
    text = r.choices[0].message.content or "{}"
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0) if m else "{}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prior", required=True); ap.add_argument("--test", required=True); ap.add_argument("--claim", required=True)
    ap.add_argument("--responses", help="recorded replies JSON: {<test basename>: {claim_read, confidence, describes_only_scenery}}")
    ap.add_argument("--model", default="gpt-4o")
    args = ap.parse_args()
    test = Path(args.test)
    if args.responses:
        reply = json.loads(Path(args.responses).read_text(encoding="utf-8"))[test.name]
    elif os.environ.get("OPENAI_API_KEY"):
        reply = call_model(Path(args.prior), test, args.claim, args.model)
    else:
        print("no --responses and no OPENAI_API_KEY: the judge has nothing to judge with", file=sys.stderr); return 2
    v = judge(args.claim, reply)
    print(json.dumps(asdict(v), indent=1))
    return 0 if v.verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
