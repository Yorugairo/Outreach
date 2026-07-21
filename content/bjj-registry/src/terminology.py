"""terminology.py — controlled BJJ vocabulary + keyword/intent mapping.

Purpose: ground generated pSEO content in SPECIFIC Brazilian Jiu-Jitsu
lexicon and long-tail keywords instead of generic SEO filler
(e.g. "BJJ near me", "martial arts classes").

Everything here is a factual vocabulary — no academy counts, rankings, or
stats are invented. Extend the lists as the registry's taxonomy grows.

Design:
- BJJ_TERMS: a reviewed glossary; `tiers` controls where each term surfaces.
- KEYWORD_INTENTS: intent -> specific long-tail phrase templates using
  {city}/{state} placeholders. These REPLACE vague "near me" phrasing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Term:
    term: str
    category: str           # position|submission|technique|gear|training_type|competition|rank|culture
    definition: str         # short, factual
    tiers: tuple            # which tiers naturally surface this term
    usage: str              # an example sentence fragment (operator-editable)


# Reviewed BJJ glossary. Categories map to what a newcomer actually encounters.
BJJ_TERMS = [
    Term("guard", "position",
         "A ground position where you're on your back controlling an opponent with your legs, framing distance and setting up submissions.",
         ("city", "county"), "You'll spend early classes learning to retain and play guard."),
    Term("mount", "position",
         "A dominant ground position where you sit on your opponent's chest, maximizing control and strike/submission threat.",
         ("city", "county"), "Escaping the mount is a core beginner defensive skill."),
    Term("side control", "position",
         "A pinning position where you lie perpendicular across your opponent's torso, limiting their movement.",
         ("city",), "Side control is where many positional escapes are drilled."),
    Term("back control", "position",
         "A dominant position behind your opponent's back, often with hooks, setting up the rear-naked choke.",
         ("city",), "Back control is the highest-scoring position in competition."),
    Term("half guard", "position",
         "A guard variation where you trap one of your opponent's legs, used to sweep or recover full guard.",
         ("city",), "Half guard is a common entry point from bottom positions."),
    Term("rear-naked choke", "submission",
         "A choke applied from the back using arms around the neck; the most reliable finish from back control.",
         ("city", "state"), "The rear-naked choke is the signature back-control submission."),
    Term("triangle choke", "submission",
         "A blood choke using the legs around the opponent's neck and one arm, forming a triangle with the thighs.",
         ("city",), "The triangle is a guard-based submission taught early."),
    Term("armbar", "submission",
         "A joint lock extending the elbow, typically applied from guard, mount, or back.",
         ("city", "state"), "The armbar is foundational across gi and no-gi."),
    Term("kimura", "submission",
         "A shoulder/elbow lock applied with a figure-four grip on the wrist, effective from many positions.",
         ("city",), "The kimura is a versatile shoulder lock from side and guard."),
    Term("guillotine", "submission",
         "A front headlock choke commonly used on stands-up takedown attempts or from top positions.",
         ("city",), "The guillotine is a frequent standing and turtle submission."),
    Term("heel hook", "submission",
         "A leg lock attacking the knee by rotating the heel; predominantly a no-gi submission with strict safety rules.",
         ("city", "state"), "Heel hooks are a no-gi specialty governed by belt/skill restrictions."),
    Term("sweep", "technique",
         "A movement from the bottom that reverses positions, putting you on top.",
         ("city",), "Sweeps let you go from defensive guard to dominant top."),
    Term("shrimp / hip escape", "technique",
         "A foundational movement that creates space by driving the hips away, used to escape pins.",
         ("city",), "The shrimp (hip escape) is drilled in nearly every first class."),
    Term("bridge", "technique",
         "An explosive hip drive used to displace a top opponent from mount or side control.",
         ("city",), "Bridging is a primal escape taught in week one."),
    Term("gi", "gear",
         "The traditional uniform (jacket, pants, belt) used in gi BJJ; grips on the cloth enable control and submissions.",
         ("city", "state", "national"), "Training in the gi builds grips, patience, and technical control."),
    Term("no-gi", "gear",
         "Training without the uniform, in rashguard and shorts; emphasizes body-control grips and submission grappling.",
         ("city", "state", "national"), "No-gi submission grappling is faster and closer to MMA."),
    Term("rashguard", "gear",
         "A tight athletic shirt worn in no-gi to reduce friction and skin contact.",
         ("city",), "You'll wear a rashguard and shorts for no-gi sessions."),
    Term("belt ranks", "rank",
         "Progression from white through blue, purple, brown, to black belt, earned over years of consistent training.",
         ("city", "state"), "Belt rank reflects time, skill, and mat hours, not athleticism alone."),
    Term("open mat", "training_type",
         "Unstructured training time for free rolling and cross-training with partners from any class.",
         ("city", "county"), "Open mats build community and let you test skills live."),
    Term("rolling", "training_type",
         "Live sparring practice against a resisting partner, the core of BJJ skill development.",
         ("city",), "Most classes end with several rounds of rolling."),
    Term("drilling", "training_type",
         "Repetitive practice of a technique with a cooperative partner to build muscle memory.",
         ("city",), "Drilling precedes rolling so techniques become reflexive."),
    Term("competition team", "training_type",
         "A group within an academy focused on tournament preparation and rules-specific training.",
         ("city", "state"), "Competition teams train explicitly for tournament rulesets."),
    Term("self-defense", "training_type",
         "Curriculum emphasizing escapes, control, and containment for real-world scenarios.",
         ("city", "state"), "Self-defense tracks focus on pragmatic escapes and control."),
    Term("IBJJF", "competition",
         "The International Brazilian Jiu-Jitsu Federation, governing the largest gi tournament circuit worldwide.",
         ("state", "national"), "IBJJF rules shape much of traditional gi competition."),
    Term("NAGA", "competition",
         "A large grappling organization running both gi and no-gi tournaments across the US.",
         ("state", "national"), "NAGA events are common regional no-gi and gi competitions."),
    Term("ADCC", "competition",
         "The premier invitation-only no-gi submission grappling championship.",
         ("state", "national"), "ADCC sets the standard for elite no-gi rulesets."),
    Term("lineage", "culture",
         "The instructor-to-instructor chain tracing a school's teaching back to the Gracie pioneers.",
         ("state", "national"), "Lineage tells you a school's pedagogical DNA."),
    Term("affiliation", "culture",
         "A school's formal tie to a larger team or brand (e.g. Gracie Barra, Atos) for curriculum and events.",
         ("state", "national"), "Affiliation often brings standardized curriculum and seminars."),
    Term("professor", "culture",
         "The title for a BJJ instructor (typically brown/black belt) who leads technical instruction.",
         ("city",), "Your professor guides curriculum and belt progression."),
]


# Intent -> specific long-tail keyword templates. {city}/{state} filled at render.
# These REPLACE vague "near me" phrasing with discipline + geo specificity.
KEYWORD_INTENTS = {
    "national": [
        "Brazilian Jiu-Jitsu academies in the United States",
        "IBJJF affiliated BJJ schools USA",
        "Gracie lineage Brazilian Jiu-Jitsu directory",
        "where to train BJJ in America",
    ],
    "state": [
        "{state} Brazilian Jiu-Jitsu academies",
        "{state} no-gi submission grappling competition",
        "{state} IBJJF affiliated BJJ schools",
        "best BJJ gyms in {state}",
        "{state} Gi and No-Gi tournament schedule",
    ],
    "county": [
        "Brazilian Jiu-Jitsu in {county}, {state}",
        "{county} no-gi open mat sessions",
        "BJJ academies in {county} {state}",
        "where to roll in {county} {state}",
    ],
    "city": [
        "Brazilian Jiu-Jitsu academy in {city}, {state}",
        "no-gi submission grappling in {city} {state}",
        "gi fundamentals beginner class {city}",
        "competition team {city} {state}",
        "kids jiu jitsu {city}",
        "women's BJJ {city}",
        "self-defense martial arts {city} {state}",
        "{city} {state} Brazilian Jiu-Jitsu academy reviews",
    ],
}


def select_terms(tier: str, limit: int = 6) -> list[Term]:
    """Return the glossary terms most relevant to a tier."""
    picked = [t for t in BJJ_TERMS if tier in t.tiers]
    # Stable, deterministic order; cap to limit for readability
    return picked[:limit]


def related_keywords(facts) -> list[str]:
    """Render the intent-specific long-tail keywords for a location."""
    templates = KEYWORD_INTENTS.get(facts.tier, [])
    out = []
    for tpl in templates:
        out.append(tpl.format(
            city=facts.city or facts.name,
            state=facts.state or "",
            county=facts.county or "",
        ).strip())
    return out
