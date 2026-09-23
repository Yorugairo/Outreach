"""Narrative-first opening proof. Same approved take; native ledger and real art.

All timings resolve from the selected take. The original pilot table remains
untouched so the rejected treatment remains reproducible.
"""
from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("fed_minute_anchor_helpers", HERE / "SHOT-TABLE-PILOT.py")
_old = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _old
_spec.loader.exec_module(_old)

AUTHORING_STATUS = "MINUTE_REBUILD_REVIEW_NOT_APPROVED"
GROUPS = ("M01",)
SEGMENT_GROUPS = {"minute": GROUPS}
END = "The companies replacing cheap debt still need financing, even as one source of support behind the banks runs down."
HALL = "w4-finance-evidence-hall-v1;idle=none;use=bridge"
SHOP = "w2-owner-workshop-world-v1;idle=none;use=landing"
CASH = "prop-icon-cash-liquidity-stack-v1"
BANK = "prop-icon-central-bank-fx-v2"
AUDIT = "prop-badge-fundamental-financial-audit-v1"
RATE = "prop-icon-interest-rates-monetary-policy-v2"
GOODS = "prop-icon-critical-minerals-mining-v1"
GROWTH = "prop-icon-seed-capital-growth-v1"
DRAIN = "prop-liquidity-drain-pump-v1"


def register_assets(docks):
    """Reuse approved library plates without altering their approval records."""
    claims = HERE.parent / "review/claims"
    for aid, wave, digest in (
        ("world-adviser-signature-v1", 3, "02516ddf660bda77b9dc5cfa1956f056cc72d3ed8ea54910010df6f292a948a3"),
        ("world-treasury-cash-count", 5, "13515928ae8effe827115175b4e20070d674e0076ca989ca9231181b0986bb19"),
    ):
        folder = claims / f"steel-and-paper-plates-wave-{wave}"
        approvals = json.loads((folder / "approvals.json").read_text())
        path = folder / "objects" / f"{aid}.png"
        if aid not in approvals.get("operator_approved", []):
            raise ValueError(f"library plate lacks operator approval: {aid}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"library plate changed: {aid}")
        docks.register(aid, path)


def group_end_phrase(group):
    if group != "M01":
        raise ValueError(group)
    return END


def specs_for(segment):
    if segment != "minute":
        raise ValueError(segment)
    return ()


def group_ranges(rows, segment="minute"):
    return {"M01": (0.0, float(rows[-1][1]))}


def build_rows(words, runtime_s, segment):
    if segment != "minute":
        raise ValueError(segment)
    at = lambda phrase: _old._anchor(words, phrase)
    cut = lambda phrase, exit: _old._cut_before(words, phrase, exit)

    def stamp(phrase, end, icon, label, x, y, size=220, ink="charcoal"):
        start = at(phrase)
        return {"kind": "chip", "form": "stamp", "at": start,
                "dur": round(end-start, 3), "icon": icon, "label": label,
                "size": max(180, size), "ink": ink,
                "target": {"kind": "point", "x": x, "y": y}}

    def datum(index, series=0):
        return {"kind": "datum", "index": index, "series": series}

    def camera(start, end, look, zoom, screen=None):
        return {"attention": "locked", "keys": [
            {"t": start, "zoom": 1.0, "look": [.5, .5]},
            {"t": end, "zoom": zoom, "look": look, "at": screen or look, "ease": "inout"}]}

    # One complete history; the first visible state stops at its actual peak.
    # Only the unshown years draw forward. No repeated chart or full redraw.
    rrp = json.loads((HERE / "evidence/objects/fed-on-rrp-history.series.json").read_text())
    pts = rrp["series"][0]["pts"]
    peak = max(range(len(pts)), key=lambda i: pts[i][1])
    last = len(pts)-1
    balance_history = json.loads((HERE / "evidence/objects/fed-assets-reserves-history.series.json").read_text())
    balance_last = len(balance_history["series"][1]["pts"])-1
    chart_start = at("By September eighteenth, that parking lot was almost empty.") + .20
    shop_start = cut("Imagine you own a workshop.", "melt:splash:plate:1.0")
    machine_start = cut("Your machine still works.", "cut")
    promise_start = cut("You’ll leave with three checks", "door:left:0.8")
    bio_start = cut("I worked in business risk at JPMorgan", "cut")
    support_start = cut("By the end of this video", "door:right:0.8")
    wall_at = at("Meanwhile, companies face a debt wall.")
    cash_start = cut("Money funds had parked", "door:right:0.55")
    loan_start = at("Your two-percent loan is coming due")
    machine_camera = camera(machine_start, machine_start+1.3, [.23,.64], 2.25, [.45,.60])
    machine_camera["keys"].extend([
        {"t": at("Your customers still"), "zoom": 2.25, "look": [.23,.64], "at": [.45,.60]},
        {"t": at("wages, materials, or the next hire.")-.05, "zoom": 1,
         "look": [.45,.5], "at": [.45,.5], "ease": "inout"},
    ])
    rows = [
        (0, cash_start, HALL, (0, 0, 0), [], None, [
            stamp("The Fed’s balance fell by trillions.", cash_start, BANK, "FED ASSETS\nFELL", .40, .25, 175),
            stamp("Bank reserves barely budged.", cash_start, CASH, "BANK BALANCES\nBARELY MOVED", .61, .25, 175),
        ]),
        (cash_start, chart_start, "world-treasury-cash-count;idle=none;use=bridge", (.045,-12,-6), [], "door:right:0.55", [
            stamp("Money funds had parked", chart_start, CASH, "MONEY FUNDS\nABOUT $2.5 TRILLION", .50, .22, 190, "cream"),
        ]),
        (chart_start, shop_start,
         "ledger:fed-on-rrp-history:line::right:built:cut;idle=live;then=debt-wall-2025-2027:bars",
         (0, 0, 0), [], None, [
             {"kind": "build_to", "at": 0, "dur": .1, "target": datum(peak)},
             {"kind": "spotlight", "at": chart_start+.05, "dur": .5, "target": datum(peak)},
             {"kind": "build_to", "at": chart_start+.20, "dur": 2.15, "target": datum(last)},
             {"kind": "callout", "at": chart_start+2.35,
              "dur": .65, "target": datum(last)},
             {"kind": "figure", "at": chart_start+2.4, "dur": .7,
              "target": datum(last), "text": "$0.576bn", "sub": "18 Sep 2026", "dy": -1},
             {"kind": "chart_to", "at": wall_at, "dur": 2.6, "to": "recast", "state": 1, "keyed": False},
             {"kind": "retitle", "at": wall_at+2.0, "dur": 1.3, "text": "THE CORPORATE DEBT WALL"},
             {"kind": "chart_to", "at": at("corporate debt maturing"), "dur": .9,
              "to": "park", "scale": .95, "anchor": "left"},
             stamp("corporate debt maturing", shop_start, AUDIT, "$3.184 TRILLION\n2025–2027", .85, .45, 215, "cream"),
             {"kind": "spotlight", "at": at("twenty twenty-five through"), "dur": .6, "target": datum(0)},
             {"kind": "spotlight", "at": at("twenty twenty-seven."), "dur": .8, "target": datum(2)},
         ]),
        (shop_start, machine_start, SHOP, (0.035,12,-4),
         [("world-adviser-signature-v1", 0, loan_start, machine_start,
           {"centre": True, "centre_w": .56, "centre_x": .70, "centre_y": .44, "card_aspect": .667})],
         "melt:splash:plate:1.0", [
            stamp("Your two-percent loan is coming due", machine_start, CASH, "OLD LOAN\n2%", .57, .28, 180, "cream"),
            stamp("and replacing it at seven percent", machine_start, RATE, "RENEWAL\n7%", .80, .28, 180, "cream"),
        ]),
        (machine_start, promise_start, "w2-owner-workshop-world-v1;idle=none;use=bridge", (0,0,0), [], "cut", [
            stamp("wages, materials, or the next hire.", promise_start, CASH, "WAGES", .60, .40, 180, "cream"),
            stamp("materials, or the next hire.", promise_start, GOODS, "MATERIALS", .75, .40, 180, "cream"),
            stamp("the next hire.", promise_start, GROWTH, "NEXT HIRE", .88, .40, 180, "cream"),
        ], machine_camera),
        (promise_start, bio_start, HALL, (0.04, -14, 0), [], "door:left:0.8", [
            stamp("public data to help protect", bio_start, AUDIT, "PUBLIC DATA\nYOUR MONEY", .5, .24, 205),
        ]),
        (bio_start, support_start, HALL, (0,0,0), [], "cut", [],
         camera(bio_start, bio_start+1.3, [.26,.59], 1.8, [.43,.55])),
        (support_start, round(runtime_s, 3),
         "ledger:fed-assets-reserves-history:line::right:axes:cut;build=lines:4.2;idle=live",
         (0,0,0), [], "door:right:0.8", [
             {"kind": "chart_to", "at": at("The companies replacing cheap debt"), "dur": .6,
              "to": "park", "scale": .80, "anchor": "left"},
             {"kind": "callout", "at": 58.7, "dur": .8,
              "target": datum(balance_last, 1)},
             stamp("still need financing", at("even as one source of support behind the banks runs down."), CASH,
                   "REFINANCING", .85, .30, 190, "cream"),
             stamp("even as one source of support behind the banks runs down.", runtime_s, DRAIN,
                   "LESS BACKUP", .85, .48, 500, "cream"),
         ]),
    ]
    return rows
