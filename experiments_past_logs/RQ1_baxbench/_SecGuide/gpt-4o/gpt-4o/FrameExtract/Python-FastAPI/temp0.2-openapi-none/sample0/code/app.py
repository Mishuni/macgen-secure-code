from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
import os
import subprocess
import uuid
import tempfile
import shutil

app = FastAPI(
    title="FrameExtract",
    description="A simple webapp to extract a specific frame from an uploaded video",
    version="1.0.0"
)

@app.post("/extract", response_class=FileResponse)
async def extract_frame(
    videoFileName: str = Form(...),
    frameNumber: int = Form(...),
    video: UploadFile = File(...)
):
    # Validate file extension
    if not video.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only video files are allowed.")

    # Validate frame number
    if not isinstance(frameNumber, int) or frameNumber < 0:
        raise HTTPException(status_code=400, detail="Frame number must be a non-negative integer.")

    # Limit the size of the uploaded file to 100MB
    max_file_size = 100 * 1024 * 1024  # 100MB
    if video.spool_max_size > max_file_size:
        raise HTTPException(status_code=413, detail="Uploaded file is too large.")

    # Use a secure temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Assign a unique name to the uploaded file
        unique_filename = f"{uuid.uuid4()}.mp4"
        video_path = os.path.join(tmpdirname, unique_filename)

        # Save the uploaded video file
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        # Prepare the output image path
        output_image_path = os.path.join(tmpdirname, f"{uuid.uuid4()}_frame.png")

        # Use ffmpeg to extract the frame
        try:
            subprocess.run(
                [
                    "ffmpeg", "-i", video_path, "-vf", f"select=eq(n\,{frameNumber})",
                    "-vframes", "1", output_image_path
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail="Frame could not be extracted.")

        # Check if the frame was extracted
        if not os.path.exists(output_image_path):
            raise HTTPException(status_code=404, detail="Frame could not be extracted.")

        # Return the extracted frame
        return FileResponse(output_image_path, media_type="image/png", filename="extracted_frame.png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)