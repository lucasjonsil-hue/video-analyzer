"""Gym notepad (spec: notes/project_ideas.md, "Gym Notepad Feature").

Step 1 of the build order: capture rough gym notes (plus optional structured
exercise/weight quick-add) — no AI review yet. Notes live in gym_data.json
locally (like planner_memory.json) so other sectors (e.g. the planner
estimating session length from the routine) can read them server-side.

- FastAPI routes (mounted into main.py): GET /gym, GET /api/gym/notes,
  POST /api/gym/notes, DELETE /api/gym/notes/{note_id}
- Data shape per note: { id, text, date, exercise?, weight?, status }
  with status "new" | "reviewed" | "applied" (only "new" is written today;
  the later AI-review step moves notes through the other states).
- Token budget for the future review step: keyword-match the note/exercise
  text against the summary bullets in notes/fitness.md (never the full
  transcripts) and include only matching bullets in the prompt.
"""

import json
import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GYM_DATA_PATH = os.path.join(BASE_DIR, "gym_data.json")


def _load_data() -> dict:
    if os.path.exists(GYM_DATA_PATH):
        with open(GYM_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # routine is empty until the routine feature lands; kept here so the
    # file shape is stable for future cross-sector readers.
    return {"routine": [], "notes": []}


def _save_data(data: dict) -> None:
    with open(GYM_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


router = APIRouter()


@router.get("/gym", response_class=HTMLResponse)
async def gym_page():
    with open(os.path.join(BASE_DIR, "gym.html"), "r", encoding="utf-8") as f:
        return f.read()


@router.get("/api/gym/notes")
async def list_notes():
    return JSONResponse(content=_load_data())


@router.post("/api/gym/notes")
async def add_note(payload: dict = Body(...)):
    text = (payload.get("text") or "").strip()
    exercise = (payload.get("exercise") or "").strip()
    weight = payload.get("weight")
    if weight in ("", None):
        weight = None
    else:
        try:
            weight = float(weight)
        except (TypeError, ValueError):
            raise HTTPException(status_code=422, detail="weight must be a number")
    if not text and not exercise:
        raise HTTPException(status_code=422, detail="write a note or log an exercise")

    note = {
        "id": uuid.uuid4().hex[:12],
        "text": text,
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "new",
    }
    if exercise:
        note["exercise"] = exercise
    if weight is not None:
        note["weight"] = weight

    data = _load_data()
    data["notes"].append(note)
    _save_data(data)
    return JSONResponse(content=note)


@router.delete("/api/gym/notes/{note_id}")
async def delete_note(note_id: str):
    data = _load_data()
    remaining = [n for n in data["notes"] if n["id"] != note_id]
    if len(remaining) == len(data["notes"]):
        raise HTTPException(status_code=404, detail="note not found")
    data["notes"] = remaining
    _save_data(data)
    return JSONResponse(content={"deleted": note_id})
