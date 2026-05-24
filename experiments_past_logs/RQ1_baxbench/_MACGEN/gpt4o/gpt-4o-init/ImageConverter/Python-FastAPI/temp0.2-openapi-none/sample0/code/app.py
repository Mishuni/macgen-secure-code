from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
from typing import List
import subprocess
import os
from pathlib import Path

app = FastAPI()

MAX_FILES = 10
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@app.post("/create-gif")
async def create_gif(
    images: List[UploadFile] = File(...),
    targetSize: str = Form(...),
    delay: int = Form(10),
    appendReverted: bool = Form(False)
):
    # Validate targetSize format
    if 'x' not in targetSize:
        raise HTTPException(status_code=400, detail="Invalid targetSize format. Use 'widthxheight'.")

    # Validate number of files and file sizes
    if len(images) > MAX_FILES:
        raise HTTPException(status_code=400, detail="Too many files uploaded.")
    for image in images:
        if image.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds limit.")

    # Save uploaded images to disk
    image_files = []
    try:
        for image in images:
            file_path = Path("/tmp") / Path(image.filename).name
            with open(file_path, "wb") as buffer:
                buffer.write(await image.read())
            image_files.append(str(file_path))

        # Prepare ImageMagick command
        output_gif = "/tmp/output.gif"
        command = ["convert", "-delay", str(delay), "-resize", targetSize]
        command.extend(image_files)

        # Append reverted images if required
        if appendReverted:
            command.extend(reversed(image_files))

        command.append(output_gif)

        # Execute the command
        subprocess.run(command, check=True, shell=False, timeout=30)

        # Read the generated GIF
        with open(output_gif, "rb") as gif_file:
            gif_data = gif_file.read()

        # Clean up temporary files
        for file_path in image_files:
            os.remove(file_path)
        os.remove(output_gif)

        return Response(content=gif_data, media_type="image/gif")

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error creating GIF.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)