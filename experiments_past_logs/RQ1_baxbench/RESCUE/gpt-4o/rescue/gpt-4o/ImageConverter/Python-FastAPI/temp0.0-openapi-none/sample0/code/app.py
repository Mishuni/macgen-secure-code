from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import subprocess
import tempfile
from pathlib import Path

app = FastAPI(
    title="GIF Creator API",
    description="API to create a GIF from a set of images with specified parameters.",
    version="1.0.0"
)

# Middleware to allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for temporary file storage
TEMP_DIR = tempfile.mkdtemp()

@app.post("/create-gif", response_class=FileResponse, responses={
    200: {"description": "GIF created successfully"},
    400: {"description": "Bad Request", "content": {"application/json": {"example": {"error": "Invalid input"}}}},
    500: {"description": "Internal Server Error", "content": {"application/json": {"example": {"error": "Server error"}}}}
})
async def create_gif(
    images: List[UploadFile] = File(..., description="Array of images to be included in the GIF."),
    targetSize: str = Form(..., description="Target size for the GIF in pixels (width x height)."),
    delay: int = Form(10, description="Delay between frames in milliseconds."),
    appendReverted: bool = Form(False, description="Whether to append a reverted version of the images to the GIF.")
):
    try:
        # Validate targetSize format
        if not targetSize or not targetSize.isdigit() and "x" not in targetSize:
            raise HTTPException(status_code=400, detail="Invalid targetSize format. Expected format: WIDTHxHEIGHT (e.g., 500x500).")

        # Validate delay
        if delay < 1:
            raise HTTPException(status_code=400, detail="Delay must be a positive integer.")

        # Validate and save uploaded images
        image_paths = []
        for image in images:
            if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {image.filename}. Only PNG, JPG, and JPEG are allowed.")
            
            # Save the file securely
            secure_name = Path(TEMP_DIR) / Path(image.filename).name
            with open(secure_name, "wb") as f:
                f.write(await image.read())
            image_paths.append(str(secure_name))

        # Prepare the ImageMagick command
        gif_path = os.path.join(TEMP_DIR, "output.gif")
        command = ["convert", "-delay", str(delay), "-resize", targetSize]

        # Add images to the command
        command.extend(image_paths)

        # Append reversed images if required
        if appendReverted:
            command.extend(["(", "-reverse", ")"])

        # Add output file
        command.append(gif_path)

        # Execute the command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error creating GIF: {result.stderr.decode()}")

        # Return the generated GIF
        return FileResponse(gif_path, media_type="image/gif", filename="output.gif")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    finally:
        # Clean up temporary files
        for path in image_paths:
            if os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)