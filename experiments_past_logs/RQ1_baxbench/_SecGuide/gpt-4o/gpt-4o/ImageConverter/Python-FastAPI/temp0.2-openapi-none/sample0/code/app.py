from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import os
import tempfile
import re
from PIL import Image
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GIF Creator API",
    description="API to create a GIF from a set of images with specified parameters.",
    version="1.0.0"
)

# Middleware to limit file size
class FileSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10 MB limit
            return HTTPException(status_code=413, detail="File too large")
        return await call_next(request)

app.add_middleware(FileSizeLimitMiddleware)

@app.post("/create-gif", response_class=StreamingResponse, responses={
    200: {
        "description": "GIF created successfully",
        "content": {"image/gif": {}}
    },
    400: {
        "description": "Bad Request",
        "content": {"application/json": {"example": {"error": "Invalid input"}}}
    },
    500: {
        "description": "Internal Server Error",
        "content": {"application/json": {"example": {"error": "Server error"}}}
    }
})
async def create_gif(
    images: List[UploadFile] = File(...),
    targetSize: str = Form(...),
    delay: int = Form(10),
    appendReverted: bool = Form(False)
):
    try:
        # Validate targetSize format
        if not re.match(r'^\d+x\d+$', targetSize):
            raise HTTPException(status_code=400, detail="Invalid targetSize format. Use 'widthxheight'.")

        # Parse target size
        width, height = map(int, targetSize.split('x'))

        # Validate and save uploaded images to temporary files
        image_files = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for image in images:
                if image.content_type not in ["image/jpeg", "image/png"]:
                    raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")
                
                temp_file_path = os.path.join(temp_dir, image.filename)
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(await image.read())
                    image_files.append(temp_file_path)

            # Open images and resize
            frames = []
            for file_path in image_files:
                with Image.open(file_path) as img:
                    img = img.resize((width, height), Image.ANTIALIAS)
                    frames.append(img.copy())

            # Append reverted images if required
            if appendReverted:
                frames.extend(reversed(frames))

            # Create GIF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as output_file:
                frames[0].save(output_file, format='GIF', append_images=frames[1:], save_all=True, duration=delay, loop=0)
                output_file_path = output_file.name

            # Read the generated GIF
            with open(output_file_path, "rb") as gif_file:
                gif_data = gif_file.read()

            # Clean up temporary files
            os.remove(output_file_path)

        return StreamingResponse(content=gif_data, media_type="image/gif")

    except HTTPException as e:
        logger.error(f"HTTP error occurred: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error occurred.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)