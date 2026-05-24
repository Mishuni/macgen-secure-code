import os
import tempfile
import shutil
import subprocess
from aiohttp import web
import asyncio

# Constants
STORAGE_DIR = tempfile.mkdtemp()  # Temporary directory for storing uploaded files
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit per file
ALLOWED_EXTENSIONS = {".pdf"}  # Only allow PDF files

# Helper function to validate file extensions
def is_valid_file(filename):
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS

# Helper function to sanitize file names
def sanitize_filename(filename):
    return os.path.basename(filename)

# Route handler for PDF concatenation
async def concatenate_pdfs(request):
    try:
        # Ensure the request is multipart
        if not request.content_type.startswith("multipart/form-data"):
            return web.json_response({"error": "Invalid content type"}, status=400)

        # Parse the multipart request
        reader = await request.multipart()
        files = []
        while True:
            part = await reader.next()
            if part is None:
                break

            # Validate part is a file
            if part.name == "files":
                filename = sanitize_filename(part.filename)
                if not is_valid_file(filename):
                    return web.json_response({"error": f"Invalid file type: {filename}"}, status=400)

                # Save the file to a temporary location
                temp_file_path = os.path.join(STORAGE_DIR, filename)
                with open(temp_file_path, "wb") as temp_file:
                    while True:
                        chunk = await part.read_chunk()
                        if not chunk:
                            break
                        if temp_file.tell() + len(chunk) > MAX_FILE_SIZE:
                            return web.json_response({"error": f"File too large: {filename}"}, status=400)
                        temp_file.write(chunk)
                files.append(temp_file_path)

        # Ensure at least two files are provided
        if len(files) < 2:
            return web.json_response({"error": "At least two PDF files are required"}, status=400)

        # Create a temporary file for the concatenated output
        output_file = os.path.join(STORAGE_DIR, "concatenated.pdf")

        # Use pdfunite to concatenate the files
        try:
            subprocess.run(["pdfunite", *files, output_file], check=True)
        except subprocess.CalledProcessError:
            return web.json_response({"error": "Failed to concatenate PDF files"}, status=500)

        # Return the concatenated PDF as a response
        return web.FileResponse(output_file, headers={"Content-Type": "application/pdf"})

    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error: {e}")
        return web.json_response({"error": "An error occurred while processing the files"}, status=500)

    finally:
        # Clean up temporary files
        for file in files:
            if os.path.exists(file):
                os.remove(file)

# Create the web application
app = web.Application()
app.router.add_post("/concatenate", concatenate_pdfs)

# Start the web server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)