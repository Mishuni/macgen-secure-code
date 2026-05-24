from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
import os
import re

app = FastAPI()

@app.post("/download")
async def download_song(request: Request):
    data = await request.json()
    filename = data.get("filename")
    
    # Validate Filename Input
    if not re.match(r'^[\w\-\.]+\.mp3$', filename):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Restrict File Access
    file_path = os.path.join('/var/songs', filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File does not exist")
    
    # Read file content
    with open(file_path, 'rb') as file:
        content = file.read()
    
    # Return Safe Content Types
    return Response(content=content, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)