from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import subprocess
import tempfile

app = FastAPI()

OUTPUT_DIR = "/tmp/"  # Use a temporary directory for output

def secure_filename(filename: str) -> str:
    # Sanitize the filename to prevent directory traversal
    return os.path.basename(filename)

@app.post("/extract")
async def extract_frame(videoFileName: str, frameNumber: int, video: UploadFile = File(...)):
    # Validate inputs
    if frameNumber < 0:
        raise HTTPException(status_code=400, detail="Frame number must be a non-negative integer.")
    
    # Secure the filename
    safe_video_filename = secure_filename(videoFileName)
    
    # Save the uploaded video file
    video_path = os.path.join(OUTPUT_DIR, safe_video_filename)
    with open(video_path, "wb") as buffer:
        buffer.write(await video.read())
    
    # Prepare the output image path
    output_image_path = os.path.join(OUTPUT_DIR, f"frame_{frameNumber}.png")
    
    # Use ffmpeg to extract the frame
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"select=eq(n\\,{frameNumber})",
        "-vframes", "1",
        output_image_path
    ]
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=404, detail=f"Frame at index {frameNumber} could not be found.")
    
    # Check if the output image was created
    if not os.path.exists(output_image_path):
        raise HTTPException(status_code=404, detail=f"Frame at index {frameNumber} could not be found.")
    
    return FileResponse(output_image_path, media_type="image/png")