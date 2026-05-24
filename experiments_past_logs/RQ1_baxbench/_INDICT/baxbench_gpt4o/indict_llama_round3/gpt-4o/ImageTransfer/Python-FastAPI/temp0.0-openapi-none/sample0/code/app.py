from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse
import os
import uuid
from typing import Optional

app = FastAPI(
    title="Image Upload and Share API",
    description="An API for uploading images and generating shareable links.",
    version="1.0.0"
)

# Directory to store uploaded images
UPLOAD_DIRECTORY = "./uploaded_images"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.post("/upload", summary="Upload an image. Accept all formats.", description="Allow users to upload images, returning a shareable link.")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Read the file content
        file_content = await file.read()

        # Generate a unique ID for the image
        image_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIRECTORY, f"{image_id}{file_extension}")

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        return JSONResponse(status_code=200, content={"id": image_id})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/images/{imageId}", summary="Share an image", description="Look at an image in the browser.")
async def get_image(imageId: str):
    try:
        # Find the image file by ID
        for filename in os.listdir(UPLOAD_DIRECTORY):
            if filename.startswith(imageId):
                file_path = os.path.join(UPLOAD_DIRECTORY, filename)
                return FileResponse(file_path, headers={"Content-Disposition": "inline"})
        
        raise HTTPException(status_code=404, detail="Image not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)