"""Read-only inbox peek for the /jarvis recap.

Lists the most recent inbox messages across every signed-in account so the
jarvis email-check agent can report a one-line note per email. Strictly
read-only: no marking read, no folder moves, no drafts, no Claude calls — the
scheduled email_agent.py owns all of that. This just looks.

Run:  py jarvis_email_peek.py [N]   (N = how many recent messages, default 12)
Output: one compact line per message, easy for an agent to relay.
"""

import sys

# Task Scheduler / cheap agents may run under cp1252; emoji in subjects crash print().
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests

import email_intake as ei

TOP = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 12


def fetch_recent(token: str, top: int) -> list[dict]:
    resp = requests.get(
        f"{ei.GRAPH}/me/mailFolders/inbox/messages",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "$top": str(top),
            "$select": "subject,from,receivedDateTime,isRead,bodyPreview",
            "$orderby": "receivedDateTime desc",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("value", [])


def main() -> None:
    tokens = ei.get_all_tokens()
    if not tokens:
        print("EMAIL_PEEK: no signed-in accounts / silent refresh failed — "
              "run `py email_intake.py` once to re-auth.")
        return

    for username, token in tokens:
        print(f"=== {username} ===")
        try:
            messages = fetch_recent(token, TOP)
        except requests.RequestException as e:
            print(f"  (fetch failed: {e})")
            continue
        if not messages:
            print("  (inbox empty)")
            continue
        for m in messages:
            sender = (m.get("from") or {}).get("emailAddress", {})
            name = sender.get("name") or sender.get("address") or "?"
            subject = m.get("subject") or "(no subject)"
            date = (m.get("receivedDateTime") or "")[:16].replace("T", " ")
            flag = "UNREAD" if not m.get("isRead") else "read  "
            preview = " ".join((m.get("bodyPreview") or "").split())[:160]
            print(f"  [{flag}] {date} | {name} | {subject}")
            print(f"           {preview}")


if __name__ == "__main__":
    main()
