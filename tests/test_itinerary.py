from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from src.itinerary import (
    Accommodation,
    DietaryPreference,
    ItineraryRequest,
    generate_demo_itinerary,
    generate_gemini_itinerary,
    markdown_itinerary,
    update_day,
    validate_request,
    _make_itinerary,
)


def request(**overrides):
    values = dict(destination="Jaipur", origin="Mumbai", days=3, travelers=2, budget_inr=50000,
                  preferences=["Culture", "Food"], accommodation=Accommodation.COMFORT,
                  dietary=DietaryPreference.VEGETARIAN, start_date=date.today() + timedelta(days=30))
    values.update(overrides)
    return ItineraryRequest(**values)


def test_valid_request_has_no_errors():
    assert validate_request(request()) == []


@pytest.mark.parametrize("changes", [
    {"destination": ""}, {"days": 0}, {"days": 15}, {"travelers": 0}, {"budget_inr": 999},
    {"start_date": date.today() - timedelta(days=1)},
])
def test_invalid_request_returns_message(changes):
    assert validate_request(request(**changes))


def test_demo_plan_and_budget_are_complete():
    req = request()
    plan = generate_demo_itinerary(req)
    assert len(plan.days) == req.days
    assert [day.day for day in plan.days] == [1, 2, 3]
    assert all(day.morning.title and day.afternoon.title and day.evening.title for day in plan.days)
    assert plan.budget.total == sum(plan.budget.categories.values())
    assert plan.budget.total > 0


def test_markdown_contains_costs_and_daily_sections():
    req = request()
    output = markdown_itinerary(req, generate_demo_itinerary(req))
    assert "Estimated budget" in output
    assert "## Day 1" in output and "## Day 3" in output
    assert "Remaining" in output


def test_gemini_missing_key_is_actionable(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        generate_gemini_itinerary(request())


def test_incomplete_ai_response_is_rejected():
    req = request(days=1)
    with pytest.raises(ValueError, match="incomplete or invalid"):
        _make_itinerary(req, {"title": "Trip"}, "ai")


def test_day_edits_are_validated_and_preserve_other_days():
    req = request()
    plan = generate_demo_itinerary(req)
    updated = update_day(plan, 1, {"title": "A custom day", "local_food": "A vegetarian thali"})
    assert updated.days[0].title == "A custom day"
    assert updated.days[0].local_food == "A vegetarian thali"
    assert updated.days[0].attraction == plan.days[0].attraction
    assert updated.days[1] == plan.days[1]
    with pytest.raises(ValueError, match="unsupported"):
        update_day(plan, 1, {"day": 2})


def test_day_edit_rejects_empty_activity_title():
    plan = generate_demo_itinerary(request())
    with pytest.raises(ValidationError):
        update_day(plan, 1, {"morning": {"title": "", "description": "Keep this description valid."}})
