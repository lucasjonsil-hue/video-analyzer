"""Clipper pipeline — one command: py pipeline.py <url_or_path>

URL/file -> download -> transcribe (word timestamps) -> Claude picks viral moments
-> cut to vertical 1080x1920 -> burn captions. Clips land in output/.
"""

import json
import sys
import time

from captions import caption_clips
from common import OUTPUT_DIR
from cut import cut
from ingest import ingest
from moments import find_moments
from transcribe import transcribe


def stage(label: str):
    print(f"\n=== {label} ===", flush=True)
    return time.time()


def main(src: str) -> None:
    t = stage("1/5 ingest")
    video = ingest(src)
    print(f"video: {video}  ({time.time() - t:.0f}s)")

    t = stage("2/5 transcribe (local Whisper, may take a few minutes)")
    transcript = transcribe(video)
    print(f"transcript: {transcript}  ({time.time() - t:.0f}s)")

    t = stage("3/5 pick moments (Claude)")
    moments_path = find_moments(transcript)
    print(f"moments: {moments_path}  ({time.time() - t:.0f}s)")

    t = stage("4/5 cut vertical clips")
    clips = cut(moments_path)
    print(f"{len(clips)} clip(s)  ({time.time() - t:.0f}s)")

    t = stage("5/5 burn captions")
    caption_clips(moments_path, transcript)
    print(f"captions burned  ({time.time() - t:.0f}s)")

    with open(moments_path, encoding="utf-8") as f:
        moments = json.load(f)["moments"]
    print(f"\nDone. Clips in {OUTPUT_DIR}")
    for i, m in enumerate(moments, start=1):
        print(f"  clip_{i:02d}.mp4  [{m['start']:.0f}s-{m['end']:.0f}s]  hook: {m['hook_text']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: py pipeline.py <url_or_path>")
    main(sys.argv[1])
