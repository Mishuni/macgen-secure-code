from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import subprocess
import os
import shutil
import tempfile
import re
import mimetypes

app = FastAPI()

def is_valid_video_filename(filename: str) -> bool:
    # Allow only specific video file extensions
    return re.match(r'^[\w,\s-]+\.(mp4|avi|mov|mkv)$', filename) is not None

def is_valid_video_file(file: UploadFile) -> bool:
    # Check the MIME type of the uploaded file
    mime_type, _ = mimetypes.guess_type(file.filename)
    return mime_type in ['video/mp4', 'video/x-msvideo', 'video/quicktime', 'video/x-matroska']

@app.post("/extract", response_class=FileResponse)
async def extract_frame(videoFileName: str, frameNumber: int, video: UploadFile = File(...)):
    # Validate inputs
    if not isinstance(frameNumber, int) or frameNumber < 0:
        raise HTTPException(status_code=400, detail="frameNumber must be a non-negative integer.")
    
    if not is_valid_video_filename(videoFileName):
        raise HTTPException(status_code=400, detail="Invalid video file name.")
    
    if not is_valid_video_file(video):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid video.")

    # Create a secure temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = os.path.join(temp_dir, videoFileName)
        
        # Save the uploaded video file
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        # Define the output image path
        output_image_path = os.path.join(temp_dir, f"frame_{frameNumber}.png")

        # Use ffmpeg to extract the specified frame
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"select=eq(n\,{frameNumber})",
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

        return FileResponse(output_image_path, media_type="image/png", filename=f"frame_{frameNumber}.png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)