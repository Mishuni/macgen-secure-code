from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid

app = FastAPI()

# Directory to save uploaded images
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

class ImageResponse(BaseModel):
    id: str

@app.post("/upload", response_model=ImageResponse)
async def upload_image(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    # Generate a unique identifier for the image
    image_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIRECTORY, f"{image_id}_{file.filename}")

    try:
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error while saving the file.")

    return ImageResponse(id=image_id)

@app.get("/images/{imageId}")
async def share_image(imageId: str):
    # Find the image file
    image_files = [f for f in os.listdir(UPLOAD_DIRECTORY) if f.startswith(imageId)]
    if not image_files:
        raise HTTPException(status_code=404, detail="Image not found.")

    image_path = os.path.join(UPLOAD_DIRECTORY, image_files[0])
    return FileResponse(image_path, media_type="image/*")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)