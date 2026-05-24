from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from pathlib import Path
import os

# Initialize FastAPI app
app = FastAPI(
    title="SongDownloader",
    description="A simple webapp API for providing the songs stored on this server",
    version="1.0.11"
)

# Define the directory where songs are stored
SONG_DIRECTORY = Path("/var/songs")

# Ensure the directory exists and is secure
if not SONG_DIRECTORY.exists() or not SONG_DIRECTORY.is_dir():
    raise RuntimeError(f"Song directory {SONG_DIRECTORY} does not exist or is not a directory.")

# Pydantic model for request body validation
class SongRequest(BaseModel):
    filename: str = Field(..., example="peters_mixtape.mp3")

    def validate_filename(self) -> Path:
        """
        Validates the filename to ensure it is safe and resolves to a file within the SONG_DIRECTORY.
        """
        # Prevent directory traversal attacks by resolving the path
        sanitized_path = SONG_DIRECTORY / os.path.basename(self.filename)
        if not sanitized_path.exists() or not sanitized_path.is_file():
            raise HTTPException(status_code=404, detail="File does not exist")
        if not sanitized_path.is_relative_to(SONG_DIRECTORY):
            raise HTTPException(status_code=400, detail="Invalid file path")
        return sanitized_path

@app.post("/download", responses={
    200: {"description": "Successful streaming of the song.", "content": {"audio/mpeg": {}}},
    404: {"description": "File does not exist"},
    400: {"description": "Invalid input"}
})
async def download_song(request: SongRequest):
    """
    Endpoint to retrieve the chosen song from the server.
    """
    try:
        # Validate and sanitize the filename
        song_path = request.validate_filename()
        # Return the file as a response
        return FileResponse(song_path, media_type="audio/mpeg", headers={"Access-Control-Allow-Origin": "*"})
    except HTTPException as e:
        # Raise HTTP exceptions for invalid input or missing files
        raise e
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Run the application using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)