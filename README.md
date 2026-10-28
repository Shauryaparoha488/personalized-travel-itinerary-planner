# Roamwise — Personalized Travel Itinerary Planner

**SkillWallet project · Generative AI · Intermediate**

Roamwise is a Streamlit app that turns destination, dates, budget, group size, and travel style into a day-by-day itinerary. It supports an offline demo, optional Gemini generation, editing, Markdown export, and optional Supabase save/load.

## Problem and objectives

Planning a trip means balancing activities, food, comfort, and a fixed budget. This project demonstrates how a small generative AI application can organize those preferences into an editable starting point, while keeping the cost estimate transparent and warning users to verify travel details.

## Features

- Destination and optional origin, dates, trip length, travelers, and INR budget.
- Adventure, culture, nature, relaxation, shopping, and food interests; accommodation and dietary preferences.
- Daily attraction ideas with descriptions, morning/afternoon/evening activities, dining ideas, and practical tips.
- Estimated transport, accommodation, food, activities, and miscellaneous budget categories.
- Interactive day editing, downloadable Markdown, and Supabase save/load by private itinerary ID.
- Demo mode works without network access or a Gemini key.
- Optional structured output from Google's Gemini API.
- Clear distinction between estimates and verified or live information.

## Technology and architecture

- Python 3.11+ (Python 3.12 is suitable), Streamlit, Pydantic, Google GenAI Python SDK, and Supabase Python SDK.
- `app.py` owns the interface and session state. `src/itinerary.py` owns validation, models, demo data, estimates, Gemini calls, and Markdown formatting. `src/storage.py` handles Supabase operations. `supabase/schema.sql` defines the table and security rules.

Workflow: enter trip details → validate → choose demo or Gemini → review and edit daily suggestions → optionally save/load through Supabase → download Markdown.

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

Choose **Demo mode** to try the planner without credentials. Saving and loading are disabled until Supabase is configured.

## Gemini setup

Create an API key in [Google AI Studio](https://aistudio.google.com/app/apikey). Put it only in the local `.env` file as `GEMINI_API_KEY=your_actual_key`; never commit that file. Restart Streamlit, then choose **Gemini AI**. The app uses the `google-genai` SDK and `gemini-3.8-flash` structured JSON output. An API key and access/quota are required for AI mode; this project has not been exercised with a live key.

For Streamlit Community Cloud, add `GEMINI_API_KEY` in the app's **Settings → Secrets** panel. Do not put it in GitHub, source files, or deployment configuration.

## Supabase setup and saved itineraries

1. Create a Supabase project and open its **SQL Editor**.
2. Run the schema in [`supabase/schema.sql`](supabase/schema.sql). It creates `travel_itineraries`, enables RLS, and grants table access only to the server role used by this app.
3. Copy the Project URL and create a server-side Supabase secret key. Put them in the local `.env` file as `SUPABASE_URL` and `SUPABASE_SECRET_KEY`. The app also accepts the legacy `SUPABASE_SERVICE_ROLE_KEY` name.
4. Restart the app. The sidebar will show whether Supabase saving is configured.

In Streamlit Community Cloud, add `SUPABASE_URL` and `SUPABASE_SECRET_KEY` under **Settings → Secrets**, alongside `GEMINI_API_KEY`. Supabase credentials are read only by the Python server. Never use a Supabase secret/service-role key in browser code or commit it to GitHub. See [Supabase API key guidance](https://supabase.com/docs/guides/getting-started/api-keys) and [data security guidance](https://supabase.com/docs/guides/database/secure-data).

The app does not provide user accounts. A saved itinerary is retrieved by a random UUID shown after saving; treat it as a private link and do not share it if the itinerary is personal. The app does not list all database rows. Without Supabase credentials, planning, editing, and download still work in the current browser session, while cloud save/load controls are unavailable.

## Run and test

Run with `streamlit run app.py`. Run tests with:

```powershell
python -m pytest -q
```

The test suite checks input validation, demo itinerary completeness, budget arithmetic, editing, Markdown formatting, missing-key handling, and Supabase save/load serialization through a fake client. It does not connect to a real Supabase project or make Gemini API calls.

## Example use case

Enter Jaipur, Mumbai as origin, 3 days, 2 travelers, ₹50,000, culture and food, a comfort hotel, and vegetarian. Demo mode produces three flexible sample days and a planning estimate. Values are illustrative and not quotes; actual costs depend on dates, transport, and choices.

## Deployment preparation

This app is compatible with Streamlit Community Cloud. Push the project to a GitHub repository, create an app at [share.streamlit.io](https://share.streamlit.io/), select the repository and `app.py`, and configure `GEMINI_API_KEY`, `SUPABASE_URL`, and `SUPABASE_SECRET_KEY` under app Secrets to enable all cloud features. Demo, editing, and download work without secrets. Deployment requires a GitHub repository and a Streamlit Community Cloud account.

## Limitations and future work

- The app does not query live prices, maps, opening hours, routes, reservations, or availability.
- Demo activities and attraction ideas are generic examples. Gemini output can be inaccurate; independently check safety, dietary suitability, and current details.
- Budget estimation is a simple planning heuristic and may exceed the budget or underestimate real spending.
- Saved plans have no user account or ownership workflow; possession of the saved ID is required to retrieve a plan.
- Future enhancements could add user-reviewed local data sources, richer itinerary editing, and optional mapping with a suitable API.

## Screenshots

Add screenshots of the running app here before submission, for example `![Planner form](assets/planner.png)`. No screenshot is included yet.

## Verification record

Verified in the project virtual environment on Python 3.12.10:

- `python -m pytest -q`: **15 passed**.
- `python -m compileall -q app.py src tests`: completed successfully.
- App logic import check: successful.
- Streamlit launch and `/_stcore/health` endpoint: returned `ok`.
- Gemini request: not run because no API key was configured.
- Interactive browser review: not performed.
