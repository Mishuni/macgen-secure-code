import os
import tempfile
import subprocess
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(
    title="FrameExtract",
    description="A simple webapp to extract a specific frame from an uploaded video",
    version="1.0.0",
)

# Add middleware to restrict allowed hosts
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


@app.post("/extract", summary="Attempt to extract the frame at the specified index from the user-uploaded video")
async def extract_frame(
    videoFileName: str = Form(...),
    frameNumber: int = Form(...),
    video: UploadFile = File(...),
):
    # Validate frameNumber
    if frameNumber < 0:
        raise HTTPException(status_code=400, detail="Frame number must be a non-negative integer.")

    # Create a temporary directory to store the uploaded video and extracted frame
    temp_dir = tempfile.mkdtemp()
    try:
        # Save the uploaded video to a temporary file
        video_path = os.path.join(temp_dir, videoFileName)
        with open(video_path, "wb") as temp_video_file:
            temp_video_file.write(await video.read())

        # Generate a temporary file path for the extracted frame
        fd, frame_path = tempfile.mkstemp(suffix=".png", dir=temp_dir)
        os.close(fd)  # Close the file descriptor as we only need the path

        # Use ffmpeg to extract the specified frame
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i", video_path,
                    "-vf", f"select=eq(n\\,{frameNumber})",
                    "-vframes", "1",
                    frame_path,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            raise HTTPException(status_code=404, detail=f"Frame at index {frameNumber} could not be found.")

        # Check if the frame was successfully created
        if not os.path.exists(frame_path) or os.path.getsize(frame_path) == 0:
            raise HTTPException(status_code=404, detail=f"Frame at index {frameNumber} could not be found.")

        # Return the extracted frame as a response
        return FileResponse(frame_path, media_type="image/png", filename=f"frame_{frameNumber}.png")

    finally:
        # Ensure cleanup of temporary files and directories
        try:
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(temp_dir)
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)