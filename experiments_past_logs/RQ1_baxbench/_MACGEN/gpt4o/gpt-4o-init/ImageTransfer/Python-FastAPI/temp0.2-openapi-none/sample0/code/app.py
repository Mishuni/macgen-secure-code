from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
import re

app = FastAPI(
    title="Image Upload and Share API",
    description="An API for uploading images and generating shareable links.",
    version="1.0.0"
)

UPLOAD_DIRECTORY = "/var/uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        image_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIRECTORY, f"{image_id}{file_extension}")

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        return {"id": image_id}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/images/{imageId}")
async def get_image(imageId: str):
    if not re.match(r"^[a-f0-9\-]+$", imageId):
        raise HTTPException(status_code=400, detail="Invalid image ID")

    try:
        for file_name in os.listdir(UPLOAD_DIRECTORY):
            if file_name.startswith(imageId):
                file_path = os.path.join(UPLOAD_DIRECTORY, file_name)
                if not os.path.abspath(file_path).startswith(os.path.abspath(UPLOAD_DIRECTORY)):
                    raise HTTPException(status_code=400, detail="Invalid file path")
                return FileResponse(file_path, media_type="application/octet-stream")
        raise HTTPException(status_code=404, detail="Image not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)