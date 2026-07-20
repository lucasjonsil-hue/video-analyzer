"""Stage 5 — captions: burn big bold word-timed captions into each clip in output/."""

import json
import os
import subprocess
import sys

from common import OUTPUT_DIR

ASS_HEADER = """\
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Arial Black,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,0,2,40,40,640,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ass_time(t: float) -> str:
    t = max(t, 0.0)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def build_ass(words: list[dict], clip_start: float, clip_end: float) -> str:
    """Group the clip's words 2-3 per caption, times relative to the clip start."""
    in_clip = [w for w in words if clip_start <= w["start"] < clip_end and w["word"]]
    lines = [ASS_HEADER]
    group_size = 3
    for i in range(0, len(in_clip), group_size):
        group = in_clip[i:i + group_size]
        start = group[0]["start"] - clip_start
        end = min(group[-1]["end"], clip_end) - clip_start
        text = " ".join(w["word"] for w in group).upper().replace("{", "").replace("}", "")
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Caption,,0,0,0,,{text}\n")
    return "".join(lines)


def caption_clips(moments_path: str, transcript_path: str) -> list[str]:
    """Overwrite each output/clip_NN.mp4 with a captioned version."""
    with open(moments_path, encoding="utf-8") as f:
        moments = json.load(f)["moments"]
    with open(transcript_path, encoding="utf-8") as f:
        words = json.load(f)["words"]

    done = []
    for i, m in enumerate(moments, start=1):
        clip_name = f"clip_{i:02d}.mp4"
        clip_path = os.path.join(OUTPUT_DIR, clip_name)
        ass_name = f"clip_{i:02d}.ass"
        with open(os.path.join(OUTPUT_DIR, ass_name), "w", encoding="utf-8") as f:
            f.write(build_ass(words, m["start"], m["end"]))

        tmp_name = f"clip_{i:02d}_captioned.mp4"
        # cwd + relative names sidesteps ffmpeg's Windows drive-colon filter escaping.
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", clip_name, "-vf", f"ass={ass_name}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "copy",
            tmp_name,
        ]
        subprocess.run(cmd, check=True, cwd=OUTPUT_DIR)
        os.replace(os.path.join(OUTPUT_DIR, tmp_name), clip_path)
        done.append(clip_path)
    return done


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: py captions.py <moments_json> <transcript_json>")
    for c in caption_clips(sys.argv[1], sys.argv[2]):
        print(c)
