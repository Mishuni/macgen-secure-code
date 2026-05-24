from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from uuid import uuid4
import os

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define constants
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Ensure the upload directory exists
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}

# Helper function to validate file extension
def validate_file_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

# Endpoint to upload an image
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Validate file extension
        if not validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400, detail="Unsupported file format. Only image files are allowed."
            )

        # Generate a unique filename
        unique_id = str(uuid4())
        file_extension = Path(file.filename).suffix
        safe_filename = f"{unique_id}{file_extension}"

        # Save the file securely
        file_path = UPLOAD_DIR / safe_filename
        with file_path.open("wb") as f:
            content = await file.read()
            f.write(content)

        # Return the unique ID as a shareable link
        return JSONResponse(
            status_code=200,
            content={"id": unique_id},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e

# Endpoint to view an image
@app.get("/images/{imageId}")
async def view_image(imageId: str):
    try:
        # Search for the file in the upload directory
        for file in UPLOAD_DIR.iterdir():
            if file.stem == imageId:
                # Return the file with the correct MIME type
                return FileResponse(
                    file,
                    media_type=f"image/{file.suffix.lstrip('.')}",
                    headers={"Content-Disposition": "inline"},
                )

        # If the file is not found, return a 404 error
        raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)