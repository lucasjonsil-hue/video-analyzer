"""Stage 4 — cut: moments JSON -> ffmpeg -> output/clip_01.mp4 ... (vertical 1080x1920)."""

import json
import os
import subprocess
import sys

from common import OUTPUT_DIR

# Center-crop to 9:16 (never wider than the source), then fit onto a 1080x1920 canvas.
VF = (
    "crop='min(iw,ih*9/16)':ih,"
    "scale=1080:1920:force_original_aspect_ratio=decrease,"
    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
)


def cut(moments_path: str) -> list[str]:
    """Cut every moment into a vertical clip; returns the list of clip paths."""
    with open(moments_path, encoding="utf-8") as f:
        data = json.load(f)
    clips = []
    for i, m in enumerate(data["moments"], start=1):
        out = os.path.join(OUTPUT_DIR, f"clip_{i:02d}.mp4")
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-ss", str(m["start"]), "-to", str(m["end"]), "-i", data["video"],
            "-vf", VF,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k",
            out,
        ]
        subprocess.run(cmd, check=True)
        clips.append(out)
    return clips


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: py cut.py <moments_json>")
    for c in cut(sys.argv[1]):
        print(c)
