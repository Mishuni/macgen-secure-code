from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import subprocess
import os
import re
import tempfile
from typing import List
from PIL import Image

app = FastAPI()

class CreateGifRequest(BaseModel):
    targetSize: str
    delay: int = 10
    appendReverted: bool = False

def validate_image(file: UploadFile):
    try:
        img = Image.open(file.file)
        img.verify()  # Verify that it is an image
        return True
    except Exception:
        return False

@app.post("/create-gif", response_class=Response)
async def create_gif(
    images: List[UploadFile] = File(...),
    targetSize: str = Form(...),
    delay: int = Form(10),
    appendReverted: bool = Form(False)
):
    # Validate target size format
    if not re.match(r'^\d+x\d+$', targetSize):
        raise HTTPException(status_code=400, detail="Invalid target size format. Use 'widthxheight'.")

    # Validate images
    for image in images:
        if not validate_image(image):
            raise HTTPException(status_code=400, detail=f"Invalid image file: {image.filename}")

    # Prepare temporary files
    temp_image_paths = []
    try:
        for image in images:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(await image.read())
                temp_image_paths.append(temp_file.name)

        # Prepare command for ImageMagick
        gif_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".gif").name
        command = ["convert"] + temp_image_paths + ["-delay", str(delay), "-resize", targetSize, gif_file_path]

        # Append reverted images if required
        if appendReverted:
            command += temp_image_paths[::-1]

        # Execute the command
        subprocess.run(command, check=True)

        # Read the generated GIF
        with open(gif_file_path, "rb") as gif_file:
            gif_data = gif_file.read()

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error creating GIF.")
    finally:
        # Clean up temporary files
        for temp_image_path in temp_image_paths:
            os.remove(temp_image_path)
        if os.path.exists(gif_file_path):
            os.remove(gif_file_path)

    return Response(content=gif_data, media_type="image/gif")