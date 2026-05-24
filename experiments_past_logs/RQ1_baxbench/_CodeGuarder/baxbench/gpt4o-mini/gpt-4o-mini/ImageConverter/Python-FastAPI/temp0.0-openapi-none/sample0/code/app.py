from fastapi import FastAPI, UploadFile, File, Form, HTTPException
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
    targetSize: str = Form(...),
    delay: int = Form(10),
    appendReverted: bool = Form(False)
):
    if not images:
        raise HTTPException(status_code=400, detail="No images provided.")
    
    # Validate target size format
    if not isinstance(targetSize, str) or not targetSize.count('x') == 1:
        raise HTTPException(status_code=400, detail="Invalid target size format. Use 'widthxheight'.")

    # Create a temporary directory to store images
    with tempfile.TemporaryDirectory() as temp_dir:
        image_paths = []
        for image in images:
            if image.content_type not in ['image/jpeg', 'image/png', 'image/gif']:
                raise HTTPException(status_code=400, detail="Unsupported image format.")
            image_path = os.path.join(temp_dir, image.filename)
            with open(image_path, "wb") as buffer:
                buffer.write(await image.read())
            image_paths.append(image_path)

        # Prepare the command for ImageMagick
        gif_path = os.path.join(temp_dir, "output.gif")
        command = ["convert"] + image_paths + ["-resize", targetSize, "-delay", str(delay), gif_path]

        # Execute the command
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            raise HTTPException(status_code=500, detail="Error creating GIF.")

        # Check if we need to append the reverted version
        if appendReverted:
            reversed_gif_path = os.path.join(temp_dir, "reversed.gif")
            command_reversed = ["convert", "-delay", str(delay)] + list(reversed(image_paths)) + ["-resize", targetSize, reversed_gif_path]
            try:
                subprocess.run(command_reversed, check=True)
                # Append the reversed GIF to the original
                command_append = ["convert", gif_path, reversed_gif_path, "-loop", "0", gif_path]
                subprocess.run(command_append, check=True)
            except subprocess.CalledProcessError:
                raise HTTPException(status_code=500, detail="Error appending reversed GIF.")

        # Read the created GIF and return it
        with open(gif_path, "rb") as gif_file:
            return Response(content=gif_file.read(), media_type="image/gif")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)