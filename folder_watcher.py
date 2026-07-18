"""Folder watcher for Life Hacker 3000 — auto-analyze dropped video files.

Watches a folder (default: F:\\Life3000\\inbox_videos) and feeds every new
video file through the analyzer's /analyze endpoint, one at a time (the
server can't handle concurrent requests). Processed files move to done/,
failures to failed/, so nothing is ever analyzed twice or deleted.

Run:  py folder_watcher.py [folder]   (with the analyzer server running)
Stop with Ctrl+C. Point your phone-sync app (e.g. OneDrive camera roll,
Syncthing) at the watch folder and saved videos analyze themselves.
"""

import os
import shutil
import sys
import time

import requests

ANALYZER_URL = "http://127.0.0.1:8000/analyze"
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".webm", ".mkv", ".m4v"}
POLL_SECONDS = 10

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WATCH_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, "inbox_videos")
DONE_DIR = os.path.join(WATCH_DIR, "done")
FAILED_DIR = os.path.join(WATCH_DIR, "failed")


def is_stable(path: str) -> bool:
    """True once the file has stopped growing (finished copying/syncing)."""
    try:
        size1 = os.path.getsize(path)
        time.sleep(2)
        size2 = os.path.getsize(path)
    except OSError:
        return False
    return size1 == size2 and size1 > 0


def analyze(path: str) -> tuple[bool, str]:
    name = os.path.basename(path)
    try:
        with open(path, "rb") as f:
            resp = requests.post(ANALYZER_URL, files={"video": (name, f, "video/mp4")}, timeout=600)
    except requests.RequestException as e:
        return False, str(e)
    if resp.status_code != 200:
        try:
            return False, str(resp.json().get("detail", resp.status_code))
        except ValueError:
            return False, f"HTTP {resp.status_code}"
    result = resp.json()
    return True, f"{result.get('note_category', '?')}: {result.get('summary', '')[:80]}"


def main() -> None:
    for d in (WATCH_DIR, DONE_DIR, FAILED_DIR):
        os.makedirs(d, exist_ok=True)
    try:
        requests.get("http://127.0.0.1:8000/", timeout=5)
    except requests.RequestException:
        raise SystemExit(
            "The video analyzer server isn't running. Start it first:\n"
            "  py -m uvicorn main:app --host 127.0.0.1 --port 8000"
        )
    print(f"Watching {WATCH_DIR} — drop video files there ({', '.join(sorted(VIDEO_EXTS))}). Ctrl+C to stop.")

    while True:
        for name in sorted(os.listdir(WATCH_DIR)):
            path = os.path.join(WATCH_DIR, name)
            if not os.path.isfile(path) or os.path.splitext(name)[1].lower() not in VIDEO_EXTS:
                continue
            if not is_stable(path):
                print(f"  {name}: still copying, will retry")
                continue
            print(f"  analyzing {name} …", flush=True)
            ok, info = analyze(path)
            dest = os.path.join(DONE_DIR if ok else FAILED_DIR, name)
            if os.path.exists(dest):
                stem, ext = os.path.splitext(name)
                dest = os.path.join(DONE_DIR if ok else FAILED_DIR, f"{stem}_{int(time.time())}{ext}")
            shutil.move(path, dest)
            print(f"    {'ok' if ok else 'FAIL'} — {info}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
