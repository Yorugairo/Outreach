"""V15 first-act choreography: narrative worlds carry decisions; ledgers prove numbers.

The table deliberately supplies at least one approved art-plate candidate per
ten seconds across the first act.  Evidence becomes the full stage only when
the number itself is the subject.  It is never duplicated as a dock over the
same chart page, and each chart builds before its terminal datum is lit.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4] / "content/video_engine/scripts"))
from authoring import words as W


AUTHORING_STATUS = "V15_FIRST_ACT_QUARANTINED_REVIEW"
SEGMENT_GROUPS = {"pilot": ("first_act",)}

SHOP = "w2-owner-workshop-world-v1;idle=none;use=landing"
HALL = "world-mike-risk-underwriting-v1;idle=none"
FOLIO = "p2-owner-loan-folio-v1"
CASH = "prop-icon-cash-liquidity-stack-v1"
AUDIT = "prop-badge-fundamental-financial-audit-v1"

DOCK_META = []


def specs_for(segment):
    return ()


def group_ranges(rows, segment="pilot"):
    return {"first_act": (0.0, rows[-1][1])}


def build_rows(words, runtime_s, segment):
    at = lambda phrase: W.at(words, phrase)

    def chip(phrase, end, icon, text, x, y, *, size=205, ink="cream"):
        # V15 visual review rejected generic UI stamps over narrative art.
        # Keep the semantic calls in the authored table while emitting nothing;
        # a later replacement must be a motivated prop, document, or ledger.
        return None

    def camera(start, end, look, zoom=1.12):
        return {"attention": "locked", "keys": [
            {"t": start, "zoom": 1.0, "look": [.5, .5]},
            {"t": end, "zoom": zoom, "look": look, "at": [.5, .5], "ease": "inout"},
        ]}

    def paper(asset, start, end, *, x=.76, y=.48, width=.30, arrive="throw"):
        # The blank folio read as a mystery note, not a renewal letter.  It is
        # disabled until the engine can typeset a real document onto the prop.
        return None

    # Measured narrative anchors.
    employer = at("Your employer can make every payment")
    promotion = at("and still cancel your promotion")
    trouble = at("The trouble starts")
    imagine = at("Imagine you own a workshop")
    orders = at("Your crew has orders waiting")
    interest = at("The extra interest")
    delay = at("You delay the hire")
    bank_paid = at("But the bank gets paid")
    promise = at("Stay for three checks")
    bills = at("Your own monthly bills")
    bio = at("I worked in Business Risk")
    refinance = at("Refinancing replaces")
    renewal = at("That renewal letter")
    follow = at("Follow the cutback")
    gives_up = at("Each one gives up")
    reaches = at("The need to refinance")
    all_need = at("Governments, businesses and households")
    owner_waits = at("The owner plans")
    washington = at("Like the workshop")
    debt = at("In August")
    net_interest = at("Through August")
    cents = at("That was about twenty-two cents")
    feedback = at("Interest itself adds")
    more_borrowing = at("more borrowing and more interest")
    faster = at("Faster spending")
    alongside = at("That puts Washington")
    treasury = at("On September seventeenth")
    lender = at("Put yourself in the lender's seat")
    owner_asks = at("The owner asks")
    why = at("Why accept less")
    fed = at("The Fed sets")
    investors = at("Those investors weigh")
    overnight = at("An overnight cut")
    quote = at("The quote still")
    due = at("But the existing loan")
    signpost = at("The debt trap is")

    # The first 92 seconds stay in the human world.  Inserts are physical
    # objects inside that world rather than generic cards or pictograms.
    rows = [
        (0.0, employer,
         "ledger:debt-gross-history:line:429:right:axes:cut;idle=live",
         (0, 0, 0), [], "door:left:0.8", [
            # Cold-open action: the line builds under the first complete idea,
            # then the endpoint is identified.  The light clarifies the datum;
            # it does not count as a motion event in the density gate.
            # The $40T figure is withheld for the later evidentiary callback.
            {"kind": "spotlight", "at": 3.04, "dur": .28,
             "target": {"kind": "datum", "index": 429, "series": 0}},
        ]),
        (employer, imagine, "world-internal-memo-v1;idle=drift;drift=14", (.025, -4, 1), [],
         "door:left:0.65", [
            # Sentence response, not a decorative badge: the employer's two
            # simultaneous decisions are written as a payroll review.
            {"kind": "agenda", "at": employer, "dur": imagine - employer,
             "idle": "breath",
             "target": {"kind": "region", "x0": .54, "y0": .06, "x1": .95, "y1": .43},
             "rows": [
                 {"n": 1, "text": "PAYMENTS", "sub": "CURRENT", "at": employer},
                 {"n": 2, "text": "PROMOTION", "sub": "CANCELLED", "at": promotion},
                 {"n": 3, "text": "DEFAULTS", "sub": "NONE YET", "at": trouble},
             ]},
         ]),
        (imagine, interest, SHOP, (.035, 9, -3), [
            paper(FOLIO, at("the machine loan"), interest, x=.78, width=.27),
        ], "door:left:0.8", [
            chip("orders waiting", interest, AUDIT, "ORDERS WAITING", .73, .50),
        ]),
        (interest, promise, "world-receipt-macro-v1;idle=none", (.035, 7, -2), [], "slide:left:0.8", [
            chip("The extra interest", delay, CASH, "MONEY FOR A WORKER", .72, .28),
            chip("You delay the hire", bank_paid, AUDIT, "HIRE DELAYED", .72, .53),
            chip("But the bank gets paid", promise, CASH, "BANK PAID", .73, .28, ink="charcoal"),
        ]),
        (promise, bio, HALL, (.025, 0, -5), [], "door:left:0.8", [
            chip("Stay for three checks", bills, AUDIT, "THREE CHECKS", .50, .28, size=235, ink="charcoal"),
            chip("Your own monthly bills", bio, CASH, "START WITH YOUR BILLS", .50, .56, size=220, ink="charcoal"),
        ]),
        (bio, renewal, HALL, (0, 0, 0), [], None, [
            chip("what each payment cost", refinance, AUDIT, "WHAT DID THE PAYMENT COST?", .51, .31, size=245, ink="charcoal"),
        ], camera(bio, renewal, [.28, .61], 1.42)),
        (renewal, gives_up, "world-signature-close;idle=none", (.04, -7, 0), [
            paper(FOLIO, renewal, gives_up, x=.79, width=.27),
        ], "dip", [
            chip("from the owner to the worker", gives_up, CASH, "WORKER · CUSTOMER · SUPPLIER", .66, .25, size=245),
        ]),
        (gives_up, owner_waits, "world-lease-contracts-bound;idle=none", (.04, 6, -1), [], "blurzoom:0.8", [
            chip("old debt coming due", owner_waits, AUDIT, "OLD DEBT · NEW PRICE", .70, .37, size=235),
        ]),
        (owner_waits, washington, "world-dawn-factory-v1;idle=none", (.04, 10, -3), [], "slide:left:0.8", [
            chip("put the next purchase on hold", washington, AUDIT, "NEXT MACHINE\nON HOLD", .75, .34, size=230),
        ]),

        # Federal debt is now the subject, so the evidence ledger becomes the
        # world. Axes entry draws the one-line page; focus waits for the landing.
        (washington, debt,
         "ledger:debt-gross-history:line:429:right:axes:cut;idle=live",
         (0, 0, 0), [], "slide:left:0.8", [
             {"kind": "spotlight", "at": washington + 4.0, "dur": 1.5,
              "target": {"kind": "datum", "index": 429, "series": 0}},
         ]),
        (debt, net_interest,
         "ledger:debt-gross-history:line:429:right:axes:cut;idle=live",
         (0, 0, 0), [], None, [
             {"kind": "figure", "at": debt + 3.3, "dur": 2.0,
              "target": {"kind": "datum", "index": 429, "series": 0},
              "text": "$40T+", "sub": "gross federal debt", "color": "neg", "dy": -.9},
         ]),
        (net_interest, feedback,
         "ledger:cbo-interest-revenue:bars:1:right:axes:cut;idle=live",
         (0, 0, 0), [], "melt:throw", [
             {"kind": "spotlight", "at": net_interest + 3.1, "dur": 1.6,
              "target": {"kind": "datum", "index": 1, "series": 0}},
             {"kind": "figure", "at": cents, "dur": 1.2,
              "target": {"kind": "datum", "index": 1, "series": 0},
              "text": "$1.052T", "sub": "net interest · Oct–Aug", "color": "neg", "dy": -.9},
             {"kind": "chart_to", "at": cents + 1.3, "dur": 2.4, "to": "compare",
              "form": "melt", "then": "throw", "hold": "gone",
              "metric": {"value": 1052, "text": "$1.052T", "label": "net interest"},
              "comparator": {"value": .2171, "text": "22¢ / $1", "label": "of federal revenue"},
              "inputs": {"net_interest_usd_billions": 1052, "revenue_usd_billions": 4845},
              "derive": "net_interest_usd_billions / revenue_usd_billions",
              "source": "[DERIVED: CBO FY2026 October–August preliminary estimates · 1,052 / 4,845 = 21.71%]"},
         ]),
        (feedback, more_borrowing, "world-treasury-cash-count;idle=none", (.04, -7, 0), [], "melt:splash:plate", [
            chip("Interest itself adds", more_borrowing, CASH, "INTEREST FINANCES INTEREST", .70, .34, size=240),
        ]),
        (more_borrowing, treasury, "world-bond-prospectus;idle=none", (.035, 6, -1), [], "slide:left:0.8", [
            chip("alongside businesses like our workshop", treasury, AUDIT, "ONE MARKET FOR MONEY", .50, .31, size=240, ink="charcoal"),
        ]),

        # The yield record earns one full-stage page; focus lands on the dated
        # endpoint rather than washing light across the line.
        (treasury, lender,
         "ledger:treasury-20y-yield:line:427:right:axes:cut;idle=live",
         (0, 0, 0), [], "door:left:0.8", [
             {"kind": "spotlight", "at": treasury + 3.1, "dur": 1.8,
              "target": {"kind": "datum", "index": 427, "series": 0}},
             {"kind": "figure", "at": treasury + 3.2, "dur": 2.0,
              "target": {"kind": "datum", "index": 427, "series": 0},
              "text": ">5%", "sub": "20-year Treasury", "color": "neg", "dy": -.9},
         ]),
        (lender, why, HALL, (0, 0, 0), [
            paper(FOLIO, owner_asks, why, x=.78, width=.28),
        ], "melt:splash:plate", [
            chip("Put yourself in the lender's seat", owner_asks, AUDIT, "LENDER'S CHOICE", .48, .28, size=230, ink="charcoal"),
        ]),
        (why, investors, "world-signal-box-levers-v1;idle=none", (.04, 7, 0), [], "door:left:0.8", [
            chip("overnight target", investors, AUDIT, "OVERNIGHT", .28, .31, size=185),
            chip("price of lending for years", investors, CASH, "TWENTY YEARS", .72, .31, size=185),
        ]),
        (investors, quote, "world-trading-desk-dark;idle=none", (.035, 7, -2), [], "door:right:0.8", [
            chip("inflation, time and the risk of nonpayment", quote, AUDIT, "TIME · INFLATION · RISK", .70, .34, size=235),
        ]),
        (quote, runtime_s, SHOP, (.035, -7, -2), [
            paper(FOLIO, quote, due, x=.78, width=.29, arrive="land"),
        ], "dip", [
            chip("comes due now", signpost, CASH, "DUE NOW", .74, .28, size=230),
            chip("new borrowing cost", runtime_s, AUDIT, "CAN'T AFFORD TO WAIT", .68, .54, size=245, ink="charcoal"),
        ]),
    ]

    clipped = []
    for row in rows:
        start, end, plate, kb, docks, exit_, species, *camera_spec = row
        if start >= runtime_s:
            break
        end = min(end, runtime_s)
        docks = [(a, i, s, min(e, end), o) for dock in docks if dock is not None
                 for a, i, s, e, o in [dock] if s < end]
        normalized = []
        for item in species:
            if item is None:
                continue
            item = dict(item)
            if isinstance(item.get("dur"), (int, float)):
                item["dur"] = max(.1, min(item["dur"], end - item["at"]))
            if item.get("until", end) > end:
                item["until"] = end
            if item.get("at", start) < end:
                normalized.append(item)
        clipped.append((start, end, plate, kb, docks, exit_, normalized, *camera_spec))
    return clipped
