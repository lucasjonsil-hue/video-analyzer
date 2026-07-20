"""Shared paths/config for the clipper pipeline. Lives inside F:\\Life3000\\clipper."""

import os

from dotenv import load_dotenv

CLIPPER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CLIPPER_DIR)

# Reuse the main project's .env (ANTHROPIC_API_KEY) and Whisper model cache.
load_dotenv(os.path.join(PROJECT_DIR, ".env"))
MODEL_DIR = os.path.join(PROJECT_DIR, "models")

SOURCE_DIR = os.path.join(CLIPPER_DIR, "source")
TRANSCRIPTS_DIR = os.path.join(CLIPPER_DIR, "transcripts")
MOMENTS_DIR = os.path.join(CLIPPER_DIR, "moments")
OUTPUT_DIR = os.path.join(CLIPPER_DIR, "output")

for d in (SOURCE_DIR, TRANSCRIPTS_DIR, MOMENTS_DIR, OUTPUT_DIR):
    os.makedirs(d, exist_ok=True)

# Text-only moment picking is cheap; override with CLIPPER_MODEL in .env if needed.
CLIPPER_MODEL = os.environ.get("CLIPPER_MODEL", "claude-sonnet-5")


def stem_for(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]
