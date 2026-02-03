from datetime import date, datetime, timedelta
import json

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .db import SessionLocal, init_db
from .gemini_client import GeminiError, call_gemini_extract
from .models import Meeting, Task

app = FastAPI(title="Solo PM MVP")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def index(request: Request) -> object:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "today": date.today().isoformat(),
            "error": None,
            "form": {},
        },
    )


@app.post("/meetings/process")
def process_meeting(
    request: Request,
    title: str = Form(...),
    meeting_date: str = Form(...),
    timezone: str = Form(...),
    gemini_notes: str = Form(...),
    transcript: str | None = Form(None),
    db: Session = Depends(get_db),
) -> object:
    form_payload = {
        "title": title,
        "meeting_date": meeting_date,
        "timezone": timezone,
        "gemini_notes": gemini_notes,
        "transcript": transcript or "",
    }

    try:
        extraction = call_gemini_extract(form_payload)
    except GeminiError as exc:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "today": date.today().isoformat(),
                "error": str(exc),
                "form": form_payload,
            },
            status_code=400,
        )

    meeting = Meeting(
        title=title,
        meeting_date=date.fromisoformat(meeting_date),
        timezone=timezone,
        gemini_notes=gemini_notes,
        transcript=transcript,
        summary=extraction["meeting_summary"]["summary"],
        decisions=json.dumps(extraction["meeting_summary"].get("decisions", [])),
        risks_blockers=json.dumps(
            extraction["meeting_summary"].get("risks_blockers", [])
        ),
    )

    tasks = []
    for item in extraction.get("tasks", []):
        due_date_value = item.get("due_date")
        due_date = None
        if due_date_value:
            try:
                due_date = date.fromisoformat(due_date_value)
            except ValueError:
                due_date = None
        source = item.get("source", {})
        task = Task(
            title=item.get("title", "Untitled"),
            project=item.get("project"),
            due_date=due_date,
            due_date_confidence=float(item.get("due_date_confidence", 0.0)),
            priority=item.get("priority", "medium"),
            status=item.get("status", "proposed"),
            confidence=float(item.get("confidence", 0.0)),
            source_type=source.get("type", "notes"),
            source_quote=source.get("quote", ""),
            tags=json.dumps(item.get("tags", [])),
        )
        tasks.append(task)

    meeting.tasks = tasks
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return RedirectResponse(url=f"/meetings/{meeting.id}", status_code=303)


@app.get("/meetings/{meeting_id}")
def meeting_detail(
    request: Request, meeting_id: int, db: Session = Depends(get_db)
) -> object:
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        return RedirectResponse(url="/", status_code=302)

    decisions = json.loads(meeting.decisions) if meeting.decisions else []
    risks = json.loads(meeting.risks_blockers) if meeting.risks_blockers else []

    return templates.TemplateResponse(
        "meeting.html",
        {
            "request": request,
            "meeting": meeting,
            "decisions": decisions,
            "risks": risks,
            "tasks": meeting.tasks,
        },
    )


@app.get("/agenda")
def agenda_redirect(request: Request) -> RedirectResponse:
    target_date = request.query_params.get("date")
    if target_date:
        return RedirectResponse(url=f"/agenda/{target_date}", status_code=302)
    today = date.today().isoformat()
    return RedirectResponse(url=f"/agenda/{today}", status_code=302)


@app.get("/agenda/{target_date}")
def agenda_view(
    request: Request, target_date: str, db: Session = Depends(get_db)
) -> object:
    selected_date = date.fromisoformat(target_date)
    next_seven = selected_date + timedelta(days=7)

    tasks = db.query(Task).filter(Task.status != "done").all()

    due_today = [t for t in tasks if t.due_date == selected_date]
    overdue = [t for t in tasks if t.due_date and t.due_date < selected_date]
    next_7_days = [
        t for t in tasks if t.due_date and selected_date < t.due_date <= next_seven
    ]
    no_due_date = [t for t in tasks if t.due_date is None]

    return templates.TemplateResponse(
        "agenda.html",
        {
            "request": request,
            "selected_date": selected_date,
            "due_today": due_today,
            "overdue": overdue,
            "next_7_days": next_7_days,
            "no_due_date": no_due_date,
        },
    )
