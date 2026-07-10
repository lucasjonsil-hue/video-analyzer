"""Email intake for Life Hacker 3000.

Checks the Outlook.com inbox for unread emails whose subject contains "video",
extracts any video links (Instagram/YouTube/TikTok) from the body, feeds each
one to the local video analyzer, then marks the email as read.

Run:  py email_intake.py   (from F:\\Life3000, with the analyzer server running)

First run prints a login code — sign in once at microsoft.com/devicelogin and
the token is cached locally (ms_token_cache.json) so later runs are automatic.
Requires MS_CLIENT_ID in .env (see CLAUDE.md, Email & Calendar section).
"""

import os
import re
import requests
import msal
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_CACHE_PATH = os.path.join(BASE_DIR, "ms_token_cache.json")

CLIENT_ID = os.environ.get("MS_CLIENT_ID")
AUTHORITY = "https://login.microsoftonline.com/consumers"
SCOPES = ["Mail.ReadWrite"]
GRAPH = "https://graph.microsoft.com/v1.0"
ANALYZER_URL = "http://127.0.0.1:8000/analyze-url"

VIDEO_URL_RE = re.compile(
    r"https?://(?:www\.)?"
    r"(?:instagram\.com/(?:reel|p)/[A-Za-z0-9_-]+"
    r"|youtube\.com/watch\?v=[A-Za-z0-9_-]+"
    r"|youtu\.be/[A-Za-z0-9_-]+"
    r"|tiktok\.com/[^\s\"'<>]+"
    r")[^\s\"'<>]*"
)


def get_token() -> str:
    if not CLIENT_ID:
        raise SystemExit(
            "MS_CLIENT_ID is missing from .env — do the one-time app registration "
            "described in CLAUDE.md (Email & Calendar section) and add the client ID."
        )
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_PATH):
        with open(TOKEN_CACHE_PATH, "r", encoding="utf-8") as f:
            cache.deserialize(f.read())
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)

    result = None
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    if not result:
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise SystemExit(f"Could not start device login: {flow}")
        print(flow["message"])
        result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        raise SystemExit(f"Login failed: {result.get('error_description')}")

    if cache.has_state_changed:
        with open(TOKEN_CACHE_PATH, "w", encoding="utf-8") as f:
            f.write(cache.serialize())
    return result["access_token"]


def fetch_unread_messages(token: str) -> list[dict]:
    resp = requests.get(
        f"{GRAPH}/me/mailFolders/inbox/messages",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "$filter": "isRead eq false",
            "$top": "20",
            "$select": "id,subject,body",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("value", [])


def mark_read(token: str, message_id: str) -> None:
    requests.patch(
        f"{GRAPH}/me/messages/{message_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"isRead": True},
        timeout=30,
    ).raise_for_status()


def analyze(url: str) -> tuple[bool, str]:
    try:
        resp = requests.post(ANALYZER_URL, data={"url": url}, timeout=300)
    except requests.RequestException as e:
        return False, str(e)
    if resp.status_code != 200:
        detail = resp.json().get("detail", resp.text[:120]) if resp.text else str(resp.status_code)
        return False, str(detail)
    result = resp.json()
    return True, f"{result.get('note_category', '?')}: {result.get('summary', '')[:100]}"


def main() -> None:
    try:
        requests.get("http://127.0.0.1:8000/", timeout=5)
    except requests.RequestException:
        raise SystemExit(
            "The video analyzer server isn't running. Start it first:\n"
            "  py -m uvicorn main:app --host 127.0.0.1 --port 8000"
        )

    token = get_token()
    messages = fetch_unread_messages(token)
    video_emails = [m for m in messages if "video" in (m.get("subject") or "").lower()]
    print(f"Unread emails: {len(messages)}, with 'video' in subject: {len(video_emails)}")

    processed = failed = 0
    for msg in video_emails:
        body = msg.get("body", {}).get("content", "")
        urls = sorted(set(VIDEO_URL_RE.findall(body)))
        if not urls:
            print(f"  [{msg['subject']}] no video links found, skipping")
            continue
        print(f"  [{msg['subject']}] {len(urls)} link(s)")
        for url in urls:
            ok, info = analyze(url)
            status = "ok " if ok else "FAIL"
            print(f"    {status} {url}\n         {info}")
            processed += ok
            failed += not ok
        mark_read(token, msg["id"])

    print(f"\nDone. {processed} analyzed, {failed} failed.")


if __name__ == "__main__":
    main()
