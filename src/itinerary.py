"""Validated itinerary models, cost estimates, Gemini generation, and formatting."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class Accommodation(str, Enum):
    BUDGET = "Budget stay"
    COMFORT = "Comfort hotel"
    PREMIUM = "Premium stay"


class DietaryPreference(str, Enum):
    ANY = "No preference"
    VEGETARIAN = "Vegetarian"
    VEGAN = "Vegan"
    JAIN = "Jain"
    OTHER = "Other dietary needs"


@dataclass
class ItineraryRequest:
    destination: str
    origin: str | None
    days: int
    travelers: int
    budget_inr: int
    preferences: list[str]
    accommodation: Accommodation
    dietary: DietaryPreference
    start_date: date | None = None


class Activity(BaseModel):
    title: str = Field(min_length=2)
    description: str = Field(min_length=8)


class DayPlan(BaseModel):
    day: int = Field(ge=1)
    title: str
    description: str
    morning: Activity
    afternoon: Activity
    evening: Activity
    local_food: str
    tip: str


class BudgetEstimate(BaseModel):
    transport: int = Field(ge=0)
    accommodation: int = Field(ge=0)
    food: int = Field(ge=0)
    activities: int = Field(ge=0)
    miscellaneous: int = Field(ge=0)
    assumptions: str

    @property
    def categories(self) -> dict[str, int]:
        return {"transport": self.transport, "accommodation": self.accommodation, "food": self.food, "activities": self.activities, "miscellaneous": self.miscellaneous}

    @property
    def total(self) -> int:
        return sum(self.categories.values())



class Itinerary(BaseModel):
    title: str
    summary: str
    days: list[DayPlan]
    budget: BudgetEstimate
    source: str = "ai"


def validate_request(request: ItineraryRequest) -> list[str]:
    """Return user-friendly validation errors for a trip request."""
    errors: list[str] = []
    if not request.destination or len(request.destination) > 80:
        errors.append("Enter a destination between 1 and 80 characters.")
    if not 1 <= request.days <= 14:
        errors.append("Trip length must be between 1 and 14 days.")
    if not 1 <= request.travelers <= 12:
        errors.append("Travelers must be between 1 and 12.")
    if request.budget_inr < 1000:
        errors.append("Budget must be at least ₹1,000.")
    if request.start_date and request.start_date < date.today():
        errors.append("Start date cannot be in the past.")
    return errors


def _estimate_budget(request: ItineraryRequest) -> BudgetEstimate:
    """Create a transparent baseline estimate; this is not a market quote."""
    per_person_day = {Accommodation.BUDGET: 1800, Accommodation.COMFORT: 3500, Accommodation.PREMIUM: 7500}[request.accommodation]
    people = request.travelers
    stay = int(per_person_day * request.days * people * 0.42)
    food = int(900 * request.days * people)
    activities = int(700 * request.days * people)
    transport = int(request.budget_inr * 0.18) if request.origin else int(request.budget_inr * 0.08)
    misc = int(request.budget_inr * 0.08)
    return BudgetEstimate(transport=transport, accommodation=stay, food=food, activities=activities, miscellaneous=misc,
                          assumptions=f"Planning estimate for {people} traveler(s), {request.days} day(s), {request.accommodation.value.lower()}; transport is a rough allowance based on whether an origin was entered.")


def _make_itinerary(request: ItineraryRequest, payload: dict[str, Any], source: str) -> Itinerary:
    try:
        result = Itinerary.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("The itinerary response was incomplete or invalid. Please try again.") from exc
    if len(result.days) != request.days or [d.day for d in result.days] != list(range(1, request.days + 1)):
        raise ValueError("The itinerary did not include each requested day. Please try again.")
    result.source = source
    return result


def generate_demo_itinerary(request: ItineraryRequest) -> Itinerary:
    """Build a deterministic demo plan without network access or credentials."""
    descriptions = [
        ("Get oriented", "Explore a walkable neighborhood and note places you may want to revisit.", "Choose a relaxed local café for breakfast.", "Ask locally about the best way to reach tomorrow's stops."),
        ("Culture and flavor", "Spend time with a museum, heritage site, or cultural district that suits your interests.", "Try a regional lunch and ask about ingredients that fit your diet.", "Leave room for an unhurried evening stroll."),
        ("A slower day", "Choose a garden, viewpoint, market, or nearby nature spot based on local advice.", "Sample a well-reviewed regional dish.", "Check transport and opening details directly before setting out."),
    ]
    days = []
    for i in range(request.days):
        title, desc, food, tip = descriptions[i % len(descriptions)]
        days.append({"day": i + 1, "title": title, "description": f"A flexible sample day in {request.destination}.",
                     "morning": {"title": f"Explore {request.destination}", "description": desc},
                     "afternoon": {"title": "Choose a local highlight", "description": "Pick an attraction or activity that matches your interests; confirm details before visiting."},
                     "evening": {"title": "Unwind nearby", "description": "Keep the evening flexible for a meal and a gentle neighborhood walk."}, "local_food": food, "tip": tip})
    budget = _estimate_budget(request).model_dump()
    return _make_itinerary(request, {"title": f"A {request.days}-day plan for {request.destination}", "summary": "A sample plan to help you start shaping your trip.", "days": days, "budget": budget}, "demo")


def generate_gemini_itinerary(request: ItineraryRequest, api_key: str | None = None) -> Itinerary:
    """Call Google's current GenAI SDK with a structured JSON response schema."""
    api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    if not api_key:
        raise ValueError("Gemini mode needs GEMINI_API_KEY. Add it to your local .env file, or choose Demo mode.")
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError("Gemini SDK is not installed. Run: python -m pip install -r requirements.txt") from exc
    prompt_data = {
        "destination": request.destination, "origin": request.origin, "days": request.days,
        "travelers": request.travelers, "budget_inr": request.budget_inr, "preferences": request.preferences,
        "accommodation": request.accommodation.value, "dietary": request.dietary.value,
        "start_date": request.start_date.isoformat() if request.start_date else None,
    }
    prompt = ("Create a practical, varied travel itinerary from the request below. Return only data matching the schema. "
              "Use INR integer estimates that add up sensibly; do not claim live prices, opening hours, availability, distances, "
              "or verified facts. Label costs as estimates and make assumptions clear. Avoid unsafe or discriminatory advice.\n"
              + json.dumps(prompt_data, ensure_ascii=False))
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.8-flash", contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=Itinerary),
        )
        if not response.text:
            raise ValueError("Gemini returned an empty response. Please retry.")
        try:
            payload = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise ValueError("Gemini returned an unreadable itinerary. Please try again.") from exc
        return _make_itinerary(request, payload, "ai")
    except ValueError:
        raise
    except Exception as exc:
        # Do not show provider response bodies, which may echo request contents.
        raise RuntimeError("Gemini could not create the itinerary right now. Check your key and connection, then retry or use Demo mode.") from exc


def markdown_itinerary(request: ItineraryRequest, plan: Itinerary) -> str:
    """Format a complete itinerary as a downloadable Markdown document."""
    lines = [f"# {plan.title}", "", plan.summary, "", f"**Destination:** {request.destination}  ", f"**Travelers:** {request.travelers}  ", f"**Duration:** {request.days} days", "", "> Suggestions and budget figures are estimates, not verified facts or live travel prices.", "", "## Estimated budget (INR)"]
    for name, amount in plan.budget.categories.items():
        lines.append(f"- {name.title()}: ₹{amount:,.0f}")
    over_budget = max(0, plan.budget.total - request.budget_inr)
    lines += [f"- **Estimated total:** ₹{plan.budget.total:,.0f}", f"- **Remaining:** ₹{max(0, request.budget_inr - plan.budget.total):,.0f}", f"- **Over budget:** ₹{over_budget:,.0f}", f"- Assumptions: {plan.budget.assumptions}", ""]
    for day in plan.days:
        lines += [f"## Day {day.day}: {day.title}", "", day.description, ""]
        for label in ("morning", "afternoon", "evening"):
            activity = getattr(day, label)
            lines.append(f"- **{label.title()} — {activity.title}:** {activity.description}")
        lines += [f"- **Local food:** {day.local_food}", f"- **Tip:** {day.tip}", ""]
    return "\n".join(lines)
