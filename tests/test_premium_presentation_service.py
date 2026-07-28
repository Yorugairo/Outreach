from src.services.premium_presentation_service import PremiumPresentationService


def test_comparison_slide_keeps_target_first_and_drops_certified() -> None:
    service = PremiumPresentationService()
    evidence = {
        "target": {"run_id": "nova", "domain": "novaryu.com", "display_name": "Nova Ryu BJJ"},
        "market": {
            "comparison_rows": [
                {"run_id": "certified", "domain": "certifiedmartialartsacadamey.com", "name": "Certified Martial Arts Academy"},
                {"run_id": "nova", "domain": "novaryu.com", "name": "Nova Ryu BJJ"},
                {"run_id": "defiance", "domain": "defiancebjj.com", "name": "Defiance BJJ"},
                {"run_id": "legend", "domain": "legendjiujitsu.com", "name": "Legend Jiu Jitsu"},
            ]
        },
    }

    rows = service._comparison_display_rows(evidence)

    assert [row["name"] for row in rows] == ["Nova Ryu BJJ", "Defiance BJJ", "Legend Jiu Jitsu"]


def test_comparison_matrix_aligns_values_to_filtered_columns() -> None:
    service = PremiumPresentationService()
    bundles = [
        {
            "run_id": "nova",
            "domain": "novaryu.com",
            "market": {"rankings": {"organic": [{"keyword": "bjj tacoma", "position": 9}]}}},
        {
            "run_id": "certified",
            "domain": "certifiedmartialartsacadamey.com",
            "market": {"rankings": {"organic": [{"keyword": "bjj tacoma", "position": 16}]}}},
        {
            "run_id": "defiance",
            "domain": "defiancebjj.com",
            "market": {"rankings": {"organic": [{"keyword": "bjj tacoma", "position": 3}]}}},
        {
            "run_id": "legend",
            "domain": "legendjiujitsu.com",
            "market": {"rankings": {"organic": [{"keyword": "bjj tacoma", "position": 7}]}}},
    ]
    evidence = {
        "target": bundles[0],
        "competitors": bundles[1:],
        "market": {"organic": [{"keyword": "bjj tacoma"}], "maps": []},
    }
    rows = [
        {"run_id": "nova", "domain": "novaryu.com", "name": "Nova Ryu BJJ"},
        {"run_id": "defiance", "domain": "defiancebjj.com", "name": "Defiance BJJ"},
        {"run_id": "legend", "domain": "legendjiujitsu.com", "name": "Legend Jiu Jitsu"},
    ]

    matrix = service._comparison_keyword_matrix(evidence, rows)

    assert matrix[0]["observations"] == [
        {"organic": 9, "maps": None},
        {"organic": 3, "maps": None},
        {"organic": 7, "maps": None},
    ]


def test_ai_slide_uses_customer_facing_answer_readiness_copy() -> None:
    html = PremiumPresentationService()._ai_slide({"ai_score": 64})

    assert "Make Nova the answer" in html
    assert "when students search" in html
    assert "books a first class" in html
    assert "not a claim" not in html


def test_organic_slide_names_the_program_surface_gap() -> None:
    html = PremiumPresentationService()._rankings_slide(
        "Tacoma organic rankings",
        "A location-focused website lacking",
        "ranked program surfaces",
        [],
        "2026-07-27",
    )

    assert "A location-focused website lacking" in html
    assert "ranked program surfaces" in html
    assert "program pages new students need" in html


def test_mobile_comparison_keeps_nova_and_drops_only_legend() -> None:
    css = PremiumPresentationService._responsive_overrides()

    assert "#slide-9 .rank-table th:nth-child(2)" in css
    assert "display: table-cell !important" in css
    assert "#slide-9 .rank-table th:nth-child(4)" in css
    assert "display: none !important" in css
