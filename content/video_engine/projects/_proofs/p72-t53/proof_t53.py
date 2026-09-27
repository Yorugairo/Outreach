"""P72 T53 (a) - `the-hidden-base` (harvest R1, BUB 0:00-0:48) PROVED AS A BEAT on the iceberg stage (E99 s60, s70).

    python content/video_engine/projects/_proofs/p72-t53/proof_t53.py              # build the beat + its strip
    python content/video_engine/projects/_proofs/p72-t53/proof_t53.py --strip-only # re-shoot the strip

P71 T34 stopped this recipe (its discovery beat stays in proof_t34.py, unchanged): the raised camera showed the void over
a full-stage page, the base was still on screen, the glow edged the whole bar, and no committed object paired the two
stocks. T53 (a) built the four: the page's own sky over a raised pedestal, the water under the balance-sheet rule
(`hlines[i].water`), the light on ONE part of a stacked bar (`glow {bar, segment}`) and the committed object
`ev-leases-iceberg-v1` (derive_iceberg.py: $261B of bonds over $822B of lease commitments, derived, never typed).

THE BEAT, H row 16's own words off the Steel and Paper H scratch take: "And that's the borrowing you can see. Go into the
filings and there's another eight hundred and twenty-two billion in lease commitments ... that have never landed on a
balance sheet." The page opens with the camera RAISED - the tip (the bonds, $261B) over the waterline "the balance sheet",
the base below the frame - and as the voice goes into the filings the camera drops through the water to the base ($822B, under
water, its figure written) - on "there's another eight hundred", the first word after the page's build has settled (M14
refused "Go into the filings", 2.7 s, inside the build's 0-3.0 s); on "never landed on" the light falls on the hidden part
only.

The door is P71 T34's (proof_t34.py, IMPORTED, never edited - its module globals HERE / TAG are pointed at this slice so
its build and strip land in `build-lab-the-hidden-base/` beside THIS file, gitignored). The page is the COMMITTED object,
compiled in the Steel and Paper project itself; the project is read and asserted unmoved (P69's door does it).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "p71-recipes"))

import proof_t34 as P34   # noqa: E402  (imported, never edited)
from authoring import table as T   # noqa: E402

P34.HERE = HERE                      # the build and the strip land beside THIS file
P34.TAG = "P72 T53"
ICE_PAGE = "ev-leases-iceberg-v1"
PLATE = f"ledger:{ICE_PAGE}:bars::right:axes:cut;idle=live;readability=longform"
PEDESTAL_BY = 0.45       # raised so the waterline opens near the frame's foot: the base below the frame (BUB frame 1: 0.615 H)
PEDESTAL_S = 2.4         # T32's one move (BUB: one move, then still)
GLOW_S = 0.68            # the glow golden's edge-up (T34's GLOW_S)


def _times(ws: list) -> tuple[float, float, float, float]:
    return (T.at(ws, "the borrowing you can see"), T.at(ws, "there's another eight"), T.at(ws, "lease commitments"),
            T.at(ws, "never landed on"))


def _row(ws: list, runtime: float) -> tuple:
    _see, t_go, _lease, t_never = _times(ws)
    species = [{"kind": "glow", "at": t_never, "dur": GLOW_S, "bar": 0, "segment": 0}]   # the HIDDEN part only (segment 0: the leases)
    camera = {"keys": [], "pedestal": {"at": t_go, "dur": PEDESTAL_S, "by": PEDESTAL_BY}}
    return (0.0, runtime, PLATE, (0, 0, 0), [], None, species, camera)


def _strip(ws: list) -> list:
    t_see, t_go, t_lease, t_never = _times(ws)
    return [(round(t_see + 0.6, 2), "the tip: what you can see, the base below the frame"),
            (round(t_go + PEDESTAL_S * 0.5, 2), "the pedestal down through the water"),
            (round(max(t_go + PEDESTAL_S + 0.3, t_lease + 0.8), 2), "the base: the hidden part, true proportion, written"),
            (round(t_never + GLOW_S + 0.4, 2), "the light on the hidden part only")]


BEAT = P34.Beat("the-hidden-base", "And that's the borrowing", "never landed on", _row, _strip)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strip-only", action="store_true")
    ap.add_argument("--strips", type=Path, default=HERE)
    args = ap.parse_args()
    if not args.strip_only:
        rc = P34.build_beat(BEAT)
        if rc:
            print(f"FAIL: recipe:{BEAT.slug} did not compile (rc {rc})")
            return rc
    P34.render_strip(BEAT.slug, args.strips)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
