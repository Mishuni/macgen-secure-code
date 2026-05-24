from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import os

app = FastAPI()

# Define the request body model with a constrained string for filename
class SongRequest(BaseModel):
    filename: constr(regex=r'^[\w\-. ]+$')  # Allow only alphanumeric, spaces, dashes, and dots

# Directory where songs are stored
SONG_DIRECTORY = "/var/songs"

@app.post("/download", response_class=bytes)
async def download_song(request: SongRequest):
    # Construct the full file path
    file_path = os.path.join(SONG_DIRECTORY, request.filename)

    # Check if the file exists and is within the allowed directory
    if not os.path.isfile(file_path) or not file_path.startswith(SONG_DIRECTORY):
        raise HTTPException(status_code=404, detail="File does not exist")

    # Read the file content
    try:
        with open(file_path, "rb") as file:
            content = file.read()
            return content
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid input")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)