from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os

app = FastAPI()

class SongRequest(BaseModel):
    filename: str

@app.post("/download")
async def download_song(request: SongRequest):
    # Validate the filename to prevent path traversal
    if not request.filename.isalnum() and not request.filename.endswith('.mp3'):
        raise HTTPException(status_code=400, detail="Invalid input")

    # Define the directory where songs are stored
    songs_directory = "/var/songs"
    file_path = os.path.join(songs_directory, request.filename)

    # Check if the file exists
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File does not exist")

    # Return the file as a response
    return FileResponse(file_path, media_type='audio/mpeg')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)