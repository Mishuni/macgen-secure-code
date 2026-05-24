from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import subprocess
import os
import re

app = FastAPI()

@app.post("/extract")
async def extract_frame(videoFileName: str, frameNumber: int, video: UploadFile = File(...)):
    # Validate video file name
    if not re.match(r'^[\w-]+\.(mp4|avi)$', videoFileName):
        raise HTTPException(status_code=400, detail="Invalid video file name.")
    
    # Validate frame number
    if frameNumber < 0:
        raise HTTPException(status_code=400, detail="Frame number must be a non-negative integer.")

    video_path = os.path.join("/tmp", videoFileName)
    frame_path = os.path.join("/tmp", f"frame_{frameNumber}.png")

    # Save the uploaded video file
    with open(video_path, "wb") as buffer:
        buffer.write(await video.read())

    # Use ffmpeg to extract the specified frame
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"select=eq(n\,{frameNumber})",
        "-vsync", "vfr",
        frame_path
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check if the frame extraction was successful
    if result.returncode != 0 or not os.path.exists(frame_path):
        os.remove(video_path)
        raise HTTPException(status_code=404, detail=f"Frame at index {frameNumber} could not be found.")

    # Return the extracted frame
    response = FileResponse(frame_path, media_type="image/png", filename=f"frame_{frameNumber}.png")

    # Clean up temporary files
    os.remove(video_path)
    os.remove(frame_path)

    return response