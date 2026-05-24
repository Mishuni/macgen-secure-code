from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List
import subprocess
import tempfile
import os
import re

app = FastAPI(
    title="GIF Creator API",
    description="API to create a GIF from a set of images with specified parameters.",
    version="1.0.0"
)

def validate_target_size(target_size: str):
    if not re.match(r'^\d+x\d+$', target_size):
        raise ValueError("Target size must be in the format 'widthxheight', e.g., '500x500'.")

@app.post("/create-gif", summary="Create a GIF from images")
async def create_gif(
    images: List[UploadFile] = File(..., description="Array of images to be included in the GIF."),
    targetSize: str = Form(..., description="Target size for the GIF in pixels (width x height).", example="500x500"),
    delay: int = Form(10, description="Delay between frames in milliseconds.", example=100),
    appendReverted: bool = Form(False, description="Whether to append a reverted version of the images to the GIF.", example=True)
):
    try:
        validate_target_size(targetSize)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            image_paths = []
            for image in images:
                if not image.content_type.startswith('image/'):
                    raise HTTPException(status_code=400, detail="Uploaded file is not an image.")
                
                image_path = os.path.join(temp_dir, image.filename)
                with open(image_path, "wb") as buffer:
                    buffer.write(await image.read())
                image_paths.append(image_path)

            if appendReverted:
                image_paths.extend(reversed(image_paths))

            output_gif_path = os.path.join(temp_dir, "output.gif")
            convert_command = [
                "convert",
                "-delay", str(delay),
                "-resize", targetSize,
                *image_paths,
                output_gif_path
            ]

            subprocess.run(convert_command, check=True, shell=False)

            return FileResponse(
                output_gif_path,
                media_type="image/gif",
                filename="output.gif"
            )
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error occurred while creating GIF.")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)