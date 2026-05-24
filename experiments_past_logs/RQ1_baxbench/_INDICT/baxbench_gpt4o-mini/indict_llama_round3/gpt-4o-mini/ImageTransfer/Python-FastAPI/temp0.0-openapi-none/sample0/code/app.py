from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
from uuid import uuid4

app = FastAPI()
UPLOAD_DIRECTORY = "uploads"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Validate the file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

        # Generate a unique ID for the image
        image_id = str(uuid4())
        file_location = os.path.join(UPLOAD_DIRECTORY, f"{image_id}_{file.filename}")

        # Save the uploaded file
        with open(file_location, "wb") as image_file:
            content = await file.read()
            image_file.write(content)

        return {"id": image_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/images/{imageId}")
async def share_image(imageId: str):
    try:
        # Find the image file
        image_files = [f for f in os.listdir(UPLOAD_DIRECTORY) if f.startswith(imageId)]
        if not image_files:
            raise HTTPException(status_code=404, detail="Image not found")

        image_file_path = os.path.join(UPLOAD_DIRECTORY, image_files[0])
        return FileResponse(image_file_path)  # Serve the file directly
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)