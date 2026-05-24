from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, constr
import subprocess
import os
import tempfile

app = FastAPI()

class GIFRequest(BaseModel):
    targetSize: constr(regex=r'^\d+x\d+$')  # e.g., "500x500"
    delay: int = 10
    appendReverted: bool = False

@app.post("/create-gif", response_class=Response)
async def create_gif(
    images: list[UploadFile] = File(...),
    request: GIFRequest
):
    # Validate target size
    width, height = map(int, request.targetSize.split('x'))
    
    # Create a temporary directory to store images
    with tempfile.TemporaryDirectory() as temp_dir:
        image_paths = []
        
        # Save uploaded images to the temporary directory
        for image in images:
            if not image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="Invalid image format.")
            image_path = os.path.join(temp_dir, image.filename)
            with open(image_path, "wb") as f:
                content = await image.read()
                f.write(content)
            image_paths.append(image_path)

        # Prepare the command for ImageMagick
        gif_path = os.path.join(temp_dir, "output.gif")
        command = ["convert", "-delay", str(request.delay), *image_paths, gif_path]

        # Append reverted images if requested
        if request.appendReverted:
            command += image_paths[::-1]

        # Execute the command
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            raise HTTPException(status_code=500, detail="Error creating GIF.")

        # Read the generated GIF
        with open(gif_path, "rb") as f:
            gif_data = f.read()

    return Response(content=gif_data, media_type="image/gif")