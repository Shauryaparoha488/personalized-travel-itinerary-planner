"""Server-side persistence for saved travel itineraries in Supabase."""

from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID, uuid4

from src.itinerary import (
    Accommodation,
    DietaryPreference,
    Itinerary,
    ItineraryRequest,
)


class SupabaseStore:
    """Small Supabase Data API wrapper using a server-only secret key."""

    table_name = "travel_itineraries"

    def __init__(self, url: str, secret_key: str, client: Any | None = None):
        if not url.strip() or not secret_key.strip():
            raise ValueError("Supabase URL and server secret key are required.")
        if client is None:
            try:
                from supabase import create_client
            except ImportError as exc:
                raise RuntimeError("Supabase support is not installed. Install requirements.txt.") from exc
            client = create_client(url.strip(), secret_key.strip())
        self.client = client

    def save(self, request: ItineraryRequest, plan: Itinerary, record_id: str | None = None) -> str:
        """Insert a new plan or update the plan identified by its unguessable ID."""
        identifier = str(UUID(record_id)) if record_id else str(uuid4())
        payload = {
            "id": identifier,
            "destination": request.destination,
            "trip_request": {
                "destination": request.destination,
                "origin": request.origin,
                "days": request.days,
                "travelers": request.travelers,
                "budget_inr": request.budget_inr,
                "preferences": request.preferences,
                "accommodation": request.accommodation.value,
                "dietary": request.dietary.value,
                "start_date": request.start_date.isoformat() if request.start_date else None,
            },
            "itinerary": plan.model_dump(mode="json"),
        }
        try:
            self.client.table(self.table_name).upsert(payload, on_conflict="id").execute()
        except Exception as exc:
            raise RuntimeError("Could not save this itinerary to Supabase. Check your Supabase setup and try again.") from exc
        return identifier

    def load(self, record_id: str) -> tuple[ItineraryRequest, Itinerary] | None:
        """Load one plan by ID. The ID acts as a private retrieval link."""
        try:
            identifier = str(UUID(record_id.strip()))
        except (ValueError, AttributeError) as exc:
            raise ValueError("Enter a valid saved itinerary ID.") from exc
        try:
            response = (
                self.client.table(self.table_name)
                .select("id, trip_request, itinerary")
                .eq("id", identifier)
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise RuntimeError("Could not load this itinerary from Supabase. Check your Supabase setup and try again.") from exc
        rows = response.data or []
        if not rows:
            return None
        row = rows[0]
        request_data = row["trip_request"]
        start_date = request_data.get("start_date")
        request = ItineraryRequest(
            destination=request_data["destination"],
            origin=request_data.get("origin"),
            days=int(request_data["days"]),
            travelers=int(request_data["travelers"]),
            budget_inr=int(request_data["budget_inr"]),
            preferences=list(request_data.get("preferences", [])),
            accommodation=Accommodation(request_data["accommodation"]),
            dietary=DietaryPreference(request_data["dietary"]),
            start_date=date.fromisoformat(start_date) if start_date else None,
        )
        return request, Itinerary.model_validate(row["itinerary"])
