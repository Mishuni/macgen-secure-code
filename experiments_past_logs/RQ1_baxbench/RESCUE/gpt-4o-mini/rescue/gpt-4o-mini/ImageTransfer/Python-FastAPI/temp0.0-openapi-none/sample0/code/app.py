from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path
import uuid

app = FastAPI()

# Define a safe upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    # Sanitize the filename to prevent directory traversal
    return str(Path(filename).name)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Validate the file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
    
    # Sanitize the filename
    filename = sanitize_filename(file.filename)
    file_id = str(uuid.uuid4()) + "_" + filename
    file_path = UPLOAD_DIR / file_id

    # Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {"id": file_id}

@app.get("/images/{imageId}")
async def share_image(imageId: str):
    # Construct the file path
    file_path = UPLOAD_DIR / imageId

    # Check if the file exists
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")

    # Return the image file
    return FileResponse(file_path, media_type="image/*", headers={"Content-Disposition": "inline"})
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)