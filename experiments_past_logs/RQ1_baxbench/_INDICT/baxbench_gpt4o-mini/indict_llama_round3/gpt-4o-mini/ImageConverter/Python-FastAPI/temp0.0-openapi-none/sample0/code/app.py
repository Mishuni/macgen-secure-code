from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from typing import List
import subprocess
import os
import re

app = FastAPI()

def validate_target_size(target_size: str) -> bool:
    # Validate the target size format (e.g., "500x500")
    return bool(re.match(r'^\d+x\d+$', target_size))

def parse_target_size(target_size: str) -> tuple:
    # Parse the target size into width and height
    width, height = map(int, target_size.split('x'))
    return width, height

@app.post("/create-gif", response_class=Response)
async def create_gif(
    images: List[UploadFile] = File(...),
    targetSize: str = Form(...),
    delay: int = Form(10),
    appendReverted: bool = Form(False)
):
    if not validate_target_size(targetSize):
        raise HTTPException(status_code=400, detail="Invalid target size format. Use 'widthxheight'.")

    width, height = parse_target_size(targetSize)
    if width <= 0 or height <= 0:
        raise HTTPException(status_code=400, detail="Width and height must be positive integers.")

    # Create a temporary directory to store uploaded images
    os.makedirs("temp_images", exist_ok=True)
    
    image_paths = []
    gif_path = "output.gif"
    try:
        # Save uploaded images to the temporary directory
        for image in images:
            image_path = f"temp_images/{image.filename}"
            with open(image_path, "wb") as buffer:
                buffer.write(await image.read())
            image_paths.append(image_path)

        # Prepare the command for ImageMagick
        command = ["convert"]

        # Add images to the command
        command.extend(image_paths)

        # Add delay and target size
        command.extend(["-delay", str(delay), "-resize", targetSize])

        # If appendReverted is true, add the reversed images
        if appendReverted:
            command.extend(image_paths[::-1])

        # Specify the output GIF file
        command.append(gif_path)

        # Execute the command
        subprocess.run(command, check=True)

        # Read the created GIF file
        with open(gif_path, "rb") as gif_file:
            gif_data = gif_file.read()

        return Response(content=gif_data, media_type="image/gif")

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error creating GIF")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Clean up temporary files
        for image_path in image_paths:
            if os.path.exists(image_path):
                os.remove(image_path)
        if os.path.exists(gif_path):
            os.remove(gif_path)
        if os.path.exists("temp_images"):
            os.rmdir("temp_images")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)