"""Gym notepad (spec: notes/project_ideas.md, "Gym Notepad Feature").

Steps 1-4 of the build order: capture rough gym notes (plus optional structured
exercise/weight quick-add), then an AI review step. Notes live in gym_data.json
locally (like planner_memory.json) so other sectors (e.g. the planner
estimating session length from the routine) can read them server-side.

- FastAPI routes (mounted into main.py): GET /gym, GET /api/gym/notes,
  POST /api/gym/notes, DELETE /api/gym/notes/{note_id},
  POST /api/gym/review, POST /api/gym/review/{sid}/{decision},
  DELETE /api/gym/routine/{exercise}
- Data shape per note: { id, text, date, exercise?, weight?, status }
  with status "new" | "reviewed" | "applied". Review moves "new" notes to
  "reviewed"; approving a suggestion marks its motivating notes "applied".
- gym_data.json also holds routine (list of {exercise, detail, source?, added})
  and review (last review run: {date, suggestions: [...]}).
- Token budget for the review step: keyword-match the note/exercise text
  against notes/fitness.md entries and include only the summary bullets and
  description paragraphs of matched entries (never the full transcripts,
  which are stripped before matching). Video suggestions ("try the workout
  from this video") come from the same matched entries.
"""

import json
import os
import re
import uuid
from datetime import datetime, timezone

import anthropic
from dotenv import load_dotenv
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GYM_DATA_PATH = os.path.join(BASE_DIR, "gym_data.json")
FITNESS_NOTES_PATH = os.path.join(BASE_DIR, "notes", "fitness.md")

client = anthropic.Anthropic()


def _load_data() -> dict:
    if os.path.exists(GYM_DATA_PATH):
        with open(GYM_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    data.setdefault("routine", [])
    data.setdefault("notes", [])
    data.setdefault("review", None)
    return data


def _save_data(data: dict) -> None:
    with open(GYM_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _parse_fitness_entries() -> list[dict]:
    """notes/fitness.md -> [{source, bullets, desc}], transcripts stripped."""
    if not os.path.exists(FITNESS_NOTES_PATH):
        return []
    with open(FITNESS_NOTES_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    entries = []
    for block in content.split("\n## ")[1:]:
        block = block.split("<details>")[0]
        source = ""
        bullets = []
        paragraphs = []
        current = []
        for line in block.strip().split("\n")[1:]:
            s = line.strip()
            if s.startswith("Source:"):
                source = s[len("Source:"):].strip()
            elif s.startswith("Creator:"):
                continue
            elif s.startswith("- "):
                bullets.append(s[2:].strip())
            elif s:
                current.append(s)
            elif current:
                paragraphs.append(" ".join(current))
                current = []
        if current:
            paragraphs.append(" ".join(current))
        if bullets or paragraphs:
            entries.append({
                "source": source,
                "bullets": bullets,
                "desc": " ".join(paragraphs)[:1500],
            })
    return entries


_STOPWORDS = {
    "this", "that", "with", "from", "have", "were", "been", "they", "them",
    "then", "than", "when", "what", "some", "more", "like", "just",
    "today", "session", "workout", "exercise", "really", "little", "tried",
    "want", "wanted", "feel", "felt", "good", "great", "next", "time",
}


def _match_entries(notes: list[dict], entries: list[dict], max_matched: int = 4) -> list[dict]:
    """Pick fitness entries whose bullets/desc share words with the notes.

    Pads with the most recent entries (min 3 total) so the reviewer always
    has video material to suggest workouts from, even with sparse notes.
    """
    tokens = set()
    for n in notes:
        text = f"{n.get('text', '')} {n.get('exercise', '')}"
        for word in re.findall(r"[a-zA-Z]{4,}", text.lower()):
            if word not in _STOPWORDS:
                tokens.add(word)

    scored = []
    for entry in entries:
        haystack = (" ".join(entry["bullets"]) + " " + entry["desc"]).lower()
        score = sum(1 for t in tokens if t in haystack)
        scored.append((score, entry))
    scored.sort(key=lambda pair: -pair[0])

    picked = [entry for score, entry in scored if score > 0][:max_matched]
    for entry in reversed(entries):  # newest entries are at the end of the file
        if len(picked) >= 3:
            break
        if entry not in picked:
            picked.append(entry)
    return picked


def _review_prompt(routine: list[dict], new_notes: list[dict], video_entries: list[dict]) -> str:
    notes_json = json.dumps(
        [{k: n[k] for k in ("id", "text", "date", "exercise", "weight") if k in n} for n in new_notes],
        ensure_ascii=False,
    )
    videos = "\n\n".join(
        f"Video {i + 1} (source: {e['source'] or 'unknown'}):\n{e['desc']}\n"
        + "\n".join(f"- {b}" for b in e["bullets"])
        for i, e in enumerate(video_entries)
    )
    return (
        "You are the gym-routine reviewer inside Lucas's Life Hacker 3000 tool suite. "
        "Lucas jots rough notes during gym sessions; before his next session you review them "
        "against his current routine and against notes he saved from fitness videos.\n\n"
        f"Current routine (JSON): {json.dumps(routine, ensure_ascii=False)}\n\n"
        f"New session notes (JSON, each has an id): {notes_json}\n\n"
        f"Notes Lucas saved from fitness videos he watched:\n{videos if videos else '(none)'}\n\n"
        "Respond with ONLY valid JSON, no markdown:\n"
        '{"suggestions": [{"kind": "routine" or "video", "title": "...", "why": "...", '
        '"how": "...", "source": "url or null", '
        '"routine_entry": {"exercise": "...", "detail": "..."} or null, "note_ids": ["..."]}]}\n\n'
        "Rules:\n"
        "- Max 5 suggestions total.\n"
        "- kind \"routine\": a concrete edit grounded in the session notes (swap X for Y, bump a "
        "weight, add/drop an exercise). Put the ids of the motivating notes in note_ids.\n"
        "- kind \"video\": 1-2 suggestions when the video notes contain a workout or exercise worth "
        "trying. title = what the workout is, why = one sentence on why it fits Lucas right now, "
        "how = how to actually do it (movements, sets/reps/frequency) using only what the video "
        "notes say, source = that video's URL.\n"
        "- Exercises and training methods only — skip supplement stacks, miracle claims, or "
        "anything medically dubious from the videos.\n"
        "- routine_entry is what gets added/updated in the routine if Lucas approves (short "
        "exercise name + one-line detail like sets/reps/weight); null if the suggestion doesn't "
        "change the routine.\n"
        "- If there are no session notes, focus on video suggestions.\n"
        "- Write title/why/how in plain, friendly language — Lucas is not a fitness expert."
    )


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


@router.post("/api/gym/review")
async def review_notes():
    data = _load_data()
    new_notes = [n for n in data["notes"] if n["status"] == "new"]
    entries = _parse_fitness_entries()
    if not new_notes and not entries:
        raise HTTPException(status_code=422, detail="nothing to review — no new notes and no fitness video notes yet")

    video_entries = _match_entries(new_notes, entries)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": _review_prompt(data["routine"], new_notes, video_entries)}],
    )
    raw = response.content[0].text.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            parsed = json.loads(raw[start:end])
        else:
            raise HTTPException(status_code=502, detail="review failed: model did not return valid JSON")

    valid_note_ids = {n["id"] for n in new_notes}
    suggestions = []
    for s in parsed.get("suggestions", [])[:5]:
        if not isinstance(s, dict) or not s.get("title"):
            continue
        entry = s.get("routine_entry")
        if not (isinstance(entry, dict) and entry.get("exercise")):
            entry = None
        suggestions.append({
            "id": uuid.uuid4().hex[:12],
            "kind": s.get("kind") if s.get("kind") in ("routine", "video") else "routine",
            "title": str(s.get("title", "")),
            "why": str(s.get("why", "")),
            "how": str(s.get("how", "")),
            "source": s.get("source") or None,
            "routine_entry": entry,
            "note_ids": [i for i in (s.get("note_ids") or []) if i in valid_note_ids],
            "status": "pending",
        })

    for n in data["notes"]:
        if n["status"] == "new":
            n["status"] = "reviewed"
    data["review"] = {
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "suggestions": suggestions,
    }
    _save_data(data)
    return JSONResponse(content=data)


@router.post("/api/gym/review/{suggestion_id}/{decision}")
async def decide_suggestion(suggestion_id: str, decision: str):
    if decision not in ("approve", "reject"):
        raise HTTPException(status_code=422, detail="decision must be approve or reject")
    data = _load_data()
    review = data.get("review") or {}
    for s in review.get("suggestions", []):
        if s["id"] != suggestion_id:
            continue
        if s["status"] != "pending":
            raise HTTPException(status_code=409, detail=f"suggestion already {s['status']}")
        if decision == "approve":
            s["status"] = "approved"
            entry = s.get("routine_entry")
            if entry:
                for r in data["routine"]:
                    if r["exercise"].lower() == entry["exercise"].lower():
                        r["detail"] = entry.get("detail", r.get("detail", ""))
                        if s.get("source"):
                            r["source"] = s["source"]
                        break
                else:
                    data["routine"].append({
                        "exercise": entry["exercise"],
                        "detail": entry.get("detail", ""),
                        **({"source": s["source"]} if s.get("source") else {}),
                        "added": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    })
            for n in data["notes"]:
                if n["id"] in s.get("note_ids", []):
                    n["status"] = "applied"
        else:
            s["status"] = "rejected"
        _save_data(data)
        return JSONResponse(content=data)
    raise HTTPException(status_code=404, detail="suggestion not found")


@router.delete("/api/gym/routine/{exercise}")
async def delete_routine_entry(exercise: str):
    data = _load_data()
    remaining = [r for r in data["routine"] if r["exercise"].lower() != exercise.lower()]
    if len(remaining) == len(data["routine"]):
        raise HTTPException(status_code=404, detail="routine entry not found")
    data["routine"] = remaining
    _save_data(data)
    return JSONResponse(content=data)
