"""Local calendar for Life Hacker 3000 (own-your-data version).

Lucas's calendar lives entirely in calendar_data.json on this machine — no
Microsoft/Google account, no OAuth, nothing leaves the F: drive. Events are
simple {date, optional time, title} entries added from the /calendar page.

- GET /calendar                      the page
- GET /api/calendar/events           upcoming events (past ones auto-hidden)
- POST /api/calendar/events          add one: {title, date, time?}
- POST /api/calendar/quick           natural language -> events ("dentist tue 2pm")
                                     via one cheap Haiku call, added immediately
- DELETE /api/calendar/events/{id}   remove one

upcoming_events(days) is importable by other modules — the planner feeds the
next two weeks into plan generation so prep timelines avoid conflicts.
"""

import json
import os
import uuid
from datetime import date, datetime, timedelta

import anthropic
from dotenv import load_dotenv
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

load_dotenv()
client = anthropic.Anthropic()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CALENDAR_DATA_PATH = os.path.join(BASE_DIR, "calendar_data.json")


def _load() -> dict:
    try:
        with open(CALENDAR_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"events": []}


def _save(data: dict) -> None:
    with open(CALENDAR_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _sort_key(e: dict) -> tuple:
    return (e.get("date", ""), e.get("time") or "99:99")


def upcoming_events(days: int = 30) -> list[dict]:
    """Events from today through today+days, soonest first."""
    today = date.today().isoformat()
    horizon = (date.today() + timedelta(days=days)).isoformat()
    events = [e for e in _load()["events"] if today <= e.get("date", "") <= horizon]
    return sorted(events, key=_sort_key)


router = APIRouter()


@router.get("/calendar", response_class=HTMLResponse)
async def calendar_page():
    with open(os.path.join(BASE_DIR, "calendar.html"), "r", encoding="utf-8") as f:
        return f.read()


@router.get("/api/calendar/events")
def list_events():
    return JSONResponse(content={"events": upcoming_events(60), "today": date.today().isoformat()})


@router.post("/api/calendar/events")
def add_event(payload: dict = Body(...)):
    title = str(payload.get("title", "")).strip()
    date_str = str(payload.get("date", "")).strip()
    time_str = str(payload.get("time", "")).strip()
    if not title:
        raise HTTPException(status_code=422, detail="title is required")
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD")
    if time_str:
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            raise HTTPException(status_code=422, detail="time must be HH:MM")

    data = _load()
    event = {
        "id": uuid.uuid4().hex[:12],
        "title": title,
        "date": date_str,
        "time": time_str,
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    data["events"].append(event)
    data["events"].sort(key=_sort_key)
    _save(data)
    return JSONResponse(content={"added": event})


@router.post("/api/calendar/quick")
def quick_add(payload: dict = Body(...)):
    """Turn casual text into calendar events with one cheap Haiku call."""
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=422, detail="type what's happening first")

    today = date.today()
    prompt = (
        "Extract calendar events from Lucas's casual message. "
        f"Today is {today.strftime('%A, %Y-%m-%d')}.\n\n"
        f"Message: {text}\n\n"
        "Respond with ONLY valid JSON, no markdown:\n"
        '{"events": [{"title": "...", "date": "YYYY-MM-DD", "time": "HH:MM or empty string"}]}\n\n'
        "Rules:\n"
        "- Resolve relative dates (\"tuesday\", \"next friday\", \"tomorrow\") to the NEXT future occurrence.\n"
        "- time is 24-hour HH:MM only when a clock time is stated or obvious; otherwise \"\". "
        "Vague times like \"morning\" go in the title (e.g. \"Surf with Jake (morning)\"), not in time.\n"
        "- Split multiple events into separate entries. Keep titles short, keep names people mentioned.\n"
        "- If no date is given at all, use today.\n"
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}") + 1
        if start == -1 or end <= start:
            raise HTTPException(status_code=502, detail="couldn't understand that — try rewording")
        parsed = json.loads(raw[start:end])

    data = _load()
    added = []
    for e in parsed.get("events", [])[:10]:
        if not isinstance(e, dict) or not str(e.get("title", "")).strip():
            continue
        date_str = str(e.get("date", "")).strip() or today.isoformat()
        time_str = str(e.get("time", "")).strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            time_str = ""
        event = {
            "id": uuid.uuid4().hex[:12],
            "title": str(e["title"]).strip(),
            "date": date_str,
            "time": time_str,
            "created": datetime.now().isoformat(timespec="seconds"),
        }
        data["events"].append(event)
        added.append(event)

    if not added:
        raise HTTPException(status_code=422, detail="couldn't find an event in that — try rewording")
    data["events"].sort(key=_sort_key)
    _save(data)
    return JSONResponse(content={"added": added})


@router.delete("/api/calendar/events/{event_id}")
def delete_event(event_id: str):
    data = _load()
    before = len(data["events"])
    data["events"] = [e for e in data["events"] if e.get("id") != event_id]
    if len(data["events"]) == before:
        raise HTTPException(status_code=404, detail="event not found")
    _save(data)
    return JSONResponse(content={"deleted": event_id})
