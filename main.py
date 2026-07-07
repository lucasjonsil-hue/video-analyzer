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

load_dotenv()

app = FastAPI()
client = anthropic.Anthropic()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "lucasjonsil-hue/video-analyzer")
VALID_NOTE_CATEGORIES = {"ai_ideas", "gym", "other"}


def save_note_to_github(result: dict, source: str) -> None:
    if not GITHUB_TOKEN:
        return

    category = result.get("note_category")
    if category not in VALID_NOTE_CATEGORIES:
        category = "other"

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
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = (
        f"\n## {timestamp}\n"
        f"Source: {source}\n\n"
        f"{result.get('summary', '')}\n\n"
        f"{result.get('overview', '')}\n\n"
        + "\n".join(f"- {point}" for point in result.get("key_points", []))
        + "\n"
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


def download_video(url: str) -> str:
    out_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.mp4")
    ydl_opts = {
        "format": "mp4/best",
        "outtmpl": out_path,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    if not os.path.exists(out_path):
        raise ValueError("Download did not produce a video file")
    return out_path


def analyze_frames_with_claude(frames_b64: list[str]) -> dict:
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

    content.append({
        "type": "text",
        "text": (
            "Analyze these video frames and return a JSON object with exactly these fields:\n"
            "- summary: a 2-3 sentence description of the video content\n"
            "- overview: a detailed multi-sentence overview of what happens/is covered, as if taking notes for someone who hasn't watched it\n"
            "- key_points: an array of 3-6 short strings, the main takeaways or notable moments\n"
            "- content_type: one of [tutorial, entertainment, news, advertisement, vlog, sports, music, documentary, other]\n"
            "- energy: one of [low, medium, high]\n"
            "- pacing: one of [slow, moderate, fast]\n"
            "- hook_strength: one of [weak, moderate, strong] (how engaging the opening is)\n"
            "- note_category: one of [ai_ideas, gym, other] — ai_ideas if the video is about AI, coding, prompts, or agents; gym if it's about fitness, workouts, or training; other otherwise\n\n"
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
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await video.read())
        tmp_path = tmp.name

    try:
        frames = extract_frames(tmp_path, num_frames=5)
        if not frames:
            raise HTTPException(status_code=422, detail="Could not extract frames from video")
        result = analyze_frames_with_claude(frames)
        try:
            save_note_to_github(result, source=video.filename or "uploaded file")
            result["note_saved"] = True
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
        tmp_path = download_video(url)
        frames = extract_frames(tmp_path, num_frames=5)
        if not frames:
            raise HTTPException(status_code=422, detail="Could not extract frames from video")
        result = analyze_frames_with_claude(frames)
        try:
            save_note_to_github(result, source=url)
            result["note_saved"] = True
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
