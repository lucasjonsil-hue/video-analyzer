"""Trip & event planner (CLAUDE.md section 5, v1).

Turns a natural-language event mention ("spearfishing Tuesday", "chem final
next Friday") into a prep plan and files it to notes/planner.md on GitHub.

- Trips get three plan versions: Plan A / Plan B / Fancy, each with its own
  timeline and packing list.
- Other events get a single checklist grouped by timing (now / day before /
  morning of).

Usable three ways:
- FastAPI routes (mounted into main.py): GET /planner, POST /api/plan
- CLI: py planner.py "spearfishing Tuesday, bringing my speargun"
- import: generate_plan(text) -> dict

v1 deliberately has no live weather/marine forecast source (open question in
the spec) — plans note what conditions to check and when, rather than
embedding a forecast.
"""

import base64
import json
import os
import sys
from datetime import datetime, timezone

import anthropic
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "lucasjonsil-hue/video-analyzer")
PLANNER_NOTE_PATH = "notes/planner.md"

client = anthropic.Anthropic()

# Structured-output schema: the API guarantees the response is valid JSON
# matching this shape, so no defensive parsing is needed.
PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "event_title": {"type": "string"},
        "event_date": {"type": "string", "format": "date"},
        "event_type": {
            "type": "string",
            "enum": ["trip", "event"],
        },
        "plans": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "timeline": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "phase": {"type": "string"},
                                "items": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["phase", "items"],
                            "additionalProperties": False,
                        },
                    },
                    "packing": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "description", "timeline", "packing"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["event_title", "event_date", "event_type", "plans"],
    "additionalProperties": False,
}

PLANNER_INSTRUCTIONS = """\
You are the trip/event planner module of Lucas's personal "Life Hacker 3000" system.
Lucas lives in Santa Barbara, CA. Today's date is {today}.

Given his message naming an upcoming activity, produce a prep plan:

- Resolve the event date from relative language ("Tuesday", "next Friday") against today's date, always landing on a FUTURE date.
- event_type "trip": significant activity outings (spearfishing, surf trips, camping, visiting someone out of town). Produce exactly three plans named "Plan A", "Plan B", "Fancy":
  - Plan A: primary spot/approach, ideal conditions, standard gear
  - Plan B: backup if the primary is closed or conditions are bad
  - Fancy: upgraded version — better/further spot, extra gear, possibly a charter or friend, more prep time
- event_type "event": everything else (exams, appointments, sports, social visits). Produce exactly one plan named "Checklist".
- Timeline phases work BACKWARD from the event date, using concrete dates where useful: e.g. "Week before", "Mon Jul 13", "Day before (Thu Jul 16)", "Morning of (Fri Jul 17)". Keep phases in chronological order.
- Packing lists are specific to the activity and conditions. If Lucas says he's bringing an item, include it marked "(already noted)". If he says he's NOT bringing something, leave it out this time without removing it from future suggestions.
- For ocean activities near Santa Barbara: note which conditions to check (swell, wind, visibility, tides — sources like NOAA/Surfline) and when, and flag legal constraints like no-take SMCAs (Coal Oil Point, Naples, Campus Point). Do not invent a specific forecast.
- Keep every item short and actionable — this is scanned on a phone.
"""


def generate_plan(text: str) -> dict:
    today = datetime.now().strftime("%A, %Y-%m-%d")
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=PLANNER_INSTRUCTIONS.format(today=today),
        output_config={"format": {"type": "json_schema", "schema": PLAN_SCHEMA}},
        messages=[{"role": "user", "content": text}],
    )
    if response.stop_reason == "refusal":
        raise ValueError("The model declined to generate a plan for this input")
    raw = next(block.text for block in response.content if block.type == "text")
    return json.loads(raw)


def format_plan_markdown(plan: dict, source_text: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"\n## {timestamp}",
        f'Source: planner — "{source_text}"',
        "",
        f"{plan['event_title']} — {plan['event_date']}",
    ]
    for version in plan["plans"]:
        lines += ["", f"### {version['name']}", version["description"]]
        for phase in version["timeline"]:
            lines.append(f"- **{phase['phase']}:** " + "; ".join(phase["items"]))
        if version["packing"]:
            lines.append("- **Packing:** " + "; ".join(version["packing"]))
    return "\n".join(lines) + "\n"


def save_plan_to_github(entry_md: str) -> bool:
    if not GITHUB_TOKEN:
        return False
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PLANNER_NOTE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    get_resp = requests.get(api_url, headers=headers, timeout=15)
    if get_resp.status_code == 200:
        existing = get_resp.json()
        current_content = base64.b64decode(existing["content"]).decode("utf-8")
        sha = existing["sha"]
    elif get_resp.status_code == 404:
        current_content = "# Planner Notes\n"
        sha = None
    else:
        get_resp.raise_for_status()

    title = entry_md.strip().splitlines()[3] if len(entry_md.strip().splitlines()) > 3 else "plan"
    payload = {
        "message": f"Add plan: {title}",
        "content": base64.b64encode((current_content + entry_md).encode("utf-8")).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha
    put_resp = requests.put(api_url, headers=headers, json=payload, timeout=15)
    put_resp.raise_for_status()
    return True


router = APIRouter()


@router.get("/planner", response_class=HTMLResponse)
async def planner_page():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "planner.html"), "r", encoding="utf-8") as f:
        return f.read()


@router.post("/api/plan")
async def create_plan(text: str = Form(...)):
    try:
        plan = generate_plan(text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    entry_md = format_plan_markdown(plan, text)
    try:
        plan["note_saved"] = save_plan_to_github(entry_md)
    except requests.RequestException:
        plan["note_saved"] = False
    return JSONResponse(content=plan)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: py planner.py "spearfishing Tuesday, bringing my speargun"')
        sys.exit(1)
    message = " ".join(sys.argv[1:])
    result = generate_plan(message)
    entry = format_plan_markdown(result, message)
    print(entry)
    saved = save_plan_to_github(entry)
    print("Saved to GitHub notes/planner.md" if saved else "NOT saved (GITHUB_TOKEN missing)")
