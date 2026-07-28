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
