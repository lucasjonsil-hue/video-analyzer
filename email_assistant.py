"""Email assistant for Life Hacker 3000 (stage 2 of the Email module).

Reads the Outlook.com inbox via Microsoft Graph, categorizes every message
(video-links / action-needed / personal / newsletter / notification / junk),
and can draft a reply for any message — the draft is created in the Outlook
Drafts folder for Lucas to review and send himself. This module never sends
mail (the token's Mail.ReadWrite scope can't send even if asked to).

Usable two ways:
- FastAPI routes (mounted into main.py): GET /email, GET /api/email/inbox,
  POST /api/email/draft
- CLI: py email_assistant.py [limit]   — prints the categorized digest

Auth reuses email_intake.py's device-code token cache (ms_token_cache.json).
"""

import html
import json
import os
import re
import sys

import anthropic
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from email_intake import get_token, GRAPH

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
client = anthropic.Anthropic()

CATEGORIES = ["video-links", "action-needed", "personal", "newsletter", "notification", "junk"]


def _strip_html(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", text or "")).strip()


def fetch_inbox(token: str, limit: int = 25) -> list[dict]:
    resp = requests.get(
        f"{GRAPH}/me/mailFolders/inbox/messages",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "$top": str(limit),
            "$select": "id,subject,from,receivedDateTime,isRead,bodyPreview",
            "$orderby": "receivedDateTime desc",
        },
        timeout=30,
    )
    resp.raise_for_status()
    messages = []
    for m in resp.json().get("value", []):
        sender = (m.get("from") or {}).get("emailAddress", {})
        messages.append({
            "id": m["id"],
            "subject": m.get("subject") or "(no subject)",
            "from_name": sender.get("name", ""),
            "from_address": sender.get("address", ""),
            "received": m.get("receivedDateTime", ""),
            "is_read": m.get("isRead", False),
            "preview": (m.get("bodyPreview") or "")[:200],
        })
    return messages


def classify_messages(messages: list[dict]) -> list[dict]:
    """One cheap Claude call to categorize + one-line-summarize the whole batch."""
    if not messages:
        return messages
    listing = "\n".join(
        f"{i}. From: {m['from_name']} <{m['from_address']}> | Subject: {m['subject']} | Preview: {m['preview']}"
        for i, m in enumerate(messages)
    )
    prompt = (
        "Categorize each email below for Lucas's personal inbox triage.\n"
        f"Categories: {', '.join(CATEGORIES)}.\n"
        "- video-links: emails Lucas sent himself containing social-media video links for his analyzer\n"
        "- action-needed: a real person or service expects a reply or an action from Lucas\n"
        "- personal: from a real person, no action required\n"
        "- newsletter: subscribed content, promos, marketing\n"
        "- notification: automated service/account notices (sign-ins, receipts, social pings)\n"
        "- junk: spam, phishing, or worthless unsolicited mail\n\n"
        "Also write a ONE-line gist (max 15 words) per email, and whether a reply seems worth drafting.\n\n"
        f"Emails:\n{listing}\n\n"
        'Respond with ONLY a JSON array, one object per email in the same order: '
        '[{"index": 0, "category": "...", "gist": "...", "reply_worthwhile": true/false}, ...]'
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    start, end = raw.find("["), raw.rfind("]") + 1
    labels = json.loads(raw[start:end]) if start != -1 else []
    by_index = {item.get("index"): item for item in labels if isinstance(item, dict)}
    for i, m in enumerate(messages):
        label = by_index.get(i, {})
        m["category"] = label.get("category") if label.get("category") in CATEGORIES else "notification"
        m["gist"] = label.get("gist", "")
        m["reply_worthwhile"] = bool(label.get("reply_worthwhile", False))
    return messages


def fetch_message_body(token: str, message_id: str) -> dict:
    resp = requests.get(
        f"{GRAPH}/me/messages/{message_id}",
        headers={"Authorization": f"Bearer {token}"},
        params={"$select": "subject,from,body,toRecipients,receivedDateTime"},
        timeout=30,
    )
    resp.raise_for_status()
    m = resp.json()
    sender = (m.get("from") or {}).get("emailAddress", {})
    return {
        "subject": m.get("subject") or "(no subject)",
        "from_name": sender.get("name", ""),
        "from_address": sender.get("address", ""),
        "text": _strip_html(m.get("body", {}).get("content", ""))[:6000],
    }


def write_reply(message: dict, guidance: str = "") -> str:
    guidance_block = f"\nLucas's guidance for this reply: {guidance}\n" if guidance else ""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": (
                "Draft a reply for Lucas to the email below. Match the sender's register (casual for "
                "friends/family, professional for business). Be concise, warm, and concrete; don't invent "
                "commitments, dates, or facts Lucas didn't state — leave a [square-bracket placeholder] "
                f"where only he can fill in the answer.{guidance_block}\n"
                f"From: {message['from_name']} <{message['from_address']}>\n"
                f"Subject: {message['subject']}\n\n"
                f"{message['text']}\n\n"
                "Respond with ONLY the reply body text — no subject line, no explanation."
            ),
        }],
    )
    return response.content[0].text.strip()


def create_reply_draft(token: str, message_id: str, reply_text: str) -> None:
    """Creates a reply draft in the Outlook Drafts folder. Does NOT send."""
    resp = requests.post(
        f"{GRAPH}/me/messages/{message_id}/createReply",
        headers={"Authorization": f"Bearer {token}"},
        json={"comment": reply_text.replace("\n", "<br>")},
        timeout=30,
    )
    resp.raise_for_status()


router = APIRouter()


@router.get("/email", response_class=HTMLResponse)
async def email_page():
    with open(os.path.join(BASE_DIR, "email.html"), "r", encoding="utf-8") as f:
        return f.read()


@router.get("/api/email/inbox")
async def api_inbox(limit: int = 25):
    try:
        token = get_token()
        messages = classify_messages(fetch_inbox(token, limit=min(limit, 50)))
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Graph API error: {e}")
    return JSONResponse(content={"messages": messages, "categories": CATEGORIES})


@router.post("/api/email/draft")
async def api_draft(payload: dict = Body(...)):
    message_id = payload.get("message_id")
    if not message_id:
        raise HTTPException(status_code=400, detail="message_id is required")
    try:
        token = get_token()
        message = fetch_message_body(token, message_id)
        reply_text = write_reply(message, guidance=payload.get("guidance", ""))
        create_reply_draft(token, message_id, reply_text)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Graph API error: {e}")
    return JSONResponse(content={
        "draft": reply_text,
        "note": "Draft created in your Outlook Drafts folder — review and send it from there.",
    })


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    inbox = classify_messages(fetch_inbox(get_token(), limit=limit))
    by_cat: dict[str, list] = {}
    for m in inbox:
        by_cat.setdefault(m["category"], []).append(m)
    for cat in CATEGORIES:
        if cat not in by_cat:
            continue
        print(f"\n=== {cat} ({len(by_cat[cat])}) ===")
        for m in by_cat[cat]:
            flag = "  [reply?]" if m["reply_worthwhile"] else ""
            print(f"- {m['subject']}  — {m['gist']}{flag}")
