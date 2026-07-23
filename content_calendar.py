"""Weekly faceless-clip content calendar (Clipfarm posting plan).

Generates a 7-day posting calendar for Lucas's faceless clipping accounts so he
posts consistently — the single biggest lever on clip earnings. Modeled on the
"Claude Cowork content calendar" idea Lucas saved (reel DYQEVXoyz9M), but built
local + cheap instead of a fragile browse-the-web agent.

Inputs (all fail soft if F:\\Clipfarm isn't mounted):
- Clipfarm campaigns.json  -> which campaign(s) are live + their rules (so the
  plan never suggests something a campaign would reject: no watermarks, likes/
  comments on, no misrepresenting the footage, etc.).
- Clipfarm notes/clipping.md -> recent clipping notes (payout rates, platform
  quirks) analyzed from Lucas's videos.

Output: a dated 7-day plan prepended to notes/content_calendar.md — per day:
platform, content type, which moment/clip to cut, title, hook, edit notes,
caption, hashtags, best post time.

Usable:
- CLI:      py content_calendar.py
- weekly:   run_content_calendar.bat via Windows Task Scheduler (Mondays)
- import:   generate_calendar() -> dict ; save_calendar_markdown(cal) -> path

Cost: one Claude call per run (Haiku by default). Override with CALENDAR_MODEL.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import anthropic
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIPFARM_DIR = os.environ.get("CLIPFARM_DIR", r"F:\Clipfarm")
CALENDAR_PATH = os.path.join(BASE_DIR, "notes", "content_calendar.md")
# Cheap by default — a weekly posting plan doesn't need a frontier model.
CALENDAR_MODEL = os.environ.get("CALENDAR_MODEL", "claude-haiku-4-5-20251001")

client = anthropic.Anthropic()

CALENDAR_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "week_of": {"type": "string", "description": "Monday of the plan week, YYYY-MM-DD"},
        "focus": {"type": "string", "description": "One line: the week's theme / which campaign(s) this serves"},
        "days": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "day": {"type": "string"},
                    "date": {"type": "string"},
                    "platform": {"type": "string", "enum": ["TikTok", "Instagram Reels", "YouTube Shorts"]},
                    "content_type": {"type": "string"},
                    "source_moment": {"type": "string", "description": "Which clip/moment to cut, or the angle if no source yet"},
                    "title": {"type": "string"},
                    "hook": {"type": "string", "description": "First 1-2 seconds of on-screen text / spoken hook"},
                    "edit_notes": {"type": "string", "description": "How to cut it (length, captions, pacing) within campaign rules"},
                    "caption": {"type": "string"},
                    "hashtags": {"type": "array", "items": {"type": "string"}},
                    "best_post_time": {"type": "string"},
                },
                "required": ["day", "date", "platform", "content_type", "source_moment",
                             "title", "hook", "edit_notes", "caption", "hashtags", "best_post_time"],
            },
        },
        "reminders": {"type": "array", "items": {"type": "string"},
                      "description": "Campaign-rule reminders to check before posting"},
    },
    "required": ["week_of", "focus", "days", "reminders"],
}

SYSTEM = """You are Lucas's faceless short-form content planner. Lucas runs a clipping
business (Clipfarm): he cuts vertical clips from long-form source videos and posts them to
faceless clip accounts to earn per-view campaign payouts. He is FACELESS-FIRST — never suggest
anything that requires showing his face or voice on camera. His #1 goal is making money from
these clips.

Today is {today}. Build a concrete posting calendar for the NEXT 7 DAYS starting today ({monday}).
Produce exactly 7 day-entries (one per calendar day). Pick the single best platform for each day
(you may note a cross-post in edit_notes) — do not create multiple entries for the same date.

Ground every suggestion in the live campaign context below. NEVER suggest anything a campaign
rule forbids. If a rule list is present, treat it as hard constraints.

{campaign_block}
{clipping_block}
Rules for the plan:
- Faceless only: clips from source footage, text hooks, captions, voiceover-optional. No face.
- Realistic cadence: 1-2 posts/day max across platforms; quality over spam (campaigns reject low-effort/engagement-farming posts).
- Each day: pick the platform, the exact moment/angle to cut, a scroll-stopping hook, edit notes (length, caption style, pacing), a caption, 3-6 hashtags, and a best post time (US audience).
- Vary hooks and moments across the week; don't repeat the same clip.
- If there's no live source video yet, plan the angle/hook so Lucas can slot footage in.
- Put campaign-rule checks (no watermarks, likes/comments enabled, no misrepresentation, no boosted promo) in `reminders`.
Keep it tight and immediately usable — this is a to-do list, not an essay."""


def _read(path, limit=4000):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()[-limit:]
    except OSError:
        return ""


def _campaign_block() -> str:
    path = os.path.join(CLIPFARM_DIR, "campaigns.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return ("No campaigns.json found (Clipfarm drive may be unmounted). Plan generic "
                "faceless clip content and tell Lucas to lock a real campaign first.\n")
    camps = data.get("campaigns", [])
    live = [c for c in camps if c.get("fits_pipeline")]
    rec = [c for c in camps if c.get("recommended")]
    lines = ["LIVE CAMPAIGN CONTEXT:"]
    for c in (rec or live or camps)[:3]:
        lines.append(
            f"- {c.get('title')} ({c.get('brand')}) — ${c.get('cpm_usd','?')} CPM, "
            f"source: {c.get('source_material','?')}"
            + (" [RECOMMENDED]" if c.get("recommended") else "")
        )
        for r in c.get("rules", [])[:8]:
            lines.append(f"    RULE: {r}")
    return "\n".join(lines) + "\n"


def _clipping_block() -> str:
    txt = _read(os.path.join(CLIPFARM_DIR, "notes", "clipping.md"), 2500)
    if not txt.strip():
        return ""
    return "RECENT CLIPPING NOTES (from analyzed videos):\n" + txt + "\n"


def generate_calendar() -> dict:
    today = datetime.now(timezone.utc)
    resp = client.messages.create(
        model=CALENDAR_MODEL,
        max_tokens=8000,
        system=SYSTEM.format(
            today=today.strftime("%Y-%m-%d (%A)"),
            monday=today.strftime("%Y-%m-%d"),
            campaign_block=_campaign_block(),
            clipping_block=_clipping_block(),
        ),
        output_config={"format": {"type": "json_schema", "schema": CALENDAR_SCHEMA}},
        messages=[{"role": "user",
                   "content": "Build this week's 7-day faceless clip posting calendar."}],
    )
    if resp.stop_reason == "refusal":
        raise ValueError("model declined to generate the calendar")
    raw = next(b.text for b in resp.content if b.type == "text")
    return json.loads(raw)


def format_markdown(cal: dict) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = [f"\n## Week of {cal.get('week_of','?')}  (generated {stamp})",
           f"Focus: {cal.get('focus','')}", ""]
    for d in cal.get("days", []):
        out += [
            f"### {d.get('day')} {d.get('date')} — {d.get('platform')}",
            f"- Type: {d.get('content_type')}",
            f"- Cut: {d.get('source_moment')}",
            f"- Title: {d.get('title')}",
            f"- Hook: {d.get('hook')}",
            f"- Edit: {d.get('edit_notes')}",
            f"- Caption: {d.get('caption')}",
            f"- Hashtags: {' '.join(d.get('hashtags', []))}",
            f"- Post at: {d.get('best_post_time')}",
            "",
        ]
    if cal.get("reminders"):
        out.append("**Before posting — campaign rule check:**")
        out += [f"- {r}" for r in cal["reminders"]]
        out.append("")
    return "\n".join(out)


def save_calendar_markdown(cal: dict) -> str:
    os.makedirs(os.path.dirname(CALENDAR_PATH), exist_ok=True)
    block = format_markdown(cal)
    header = "# Content Calendar — faceless clip posting plan\n\nNewest week first. Generated weekly by content_calendar.py.\n"
    existing = ""
    if os.path.exists(CALENDAR_PATH):
        with open(CALENDAR_PATH, encoding="utf-8") as f:
            existing = f.read()
        if existing.startswith(header):
            existing = existing[len(header):]
    with open(CALENDAR_PATH, "w", encoding="utf-8") as f:
        f.write(header + block + existing)
    return CALENDAR_PATH


def main():
    cal = generate_calendar()
    path = save_calendar_markdown(cal)
    print(f"[content_calendar] wrote {len(cal.get('days', []))}-day plan -> {path}")


if __name__ == "__main__":
    main()
