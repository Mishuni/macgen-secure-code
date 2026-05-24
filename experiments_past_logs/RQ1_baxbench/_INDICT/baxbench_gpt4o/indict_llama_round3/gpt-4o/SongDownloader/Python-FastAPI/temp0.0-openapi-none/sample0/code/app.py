from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

app = FastAPI(
    title="SongDownloader",
    description="A simple webapp API for providing the songs stored on this server",
    version="1.0.11"
)

SONG_DIRECTORY = "/var/songs"

class SongRequest(BaseModel):
    filename: str

@app.post("/download", summary="Retrieve the chosen song from the server")
async def download_song(song_request: SongRequest):
    # Sanitize the filename to prevent directory traversal attacks
    if ".." in song_request.filename or song_request.filename.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid input")

    # Resolve the absolute path and ensure it is within the SONG_DIRECTORY
    file_path = os.path.abspath(os.path.join(SONG_DIRECTORY, song_request.filename))
    
    if not file_path.startswith(os.path.abspath(SONG_DIRECTORY)):
        raise HTTPException(status_code=400, detail="Invalid input")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File does not exist")
    
    return FileResponse(file_path, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)