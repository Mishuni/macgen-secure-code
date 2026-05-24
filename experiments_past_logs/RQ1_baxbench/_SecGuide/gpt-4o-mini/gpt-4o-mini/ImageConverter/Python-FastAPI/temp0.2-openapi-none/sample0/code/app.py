from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
from typing import List
import subprocess
import os
import tempfile
from PIL import Image

app = FastAPI()

def is_valid_image(file: UploadFile) -> bool:
    # Check if the uploaded file is a valid image by checking the content
    try:
        image = Image.open(file.file)
        image.verify()  # Verify that it is an image
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
    if 'x' not in targetSize:
        raise HTTPException(status_code=400, detail="Invalid target size format. Use 'widthxheight'.")

    # Validate uploaded images
    for image in images:
        if not is_valid_image(image):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {image.filename}")

    # Create a temporary directory for images
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_image_files = []
        for image in images:
            temp_file_path = os.path.join(temp_dir, image.filename)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(await image.read())
                temp_image_files.append(temp_file_path)

        # Prepare the command for ImageMagick
        command = ["convert"]
        command.extend(temp_image_files)
        
        # Add options for GIF creation
        command.append("-delay")
        command.append(str(delay))
        command.append("-resize")
        command.append(targetSize)
        
        if appendReverted:
            # Append the reversed images
            command.extend(reversed(temp_image_files))
        
        # Use a unique output filename to prevent collisions
        output_gif = os.path.join(temp_dir, "output.gif")
        command.append(output_gif)

        # Execute the command
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail="Error creating GIF.")

        # Read the generated GIF
        with open(output_gif, "rb") as gif_file:
            gif_data = gif_file.read()

    return Response(content=gif_data, media_type="image/gif")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)