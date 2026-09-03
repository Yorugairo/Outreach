"""Open the host-on-board claim (C5 addendum): three poses of the host at the inked deckle board on the cream page."""
import json
import os
import sys
from pathlib import Path

REPO = Path(sys.argv[1])
sys.path.insert(0, str(REPO))
from content.video_engine.src.services.generation_claim import open_claim, render_work_order, GenerationClaimError  # noqa: E402

CLAIM = "steel-and-paper-host-board-v1"
W = REPO / "content/video_engine/projects/systems-and-blowups"
REFS = [
    str(W / "review/claims/finance-host-evidence-exp-2/objects/host-presents-board-v1.png"),
    str(W / "assets/generated/cutouts/actor-host-present-open-v1.png"),
    str(W / "assets/generated/cutouts/actor-host-point-right-v1.png"),
    str(REPO / "review/claims/steel-and-paper-ledger-page-v1/objects/world-ledger-inked-deckle-cream-v1.png"),
]
REFS = [r for r in REFS if Path(r).exists()]

HOST = ("THE HOST (identity anchor, exact): an adult Black man with sculpted loc twists and a trimmed goatee, BLACK rectangular "
        "glasses (critical: frames are BLACK, never blue/cobalt), deep-indigo suit, copper tie, small gold lapel pin. Same face "
        "structure, hair, glasses, and wardrobe in every image - condition on the supplied reference images. Confident, composed, "
        "warm; never caricatured. ")
BOARD = ("THE BOARD (exact, condition on the reference plate world-ledger-inked-deckle-cream-v1): a sheet of cream washi paper with a "
         "deckled edge lying on a plain cream ground fills the frame; the paper is filled solid charcoal ink #25313C right up to its "
         "deckle edge, like a chalkboard painted onto the page, EXCEPT the host's zone. The board interior is EMPTY - no chart, no "
         "text, no marks: the chart is composited later into the surface he points at. ")
BASE = ("Woodblock / vox newsprint register: carved ink contours, flat editorial colour, matte, even light from the upper left. "
        "Colours limited to cream #F4E6C7, charcoal #25313C, indigo suit, copper tie, small gold pin; no other hues, no gradients, "
        "no glow. Landscape 1920x1080; the flat opaque image IS the deliverable - flatten to RGB (no alpha), skip matting; save the "
        "same file as both source/ and objects/. The image contains no text, letters, numbers, logos or watermarks anywhere.")

slots = [
    {"asset_id": "host-board-present-v1", "kind": "world_board",
     "prompt": "WORLD BOARD OVERRIDE for this slot only: generate landscape 1920x1080. " + HOST + BOARD +
               "Subject: the host stands in the RIGHT third of the frame, in front of the cream page's right margin, three-quarter to camera, "
               "presenting the board with an open hand toward its centre; the board fills the left two thirds of the paper; the host's body never "
               "overlaps the board interior - only his presenting hand reaches into it. Quiet zone for the chart: the board's left two thirds. " + BASE},
    {"asset_id": "host-board-point-v1", "kind": "world_board",
     "prompt": "WORLD BOARD OVERRIDE for this slot only: generate landscape 1920x1080. " + HOST + BOARD +
               "Subject: the host stands in the RIGHT third of the frame, turned to the board, pointing with one finger at the board's UPPER area "
               "(a datum will be composited exactly where he points); his eyes follow his finger; the board fills the left two thirds of the paper; "
               "only his pointing hand reaches into the board interior. " + BASE},
    {"asset_id": "host-board-turned-v1", "kind": "world_board",
     "prompt": "WORLD BOARD OVERRIDE for this slot only: generate landscape 1920x1080. " + HOST + BOARD +
               "Subject: the host stands at the LEFT edge of the frame, seen from behind at three-quarter, turned to the board on his right, one "
               "hand at his chin as if reading it; the board fills the right two thirds of the paper; he does not overlap the board interior. "
               "Quiet zone for the chart: the board's right two thirds. " + BASE},
]
try:
    claim = open_claim(str(REPO), claim_id=CLAIM, style_family="woodblock-vox-newsprint-v2", slots=slots, reference_images=REFS)
except GenerationClaimError as e:
    print("CLAIM ERROR:", e)
    raise SystemExit(1)
rec = json.load(open(os.path.expanduser(f"~/.video-engine/claims/{CLAIM}.json"), encoding="utf-8"))
wo = render_work_order(rec)
d = Path(claim["delivery_dir"]); d.mkdir(parents=True, exist_ok=True)
(d / "WORK-ORDER.md").write_text(wo, encoding="utf-8")
print("claim opened:", CLAIM, "| refs:", len(REFS), "| work order:", d / "WORK-ORDER.md")
