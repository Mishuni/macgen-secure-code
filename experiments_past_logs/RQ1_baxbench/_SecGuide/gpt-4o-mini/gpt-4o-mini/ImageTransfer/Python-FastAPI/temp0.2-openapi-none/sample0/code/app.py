from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
import os
import uuid

app = FastAPI()

# Directory to store uploaded images
UPLOAD_DIRECTORY = "uploads"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

def is_image(file: UploadFile) -> bool:
    try:
        # Attempt to open the file as an image
        img = Image.open(file.file)
        img.verify()  # Verify that it is an image
        return True
    except Exception:
        return False

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    # Validate the actual content of the file
    if not is_image(file):
        raise HTTPException(status_code=400, detail="Invalid image content.")

    # Generate a unique ID for the image
    image_id = str(uuid.uuid4())
    
    # Sanitize the filename to prevent directory traversal attacks
    sanitized_filename = os.path.basename(file.filename)
    file_location = os.path.join(UPLOAD_DIRECTORY, f"{image_id}_{sanitized_filename}")

    # Check file size before reading
    if file.size > 5 * 1024 * 1024:  # Limit to 5 MB
        raise HTTPException(status_code=400, detail="File size exceeds the limit of 5 MB.")
    
    # Save the uploaded file
    with open(file_location, "wb") as image_file:
        content = await file.read()
        image_file.write(content)

    return {"id": image_id}

@app.get("/images/{imageId}")
async def share_image(imageId: str):
    # List all files in the upload directory
    files = os.listdir(UPLOAD_DIRECTORY)
    
    # Find the file that matches the imageId
    matching_files = [f for f in files if f.startswith(imageId)]
    
    if not matching_files:
        raise HTTPException(status_code=404, detail="Image not found")

    # Return the first matching file
    file_path = os.path.join(UPLOAD_DIRECTORY, matching_files[0])
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)