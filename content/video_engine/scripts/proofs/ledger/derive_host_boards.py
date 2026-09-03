"""For each host-on-board plate: measure the board (dark bbox), the innermost clean rectangle, the host's side (quiet zone),
and derive the BLANK state by returning the board region to cream paper sampled from the page margin."""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

REPO = Path(sys.argv[1])
C = REPO / "review/claims/steel-and-paper-host-board-v1/objects"
OUT = {}
for name in ("host-board-present-v1", "host-board-point-v1", "host-board-turned-v1"):
    im = Image.open(C / f"{name}.png").convert("RGB")
    a = np.asarray(im).astype(np.float32)
    H, W = a.shape[:2]
    lum = a.mean(axis=2)
    # the board: pixels within a tight colour distance of the charcoal token #25313C; the suit's shadow is bluer and further away
    charcoal = np.array([0x25, 0x31, 0x3C], np.float32)
    dist = np.sqrt(((a - charcoal) ** 2).sum(axis=2))
    board = (dist < 22).astype(np.uint8)
    # kill specks (a 5px opening) so nothing in the sleeve or hair survives as board
    bimg = Image.fromarray(board * 255).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
    board = (np.asarray(bimg) > 127).astype(np.uint8)
    # keep the big contiguous block: rows/cols where the run is long
    # the board's columns and rows are the ones the charcoal covers substantially (the host's hair or an arm never do)
    rows = np.where(board.sum(axis=1) > W * 0.4)[0]
    cols = np.where(board.sum(axis=0) > H * 0.6)[0]
    y0, y1, x0, x1 = rows.min(), rows.max(), cols.min(), cols.max()
    # the clean inner rectangle: the bbox inset by the deckle's amplitude (~1% of the frame)
    ins_x, ins_y = int(W * 0.011), int(H * 0.016)
    left, right, top, bottom = x0 + ins_x, x1 - ins_x, y0 + ins_y, y1 - ins_y
    inner = {"x": round(left / W, 4), "y": round(top / H, 4), "w": round((right - left) / W, 4), "h": round((bottom - top) / H, 4)}
    host_side = "right" if (x0 + x1) / 2 < W / 2 else "left"
    # where the host's hand or body intrudes into the board (non-board pixels inside the inner rect, middle band):
    band = board[top + int((bottom - top) * 0.12): bottom - int((bottom - top) * 0.12), left:right]
    intr = np.where(band.mean(axis=0) < 0.97)[0]
    if host_side == "right":
        hand_x = (intr.min() + left) / W if len(intr) else right / W
        chart_box = {"x": inner["x"], "y": inner["y"], "w": round(hand_x - 0.02 - inner["x"], 4), "h": inner["h"]}
    else:
        hand_x = (intr.max() + left) / W if len(intr) else left / W
        chart_box = {"x": round(hand_x + 0.02, 4), "y": inner["y"], "w": round(inner["x"] + inner["w"] - hand_x - 0.02, 4), "h": inner["h"]}
    # blank state: the board mask (feathered) filled with cream paper tiled from the page's top margin strip
    # only CHARCOAL pixels return to paper (the host's arm over the board keeps its pixels); the mask grows 4px to
    # swallow the board's edge ink and feathers 1.5px so nothing crosses the arm
    mask = np.zeros((H, W), np.uint8); mask[y0:y1 + 1, x0:x1 + 1] = board[y0:y1 + 1, x0:x1 + 1]
    m = np.asarray(Image.fromarray(mask * 255).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32) / 255
    # the paper: THIS plate's cream tone (a ring just outside the board, away from the host) + the page plate's texture only
    ring = np.zeros((H, W), bool)
    ring[max(0, y0 - 30):y0 - 6, x0:x1 + 1] = True; ring[y1 + 6:min(H, y1 + 30), x0:x1 + 1] = True
    if host_side == "right": ring[y0:y1 + 1, max(0, x0 - 30):max(1, x0 - 6)] = True
    else: ring[y0:y1 + 1, x1 + 6:min(W, x1 + 30)] = True
    ring &= (dist > 60) & (a.mean(axis=2) > 150)                      # cream only: no ink, no host
    tone = a[ring].reshape(-1, 3).mean(axis=0)
    paper_src = REPO / "review/claims/steel-and-paper-ledger-page-v1/objects/world-ledger-blank-page-cream-v1.png"
    tex = np.asarray(Image.open(paper_src).convert("RGB").resize((W, H))).astype(np.float32)
    tex = tex - tex.reshape(-1, 3).mean(axis=0)                        # texture only, zero mean
    paperW = np.clip(tone + tex * 0.7, 0, 255)
    blank = a * (1 - m[..., None]) + paperW * m[..., None]
    Image.fromarray(blank.clip(0, 255).astype(np.uint8)).save(C / f"{name}-blank.png")
    OUT[name] = {"board_bbox": {"x": round(x0 / W, 4), "y": round(y0 / H, 4), "w": round((x1 - x0) / W, 4), "h": round((y1 - y0) / H, 4)},
                 "inner": inner, "host_side": host_side, "quiet_zone": host_side, "chart_box": chart_box, "hand_x": round(float(hand_x), 4), "blank": f"{name}-blank.png"}
    print(name, OUT[name])
Path(__file__).with_name("host-boards.json").write_text(json.dumps(OUT, indent=1), encoding="utf-8")
