"""Stage 2 — transcribe: video -> transcripts/<stem>.json with word-level timestamps."""

import json
import os
import sys

from faster_whisper import WhisperModel

from common import MODEL_DIR, TRANSCRIPTS_DIR, stem_for

_model = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8", download_root=MODEL_DIR)
    return _model


def transcribe(video_path: str) -> str:
    """Transcribe with word timestamps; returns the transcript JSON path."""
    segments, info = get_model().transcribe(video_path, word_timestamps=True)
    seg_list, words = [], []
    for seg in segments:
        seg_list.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": seg.text.strip()})
        for w in seg.words or []:
            words.append({"word": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)})

    out = {
        "video": video_path,
        "language": info.language,
        "duration": round(info.duration, 2),
        "segments": seg_list,
        "words": words,
    }
    out_path = os.path.join(TRANSCRIPTS_DIR, f"{stem_for(video_path)}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: py transcribe.py <video_path>")
    print(transcribe(sys.argv[1]))
