# Project Report — Personalized Travel Itinerary Planner

**Student:** [Add your name]
**Course / SkillWallet submission:** [Add course or cohort details]
**Category / level:** Generative AI / Intermediate

## Problem statement

Travelers often need to balance interests, duration, group size, and a fixed budget. This project provides a simple interface that converts those inputs into a structured itinerary draft and a transparent planning estimate.

## Objectives

- Build an accessible Python web application using Streamlit.
- Support a working demo without API credentials and optional Gemini generation.
- Present daily attraction ideas, activities, dining ideas, tips, and a categorized INR estimate.
- Validate inputs, handle common failures, support itinerary edits, and allow Markdown export.
- Persist plans through Supabase when the server credentials are configured.

## Methodology and architecture

Users enter trip details in `app.py`. `src/itinerary.py` validates requests, produces a demo plan or calls the Google GenAI SDK for structured JSON, validates responses with Pydantic, supports day edits, estimates the budget, and formats exports. `src/storage.py` saves and loads plans through Supabase. Unit tests cover validation, demo, editing, formatting, and mocked persistence.

## Implementation

The project uses Python, Streamlit, Pydantic, the Google GenAI Python SDK, and the Supabase Python SDK. The AI prompt requests day-wise attraction and activity suggestions with dining ideas and INR estimates, and prohibits unsupported claims about live prices, hours, distances, or availability. Gemini and Supabase settings are read from local environment configuration or Streamlit Secrets and excluded from version control. Supabase RLS is enabled; only the server secret key can access the table.

## Testing and results

Verified in Python 3.12.10: `python -m pytest -q` passed all 15 tests; compileall and application logic import checks succeeded. A headless Streamlit process started and its `/_stcore/health` endpoint returned `ok`. Supabase persistence was tested with a fake client, not a live Supabase project. Gemini was not tested because no API key was configured. Interactive browser review was not performed.

## Limitations

The app does not use a live travel data provider. Demo content is illustrative. AI output and all budget estimates require independent verification and are not booking quotes. Saved itineraries use random IDs in place of user accounts; account ownership, access revocation, and multi-user authorization are not implemented.

## Conclusion

The project demonstrates an end-to-end generative AI travel-planning workflow with a usable no-key demo, structured responses, input checks, and downloadable output. Add screenshots and personal/course details before submission.
