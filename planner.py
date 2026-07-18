"""Trip & event planner (CLAUDE.md section 5, v2).

Turns a natural-language event mention ("spearfishing Tuesday", "chem final
next Friday") into a prep plan, previewed in the UI and saved to
notes/planner.md on GitHub only when Lucas approves.

- Trips get three plan versions: Plan A / Plan B / Fancy, each with its own
  timeline and packing list.
- Other events get a single checklist grouped by timing (now / day before /
  morning of).
- Gear memory (planner_memory.json): items Lucas mentions in saved plans are
  remembered per activity; core items (seen 2+ times) he doesn't mention get
  a nudge question on future plans.
- Live Open-Meteo forecast (daily + marine) for the Santa Barbara area is fed
  into the prompt so plans use real conditions instead of guessing.

Usable three ways:
- FastAPI routes (mounted into main.py): GET /planner, POST /api/plan,
  POST /api/plan/save
- CLI: py planner.py "spearfishing Tuesday, bringing my speargun"
- import: generate_plan(text) -> dict
"""

import base64
import json
import os
import sys
from datetime import datetime, timezone

import anthropic
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Body, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "lucasjonsil-hue/video-analyzer")
PLANNER_NOTE_PATH = "notes/planner.md"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEAR_MEMORY_PATH = os.path.join(BASE_DIR, "planner_memory.json")
# Default planning location: Santa Barbara, CA
SB_LAT, SB_LON = 34.42, -119.70

client = anthropic.Anthropic()

# Structured-output schema: the API guarantees the response is valid JSON
# matching this shape, so no defensive parsing is needed. Field names match
# planner.html's render() contract.
PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "event_date": {"type": "string"},
        "event_type": {
            "type": "string",
            "enum": ["trip", "event"],
        },
        "activity": {"type": "string"},
        "plans": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "summary": {"type": "string"},
                    "timeline": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "when": {"type": "string"},
                                "items": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["when", "items"],
                            "additionalProperties": False,
                        },
                    },
                    "packing": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "summary", "timeline", "packing"],
                "additionalProperties": False,
            },
        },
        "mentioned_gear": {"type": "array", "items": {"type": "string"}},
        "gear_nudges": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title", "event_date", "event_type", "activity", "plans",
                 "mentioned_gear", "gear_nudges"],
    "additionalProperties": False,
}

PLANNER_INSTRUCTIONS = """\
You are the trip/event planner module of Lucas's personal "Life Hacker 3000" system.
Lucas lives in Santa Barbara, CA. Today's date is {today}.

Given his message naming an upcoming activity, produce a prep plan:

- Resolve the event date from relative language ("Tuesday", "next Friday") against today's date, always landing on a FUTURE date. Write it like "2026-07-21 (Tuesday)"; use "unspecified" if no date was given.
- activity: one short lowercase keyword for the activity (e.g. "spearfishing", "exam", "hike").
- event_type "trip": significant activity outings (spearfishing, surf trips, camping, visiting someone out of town). Produce exactly three plans named "Plan A", "Plan B", "Fancy":
  - Plan A: primary spot/approach, ideal conditions, standard gear
  - Plan B: backup if the primary is closed or conditions are bad
  - Fancy: upgraded version — better/further spot, extra gear, possibly a charter or friend, more prep time
- event_type "event": everything else (exams, appointments, sports, social visits). Produce exactly one plan named "Checklist".
- Timeline "when" phases work BACKWARD from the event date, using concrete dates where useful: e.g. "Week before", "Day before (Thu Jul 16)", "Morning of (Fri Jul 17)". Keep phases in chronological order; drop groups that don't apply if the event is very soon.
- Packing lists are specific to the activity and conditions.
- mentioned_gear: items Lucas explicitly said he IS bringing ([] if none). If he says he's NOT bringing something, treat it as a one-time exclusion: drop it from packing, don't nudge, don't list it in mentioned_gear.
- For ocean activities near Santa Barbara: note which conditions to check (swell, wind, visibility, tides) and when, and flag legal constraints like no-take SMCAs (Coal Oil Point, Naples, Campus Point).
- Keep every item short and actionable — this is scanned on a phone.
{gear_block}{forecast_block}"""


def load_gear_memory() -> dict:
    try:
        with open(GEAR_MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def update_gear_memory(activity: str, items: list) -> None:
    if not activity or not items:
        return
    memory = load_gear_memory()
    counts = memory.setdefault(activity.strip().lower(), {})
    for item in items:
        key = str(item).strip().lower()
        if key:
            counts[key] = counts.get(key, 0) + 1
    with open(GEAR_MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def gear_memory_context() -> str:
    memory = load_gear_memory()
    lines = []
    for activity, counts in memory.items():
        core = sorted(k for k, v in counts.items() if v >= 2)
        sometimes = sorted(k for k, v in counts.items() if v == 1)
        parts = []
        if core:
            parts.append("core (always expected): " + ", ".join(core))
        if sometimes:
            parts.append("sometimes: " + ", ".join(sometimes))
        if parts:
            lines.append(f"- {activity}: " + " | ".join(parts))
    return "\n".join(lines)


def fetch_forecast_context() -> str:
    """Best-effort live forecast for the default area; returns "" if offline/unavailable."""
    lines = []
    try:
        daily = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": SB_LAT, "longitude": SB_LON,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max",
                "temperature_unit": "fahrenheit", "wind_speed_unit": "mph",
                "forecast_days": 14, "timezone": "America/Los_Angeles",
            },
            timeout=8,
        ).json()["daily"]
        for i, day in enumerate(daily["time"]):
            lines.append(
                f"- {day}: {daily['temperature_2m_min'][i]:.0f}-{daily['temperature_2m_max'][i]:.0f}F, "
                f"rain {daily['precipitation_probability_max'][i]:.0f}%, "
                f"wind {daily['wind_speed_10m_max'][i]:.0f}mph"
            )
    except Exception:
        return ""
    try:
        marine = requests.get(
            "https://marine-api.open-meteo.com/v1/marine",
            params={
                "latitude": SB_LAT, "longitude": SB_LON,
                "daily": "wave_height_max,wave_period_max",
                "forecast_days": 7, "timezone": "America/Los_Angeles",
            },
            timeout=8,
        ).json()["daily"]
        for i, day in enumerate(marine["time"]):
            if i < len(lines):
                lines[i] += (
                    f", waves {marine['wave_height_max'][i]:.1f}m"
                    f" @ {marine['wave_period_max'][i]:.0f}s"
                )
    except Exception:
        pass
    return "\n".join(lines)


def generate_plan(text: str) -> dict:
    today = datetime.now().strftime("%A, %Y-%m-%d")

    gear_block = ""
    gear = gear_memory_context()
    if gear:
        gear_block = (
            "\nLucas's gear memory — what he has brought on past trips, by activity:\n"
            f"{gear}\n"
            "If the activity matches an entry, seed the packing lists with the core items. If Lucas's message "
            "doesn't mention a core item, add a short question to gear_nudges (e.g. \"You didn't mention your "
            "weight belt — bringing it?\"). Don't nudge about 'sometimes' items. gear_nudges stays [] if there "
            "is no gear memory for this activity.\n"
        )

    forecast_block = ""
    forecast = fetch_forecast_context()
    if forecast:
        forecast_block = (
            "\nLive forecast for the Santa Barbara area (wave data where available):\n"
            f"{forecast}\n"
            "Use the actual forecast for the resolved event date in plan summaries, conditions checks, and "
            "clothing/packing choices instead of guessing.\n"
        )

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=PLANNER_INSTRUCTIONS.format(
            today=today, gear_block=gear_block, forecast_block=forecast_block
        ),
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
        f"{plan.get('title', 'Plan')} — {plan.get('event_date', 'unspecified')}",
    ]
    for version in plan.get("plans", []):
        lines += ["", f"### {version.get('name', 'Plan')}"]
        if version.get("summary"):
            lines.append(version["summary"])
        for group in version.get("timeline", []):
            lines.append(f"- **{group.get('when', '')}:** " + "; ".join(group.get("items", [])))
        if version.get("packing"):
            lines.append("- **Packing:** " + "; ".join(version["packing"]))
    return "\n".join(lines) + "\n"


def save_plan_to_github(entry_md: str, title: str = "untitled") -> bool:
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
    with open(os.path.join(BASE_DIR, "planner.html"), "r", encoding="utf-8") as f:
        return f.read()


@router.post("/api/plan")
async def create_plan(text: str = Form(...)):
    try:
        plan = generate_plan(text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    plan["request_text"] = text
    return JSONResponse(content=plan)


@router.post("/api/plan/save")
async def save_plan(payload: dict = Body(...)):
    # Saving = Lucas approved the plan, so gear he mentioned counts toward his per-activity profile
    update_gear_memory(payload.get("activity", ""), payload.get("mentioned_gear", []))
    entry = format_plan_markdown(payload, payload.get("request_text", ""))
    try:
        saved = save_plan_to_github(entry, title=payload.get("title", "untitled"))
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"GitHub save failed: {e}")
    return JSONResponse(content={"saved": saved})


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: py planner.py "spearfishing Tuesday, bringing my speargun"')
        sys.exit(1)
    message = " ".join(sys.argv[1:])
    result = generate_plan(message)
    entry = format_plan_markdown(result, message)
    print(entry)
    update_gear_memory(result.get("activity", ""), result.get("mentioned_gear", []))
    saved = save_plan_to_github(entry, title=result.get("title", "untitled"))
    print("Saved to GitHub notes/planner.md" if saved else "NOT saved (GITHUB_TOKEN missing)")
