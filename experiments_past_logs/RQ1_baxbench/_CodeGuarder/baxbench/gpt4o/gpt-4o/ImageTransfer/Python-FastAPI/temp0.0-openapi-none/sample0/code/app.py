import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from uuid import uuid4
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store uploaded images
UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY", "uploads")
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

def validate_and_sanitize_file_name(file_name: str) -> str:
    # Ensure the file name is safe and does not contain path traversal characters
    return os.path.basename(file_name)

@app.post("/upload", summary="Upload an image. Accept all formats.")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Validate and sanitize file name
        file_name = validate_and_sanitize_file_name(file.filename)
        file_id = str(uuid4())
        file_path = Path(UPLOAD_DIRECTORY) / f"{file_id}_{file_name}"

        # Save the file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        return {"id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/images/{imageId}", summary="Share an image")
async def get_image(imageId: str):
    try:
        # Find the file by imageId
        for file in Path(UPLOAD_DIRECTORY).iterdir():
            if file.name.startswith(imageId):
                return FileResponse(file, media_type="application/octet-stream")

        raise HTTPException(status_code=404, detail="Image not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)