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

import base64
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

# Task Scheduler runs this under cp1252; emoji in email subjects crash print().
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests

import email_intake as ei
from email_assistant import classify_messages, fetch_message_body, write_reply, create_reply_draft, NOREPLY_RE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER = "http://127.0.0.1:8000"

FOLDER_BY_CATEGORY = {
    "video-links": "Video Links",
    "action-needed": "Action Needed",
    "personal": "Personal",
    "newsletter": "Newsletters",
    "notification": "Notifications",
    "suspicious": "Suspicious",
    "junk": "Junk Review",
}
DRAFT_CATEGORIES = {"action-needed", "personal"}


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "lucasjonsil-hue/video-analyzer")
REMINDERS_PATH = "notes/reminders.md"


def save_reminder_to_github(m: dict) -> None:
    """Append a dated reminder from an email's extracted deadline (deduped by subject)."""
    deadline = m.get("deadline")
    if not GITHUB_TOKEN or not deadline:
        return
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{REMINDERS_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    resp = requests.get(api_url, headers=headers, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        sha = data["sha"]
    elif resp.status_code == 404:
        content = "# Reminders\n\nDeadlines and bills pulled automatically from email.\n"
        sha = None
    else:
        resp.raise_for_status()

    marker = f"(email: {m['subject']})"
    if marker in content:
        return  # this email's obligation already recorded
    entry = (
        f"\n## {deadline['date']}\n"
        f"Source: email from {m.get('from_name') or m.get('from_address', '?')}\n\n"
        f"{deadline.get('what', 'Deadline')} {marker}\n"
    )
    payload = {
        "message": f"Add reminder: {deadline.get('what', 'deadline')[:60]}",
        "content": base64.b64encode((content + entry).encode("utf-8")).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha
    requests.put(api_url, headers=headers, json=payload, timeout=15).raise_for_status()
    log(f"  reminder saved: {deadline['date']} — {deadline.get('what', '')}")


def get_token_headless() -> str:
    """Silent-only token for the first account (backfill scripts import this)."""
    tokens = ei.get_all_tokens()
    if not tokens:
        raise SystemExit(
            "Silent token refresh failed — run `py email_intake.py` once interactively to sign in again."
        )
    return tokens[0][1]


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


BACKLOG_FILE = os.path.join(BASE_DIR, "video_backlog.txt")


def queue_backlog(urls: list[str]) -> None:
    """Queue links that couldn't be analyzed; /jarvis retries them next session."""
    try:
        existing = set()
        if os.path.exists(BACKLOG_FILE):
            with open(BACKLOG_FILE, encoding="utf-8") as f:
                existing = {line.strip() for line in f if line.strip()}
        new = [u for u in urls if u not in existing]
        if new:
            with open(BACKLOG_FILE, "a", encoding="utf-8") as f:
                f.writelines(u + "\n" for u in new)
            log(f"  backlog: {len(new)} link(s) queued for retry")
    except OSError as e:
        log(f"  backlog write failed: {str(e)[:100]}")


LINK_NOTES_PATH = os.path.join(BASE_DIR, "notes", "link_notes.md")
_URL_LINE_RE = re.compile(r"https?://\S+")


def capture_link_notes(m: dict) -> None:
    """Lucas writes notes UNDER the links in the emails he sends himself. Keep
    them: extract each link + the note text beneath it and append to
    link_notes.md so the ideas/questions aren't lost (the links themselves still
    go through the analyzer separately). Links with no note are skipped. Deduped
    by a hidden per-(url, note) marker so re-runs don't pile up duplicates."""
    body = m.get("body", "") or ""
    lines = [ln.strip() for ln in body.splitlines()]
    pairs = []
    for i, ln in enumerate(lines):
        mo = _URL_LINE_RE.search(ln)
        if not mo:
            continue
        url = mo.group(0).split("?")[0].rstrip(".,")
        note_parts = []
        for nxt in lines[i + 1:i + 4]:
            if not nxt:
                continue
            if _URL_LINE_RE.search(nxt):
                break
            if "get outlook" in nxt.lower():
                continue
            note_parts.append(nxt)
        note = " ".join(note_parts).strip()
        if note:
            pairs.append((url, note))
    if not pairs:
        return
    try:
        os.makedirs(os.path.dirname(LINK_NOTES_PATH), exist_ok=True)
        existing = ""
        if os.path.exists(LINK_NOTES_PATH):
            with open(LINK_NOTES_PATH, encoding="utf-8") as f:
                existing = f.read()
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        subject = m.get("subject", "")
        new_blocks = []
        for url, note in pairs:
            marker = f"{url} :: {note}"
            if marker in existing:
                continue
            new_blocks.append(
                f"- [{stamp}] {url}\n"
                f"    NOTE: {note}\n"
                f"    (email: {subject}) — video analysis pending cross-check\n"
                f"    <!--mark:{marker}-->\n"
            )
        if new_blocks:
            with open(LINK_NOTES_PATH, "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join(new_blocks))
            log(f"  [{subject}] captured {len(new_blocks)} link-note(s) to link_notes.md")
    except OSError as e:
        log(f"  link-note capture failed: {str(e)[:100]}")


def process_video_email(token: str, m: dict) -> None:
    capture_link_notes(m)
    urls = sorted(set(ei.VIDEO_URL_RE.findall(m["body"])))
    if not urls:
        log(f"  [{m['subject']}] classified video-links but no links found")
        return
    if not ensure_server():
        queue_backlog(urls)
        return
    ok = fail = 0
    failed_urls = []
    for url in urls:
        try:
            resp = requests.post(SERVER + "/analyze-url", data={"url": url}, timeout=300)
            if resp.status_code == 200:
                ok += 1
            else:
                fail += 1
                failed_urls.append(url)
                detail = resp.json().get("detail", resp.status_code) if resp.text else resp.status_code
                log(f"    FAIL {url} — {str(detail)[:100]}")
        except requests.RequestException as e:
            fail += 1
            failed_urls.append(url)
            log(f"    FAIL {url} — {str(e)[:100]}")
    log(f"  [{m['subject']}] videos analyzed: {ok} ok, {fail} failed")
    if failed_urls:
        queue_backlog(failed_urls)
    ei.mark_read(token, m["id"])


def process_draftworthy(token: str, m: dict) -> None:
    try:
        full = fetch_message_body(token, m["id"])
        reply = write_reply(full)
        create_reply_draft(token, m["id"], reply)
        log(f"  [{m['subject']}] reply draft created in Outlook Drafts")
    except (requests.RequestException, Exception) as e:
        log(f"  [{m['subject']}] draft failed: {str(e)[:120]}")


def run_for_account(username: str, token: str) -> None:
    messages = fetch_unread(token)
    if not messages:
        log(f"[{username}] no new mail")
        return
    log(f"[{username}] {len(messages)} unread message(s) — classifying")
    classify_messages(messages)
    folder_ids = get_folder_ids(token)

    for m in messages:
        category = m["category"]
        log(f"[{category}] {m['subject']} — {m.get('gist', '')}")
        if category == "video-links":
            process_video_email(token, m)
        elif (
            category in DRAFT_CATEGORIES
            and m.get("reply_worthwhile")
            and not NOREPLY_RE.search(m.get("from_address", ""))
        ):
            process_draftworthy(token, m)
        try:
            save_reminder_to_github(m)
        except requests.RequestException as e:
            log(f"  reminder save failed: {str(e)[:100]}")
        try:
            move_message(token, m["id"], folder_ids[category])
        except requests.RequestException as e:
            log(f"  move failed: {str(e)[:120]}")


def check_wave_alerts() -> None:
    """Piggyback the planner's wave alert on this scheduled run (self-throttled to ~6h)."""
    try:
        from planner import run_wave_alert_check
        result = run_wave_alert_check()
        if result.get("new_alerts"):
            days = ", ".join(d["date"] for d in result["new_alerts"])
            log(f"wave alert: swell threshold hit on {days} — reminder filed")
    except Exception as e:
        log(f"wave alert check failed: {str(e)[:120]}")


def main() -> None:
    tokens = ei.get_all_tokens()
    if not tokens:
        raise SystemExit(
            "No account tokens available — run `py email_intake.py` once interactively to sign in again."
        )
    for username, token in tokens:
        run_for_account(username, token)
    check_wave_alerts()
    log("run complete")


if __name__ == "__main__":
    main()
