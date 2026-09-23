"""Narrative-first V13 pilot; measured words own every authored event.

The workshop is illustrative, not an observed company account. Existing paper
art is used as a document insert, not passed off as contemporary reporting.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4] / "content/video_engine/scripts"))
from authoring import words as W

AUTHORING_STATUS = "V13_SCRATCH_REVIEW_NOT_APPROVED"
SEGMENT_GROUPS = {"bed": ("opening",), "unit": ("opening",), "pilot": ("opening",)}
SHOP = "w2-owner-workshop-world-v1;idle=none;use=landing"
HALL = "w4-finance-evidence-hall-v1;idle=none;use=bridge"
FOLIO = "p2-owner-loan-folio-v1"
CASH = "prop-icon-cash-liquidity-stack-v1"
AUDIT = "prop-badge-fundamental-financial-audit-v1"


def specs_for(segment):
    return ()


def group_ranges(rows, segment="pilot"):
    return {"opening": (0.0, rows[-1][1])}


def build_rows(words, runtime_s, segment):
    # Builder supplies the entire measured take; clip only the authored prefix.
    at = lambda phrase: W.at(words, phrase)
    def stamp(phrase, end, icon, text, x, y, size=210, ink="cream"):
        t = at(phrase)
        return {"kind": "chip", "form": "stamp", "at": t, "dur": max(.1, end-t),
                "icon": icon, "label": text, "size": size, "ink": ink,
                "target": {"kind": "point", "x": x, "y": y}}
    def cam(start, end, look, zoom):
        return {"attention": "locked", "keys": [
            {"t": start, "zoom": 1.0, "look": [.5,.5]},
            {"t": end, "zoom": zoom, "look": look, "at": [.5,.5], "ease": "inout"}]}
    def paper(aid, start, end, x=.76, width=.32):
        return (aid, 0, start, end, {"centre": True, "centre_w": width,
                "centre_x": x, "centre_y": .48, "card_aspect": 1.0,
                "arrive": "throw", "mass": "paper"})

    shop = at("Imagine you own a workshop")
    hire = at("The extra interest")
    result = at("The bank gets paid")
    promise = at("Stay for three checks")
    bio = at("Working in Business Risk")
    gave_up = at("I want to know")
    renewal = at("Refinancing replaces")
    follow = at("Follow that decision")
    worker = at("A worker loses overtime")
    scale = at("The need to refinance")
    wait = at("The owner plans")
    washington = at("Like the workshop")
    # The first minute alternates human world and its causal document. It does
    # not repeatedly redraw a decorative chart or disclose all three checks.
    rows = [
        (0, shop, "world-internal-memo-v1;idle=none", (.025,8,-4), [], None, [
            stamp("Your employer can make every payment", shop, CASH, "PAYMENT MADE", .77,.25,210,"charcoal")]),
        (shop, hire, SHOP, (.03,8,-3),
         [paper(FOLIO, at("the bank sends"), hire)], "melt:splash:plate:1.0", []),
        (hire, result, SHOP, (0,0,0), [], None, [
            stamp("The extra interest", result, CASH, "HIGHER INTEREST", .73,.28),
            stamp("You delay the hire", result, AUDIT, "HIRE DELAYED", .73,.54)],
         cam(hire,result,[.58,.54],1.12)),
        (result, promise, SHOP, (.02,8,0), [], None, [
            stamp("The bank gets paid", promise, CASH, "BANK PAID", .76,.29)]),
        (promise, bio, HALL, (.025,0,-5), [], "door:left:0.8", [
            stamp("Stay for three checks", bio, AUDIT, "THREE CHECKS\nYOUR MONEY", .50,.29,240,"charcoal")]),
        (bio, gave_up, HALL, (0,0,0), [], None, [], cam(bio,gave_up,[.26,.60],1.65)),
        (gave_up, renewal, "world-internal-memo-v1;idle=none", (.035,0,5), [], "door:right:0.8", []),
        (renewal, follow, "world-adviser-signature-v1;idle=none", (.045,10,0),
         [paper(FOLIO, at("That renewal letter"), follow, .80,.28)], "melt:splash:plate:1.0", []),
        (follow, worker, SHOP, (.035,-8,0), [], "door:left:0.8", []),
        (worker, scale, SHOP, (0,0,0), [], None, [
            stamp("A worker loses overtime", scale, CASH, "LESS OVERTIME", .75,.24),
            stamp("a customer pays more", scale, AUDIT, "HIGHER PRICES", .75,.48)],
         cam(worker,scale,[.61,.52],1.14)),
        (scale, wait, HALL, (.025,0,-5),
         [paper("world-lease-contracts-bound", at("Governments businesses and households"), wait, .76,.32)],
         "melt:splash:plate:1.0", []),
        (wait, washington, SHOP, (.04,12,-3), [], "door:right:0.8", [
            stamp("The owner plans", washington, AUDIT, "NEXT PURCHASE\nON HOLD", .75,.35,240)]),
    ]
    # Further evidence rows are authored after the 90-second bed is inspected.
    if runtime_s > washington + .1:
        raise ValueError("Pilot evidence section not yet authored; use bed/unit checkpoint")
    clipped = []
    for row in rows:
        start, end, plate, kb, docks, exit_, species, *camera = row
        if start >= runtime_s:
            break
        end = min(end, runtime_s)
        docks = [(a,i,s,min(e,end),o) for a,i,s,e,o in docks if s < end]
        species = [dict(s, dur=min(s["dur"], end-s["at"])) for s in species if s["at"] < end]
        clipped.append((start,end,plate,kb,docks,exit_,species,*camera))
    return clipped
