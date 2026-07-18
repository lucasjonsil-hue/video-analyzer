"""Scheduled email agent for Life Hacker 3000 — full unattended inbox triage.

Meant to run every ~30 min via Windows Task Scheduler (run_email_agent.bat).
Each run:
1. Fetches all UNREAD inbox messages.
2. Classifies them in one cheap Claude call (email_assistant categories).
3. video-links  -> extracts the links, feeds each through the analyzer
                   (starting the server if needed), marks the email read.
   reply-worthy -> (action-needed / personal only) Sonnet writes a rough
                   reply, filed as a DRAFT in Outlook via createReply —
                   this agent cannot send mail (Mail.ReadWrite scope).
4. Moves every processed message into a category subfolder under Inbox:
   Video Links / Action Needed / Personal / Newsletters / Notifications /
   Junk Review. Messages stay unread (except processed video links), so
   folder unread-counts show what's new.

Headless-safe: if the cached Graph token can't refresh silently, it exits
with instructions instead of hanging on a device-code prompt.
Log: email_agent_runs.log (via the .bat) — one summary line per action.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime

import msal
import requests

import email_intake as ei
from email_assistant import classify_messages, fetch_message_body, write_reply, create_reply_draft

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER = "http://127.0.0.1:8000"

FOLDER_BY_CATEGORY = {
    "video-links": "Video Links",
    "action-needed": "Action Needed",
    "personal": "Personal",
    "newsletter": "Newsletters",
    "notification": "Notifications",
    "junk": "Junk Review",
}
DRAFT_CATEGORIES = {"action-needed", "personal"}


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def get_token_headless() -> str:
    """Silent-only token refresh — never opens a device-code prompt."""
    cache = msal.SerializableTokenCache()
    if os.path.exists(ei.TOKEN_CACHE_PATH):
        with open(ei.TOKEN_CACHE_PATH, "r", encoding="utf-8") as f:
            cache.deserialize(f.read())
    app = msal.PublicClientApplication(ei.CLIENT_ID, authority=ei.AUTHORITY, token_cache=cache)
    accounts = app.get_accounts()
    result = app.acquire_token_silent(ei.SCOPES, account=accounts[0]) if accounts else None
    if not result or "access_token" not in result:
        raise SystemExit(
            "Silent token refresh failed — run `py email_intake.py` once interactively to sign in again."
        )
    if cache.has_state_changed:
        with open(ei.TOKEN_CACHE_PATH, "w", encoding="utf-8") as f:
            f.write(cache.serialize())
    return result["access_token"]


def graph_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def fetch_unread(token: str) -> list[dict]:
    resp = requests.get(
        f"{ei.GRAPH}/me/mailFolders/inbox/messages",
        headers=graph_headers(token),
        params={
            "$filter": "isRead eq false",
            "$top": "25",
            "$select": "id,subject,from,receivedDateTime,isRead,bodyPreview,body",
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
            "is_read": False,
            "preview": (m.get("bodyPreview") or "")[:200],
            "body": m.get("body", {}).get("content", ""),
        })
    return messages


def get_folder_ids(token: str) -> dict:
    """Find or create the category subfolders under Inbox; returns {category: folder_id}."""
    resp = requests.get(
        f"{ei.GRAPH}/me/mailFolders/inbox/childFolders",
        headers=graph_headers(token), params={"$top": "50"}, timeout=30,
    )
    resp.raise_for_status()
    existing = {f["displayName"]: f["id"] for f in resp.json().get("value", [])}
    ids = {}
    for category, name in FOLDER_BY_CATEGORY.items():
        if name not in existing:
            create = requests.post(
                f"{ei.GRAPH}/me/mailFolders/inbox/childFolders",
                headers=graph_headers(token), json={"displayName": name}, timeout=30,
            )
            create.raise_for_status()
            existing[name] = create.json()["id"]
            log(f"created folder: {name}")
        ids[category] = existing[name]
    return ids


def move_message(token: str, message_id: str, folder_id: str) -> None:
    requests.post(
        f"{ei.GRAPH}/me/messages/{message_id}/move",
        headers=graph_headers(token), json={"destinationId": folder_id}, timeout=30,
    ).raise_for_status()


def ensure_server() -> bool:
    try:
        requests.get(SERVER + "/", timeout=5)
        return True
    except requests.RequestException:
        pass
    log("analyzer server not running — starting it")
    subprocess.Popen(
        ["py", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BASE_DIR,
        stdout=open(os.path.join(BASE_DIR, "server.log"), "a"),
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
    )
    for _ in range(12):
        time.sleep(5)
        try:
            requests.get(SERVER + "/", timeout=5)
            return True
        except requests.RequestException:
            continue
    log("server failed to start — skipping video analysis this run")
    return False


def process_video_email(token: str, m: dict) -> None:
    urls = sorted(set(ei.VIDEO_URL_RE.findall(m["body"])))
    if not urls:
        log(f"  [{m['subject']}] classified video-links but no links found")
        return
    if not ensure_server():
        return
    ok = fail = 0
    for url in urls:
        try:
            resp = requests.post(SERVER + "/analyze-url", data={"url": url}, timeout=300)
            if resp.status_code == 200:
                ok += 1
            else:
                fail += 1
                detail = resp.json().get("detail", resp.status_code) if resp.text else resp.status_code
                log(f"    FAIL {url} — {str(detail)[:100]}")
        except requests.RequestException as e:
            fail += 1
            log(f"    FAIL {url} — {str(e)[:100]}")
    log(f"  [{m['subject']}] videos analyzed: {ok} ok, {fail} failed")
    ei.mark_read(token, m["id"])


def process_draftworthy(token: str, m: dict) -> None:
    try:
        full = fetch_message_body(token, m["id"])
        reply = write_reply(full)
        create_reply_draft(token, m["id"], reply)
        log(f"  [{m['subject']}] reply draft created in Outlook Drafts")
    except (requests.RequestException, Exception) as e:
        log(f"  [{m['subject']}] draft failed: {str(e)[:120]}")


def main() -> None:
    token = get_token_headless()
    messages = fetch_unread(token)
    if not messages:
        log("no new mail")
        return
    log(f"{len(messages)} unread message(s) — classifying")
    classify_messages(messages)
    folder_ids = get_folder_ids(token)

    for m in messages:
        category = m["category"]
        log(f"[{category}] {m['subject']} — {m.get('gist', '')}")
        if category == "video-links":
            process_video_email(token, m)
        elif category in DRAFT_CATEGORIES and m.get("reply_worthwhile"):
            process_draftworthy(token, m)
        try:
            move_message(token, m["id"], folder_ids[category])
        except requests.RequestException as e:
            log(f"  move failed: {str(e)[:120]}")
    log("run complete")


if __name__ == "__main__":
    main()
