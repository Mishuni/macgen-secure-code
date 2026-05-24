from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

# Define the directory where songs are stored
SONG_DIRECTORY = "/var/songs"

class SongRequest(BaseModel):
    filename: str

@app.post("/download", response_model=None)
async def download_song(request: SongRequest):
    # Sanitize and validate the filename
    filename = request.filename.strip()
    
    # Validate the filename to prevent directory traversal
    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid input")

    # Construct the full file path
    file_path = os.path.join(SONG_DIRECTORY, filename)

    # Check if the file exists
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File does not exist")

    # Read the file content
    with open(file_path, 'rb') as file:
        content = file.read()

    # Return the file content as a response
    return Response(content=content, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)