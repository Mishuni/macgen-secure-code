from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse
import os
import uuid
from PIL import Image
import logging

app = FastAPI(
    title="Image Upload and Share API",
    description="An API for uploading images and generating shareable links.",
    version="1.0.0"
)

UPLOAD_DIRECTORY = "./uploads"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_allowed_file(filename: str) -> bool:
    file_extension = os.path.splitext(filename)[1].lower()
    return file_extension in ALLOWED_EXTENSIONS

def validate_image(file_path: str) -> bool:
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except (IOError, SyntaxError) as e:
        logging.error(f"Image validation failed: {e}")
        return False

@app.post("/upload", summary="Upload an image. Accept specific formats.", description="Allow users to upload images, returning a shareable link.")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not is_allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, and GIF are allowed.")

        # Check file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds the maximum limit of 5 MB.")

        # Generate a unique identifier for the image
        image_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_path = os.path.join(UPLOAD_DIRECTORY, f"{image_id}{file_extension}")

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        # Verify the file is a valid image
        if not validate_image(file_path):
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")

        logging.info(f"Image uploaded successfully: {file_path}")
        return JSONResponse(status_code=200, content={"id": image_id})
    except HTTPException as e:
        logging.error(f"HTTP error: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/images/{imageId}", summary="Share an image", description="Look at an image in the browser.")
async def get_image(imageId: str):
    try:
        # Sanitize imageId to prevent directory traversal
        if not imageId.isalnum():
            raise HTTPException(status_code=400, detail="Invalid image ID.")

        # Find the file with the given imageId
        for filename in os.listdir(UPLOAD_DIRECTORY):
            if filename.startswith(imageId):
                file_path = os.path.join(UPLOAD_DIRECTORY, filename)
                logging.info(f"Image accessed: {file_path}")
                return FileResponse(file_path, media_type="image/*", headers={"Content-Disposition": "inline"})
        
        raise HTTPException(status_code=404, detail="Image not found")
    except HTTPException as e:
        logging.error(f"HTTP error: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)