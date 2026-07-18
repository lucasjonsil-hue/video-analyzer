import base64
import json
import cv2
import numpy as np
import tempfile
import os
import uuid
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import anthropic
import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget
from faster_whisper import WhisperModel

from planner import router as planner_router
from email_assistant import router as email_router

load_dotenv()

# Keep temp video files and the Whisper model cache on this drive (F:) rather
# than the system default (C:), which is nearly full on this machine.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "tmp")
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

app = FastAPI()
app.include_router(planner_router)
app.include_router(email_router)
client = anthropic.Anthropic()
whisper_model = WhisperModel("base", device="cpu", compute_type="int8", download_root=MODEL_DIR)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "lucasjonsil-hue/video-analyzer")
VALID_NOTE_CATEGORIES = {
    "fitness", "productivity", "investing", "ai_coding",
    "project_ideas", "to_do", "ideas",
}


def save_note_to_github(result: dict, source: str) -> bool:
    if not GITHUB_TOKEN:
        return False

    category = result.get("note_category")
    if category not in VALID_NOTE_CATEGORIES:
        category = "ideas"

    path = f"notes/{category}.md"
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    get_resp = requests.get(api_url, headers=headers, timeout=15)
    if get_resp.status_code == 200:
        existing = get_resp.json()
        current_content = base64.b64decode(existing["content"]).decode("utf-8")
        sha = existing["sha"]
    elif get_resp.status_code == 404:
        current_content = f"# {category.replace('_', ' ').title()} Notes\n"
        sha = None
    else:
        get_resp.raise_for_status()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    creator_line = f"Creator: {result['creator']}\n" if result.get("creator") else ""
    dm_cta = result.get("dm_cta")
    dm_line = (
        f"DM-Followup: pending — comment '{dm_cta.get('keyword', '?')}' to get: {dm_cta.get('offer', '?')}\n"
        if isinstance(dm_cta, dict) else ""
    )
    claims = [c for c in result.get("claims_check") or [] if isinstance(c, dict)]
    flagged = [c for c in claims if c.get("verdict") in ("dubious", "unverifiable")]
    claims_block = ""
    if flagged or result.get("hype_level") == "heavy":
        claims_block = "\n⚠️ Reliability" + (f" (hype: {result['hype_level']})" if result.get("hype_level") else "") + ":\n"
        claims_block += "".join(
            f"- [{c.get('verdict')}] {c.get('claim', '')} — {c.get('why', '')}\n" for c in flagged
        )
    entry = (
        f"\n## {timestamp}\n"
        f"Source: {source}\n"
        f"{creator_line}{dm_line}\n"
        f"{result.get('summary', '')}\n\n"
        f"{result.get('overview', '')}\n\n"
        + "\n".join(f"- {point}" for point in result.get("key_points", []))
        + "\n"
        + claims_block
    )
    transcript = (result.get("transcript") or "").strip()
    if transcript:
        entry += (
            "\n<details><summary>Full transcript</summary>\n\n"
            f"{transcript}\n\n"
            "</details>\n"
        )
    new_content = current_content + entry

    payload = {
        "message": f"Add {category} note from video analysis",
        "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha

    put_resp = requests.put(api_url, headers=headers, json=payload, timeout=15)
    put_resp.raise_for_status()
    return True


def _github_headers() -> dict:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def _github_get_file(path: str) -> tuple[str, str | None]:
    """Returns (content, sha); sha is None if the file doesn't exist yet."""
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    resp = requests.get(api_url, headers=_github_headers(), timeout=15)
    if resp.status_code == 404:
        return "", None
    resp.raise_for_status()
    data = resp.json()
    return base64.b64decode(data["content"]).decode("utf-8"), data["sha"]


def _github_put_file(path: str, content: str, sha: str | None, message: str) -> None:
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha
    requests.put(api_url, headers=_github_headers(), json=payload, timeout=15).raise_for_status()


PENDING_DM_PATH = "notes/pending_dm_followup.md"


def save_dm_followup_to_github(result: dict, source: str) -> None:
    """Log a comment-to-DM CTA so Lucas can chase the DM and attach the payload later."""
    dm_cta = result.get("dm_cta")
    if not GITHUB_TOKEN or not isinstance(dm_cta, dict):
        return
    content, sha = _github_get_file(PENDING_DM_PATH)
    if not content:
        content = "# Pending DM Follow-ups\n"
    if f"Source: {source}\n" in content + "\n":
        return  # already flagged
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    creator_line = f"Creator: {result['creator']}\n" if result.get("creator") else ""
    category = result.get("note_category", "ideas")
    entry = (
        f"\n## {timestamp}\n"
        f"Source: {source}\n"
        f"{creator_line}"
        f"Status: pending\n"
        f"Comment keyword: {dm_cta.get('keyword', '?')}\n"
        f"Promised: {dm_cta.get('offer', '?')}\n"
        f"Filed under: {category}\n"
    )
    _github_put_file(PENDING_DM_PATH, content + entry, sha, "Flag comment-to-DM follow-up")


def resolve_dm_followup_on_github(source: str, followup_text: str) -> bool:
    """Attach DM-screenshot findings to the pending entry for `source` and mark it resolved.

    Returns True if an existing pending entry was updated, False if a standalone
    resolved entry had to be appended (no pending entry matched the source URL).
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    content, sha = _github_get_file(PENDING_DM_PATH)
    if not content:
        content = "# Pending DM Follow-ups\n"
    followup_block = f"\n### Follow-up ({timestamp})\n{followup_text.strip()}\n"

    blocks = content.split("\n## ")
    matched = False
    for i, block in enumerate(blocks[1:], start=1):
        if f"Source: {source}" in block:
            block = block.replace("Status: pending", f"Status: resolved {timestamp}", 1)
            blocks[i] = block.rstrip("\n") + "\n" + followup_block
            matched = True
            break
    if matched:
        new_content = "\n## ".join(blocks)
    else:
        new_content = content + (
            f"\n## {timestamp}\n"
            f"Source: {source}\n"
            f"Status: resolved {timestamp}\n"
            + followup_block
        )
    _github_put_file(PENDING_DM_PATH, new_content, sha, "Resolve DM follow-up")
    return matched


FLAGGED_CREATORS_PATH = "notes/flagged_creators.md"


def save_flagged_creator_to_github(result: dict, source: str) -> None:
    """Track creators whose videos carry dubious claims or heavy hype (repeat offenders accumulate)."""
    creator = (result.get("creator") or "").strip()
    if not GITHUB_TOKEN or not creator:
        return
    dubious = [c for c in result.get("claims_check") or []
               if isinstance(c, dict) and c.get("verdict") == "dubious"]
    if not dubious and result.get("hype_level") != "heavy":
        return
    content, sha = _github_get_file(FLAGGED_CREATORS_PATH)
    if not content:
        content = (
            "# Flagged Creators\n\n"
            "Creators whose videos contained dubious claims or heavy engagement-bait. "
            "More bullets under a name = repeat offender.\n"
        )
    if source in content:
        return  # this video already logged
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    reasons = "; ".join(c.get("claim", "?") for c in dubious) or "heavy hype/engagement-bait"
    bullet = f"- {date} — {reasons} — {source}\n"
    header = f"\n## {creator}\n"
    if header in content:
        head, _, tail = content.partition(header)
        content = head + header + bullet + tail
    else:
        content += header + bullet
    _github_put_file(FLAGGED_CREATORS_PATH, content, sha, f"Flag creator: {creator}")


def extract_frames(video_path: str, num_frames: int = 5) -> list[str]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        raise ValueError("Video has no frames")

    indices = [int(i * (total_frames - 1) / (num_frames - 1)) for i in range(num_frames)]
    frames_b64 = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frames_b64.append(base64.standard_b64encode(buffer).decode("utf-8"))

    cap.release()
    return frames_b64


def transcribe_audio(video_path: str) -> str:
    # Best-effort: some videos have missing/odd audio streams that crash
    # faster-whisper (IndexError) — analyze frames-only instead of failing.
    try:
        segments, _ = whisper_model.transcribe(video_path, beam_size=1, vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments).strip()
    except Exception:
        return ""


def download_video(url: str) -> tuple[str, str]:
    """Returns (local file path, creator/uploader name — may be "")."""
    out_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.mp4")
    ydl_opts = {
        "format": "mp4/best",
        "outtmpl": out_path,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        # Instagram blocks anonymous requests without TLS fingerprint impersonation (needs curl_cffi)
        "impersonate": ImpersonateTarget.from_str("chrome"),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    if not os.path.exists(out_path):
        raise ValueError("Download did not produce a video file")
    creator = (info.get("uploader") or info.get("channel") or info.get("uploader_id") or "") if info else ""
    return out_path, creator


def analyze_frames_with_claude(frames_b64: list[str], transcript: str = "") -> dict:
    content = []
    for i, frame_b64 in enumerate(frames_b64):
        content.append({
            "type": "text",
            "text": f"Frame {i + 1} of {len(frames_b64)}:"
        })
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": frame_b64,
            },
        })

    transcript_text = transcript if transcript else "(no speech detected)"
    content.append({
        "type": "text",
        "text": f"Transcript of the video's audio:\n{transcript_text}"
    })

    content.append({
        "type": "text",
        "text": (
            "Analyze these video frames and the audio transcript above, and return a JSON object with exactly these fields:\n"
            "- summary: a 2-3 sentence description of the video content\n"
            "- overview: a detailed multi-sentence overview of what happens/is covered, as if taking notes for someone who hasn't watched it\n"
            "- key_points: an array of 3-6 short strings, the main takeaways or notable moments\n"
            "- content_type: one of [tutorial, entertainment, news, advertisement, vlog, sports, music, documentary, other]\n"
            "- energy: one of [low, medium, high]\n"
            "- pacing: one of [slow, moderate, fast]\n"
            "- hook_strength: one of [weak, moderate, strong] (how engaging the opening is)\n"
            "- note_category: one of [fitness, productivity, investing, ai_coding, project_ideas, to_do, ideas]. Pick based on content:\n"
            "  - fitness: workouts, training, nutrition, sleep/recovery, exercise form\n"
            "  - productivity: calendar/scheduling, trip planning, email, general productivity or life-admin content\n"
            "  - investing: investing, markets, personal finance, portfolio/money topics\n"
            "  - ai_coding: AI, coding, prompts, agents, dev tools, or software tutorials\n"
            "  - project_ideas: the video sparks a concrete idea, upgrade, or feature for Lucas's own 'Life Hacker 3000' project (only use this if the content clearly maps to something he could build/add to his own suite of tools)\n"
            "  - to_do: the video implies a concrete action item or task Lucas should do\n"
            "  - ideas: general or miscellaneous ideas that don't fit any category above\n"
            "  Use ideas as the fallback if nothing else fits well.\n"
            "- dm_cta: null, UNLESS the video asks viewers to comment a keyword or send a DM to receive "
            "something (e.g. \"comment LINK and I'll DM you the guide\", \"DM me 'START'\", \"comment below for the template\"). "
            "In that case return an object: {\"keyword\": \"<the exact word/phrase to comment or DM>\", "
            "\"offer\": \"<what is promised in return: guide, link, discount, template, etc.>\"}. "
            "Check both the transcript and any text visible in the frames.\n"
            "- claims_check: array (max 3, [] if none) of the video's concrete factual claims — earnings figures, "
            "tool capabilities, statistics, guarantees — each as {\"claim\": \"<short restatement>\", "
            "\"verdict\": one of [\"plausible\", \"unverifiable\", \"dubious\"], \"why\": \"<one short sentence>\"}. "
            "Mark dubious anything that contradicts how these tools/markets actually work, names tools that don't "
            "seem to exist, or shows likely-fabricated earnings screenshots.\n"
            "- hype_level: one of [none, mild, heavy]. heavy = engagement-bait patterns: fabricated-looking income "
            "screenshots, \"this one trick\" framing, unverifiable get-rich claims, fake urgency.\n\n"
            "Respond with ONLY valid JSON, no markdown, no explanation."
        )
    })

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": content}],
    )

    raw = message.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
        raise ValueError(f"Claude did not return valid JSON: {raw}")


def analyze_followup_image(image_b64: str, media_type: str, keyword: str = "", offer: str = "") -> str:
    """Extract the useful payload from a DM screenshot (links, tool names, steps)."""
    context = ""
    if keyword or offer:
        context = (
            f"Context: Lucas commented '{keyword}' on a video that promised: {offer}. "
            "This screenshot is the DM he received in return.\n"
        )
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}},
                {"type": "text", "text": (
                    f"{context}"
                    "This is a screenshot of a DM received after commenting on a social-media video. "
                    "Extract the actual payload as concise markdown: every link/URL verbatim, tool or product "
                    "names, prices, steps or instructions, and a one-line verdict on whether it looks like a "
                    "genuinely useful resource or spam/upsell bait. No preamble."
                )},
            ],
        }],
    )
    return message.content[0].text.strip()


def parse_note_file(category: str, content: str) -> list[dict]:
    notes = []
    # Entries are appended as "## <timestamp>" blocks by save_note_to_github
    for block in content.split("\n## ")[1:]:
        lines = block.strip().split("\n")
        timestamp = lines[0].strip()
        source = ""
        creator = ""
        paragraphs = []
        key_points = []
        transcript_lines = []
        in_transcript = False
        for line in lines[1:]:
            line = line.strip()
            if line.startswith("<details>"):
                in_transcript = True
            elif line.startswith("</details>"):
                in_transcript = False
            elif in_transcript:
                if line:
                    transcript_lines.append(line)
            elif line.startswith("Source: "):
                source = line[len("Source: "):]
            elif line.startswith("Creator: "):
                creator = line[len("Creator: "):]
            elif line.startswith("- "):
                key_points.append(line[2:])
            elif line:
                paragraphs.append(line)
        notes.append({
            "category": category,
            "timestamp": timestamp,
            "source": source,
            "creator": creator,
            "summary": paragraphs[0] if paragraphs else "",
            "overview": paragraphs[1] if len(paragraphs) > 1 else "",
            "key_points": key_points,
            "transcript": " ".join(transcript_lines),
        })
    return notes


@app.get("/api/notes")
async def get_all_notes():
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=500, detail="GITHUB_TOKEN not configured")
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    list_resp = requests.get(
        f"https://api.github.com/repos/{GITHUB_REPO}/contents/notes",
        headers=headers, timeout=15,
    )
    list_resp.raise_for_status()
    all_notes = []
    for item in list_resp.json():
        if not item["name"].endswith(".md"):
            continue
        category = item["name"][:-3]
        file_resp = requests.get(item["download_url"], headers=headers, timeout=15)
        if file_resp.status_code == 200:
            all_notes.extend(parse_note_file(category, file_resp.text))
    all_notes.sort(key=lambda n: n["timestamp"], reverse=True)
    return JSONResponse(content={"notes": all_notes})


@app.get("/notes", response_class=HTMLResponse)
async def notes_page():
    with open("notes.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/invest", response_class=HTMLResponse)
async def invest_page():
    with open("invest.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/analyze")
async def analyze_video(video: UploadFile = File(...)):
    allowed_types = {"video/mp4", "video/avi", "video/mov", "video/quicktime", "video/x-msvideo", "video/webm"}
    if video.content_type and video.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {video.content_type}")

    suffix = os.path.splitext(video.filename or "video.mp4")[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=TEMP_DIR) as tmp:
        tmp.write(await video.read())
        tmp_path = tmp.name

    try:
        frames = extract_frames(tmp_path, num_frames=5)
        if not frames:
            raise HTTPException(status_code=422, detail="Could not extract frames from video")
        transcript = transcribe_audio(tmp_path)
        result = analyze_frames_with_claude(frames, transcript)
        result["transcript"] = transcript
        try:
            result["note_saved"] = save_note_to_github(result, source=video.filename or "uploaded file")
            save_dm_followup_to_github(result, source=video.filename or "uploaded file")
            save_flagged_creator_to_github(result, source=video.filename or "uploaded file")
        except requests.RequestException:
            result["note_saved"] = False
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        os.unlink(tmp_path)


@app.post("/analyze-url")
async def analyze_video_url(url: str = Form(...)):
    tmp_path = None
    try:
        tmp_path, creator = download_video(url)
        frames = extract_frames(tmp_path, num_frames=5)
        if not frames:
            raise HTTPException(status_code=422, detail="Could not extract frames from video")
        transcript = transcribe_audio(tmp_path)
        result = analyze_frames_with_claude(frames, transcript)
        result["transcript"] = transcript
        result["creator"] = creator
        try:
            save_note_to_github(result, source=url)
            result["note_saved"] = True
            save_dm_followup_to_github(result, source=url)
            save_flagged_creator_to_github(result, source=url)
        except requests.RequestException:
            result["note_saved"] = False
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=422, detail=f"Could not download video: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/followup")
async def dm_followup(
    screenshot: UploadFile = File(...),
    source: str = Form(...),
    keyword: str = Form(""),
    offer: str = Form(""),
):
    """Attach a DM screenshot's payload to the pending follow-up entry for `source`."""
    allowed_types = {"image/png", "image/jpeg", "image/webp", "image/gif"}
    media_type = screenshot.content_type or "image/png"
    if media_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {media_type}")
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=500, detail="GITHUB_TOKEN not configured")

    image_b64 = base64.standard_b64encode(await screenshot.read()).decode("utf-8")
    followup_text = analyze_followup_image(image_b64, media_type, keyword, offer)
    try:
        matched = resolve_dm_followup_on_github(source, followup_text)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Could not update GitHub notes: {e}")
    return JSONResponse(content={
        "resolved_existing_entry": matched,
        "followup": followup_text,
    })
