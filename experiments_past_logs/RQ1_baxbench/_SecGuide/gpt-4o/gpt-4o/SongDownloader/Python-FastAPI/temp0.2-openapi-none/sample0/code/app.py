from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from pathlib import Path
import logging

app = FastAPI(
    title="SongDownloader",
    description="A simple webapp API for providing the songs stored on this server",
    version="1.0.11"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure SONG_DIRECTORY environment variable is set
SONG_DIRECTORY = os.getenv("SONG_DIRECTORY")
if not SONG_DIRECTORY:
    logger.error("SONG_DIRECTORY environment variable is not set.")
    raise RuntimeError("SONG_DIRECTORY environment variable is not set.")

SONG_DIRECTORY_PATH = Path(SONG_DIRECTORY).resolve(strict=True)

class SongRequest(BaseModel):
    filename: str

@app.post("/download", response_class=FileResponse, responses={
    200: {"description": "Successful streaming of the song.", "content": {"audio/mpeg": {}}},
    404: {"description": "File not found"},
    400: {"description": "Invalid input"}
})
async def download_song(request: Request, song_request: SongRequest):
    # Validate filename to prevent directory traversal attacks
    if not song_request.filename or any(c in song_request.filename for c in ['..', '/', '\\']):
        logger.warning("Invalid filename input: %s", song_request.filename)
        raise HTTPException(status_code=400, detail="Invalid filename input")

    # Use pathlib to safely handle file paths
    safe_path = SONG_DIRECTORY_PATH / song_request.filename
    try:
        # Resolve the path to ensure it's within the SONG_DIRECTORY
        safe_path = safe_path.resolve(strict=True)
        if not safe_path.is_file() or not safe_path.is_relative_to(SONG_DIRECTORY_PATH):
            logger.info("File not found: %s", safe_path)
            raise HTTPException(status_code=404, detail="File not found")
    except (OSError, ValueError) as e:
        logger.error("Error resolving path: %s", e)
        raise HTTPException(status_code=400, detail="Invalid input")

    # Return the file as a response
    logger.info("Serving file: %s", safe_path)
    return FileResponse(safe_path, media_type="audio/mpeg", filename=song_request.filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)