import base64
import json
import cv2
import numpy as np
import tempfile
import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import anthropic
import yt_dlp

load_dotenv()

app = FastAPI()
client = anthropic.Anthropic()


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
            "- hook_strength: one of [weak, moderate, strong] (how engaging the opening is)\n\n"
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
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=422, detail=f"Could not download video: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
