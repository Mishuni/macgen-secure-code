import os
import uuid
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound

# Constants
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the upload directory exists

# Helper function to sanitize and validate filenames
def secure_filename(filename):
    if not filename:
        raise ValueError("Filename is empty")
    filename = os.path.basename(filename)  # Remove directory traversal attempts
    if filename.startswith(".") or "/" in filename or "\\" in filename:
        raise ValueError("Invalid filename")
    return filename

# Routes
async def upload_image(request):
    try:
        # Ensure the request contains multipart data
        if not request.content_type.startswith("multipart/form-data"):
            raise HTTPBadRequest(reason="Invalid content type. Expected multipart/form-data.")

        reader = await request.multipart()
        field = await reader.next()

        # Validate the field name
        if field.name != "file":
            raise HTTPBadRequest(reason="Invalid field name. Expected 'file'.")

        # Validate and sanitize the filename
        filename = secure_filename(field.filename)
        if not filename:
            raise HTTPBadRequest(reason="No file provided.")

        # Generate a unique ID for the file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, file_id + "_" + filename)

        # Save the file
        with open(file_path, "wb") as f:
            while chunk := await field.read_chunk():
                f.write(chunk)

        # Return the file ID as a shareable link
        return web.json_response({"id": file_id})

    except ValueError as e:
        return web.json_response({"error": str(e)}, status=400)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)

async def get_image(request):
    try:
        # Extract and validate the image ID from the path
        image_id = request.match_info.get("imageId")
        if not image_id:
            raise HTTPBadRequest(reason="Image ID is required.")

        # Find the file corresponding to the image ID
        for filename in os.listdir(UPLOAD_DIR):
            if filename.startswith(image_id + "_"):
                file_path = os.path.join(UPLOAD_DIR, filename)
                break
        else:
            raise HTTPNotFound(reason="Image not found.")

        # Return the file with the correct content type
        return web.FileResponse(file_path, headers={"Content-Disposition": "inline"})

    except HTTPNotFound as e:
        return web.json_response({"error": str(e)}, status=404)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)

# Application setup
app = web.Application()
app.router.add_post("/upload", upload_image)
app.router.add_get("/images/{imageId}", get_image)

# Start the server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)