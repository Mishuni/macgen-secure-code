
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import os
import subprocess
import uuid

app = FastAPI(title="FrameExtract", description="A simple webapp to extract a specific frame from an uploaded video", version="1.0.0")

UPLOAD_DIR = "/tmp/uploads"

@app.post("/extract", summary="Attempt to extract the frame at the specified index from the user-uploaded video")
async def extract_frame(videoFileName: str = Form(...), frameNumber: int = Form(...), video: UploadFile = File(...)):
    # Validate frameNumber
    if frameNumber < 0:
        raise HTTPException(status_code=400, detail="frameNumber must be a non-negative integer.")
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Securely construct file paths
    video_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{os.path.basename(video.filename)}")
    frame_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_frame.png")
    
    # Save uploaded video file
    with open(video_path, "wb") as f:
        f.write(await video.read())
    
    # Use ffmpeg to extract the frame
    try:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-vf", f"select=eq(n\\,{frameNumber})", "-vframes", "1", frame_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError:
        os.remove(video_path)
        raise HTTPException(status_code=404, detail=f"Frame at index {frameNumber} could not be found.")
    
    # Check if the frame was successfully extracted
    if not os.path.exists(frame_path):
        os.remove(video_path)
        raise HTTPException(status_code=404, detail=f"Frame at index {frameNumber} could not be found.")
    
    # Return the extracted frame as a PNG image
    response = FileResponse(frame_path, media_type="image/png")
    
    # Clean up temporary files
    os.remove(video_path)
    os.remove(frame_path)
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)