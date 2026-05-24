import os
import shutil
import subprocess
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from tempfile import NamedTemporaryFile

app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FrameExtractRequest(BaseModel):
    videoFileName: str
    frameNumber: int

@app.post("/extract")
async def extract_frame(
    videoFileName: str = Form(...),
    frameNumber: int = Form(...),
    video: UploadFile = File(...)
):
    # Validate frameNumber
    if frameNumber < 0:
        raise HTTPException(status_code=400, detail="Frame number must be non-negative.")

    # Save the uploaded video file securely
    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        shutil.copyfileobj(video.file, temp_video_file)
        temp_video_file_path = temp_video_file.name

    # Prepare the output image path
    with NamedTemporaryFile(delete=False, suffix=".png") as temp_image_file:
        temp_image_file_path = temp_image_file.name

    # Use ffmpeg to extract the frame
    try:
        command = [
            "ffmpeg",
            "-i", temp_video_file_path,
            "-vf", f"select=eq(n\\,{frameNumber})",
            "-vframes", "1",
            temp_image_file_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        os.remove(temp_video_file_path)
        os.remove(temp_image_file_path)
        raise HTTPException(status_code=404, detail=f"Frame at index {frameNumber} could not be found.")

    # Return the extracted frame
    return FileResponse(temp_image_file_path, media_type="image/png", filename=f"frame_{frameNumber}.png")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)