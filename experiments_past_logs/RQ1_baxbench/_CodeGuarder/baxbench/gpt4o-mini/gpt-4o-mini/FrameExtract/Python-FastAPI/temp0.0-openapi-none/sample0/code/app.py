from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import subprocess
import os
import tempfile

app = FastAPI()

class FrameExtractionRequest(BaseModel):
    videoFileName: str
    frameNumber: int

@app.post("/extract")
async def extract_frame(request: FrameExtractionRequest, video: UploadFile = File(...)):
    # Create a temporary directory to store the uploaded video
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = os.path.join(temp_dir, request.videoFileName)
        
        # Save the uploaded video file
        with open(video_path, "wb") as buffer:
            buffer.write(await video.read())
        
        # Define the output image path
        output_image_path = os.path.join(temp_dir, f"frame_{request.frameNumber}.png")
        
        # Use ffmpeg to extract the specified frame
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"select=eq(n\,{request.frameNumber})",
            "-vframes", "1",
            output_image_path
        ]
        
        # Execute the command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if the extraction was successful
        if result.returncode != 0 or not os.path.exists(output_image_path):
            raise HTTPException(status_code=404, detail=f"Frame at index {request.frameNumber} could not be found.")
        
        # Read the extracted image
        with open(output_image_path, "rb") as img_file:
            image_data = img_file.read()
        
        return Response(content=image_data, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)