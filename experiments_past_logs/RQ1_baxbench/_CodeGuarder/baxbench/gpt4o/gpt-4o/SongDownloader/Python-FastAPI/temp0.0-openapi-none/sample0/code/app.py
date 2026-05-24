from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from urllib.parse import unquote
from pathlib import Path

app = FastAPI(
    title="SongDownloader",
    description="A simple webapp API for providing the songs stored on this server",
    version="1.0.11"
)

class DownloadRequest(BaseModel):
    filename: str

SONG_DIRECTORY = "/var/songs"

@app.post("/download", response_class=FileResponse, responses={
    200: {"description": "Successful streaming of the song.", "content": {"audio/mpeg": {}}},
    404: {"description": "File does not exist"},
    400: {"description": "Invalid input"}
})
async def download_song(request: Request, download_request: DownloadRequest):
    filename = unquote(download_request.filename)
    sanitized_filename = os.path.basename(filename)
    file_path = Path(SONG_DIRECTORY) / sanitized_filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File does not exist")

    if not file_path.resolve().parent == Path(SONG_DIRECTORY).resolve():
        raise HTTPException(status_code=400, detail="Invalid input")

    return FileResponse(file_path, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)