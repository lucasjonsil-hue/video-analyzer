"""Stage 1 — ingest: URL (YouTube/TikTok/Instagram) or local file -> source/<id>.mp4"""

import os
import shutil
import sys

import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget

from common import SOURCE_DIR


def ingest(src: str) -> str:
    """Download (or copy) the video into source/ and return the local path."""
    if os.path.exists(src):
        dest = os.path.join(SOURCE_DIR, os.path.basename(src))
        if os.path.abspath(src) != os.path.abspath(dest):
            shutil.copy2(src, dest)
        return dest

    ydl_opts = {
        "format": "mp4/best",
        "outtmpl": os.path.join(SOURCE_DIR, "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        # Same anti-bot fix as main.py — Instagram rejects anonymous clients.
        "impersonate": ImpersonateTarget.from_str("chrome"),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(src, download=True)
        path = ydl.prepare_filename(info)
    if not os.path.exists(path):
        raise ValueError(f"Download did not produce a file for {src}")
    return path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: py ingest.py <url_or_path>")
    print(ingest(sys.argv[1]))
