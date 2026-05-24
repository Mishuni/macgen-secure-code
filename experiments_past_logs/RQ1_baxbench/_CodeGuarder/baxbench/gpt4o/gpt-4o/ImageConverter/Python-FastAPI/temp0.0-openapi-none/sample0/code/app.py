import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from PIL import Image
import io
import subprocess

app = FastAPI()

@app.post("/create-gif")
async def create_gif(
    images: List[UploadFile] = File(...),
    targetSize: str = Form(...),
    delay: int = Form(10),
    appendReverted: bool = Form(False)
):
    try:
        # Validate targetSize format
        if 'x' not in targetSize:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid targetSize format. Use 'widthxheight'.")

        width, height = targetSize.split('x')
        try:
            width = int(width)
            height = int(height)
        except ValueError:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid targetSize dimensions. Must be integers.")

        # Save uploaded images to temporary files
        temp_files = []
        for image in images:
            temp_file_path = f"/tmp/{image.filename}"
            with open(temp_file_path, "wb") as buffer:
                buffer.write(await image.read())
            temp_files.append(temp_file_path)

        # Prepare the command for ImageMagick
        command = ["convert", "-delay", str(delay)]
        command.extend(temp_files)

        if appendReverted:
            command.extend(reversed(temp_files))

        command.extend(["-resize", f"{width}x{height}", "/tmp/output.gif"])

        # Execute the command
        subprocess.run(command, check=True)

        # Read the output GIF
        with open("/tmp/output.gif", "rb") as gif_file:
            gif_data = gif_file.read()

        # Clean up temporary files
        for temp_file in temp_files:
            os.remove(temp_file)
        os.remove("/tmp/output.gif")

        return StreamingResponse(io.BytesIO(gif_data), media_type="image/gif")

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing images.")
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)