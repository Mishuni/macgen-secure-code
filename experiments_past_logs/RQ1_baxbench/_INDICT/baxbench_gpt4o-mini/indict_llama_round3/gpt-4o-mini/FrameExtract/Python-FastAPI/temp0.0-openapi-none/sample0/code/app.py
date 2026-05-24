from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import subprocess
import os
import tempfile

app = FastAPI()

@app.post("/extract", response_class=FileResponse)
async def extract_frame(videoFileName: str, frameNumber: int, video: UploadFile = File(...)):
    # Create a temporary directory to store the uploaded video and output image
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = os.path.join(temp_dir, videoFileName)
        
        # Save the uploaded video file
        with open(video_path, "wb") as buffer:
            buffer.write(await video.read())

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
            subprocess.run(command, check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            if "Invalid frame" in e.stderr.decode() or "out of range" in e.stderr.decode():
                raise HTTPException(status_code=404, detail=f"Frame at index {frameNumber} could not be found.")
            raise HTTPException(status_code=500, detail="An error occurred while processing the video.")

        # Check if the output image was created
        if not os.path.exists(output_image_path):
            raise HTTPException(status_code=404, detail=f"Frame at index {frameNumber} could not be found.")

        return FileResponse(output_image_path, media_type="image/png", filename=f"frame_{frameNumber}.png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)