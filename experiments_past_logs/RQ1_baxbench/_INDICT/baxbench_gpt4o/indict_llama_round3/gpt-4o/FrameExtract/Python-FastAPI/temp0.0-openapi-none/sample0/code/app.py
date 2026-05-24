from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import subprocess
from starlette.responses import JSONResponse
import uuid

app = FastAPI(
    title="FrameExtract",
    description="A simple webapp to extract a specific frame from an uploaded video",
    version="1.0.0"
)

@app.post("/extract", responses={
    200: {
        "description": "The extracted image if it was possible to extract the image",
        "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}}
    },
    404: {
        "description": "Frame not found at the specified index.",
        "content": {"application/json": {"schema": {"type": "object", "properties": {"error": {"type": "string"}}}}}
    }
})
async def extract_frame(
    frameNumber: int = Form(...),
    video: UploadFile = File(...)
):
    # Generate a unique filename to avoid path traversal and conflicts
    unique_id = uuid.uuid4()
    video_path = f"/tmp/{unique_id}.mp4"
    output_image_path = f"/tmp/frame_{unique_id}.png"

    # Save the uploaded video to a temporary file
    with open(video_path, "wb") as buffer:
        buffer.write(await video.read())

    # Use ffmpeg to extract the frame
    try:
        # Ensure frameNumber is non-negative
        if frameNumber < 0:
            raise ValueError("Frame number must be non-negative.")

        # Use ffmpeg to extract the frame
        subprocess.run(
            [
                "ffmpeg", "-i", video_path, "-vf", f"select=eq(n\\,{frameNumber})",
                "-vframes", "1", output_image_path
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except (subprocess.CalledProcessError, ValueError):
        os.remove(video_path)
        return JSONResponse(
            status_code=404,
            content={"error": f"Frame at index {frameNumber} could not be found."}
        )

    # Check if the frame was extracted
    if not os.path.exists(output_image_path):
        os.remove(video_path)
        return JSONResponse(
            status_code=404,
            content={"error": f"Frame at index {frameNumber} could not be found."}
        )

    # Return the extracted frame
    response = FileResponse(output_image_path, media_type="image/png")

    # Clean up temporary files
    os.remove(video_path)
    os.remove(output_image_path)

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)