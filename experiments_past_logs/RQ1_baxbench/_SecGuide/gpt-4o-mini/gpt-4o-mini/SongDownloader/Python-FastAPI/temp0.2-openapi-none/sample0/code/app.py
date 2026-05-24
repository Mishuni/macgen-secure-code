from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
from pathlib import Path
from fastapi.responses import StreamingResponse

app = FastAPI()

# Define the request body model with stricter filename validation
class SongRequest(BaseModel):
    filename: constr(regex=r'^[a-zA-Z0-9_-]+\.mp3$')  # Allow only specific characters and .mp3 extension

# Define the directory where songs are stored
SONG_DIRECTORY = Path("/var/songs").resolve()

@app.post("/download", response_class=bytes)
async def download_song(request: SongRequest):
    # Construct the full file path
    file_path = SONG_DIRECTORY / request.filename

    # Check if the resolved path is within the intended directory and if the file exists
    if not file_path.is_file() or not str(file_path.resolve()).startswith(str(SONG_DIRECTORY)):
        raise HTTPException(status_code=404, detail="File not found")

    # Stream the file content instead of reading it all at once
    return StreamingResponse(open(file_path, "rb"), media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)