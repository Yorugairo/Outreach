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
