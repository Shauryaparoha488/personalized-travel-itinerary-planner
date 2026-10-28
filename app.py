"""Streamlit interface for SkillWallet's Personalized Travel Itinerary Planner."""

from datetime import date, timedelta

import streamlit as st
from dotenv import load_dotenv

from src.itinerary import (
    Accommodation,
    DietaryPreference,
    ItineraryRequest,
    generate_demo_itinerary,
    generate_gemini_itinerary,
    markdown_itinerary,
    validate_request,
)


st.set_page_config(page_title="Roamwise · Travel Planner", page_icon="✦", layout="wide")
load_dotenv()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: #f6f7f4; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; color: #1d302b; }
    .hero { padding: 2rem 0 1rem; }
    .eyebrow { text-transform: uppercase; letter-spacing: .16em; color: #4d806f; font-weight: 700; font-size: .75rem; }
    .muted { color: #66736d; }
    div[data-testid="stMetric"] { background: white; padding: 1rem 1.2rem; border: 1px solid #e5eae5; border-radius: 14px; }
    .stButton button[kind="primary"] { background: #236451; border: 0; border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## ✦ Roamwise")
    st.caption("A thoughtful trip starts with a good plan.")
    page = st.radio("Explore", ["Plan a trip", "About this project"], label_visibility="collapsed")
    st.divider()
    st.caption("Costs and AI suggestions are estimates, not live quotes or verified travel advice.")

if page == "About this project":
    st.markdown('<p class="eyebrow">SkillWallet · Generative AI · Intermediate</p>', unsafe_allow_html=True)
    st.title("Travel planning, made personal")
    st.write("Roamwise turns your destination, budget and preferences into a practical day-by-day starting point.")
    st.info("Use demo mode without credentials, or add a Gemini API key locally to generate a tailored plan.")
    st.markdown("**Built with:** Python · Streamlit · Google GenAI SDK · Pydantic")
    st.markdown("See `README.md` for setup, testing, deployment, and project report details.")
    st.stop()

st.markdown('<div class="hero"><p class="eyebrow">Your next good story</p><h1>Plan a trip that feels like you.</h1><p class="muted">A flexible itinerary and sensible cost estimate, shaped around your travel style.</p></div>', unsafe_allow_html=True)

with st.form("trip_form"):
    st.subheader("The essentials")
    a, b, c = st.columns(3)
    with a:
        destination = st.text_input("Where to? *", placeholder="e.g. Jaipur")
        origin = st.text_input("Starting from (optional)", placeholder="e.g. Mumbai")
    with b:
        days = st.number_input("Trip length (days)", min_value=1, max_value=14, value=4)
        travelers = st.number_input("Travelers", min_value=1, max_value=12, value=2)
    with c:
        budget = st.number_input("Total budget (₹ INR)", min_value=1000, max_value=10_000_000, value=50000, step=5000)
        start_date = st.date_input("Start date (optional)", value=None, min_value=date.today(), max_value=date.today() + timedelta(days=730))

    st.subheader("Make it yours")
    preferences = st.multiselect("What do you enjoy?", ["Adventure", "Culture", "Nature", "Relaxation", "Shopping", "Food"], default=["Culture", "Food"])
    d, e = st.columns(2)
    with d:
        accommodation = st.selectbox("Accommodation", list(Accommodation), format_func=lambda x: x.value)
    with e:
        dietary = st.selectbox("Dietary preference", list(DietaryPreference), format_func=lambda x: x.value)
    mode = st.radio("How should we create your plan?", ["Demo mode · no API key needed", "Gemini AI · requires GEMINI_API_KEY"], horizontal=True)
    submitted = st.form_submit_button("Create my itinerary", type="primary", use_container_width=True)

if submitted:
    request = ItineraryRequest(
        destination=destination.strip(), origin=origin.strip() or None, days=int(days), travelers=int(travelers),
        budget_inr=int(budget), preferences=preferences, accommodation=accommodation,
        dietary=dietary, start_date=start_date,
    )
    errors = validate_request(request)
    if errors:
        for error in errors:
            st.error(error)
    else:
        try:
            with st.spinner("Putting together your travel plan…"):
                plan = (
                    generate_gemini_itinerary(request)
                    if mode.startswith("Gemini")
                    else generate_demo_itinerary(request)
                )
            st.session_state["plan"] = plan
            st.session_state["request"] = request
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))

if "plan" in st.session_state:
    plan = st.session_state["plan"]
    request = st.session_state["request"]
    st.divider()
    st.markdown(f'<p class="eyebrow">Your {request.days}-day escape</p>', unsafe_allow_html=True)
    st.title(plan.title)
    st.caption(plan.summary)
    if plan.source == "demo":
        st.info("Demo itinerary: sample suggestions are used to demonstrate the app. Switch to Gemini AI for a personalized response.")
    else:
        st.info("AI-generated suggestions. Verify details independently; no live prices, opening hours, routes, or availability are provided.")
    m1, m2, m3 = st.columns(3)
    m1.metric("Estimated total", f"₹{plan.budget.total:,.0f}")
    over_budget = max(0, plan.budget.total - request.budget_inr)
    m2.metric("Over budget" if over_budget else "Budget remaining", f"₹{over_budget if over_budget else request.budget_inr - plan.budget.total:,.0f}")
    m3.metric("Travelers", str(request.travelers))
    st.caption(f"Estimate for {request.travelers} traveler(s). Assumption: {plan.budget.assumptions}")
    st.subheader("Estimated budget breakdown")
    st.bar_chart({"INR": {name.title(): amount for name, amount in plan.budget.categories.items()}})
    for day in plan.days:
        with st.expander(f"Day {day.day}: {day.title}", expanded=day.day == 1):
            st.write(day.description)
            for label, item in [("Morning", day.morning), ("Afternoon", day.afternoon), ("Evening", day.evening)]:
                st.markdown(f"**{label} · {item.title}** — {item.description}")
            st.markdown(f"**Local food idea:** {day.local_food}")
            st.markdown(f"**Practical tip:** {day.tip}")
    st.download_button("Download itinerary (.md)", markdown_itinerary(request, plan), file_name="roamwise-itinerary.md", mime="text/markdown")
