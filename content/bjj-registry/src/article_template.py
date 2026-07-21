"""article_template: deterministic -> generative BJJ Registry article builder.

Each tier has its own section set + angle so generated pages are NOT thin
mail-merge clones. Facts from LocationFacts are woven in; placeholders stay
typed so operators know what to verify.
"""
from __future__ import annotations

from typing import Optional

from location_facts import LocationFacts
from terminology import related_keywords, select_terms


def _count_phrase(facts: LocationFacts) -> str:
    """Banded count phrase — never prints a hard number (it would go stale as data drifts)."""
    n = facts.academy_count
    if n is None:
        return "a growing network of academies"
    if n == 1:
        return "a single academy"
    if n < 12:
        return f"a small but real scene of around {n} academies" if n >= 4 else "a handful of academies"
    if n < 25:
        return "a couple dozen academies"
    if n < 100:
        return "dozens of academies" if n < 50 else "several dozen academies"
    if n < 1000:
        return f"hundreds of academies" if n < 500 else "well over five hundred academies"
    return "over a thousand academies"


def _lineage_phrase(facts: LocationFacts) -> str:
    if not facts.lineages_present:
        return ""
    if len(facts.lineages_present) == 1:
        return f" The scene is anchored by the {facts.lineages_present[0]} lineage."
    listed = ", ".join(facts.lineages_present[:-1]) + f" and {facts.lineages_present[-1]}"
    return f" Lineages represented include {listed}."


def _academy_bullets(facts: LocationFacts) -> str:
    if not facts.top_academies:
        return ""
    out = ["Notable academies in the registry for this area include:",
           ""]
    for a in facts.top_academies:
        bits = []
        if a.lineage:
            bits.append(f"a {a.lineage}-affiliated school")
        if a.note:
            bits.append(a.note)
        suffix = f" — {'; '.join(bits)}" if bits else ""
        loc = " ".join(filter(None, [a.city, a.state])) or facts.name
        out.append(f"- **{a.name}** ({loc}){suffix}")
    out.append("")
    out.append("> Operator note: confirm each academy against live registry data before publishing; "
               "verify affiliation and location. Affiliations reflect what the school reports — not an "
               "endorsement of its instruction.")
    return "\n".join(out)


# ---------- TIER SECTION BUILDERS ----------

def _national_sections(facts: LocationFacts) -> list[tuple[str, str]]:
    sections = []
    sections.append((
        "What the National BJJ Registry Is",
        "The National BJJ Registry is a structured, publicly searchable directory of Brazilian "
        "Jiu-Jitsu academies across the United States — but it's more than a listing. After enough "
        "years on the mats you learn that not all gyms are equal: the culture, the lineage, and the "
        "way a professor approaches instruction decide whether a beginner lasts past white belt or "
        "quits in month two. This registry maps where the art is taught, who teaches it, and how the "
        "major lineages connect — so you can walk in informed instead of guessing."
    ))
    cnt = _count_phrase(facts)
    sections.append((
        "Brazilian Jiu-Jitsu Across the United States",
        f"The registry currently tracks {cnt} nationwide. BJJ has grown well past its roots as a "
        "niche self-defense system into one of the most practical, addictive arts you can train — and "
        "unlike most martial arts, it rewards consistency over raw athleticism. The 40-year-old who "
        "shows up three nights a week will out-technique the 22-year-old athlete who rolls once a "
        "month. " + _lineage_phrase(facts)
    ))
    if facts.top_cities:
        cities = ", ".join(facts.top_cities[:8])
        sections.append((
            "Where the Scene Clusters",
            f"The art pools where people have the time, money, and culture for a hobby that humbles "
            f"them weekly. The highest density shows up in metropolitan hubs such as {cities} — places "
            "with enough population to support multiple schools, active competition teams, and open "
            "mats where you can test yourself against strangers. If you're new, start where the scene "
            "is deepest: more academies means more chances to find the room that fits you."
        ))
    if facts.lineages_present:
        sections.append((
            "Lineage & Affiliation Map",
            "Brazilian Jiu-Jitsu is a lineage art. Almost every academy traces its teaching back "
            "through a chain of instructors to Carlos and Hélio Gracie and the early pioneers — and "
            "that chain matters. A Renzo Gracie or Alliance-affiliated school tends to run a "
            "structured, competition-minded curriculum; a smaller independent might prioritize "
            "self-defense, community, or a specific game. The registry captures these affiliations so "
            "you can read a school's pedagogical DNA before you ever step on the mat. "
            + _lineage_phrase(facts)
        ))
    sections.append((
        "How to Use the Registry",
        "Filter by state, city, or lineage to find academies in your area. Every listing links to the "
        "school's public profile, its class focus — gi, no-gi, competition, self-defense — and the "
        "signals that tell you whether it's a real gym or a glorified cardio class. New to the art? "
        "Don't overthink the choice. Pick a beginner-friendly class, show up consistently for a month, "
        "and let the mat tell you which room fits. Comparing two or three options before committing is "
        "smart; paralysis by analysis keeps more people off the mats than bad gyms do."
    ))
    if facts.events:
        ev = "; ".join(facts.events)
        sections.append(("National Events & Competition", f"{ev} are part of the annual cycle the registry tracks."))
    return sections


def _state_sections(facts: LocationFacts) -> list[tuple[str, str]]:
    sections = []
    loc = f"{facts.name}, {facts.state}"
    sections.append((
        f"Brazilian Jiu-Jitsu in {facts.name}",
        f"{facts.name} has built one of the more distinctive BJJ scenes in the country, and if "
        f"you've trained in more than one state you know the 'vibe' of a scene is real. The registry "
        f"tracks {_count_phrase(facts)} across the state, ranging from large competition teams to "
        "small community gyms where the professor still remembers your name. Training culture here "
        "blends traditional gi methodology with a strong no-gi and submission-grappling presence — "
        "the kind of room where a Saturday morning open mat turns into three hours of rolling. "
        + _lineage_phrase(facts)
    ))
    if facts.top_cities:
        cities = ", ".join(facts.top_cities[:10])
        sections.append((
            f"Where to Train: Top Cities in {facts.name}",
            f"The deepest concentration of academies sits in {cities}. Each city has its own character "
            "— some lean competition-heavy with a wall of tournament medals, others prioritize "
            "self-defense and family classes where kids outnumber the adult open mat. Use the registry "
            "to drill into any city for a full academy list; if you're relocating for work, the city "
            "pages are the fastest way to find your next training home before you sign a lease."
        ))
    if facts.top_academies:
        sections.append(("Notable Academies", _academy_bullets(facts)))
    if facts.events:
        ev = "; ".join(facts.events)
        sections.append((f"Competitions & Community in {facts.name}",
                         f"{facts.name} hosts {ev}, drawing competitors from across the region and "
                         "giving newer students a clear pathway from first class to first tournament — "
                         "because the fastest way to improve is to have a date on the calendar that "
                         "you can't talk yourself out of."))
    sections.append((
        f"Starting BJJ in {facts.name} as a Beginner",
        "Most schools in the registry offer a free trial or beginner intro class, and you should take "
        "them up on it. Expect to learn fundamental positions (guard, mount, side control), how to "
        "fall safely without slamming your training partner, and basic escapes that will save you a "
        "hundred times in your first year. No prior experience or fitness level is required — the "
        "white belt who shows up consistently will be tapping blue belts before the gym bro who only "
        "trains when he's not sore. Showing up matters more than athletic background."
    ))
    return sections


def _county_sections(facts: LocationFacts) -> list[tuple[str, str]]:
    sections = []
    loc = f"{facts.name}, {facts.state}"
    sections.append((
        f"BJJ Training Hubs in {loc}",
        f"At the county level, Brazilian Jiu-Jitsu in {loc} clusters around a handful of training "
        f"hubs. The registry maps {_count_phrase(facts)} here, concentrated in the cities below. "
        "This view is the one serious hobbyists actually use: if you're deciding where to live, work, "
        "or train within the region, the commute to a good open mat is a real quality-of-life factor "
        "you only appreciate after your first 5am workout."
    ))
    if facts.top_cities:
        cities = ", ".join(facts.top_cities[:10])
        sections.append((
            "Which Cities Lead",
            f"Within {loc}, {cities} account for the majority of academy density. Larger hubs tend "
            "to support multiple schools and more frequent open mats — which means more training "
            "partners, more styles to cross-train against, and faster progress. Smaller towns often "
            "have a single tight-knit academy where everyone knows your game by week three; that "
            "intimacy is either exactly what you want or a reason to drive to the city."
        ))
    if facts.top_academies:
        sections.append(("Academies in the Registry", _academy_bullets(facts)))
    sections.append((
        "Community, Open Mats & Cross-Training",
        f"The {facts.name} BJJ community is notably collaborative: open mats, seminar visits from "
        "outside instructors, and inter-academy rolls are common. Cross-training between nearby "
        "schools is how you find the holes in your game — your home academy will happily let you "
        "discover that your guard is only good against people who already know you. Train the "
        "familiar, then go get uncomfortable somewhere else."
    ))
    if facts.events:
        ev = "; ".join(facts.events)
        sections.append(("Local Events", f"{ev} anchor the local calendar."))
    return sections


def _city_sections(facts: LocationFacts) -> list[tuple[str, str]]:
    sections = []
    loc = f"{facts.name}, {facts.state}"
    sections.append((
        f"Brazilian Jiu-Jitsu in {loc}",
        f"Whether you're a complete beginner or transferring in from another gym across the country, "
        f"{loc} offers {_count_phrase(facts)} to choose from. The local scene spans family-friendly "
        "academies where the kids' class is louder than the adults', competition teams chasing IBJJF "
        "podiums, and no-gi submission-grappling rooms that feel closer to a fight camp than a "
        "dojo. " + _lineage_phrase(facts)
    ))
    if facts.top_academies:
        sections.append(("Academies in the Registry", _academy_bullets(facts)))
    sections.append((
        "Gi vs No-Gi in " + facts.name,
        "Most academies here teach both, and you should train both even if one becomes your home. "
        "The gi (the traditional uniform) is the chess match — grips, lapel control, and a slower "
        "pace that forces real technique. No-gi is faster and closer to submission grappling and MMA: "
        "without the cloth to hold, you learn to control the body itself. Beginners often start in the "
        "gi because its structure builds fundamentals you'll lean on forever, then add no-gi once their "
        "hips stop getting smashed."
    ))
    sections.append((
        f"Where to Start: Your First Class in {loc}",
        "Pick a beginner-friendly class, wear comfortable athletic clothing (or ask about a loaner "
        "gi), and arrive 10–15 minutes early so you're not the person still tying knots when the "
        "warm-up starts. A typical first class covers warm-ups, one or two fundamental techniques, "
        "and light positional drilling with a partner. You do not need to spar on day one — anyone "
        "who tells you otherwise is running a cult, not a gym. Trim your fingernails, hydrate, and "
        "bring flip-flops for the mat boundary so you're not tracking foot fungus onto the canvas."
    ))
    sections.append((
        "Kids, Adults & Trial Options",
        "Many registry academies in " + loc + " run separate kids and adults programs, with women's "
        "classes at some locations — worth knowing if you want a room where you won't be the only "
        "person who isn't a 20-year-old wrestler. Look for a free trial or intro offer so you can test "
        "the culture, the coaching, and the vibe before you commit a bank account to it."
    ))
    return sections


def _insights_section(facts: LocationFacts) -> tuple[str, str] | None:
    """Market-insight section driven by registry_region_score_aggregates_v1.

    KEY CONSTRAINT (operator preference): the published prose carries NO hard numbers.
    Scores refresh, and a printed '71.4' goes stale the moment the aggregate shifts.
    Instead we convert the metrics into qualitative bands and relative framings
    ('runs above the state average', 'a deep elite tier', 'uneven quality') that
    stay true as the underlying data drifts. The raw numbers remain in
    facts.insights as silent signal (and feed the LLM bundle) — they inform, they
    do not print.
    """
    ins = facts.insights
    if not ins or ins.get("sample_size", 0) < 3:
        return None  # too thin to make a defensible claim

    avg = ins.get("avg_registry_score")
    median = ins.get("median_registry_score")
    pct85 = ins.get("pct_85_plus")
    pct70 = ins.get("pct_70_plus")
    n = ins.get("sample_size")
    nat = ins.get("national_avg")
    parent = ins.get("state_avg") if facts.tier in ("city", "county") else ins.get("national_avg")
    parent_label = "state" if facts.tier in ("city", "county") else "national"

    loc = facts.name if facts.tier == "national" else f"{facts.name}, {facts.state or ''}".strip()

    def _band(v):
        if v is None:
            return None
        if v >= 75:
            return "strong"
        if v >= 68:
            return "solid"
        if v >= 60:
            return "moderate"
        return "developing"

    def _rel(val, base):
        if val is None or base is None:
            return None
        if val - base >= 3:
            return "above"
        if val - base <= -3:
            return "below"
        return "in line with"

    lines = [
        f"We grade every academy in the registry on a single quality signal — the same registry "
        f"score that ranks gyms in the directory. Here's how the scene in {loc} reads:",
    ]

    avg_band = _band(avg)
    rel = _rel(avg, parent)
    if avg_band and rel:
        tier_word = {
            "strong": "a genuinely strong training market",
            "solid": "a solid, dependable training market",
            "moderate": "a moderate but growing training market",
            "developing": "a developing market still finding its feet",
        }[avg_band]
        rel_word = {
            "above": f"it sits above the {parent_label} average",
            "below": f"it trails the {parent_label} average",
            "in line with": f"it tracks the {parent_label} average",
        }[rel]
        lines.append(
            f"- **Overall quality: {tier_word}** — {rel_word}, so the typical room here is "
            f"{'worth the drive' if avg_band in ('strong','solid') else 'a place to vet carefully before committing'}."
        )

    if median is not None and avg is not None:
        if median < avg - 3:
            lines.append(
                "- **Quality is uneven.** A few standout academies pull the average up, which means "
                "the scene has a clear top tier worth chasing — and a middle that needs a trial class to sort out."
            )
        elif median > avg + 3:
            lines.append(
                "- **Quality is consistent.** The median sits at or above the average, so most rooms "
                "are reliably well-run rather than propped up by one famous gym."
            )
        else:
            lines.append(
                "- **Quality is consistent.** The median tracks the average, so what you see in the "
                "directory is what you tend to get on the mats."
            )

    if pct85 is not None:
        el = "a deep elite tier" if pct85 >= 15 else ("a real elite tier" if pct85 >= 8 else "a thin elite tier")
        nat_cmp = ""
        if nat is not None:
            nat_cmp = " — richer than most of the country" if pct85 >= (nat + 3) else (" — thinner than the national picture" if pct85 <= (nat - 3) else " — in line with the national picture")
        lines.append(
            f"- **Elite depth: {el}**{nat_cmp}. If you're serious about competing, there are rooms here "
            "that train people who medal, not just survive."
        )

    if pct70 is not None:
        if pct70 >= 60:
            lines.append(
                "- **Most options clear the bar.** The large majority of academies here score as "
                "legitimate, well-run gyms — the risk of landing in a dead-end room is low."
            )
        elif pct70 >= 40:
            lines.append(
                "- **Most options are legitimate,** though a meaningful share sit in the developing "
                "range — the registry's filters and reviews will help you separate them."
            )
        else:
            lines.append(
                "- **Quality is mixed.** A meaningful share of academies are still developing, so lean "
                "on trial classes and the registry's verified listings before you commit."
            )

    lines.append("")
    lines.append(
        "> Operator note: these read as qualitative bands, not live statistics, so the article stays "
        "true as scores refresh. The underlying registry score is computed from published gym signals "
        "(verified listings, engagement, retention proxies); treat it as a directional guide, not a "
        "rating-agency verdict."
    )
    return ("Market Insights", "\n".join(lines))


def _vocab_section(facts: LocationFacts) -> tuple[str, str] | None:
    """Surface discipline-specific BJJ vocabulary so content is grounded,
    not generic 'near me' filler."""
    if facts.tier == "national":
        return None  # national uses lineage map instead
    terms = select_terms(facts.tier, limit=6)
    if not terms:
        return None
    lines = ["Specific terms you'll encounter on the mats here:"]
    for t in terms:
        lines.append(f"- **{t.term}** — {t.definition}")
    lines.append("")
    lines.append("> Operator note: confirm term usage fits your local curriculum; this is a "
                 "standard BJJ glossary, not a claim about any specific academy.")
    return ("BJJ Vocabulary You'll Hear", "\n".join(lines))


def _keyword_block(facts: LocationFacts) -> tuple[str, str]:
    kws = related_keywords(facts)
    if not kws:
        return ("", "")
    body = ("Long-tail search intents this page targets (geo + discipline specific, "
            "not generic local phrasing):\n\n" + "\n".join(f"- {k}" for k in kws))
    return ("Targeted Search Intents", body)


_SECTION_BUILDERS = {
    "national": _national_sections,
    "state": _state_sections,
    "county": _county_sections,
    "city": _city_sections,
}


def _faq(facts: LocationFacts) -> list[tuple[str, str]]:
    loc = facts.name if facts.tier == "national" else f"{facts.name}, {facts.state or ''}".strip()
    faqs = {
        "national": [
            ("What is the National BJJ Registry?",
             "A public, structured directory of Brazilian Jiu-Jitsu academies across the United States, "
             "organized by location and lineage. Think of it as a map of the scene: who's teaching where, "
             "and under which lineage — the two facts that actually predict whether a gym is worth your time."),
            ("How many BJJ academies are in the US?",
             f"The registry currently tracks {_count_phrase(facts)}. Counts move constantly as schools "
             "open, close, or rebrand, so treat the number as a live snapshot rather than gospel."),
            ("How do I find a Brazilian Jiu-Jitsu academy by state and city?",
             "Use the state and city filters to drill down to academies in your area, then compare class "
             "focus (gi, no-gi, competition, self-defense) and the community signals. Read the lineages, "
             "then visit two or three — the mat will tell you more in one roll than any website will."),
        ],
        "state": [
            (f"How many BJJ academies are in {facts.name}?",
             f"The registry lists {_count_phrase(facts)} across {facts.name}, concentrated in its major "
             "metropolitan areas. Density matters: more schools nearby means more training partners and "
             "more styles to learn from."),
            (f"Which city in {facts.name} has the most BJJ gyms?",
             (f"{facts.top_cities[0]} leads by density." if facts.top_cities else "See the city pages for the latest breakdown.")),
            (f"Is {facts.name} good for beginner BJJ?",
             "Yes. Most schools here run trial classes and beginner-focused instruction that assumes zero "
             "experience — you'll learn to survive before you learn to attack, which is exactly the right order."),
        ],
        "county": [
            (f"Where is BJJ most concentrated in {loc}?",
             (f"{facts.top_cities[0]} has the highest academy density." if facts.top_cities else "Academies are distributed across the county's cities.")),
            ("Are there open mats in the county?",
             "The local BJJ community is collaborative, with regular open mats and inter-academy training. "
             "Show up to an open mat even if you train elsewhere — rolling with strangers is how you find "
             "out what your game is actually made of."),
        ],
        "city": [
            (f"Where can I train Brazilian Jiu-Jitsu in {loc}?",
             f"The registry lists {_count_phrase(facts)} in {loc}, from beginner-friendly gyms to "
             "competition teams. Don't pick on Google stars alone — visit, roll, and see which room respects "
             "you as a white belt."),
            (f"Do I need experience to start BJJ in {facts.name}?",
             "No. Beginner classes assume no prior training; you'll learn fundamentals and drill with a "
             "partner on day one. The only prerequisite is showing up with an open mind and trimmed nails."),
            (f"What should I bring to my first BJJ class in {loc}?",
             "Comfortable athletic clothing or a loaner gi, trimmed nails, a water bottle, and flip-flops "
             "for the mat edge. Leave your ego in the car — every black belt started where you're starting."),
            (f"How much does BJJ cost in {loc}?",
             "Pricing varies by academy; many offer a free trial or intro offer so you can evaluate the "
             "culture before paying. If a gym won't let you watch or try a class, that's your answer."),
        ],
    }
    return faqs.get(facts.tier, [])


def build_article(facts: LocationFacts, brand: str = "National BJJ Registry") -> dict:
    """Return a dict with title, meta, h1, markdown body, faq, and JSON-LD."""
    builder = _SECTION_BUILDERS.get(facts.tier)
    if builder is None:
        raise ValueError(f"Unknown tier: {facts.tier}")
    sections = builder(facts)
    faqs = _faq(facts)

    h1 = {
        "national": "The National BJJ Registry: Mapping Brazilian Jiu-Jitsu Across the United States",
        "state": f"Brazilian Jiu-Jitsu in {facts.name}: Academies, Lineages & Where to Train",
        "county": f"BJJ in {facts.name}, {facts.state}: Training Hubs, Academies & Community",
        "city": f"Brazilian Jiu-Jitsu in {facts.name}, {facts.state}: Where to Start Training",
    }[facts.tier]

    lede = facts.intro_hook or {
        "national": "A complete, searchable map of where Brazilian Jiu-Jitsu is taught across America — built for students, coaches, and the curious newcomer who'd rather walk in informed than guess.",
        "state": f"Everything you need to understand the {facts.name} Brazilian Jiu-Jitsu scene before you commit: where the academies cluster, which lineages run the rooms, and exactly how to take your first class without looking lost.",
        "county": f"A county-level view of BJJ in {facts.name}, {facts.state} — the cities that lead the scene, the academies worth knowing, and the open-mat community that ties a region together.",
        "city": f"A no-fluff guide to starting Brazilian Jiu-Jitsu in {facts.name}, {facts.state}: named academies, the gi-vs-no-gi call, and what actually happens on your first day on the mat.",
    }[facts.tier]

    # Breadcrumb + internal links
    crumbs = facts.breadcrumb()
    crumb_md = " › ".join(f"[{label}](/{slug})" for label, slug in crumbs[:-1]) + f" › {crumbs[-1][0]}"

    body = [f"*Part of the {brand}.*", "", crumb_md, "", f"# {h1}", "", f"> {lede}", ""]
    for title, text in sections:
        body.append(f"## {title}")
        body.append("")
        body.append(text)
        body.append("")
    insights = _insights_section(facts)
    if insights:
        body.append(f"## {insights[0]}")
        body.append("")
        body.append(insights[1])
        body.append("")
    vocab = _vocab_section(facts)
    if vocab:
        body.append(f"## {vocab[0]}")
        body.append("")
        body.append(vocab[1])
        body.append("")
    kw = _keyword_block(facts)
    if kw[0]:
        body.append(f"## {kw[0]}")
        body.append("")
        body.append(kw[1])
        body.append("")
    if faqs:
        body.append("## Frequently Asked Questions")
        body.append("")
        for q, a in faqs:
            body.append(f"### {q}")
            body.append("")
            body.append(a)
            body.append("")
    body.append("---")
    body.append("")
    body.append(f"*Listing data is maintained by the {brand}. Verify academy details directly with "
                "each school before enrolling.*")

    # Child links
    child_links = ""
    if facts.child_slugs:
        child_links = "\n\n**Explore further:**\n" + "\n".join(
            f"- [{(s.replace('-', ' ').title())}](/{s})" for s in facts.child_slugs
        )

    markdown = "\n".join(body) + child_links

    jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1,
        "description": facts.meta_description(),
        "publisher": {"@type": "Organization", "name": brand},
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"/{facts.slug}"},
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": label, "item": f"/{slug}"}
                for i, (label, slug) in enumerate(crumbs)
            ],
        },
    }

    return {
        "tier": facts.tier,
        "slug": facts.slug,
        "title_tag": facts.title_tag(brand),
        "meta_description": facts.meta_description(),
        "h1": h1,
        "markdown": markdown,
        "faq": faqs,
        "jsonld": jsonld,
        "verified": facts.academy_count_verified or any(a.verified for a in facts.top_academies),
    }


def build_article_llm(facts: LocationFacts, brand: str = "National BJJ Registry",
                      cfg=None) -> dict:
    """LLM-rendered variant of build_article.

    The LLM rewrites only the per-tier section *bodies* (the parts where voice
    matters). Structure, insights, vocab, keywords, FAQ, and JSON-LD stay
    deterministic/template-controlled. If the LLM fails or the guard rejects the
    output, this raises RuntimeError so the caller can fall back to build_article.
    """
    from fact_bundle import build_bundle
    from llm_writer import render_sections
    from llm_guard import guard

    builder = _SECTION_BUILDERS.get(facts.tier)
    if builder is None:
        raise ValueError(f"Unknown tier: {facts.tier}")
    sections = builder(facts)
    headings = [title for title, _ in sections]

    bundle = build_bundle(facts)
    prose = render_sections(bundle, headings, cfg=cfg)
    if not prose:
        raise RuntimeError("llm_writer returned no prose")
    ok, reason = guard(bundle, prose)
    if not ok:
        raise RuntimeError(f"llm_guard rejected output: {reason}")

    # Splice LLM prose into the deterministic structure (heading order preserved)
    prose_by_heading = _parse_llm_sections(prose)
    new_sections = []
    for title, _ in sections:
        body = prose_by_heading.get(title, sections_dict_get(sections, title))
        new_sections.append((title, body))

    # Rebuild via the same pipeline but with swapped section bodies.
    return _assemble(facts, new_sections, brand)


def sections_dict_get(sections, title):
    for t, b in sections:
        if t == title:
            return b
    return ""


def _parse_llm_sections(prose: str) -> dict[str, str]:
    """Parse '## Heading\\n<body>' blocks from LLM output into {heading: body}."""
    out: dict[str, str] = {}
    cur = None
    buf = []
    for line in prose.splitlines():
        if line.startswith("## "):
            if cur is not None:
                out[cur] = "\n".join(buf).strip()
            cur = line[3:].strip()
            buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf).strip()
    return out


def _assemble(facts: LocationFacts, sections: list[tuple[str, str]], brand: str) -> dict:
    """Build the full article dict from pre-rendered section bodies.

    Mirrors build_article's assembly (breadcrumb, lede, insights, vocab, keywords,
    FAQ, JSON-LD) but uses `sections` instead of calling the builder again.
    """
    faqs = _faq(facts)
    crumbs = facts.breadcrumb()
    crumb_md = " > ".join(f"[{label}](/{slug})" for label, slug in crumbs)
    lede = _lede_for(facts)

    body = [f"*Part of the {brand}.*", "", crumb_md, "", f"# {_h1_for(facts)}", "", f"> {lede}", ""]
    for title, text in sections:
        body.append(f"## {title}")
        body.append("")
        body.append(text)
        body.append("")
    insights = _insights_section(facts)
    if insights:
        body.append(f"## {insights[0]}")
        body.append("")
        body.append(insights[1])
        body.append("")
    vocab = _vocab_section(facts)
    if vocab:
        body.append(f"## {vocab[0]}")
        body.append("")
        body.append(vocab[1])
        body.append("")
    kw = _keyword_block(facts)
    if kw[0]:
        body.append(f"## {kw[0]}")
        body.append("")
        body.append(kw[1])
        body.append("")
    if faqs:
        body.append("## Frequently Asked Questions")
        body.append("")
        for q, a in faqs:
            body.append(f"### {q}")
            body.append("")
            body.append(a)
            body.append("")
    body.append("---")
    body.append("")
    body.append(f"*Listing data is maintained by the {brand}. Verify academy details directly with "
                "each school before enrolling.*")

    child_links = ""
    if facts.child_slugs:
        child_links = "\n\n**Explore further:**\n" + "\n".join(
            f"- [{(s.replace('-', ' ').title())}](/{s})" for s in facts.child_slugs
        )
    markdown = "\n".join(body) + child_links

    h1 = _h1_for(facts)
    crumbs = facts.breadcrumb()
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1,
        "description": facts.meta_description(),
        "publisher": {"@type": "Organization", "name": brand},
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": label, "item": f"/{slug}"}
                for i, (label, slug) in enumerate(crumbs)
            ],
        },
    }
    return {
        "tier": facts.tier,
        "slug": facts.slug,
        "title_tag": facts.title_tag(brand),
        "meta_description": facts.meta_description(),
        "h1": h1,
        "markdown": markdown,
        "faq": faqs,
        "jsonld": jsonld,
        "verified": facts.academy_count_verified or any(a.verified for a in facts.top_academies),
    }


def _lede_for(facts: LocationFacts) -> str:
    return facts.intro_hook or {
        "national": "A complete, searchable map of where Brazilian Jiu-Jitsu is taught across America — built for students, coaches, and the curious newcomer who'd rather trust a structured registry than a random Google result.",
        "state": f"A no-fluff guide to Brazilian Jiu-Jitsu in {facts.name}: where the academies cluster, which lineages run deep, and how a beginner actually gets started on the mats.",
        "county": f"The BJJ training hubs across {facts.name}, {facts.state}: which cities lead, what the local academies offer, and where the open-mat community actually trains.",
        "city": f"Where to start Brazilian Jiu-Jitsu in {facts.name}, {facts.state} — named academies, gi versus no-gi, and what your first class actually looks like.",
    }[facts.tier]


def _h1_for(facts: LocationFacts) -> str:
    return {
        "national": "The National BJJ Registry: Mapping Brazilian Jiu-Jitsu Across the United States",
        "state": f"Brazilian Jiu-Jitsu in {facts.name}: Academies, Lineages & Where to Train",
        "county": f"BJJ in {facts.name}, {facts.state}: Training Hubs, Academies & Community",
        "city": f"Brazilian Jiu-Jitsu in {facts.name}, {facts.state}: Where to Start Training",
    }[facts.tier]


def _token(value: Optional[str]) -> Optional[str]:
    """Mirror the registry import script's token() normalization:
    lowercase, strip every non-alphanumeric character."""
    if not value:
        return None
    norm = "".join(ch for ch in str(value).lower() if ch.isalnum())
    return norm or None


def build_blog_row(facts: LocationFacts, brand: str = "National BJJ Registry") -> dict:
    """Return a registry-compatible programmatic-blog JSONL row.

    Matches scripts/import-programmatic-blog-posts.mjs expectations so the
    output drops straight into `public.blog_posts` and cascades through
    `registry_internal.registry_blog_distribution_current` to the correct
    national/state/county/city/market/zip/neighborhood/gym surfaces.

    Distribution mapping (mirrors BLOG_DISTRIBUTION_CASCADE.md):
      national -> scope_type national
      state    -> scope_type state,  state_code
      county   -> scope_type county, state_code + county_token
      city     -> scope_type city,   state_code + city_token
    """
    article = build_article(facts, brand)
    distribution: dict = {"scope_type": facts.tier}
    if facts.tier == "state":
        distribution["state_code"] = (facts.state or "").upper()
    elif facts.tier == "county":
        distribution["state_code"] = (facts.state or "").upper()
        distribution["county_token"] = _token(facts.county)
    elif facts.tier == "city":
        distribution["state_code"] = (facts.state or "").upper()
        distribution["city_token"] = _token(facts.city)

    # Editorial/category targeting keeps generated articles from flooding
    # every gym site (review rule: don't duplicate generic BJJ copy).
    if facts.tier == "national":
        distribution["target_page_keys"] = ["beginners"]
        distribution["target_topic_tokens"] = ["beginner", "whitebelt", "curriculum"]
    elif facts.tier in ("state", "county", "city"):
        distribution["target_topic_tokens"] = ["beginner"]

    row = {
        "slug": article["slug"],
        "title": article["title_tag"],
        "excerpt": article["meta_description"],
        "content_md": article["markdown"],
        "cover_image": None,
        "tenant_id": None,
        "metadata": {
            "content_type": "registry_editorial",
            "distribution": distribution,
        },
    }
    return row
