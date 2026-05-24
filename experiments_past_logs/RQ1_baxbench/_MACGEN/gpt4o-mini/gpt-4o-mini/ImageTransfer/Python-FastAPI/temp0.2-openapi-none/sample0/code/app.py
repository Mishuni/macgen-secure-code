from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
import os
import uuid

app = FastAPI()
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the limit of 5 MB.")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
    
    # Generate a unique identifier for the file
    image_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{image_id}{file_extension}")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"id": image_id}

@app.get("/images/{imageId}")
async def share_image(imageId: str):
    # Check for files with the given imageId
    image_files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(imageId)]
    
    if not image_files:
        raise HTTPException(status_code=404, detail="Image not found.")
    
    image_path = os.path.join(UPLOAD_DIR, image_files[0])
    
    with open(image_path, "rb") as f:
        content = f.read()
    
    # Serve the image with inline disposition
    return Response(content=content, media_type="image/jpeg", headers={"Content-Disposition": "inline"})