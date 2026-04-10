from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import time

from src.stream_inference import run_stream

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Backend is running"}


@app.post("/upload")
async def upload_video(video: UploadFile, context: str = Form(...)):

    os.makedirs("temp", exist_ok=True)

    video_path = f"temp/{video.filename}"

    with open(video_path, "wb") as f:
        f.write(await video.read())

    def event_stream():

        for result in run_stream(video_path, context):

            yield f"data:{json.dumps(result)}\n\n"
            time.sleep(0.01)

    return StreamingResponse(event_stream(), media_type="text/event-stream")