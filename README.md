# Roamwise — Personalized Travel Itinerary Planner

**SkillWallet project · Generative AI · Intermediate**

Roamwise is a beginner-friendly Streamlit app that turns a destination, trip length, budget, group size, and travel preferences into a day-by-day travel planning draft. It includes a no-key demo and optional Gemini generation.

## Problem and objectives

Planning a trip means balancing activities, food, comfort, and a fixed budget. This project demonstrates how a small generative AI application can organize those preferences into an editable starting point, while keeping the cost estimate transparent and warning users to verify travel details.

## Features

- Destination and optional origin, dates, trip length, travelers, and INR budget.
- Adventure, culture, nature, relaxation, shopping, and food interests; accommodation and dietary preferences.
- Morning, afternoon, and evening suggestions, local food ideas, and practical tips for each day.
- Estimated transport, accommodation, food, activities, and miscellaneous budget categories.
- Downloadable Markdown itinerary.
- Demo mode works without network access or a Gemini key.
- Optional structured output from Google's Gemini API.
- Clear distinction between estimates and verified or live information.

## Technology and architecture

- Python 3.11+ (Python 3.12 is suitable), Streamlit, Pydantic, Google GenAI Python SDK.
- `app.py` owns the interface and session state. `src/itinerary.py` owns validation, models, demo data, cost estimates, Gemini calls, and Markdown formatting. `tests/` covers key behaviors.

Workflow: enter trip details → validate → choose demo or Gemini → validate structured itinerary → review estimated budget and daily plan → download Markdown.

## Windows setup

Open PowerShell in the project directory and run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

If PowerShell blocks activation, use the environment's executable directly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Choose **Demo mode** to try it immediately. No API key is needed.

## Gemini setup

Create an API key in [Google AI Studio](https://aistudio.google.com/app/apikey). Put it only in the local `.env` file as `GEMINI_API_KEY=your_actual_key`; never commit that file. Restart Streamlit, then choose **Gemini AI**. The app uses the `google-genai` SDK and `gemini-3.8-flash` structured JSON output. An API key and access/quota are required for AI mode; this project has not been exercised with a live key.

For Streamlit Community Cloud, add `GEMINI_API_KEY` in the app's **Settings → Secrets** panel. Do not put it in GitHub, source files, or deployment configuration.

## Run and test

Run with `streamlit run app.py`. Run tests with:

```powershell
python -m pytest -q
```

The test suite checks input validation, demo itinerary completeness, estimated budget arithmetic, Markdown formatting, and missing-key handling. See the results recorded after local verification below.

## Example use case

Enter Jaipur, Mumbai as origin, 3 days, 2 travelers, ₹50,000, culture and food, a comfort hotel, and vegetarian. Demo mode produces three flexible sample days and a planning estimate. Values are illustrative and not quotes; actual costs depend on dates, transport, and choices.

## Deployment preparation

This app is compatible with Streamlit Community Cloud. Push the project to a GitHub repository, create an app at [share.streamlit.io](https://share.streamlit.io/), select the repository and `app.py`, and optionally configure `GEMINI_API_KEY` under app Secrets. Demo mode works without secrets. Deployment was not published as part of this local project setup.

## Limitations and future work

- The app does not query live prices, maps, opening hours, routes, reservations, or availability.
- Demo activities are generic examples. Gemini output can be inaccurate; independently check safety, dietary suitability, and current details.
- Budget estimation is a simple planning heuristic and may exceed the budget or underestimate real spending.
- Future enhancements could add user-reviewed local data sources, richer itinerary editing, and optional mapping with a suitable API.

## Screenshots

Add screenshots of the running app here before submission, for example `![Planner form](assets/planner.png)`. No screenshot is included yet.

## Verification record

Verified in the project virtual environment on Python 3.12.10:

- `python -m pytest -q`: **11 passed**.
- `python -m compileall -q app.py src tests`: completed successfully.
- App logic import check: successful.
- Streamlit launch and `/_stcore/health` endpoint: returned `ok`.
- Gemini request: not run because no API key was configured.
- Interactive browser review: not performed.
