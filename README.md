# Solo PM MVP (Gemini-powered)

A tiny FastAPI + Jinja2 web app for solo project managers to paste Gemini meeting notes, extract a structured summary + tasks, and view a daily agenda.

## Requirements
- Python 3.10+
- A Gemini API key in `GEMINI_API_KEY`

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
export GEMINI_API_KEY="your_key_here"
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Sample meeting notes
Paste the following into the form to test the flow:

```
Project Phoenix kickoff:
- Decide to ship MVP by Oct 15.
- Risks: unclear scope around integrations; potential delay if vendor API access slips.
- Action: Send vendor access request email today.
- Action: Draft weekly status update template by Friday.
- Action: Create task list for onboarding flows; target early next week.
```

## What it does
- Extracts a meeting summary, decisions, and risks/blockers.
- Extracts proposed tasks with due dates and supporting quotes.
- Shows a daily agenda (due today, overdue, next 7 days, no due date).

## Notes
- Data is stored in `solo_pm.db` (SQLite) in the project root.
- All UI is server-rendered (FastAPI + Jinja2). Minimal CSS only.
