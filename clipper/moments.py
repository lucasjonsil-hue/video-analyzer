"""Stage 3 — moments: transcript JSON -> Claude -> moments/<stem>.json (top 5 clips)."""

import json
import os
import re
import sys

import anthropic

from common import CLIPPER_MODEL, MOMENTS_DIR, stem_for

PROMPT = """\
You are picking the most viral-worthy clips from a video transcript for short-form \
platforms (TikTok/Reels/Shorts). Each line is "[start-end] text" in seconds.

Pick the {n} best 15-60 second moments. Prioritize: strong hooks, punchlines, \
surprising claims, actionable tips. Each moment must start and end on natural \
sentence boundaries taken from the timestamps, be 15-60 seconds long, and moments \
must not overlap.

Return ONLY a valid JSON array, no other text, each element exactly:
{{"start": <seconds>, "end": <seconds>, "hook_text": "<first spoken line of the clip>", "reason": "<one line: why this could go viral>"}}

Transcript ({duration}s total):
{transcript}
"""


def find_moments(transcript_path: str, n: int = 5) -> str:
    """Ask Claude for the top clip-worthy moments; returns the moments JSON path."""
    with open(transcript_path, encoding="utf-8") as f:
        tr = json.load(f)
    lines = "\n".join(f"[{s['start']}-{s['end']}] {s['text']}" for s in tr["segments"])
    # A video can only support so many non-overlapping 15s+ clips.
    n = max(1, min(n, int(tr["duration"] // 20)))

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=CLIPPER_MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": PROMPT.format(n=n, duration=tr["duration"], transcript=lines)}],
    )
    # The model may emit a thinking block first — take the text block, wherever it is.
    text = next(b.text for b in resp.content if b.type == "text").strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)  # tolerate stray prose/code fences
    if not match:
        raise ValueError(f"Claude did not return a JSON array:\n{text[:500]}")
    moments = json.loads(match.group(0))

    for m in moments:
        m["start"], m["end"] = float(m["start"]), float(m["end"])
        if not (5 <= m["end"] - m["start"] <= 90):
            raise ValueError(f"Moment has implausible length: {m}")
        m["end"] = min(m["end"], tr["duration"])

    out_path = os.path.join(MOMENTS_DIR, f"{stem_for(transcript_path)}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"video": tr["video"], "moments": moments}, f, ensure_ascii=False, indent=1)
    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: py moments.py <transcript_json>")
    print(find_moments(sys.argv[1]))
