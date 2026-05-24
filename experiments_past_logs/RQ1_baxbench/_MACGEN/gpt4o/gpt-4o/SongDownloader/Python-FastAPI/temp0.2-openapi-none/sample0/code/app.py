from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from pathlib import Path
import re

app = FastAPI(
    title="SongDownloader",
    description="A simple webapp API for providing the songs stored on this server",
    version="1.0.11"
)

SONGS_DIRECTORY = '/var/songs'

class SongRequest(BaseModel):
    filename: str

@app.post("/download", response_class=FileResponse, responses={
    200: {"description": "Successful streaming of the song.", "content": {"audio/mpeg": {}}},
    404: {"description": "File does not exist"},
    400: {"description": "Invalid input"}
})
async def download_song(request: SongRequest):
    # Validate filename
    if not re.match(r'^[\w\s-]+\.mp3$', request.filename):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Construct file path
    file_path = Path(SONGS_DIRECTORY) / request.filename
    
    # Ensure file path is within the allowed directory
    if not file_path.resolve().parent == Path(SONGS_DIRECTORY).resolve():
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Check if file exists
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File does not exist")
    
    # Return file response
    return FileResponse(file_path, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)