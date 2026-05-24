import os
import tempfile
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from typing import List
from PIL import Image, ImageSequence
import shutil
import re
from starlette.responses import StreamingResponse

app = FastAPI()

# Constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg"}

@app.post('/create-gif')
async def create_gif(
    images: List[UploadFile] = File(...),
    target_size: str = Form(...),
    delay: int = Form(10),
    append_reverted: bool = Form(False)
):
    # Validate target_size format
    if not re.match(r'^\d+x\d+$', target_size):
        raise HTTPException(status_code=400, detail="Invalid target size format. Expected format: '100x100'.")

    # Validate delay
    if delay <= 0:
        raise HTTPException(status_code=400, detail="Delay must be a positive integer.")

    # Create a secure temporary directory
    temp_dir = tempfile.mkdtemp()

    try:
        # Save images to the temporary directory
        image_paths = []
        for i, image in enumerate(images):
            # Validate file size
            if image.size > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail=f"File {image.filename} exceeds the maximum size of 5 MB.")

            # Validate MIME type
            if image.content_type not in ALLOWED_MIME_TYPES:
                raise HTTPException(status_code=400, detail=f"File {image.filename} has an unsupported file type.")

            image_path = os.path.join(temp_dir, f'image_{i}.png')
            with open(image_path, 'wb') as f:
                shutil.copyfileobj(image.file, f)
            image_paths.append(image_path)

        # Create GIF using Pillow
        gif_path = os.path.join(temp_dir, 'output.gif')
        frames = [Image.open(image_path) for image_path in image_paths]

        # Resize images
        frames = [frame.resize(tuple(map(int, target_size.split('x')))) for frame in frames]

        # Append reversed frames if needed
        if append_reverted:
            frames.extend(reversed(frames))

        # Save as GIF
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=delay,
            loop=0
        )

        # Stream the GIF as a response
        return StreamingResponse(open(gif_path, 'rb'), media_type="image/gif")

    except (OSError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Clean up temporary files
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)