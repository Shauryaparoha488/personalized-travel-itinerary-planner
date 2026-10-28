# Project Report — Personalized Travel Itinerary Planner

**Student:** [Add your name]
**Course / SkillWallet submission:** [Add course or cohort details]
**Category / level:** Generative AI / Intermediate

## Problem statement

Travelers often need to balance interests, duration, group size, and a fixed budget. This project provides a simple interface that converts those inputs into a structured itinerary draft and a transparent planning estimate.

## Objectives

- Build an accessible Python web application using Streamlit.
- Support a working demo without API credentials and optional Gemini generation.
- Present daily activities, food ideas, tips, and a categorized INR estimate.
- Validate inputs, handle common failures, and allow Markdown export.

## Methodology and architecture

Users enter trip details in `app.py`. `src/itinerary.py` validates the request, produces a deterministic demo plan or calls the Google GenAI SDK for structured JSON, validates the result with Pydantic, calculates the remaining budget, and formats an export. Unit tests cover validation and core demo flows.

## Implementation

The project uses Python, Streamlit, Pydantic, and the Google GenAI Python SDK. The AI prompt requests day-by-day JSON and explicitly prohibits unsupported claims about live prices, hours, distances, or availability. Secrets are read from `GEMINI_API_KEY` and excluded from version control.

## Testing and results

Verified in Python 3.12.10: `python -m pytest -q` passed all 11 tests; compileall and application logic import checks succeeded. A headless Streamlit process started and its `/_stcore/health` endpoint returned `ok`. Gemini was not tested because no API key was configured. Interactive browser review was not performed.

## Limitations

The app does not use a live travel data provider. Demo content is illustrative. AI output and all budget estimates require independent verification and are not booking quotes.

## Conclusion

The project demonstrates an end-to-end generative AI travel-planning workflow with a usable no-key demo, structured responses, input checks, and downloadable output. Add screenshots and personal/course details before submission.
