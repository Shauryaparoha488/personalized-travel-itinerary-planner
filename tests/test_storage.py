from datetime import date

from src.itinerary import (
    Accommodation,
    DietaryPreference,
    ItineraryRequest,
    generate_demo_itinerary,
    update_day,
)
from src.storage import SupabaseStore


class Response:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, rows):
        self.rows = rows
        self.payload = None
        self.query_id = None

    def upsert(self, payload, **kwargs):
        self.payload = payload
        return self

    def select(self, _columns):
        return self

    def eq(self, _column, value):
        self.query_id = value
        return self

    def limit(self, _count):
        return self

    def execute(self):
        if self.payload:
            self.rows[self.payload["id"]] = self.payload
            return Response([self.payload])
        row = self.rows.get(self.query_id)
        return Response([row] if row else [])


class FakeClient:
    def __init__(self):
        self.rows = {}

    def table(self, _name):
        return FakeTable(self.rows)


def test_supabase_store_round_trips_request_and_plan():
    request = ItineraryRequest(
        destination="Kochi", origin=None, days=2, travelers=1, budget_inr=20000,
        preferences=["Nature", "Food"], accommodation=Accommodation.BUDGET,
        dietary=DietaryPreference.VEGAN, start_date=date(2027, 1, 5),
    )
    plan = generate_demo_itinerary(request)
    store = SupabaseStore("https://example.supabase.co", "test-secret", FakeClient())
    saved_id = store.save(request, plan)
    loaded_request, loaded_plan = store.load(saved_id)
    assert loaded_request == request
    assert loaded_plan == plan
    edited_plan = update_day(plan, 1, {"title": "Saved edit"})
    store.save(request, edited_plan, saved_id)
    _, reloaded_plan = store.load(saved_id)
    assert reloaded_plan.days[0].title == "Saved edit"


def test_supabase_store_rejects_malformed_id():
    store = SupabaseStore("https://example.supabase.co", "test-secret", FakeClient())
    try:
        store.load("not-a-uuid")
    except ValueError as error:
        assert "valid saved itinerary ID" in str(error)
    else:
        raise AssertionError("Expected a malformed ID to be rejected")
