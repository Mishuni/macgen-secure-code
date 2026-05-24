import os
import zipfile
import tempfile
from aiohttp import web

# Constants
UPLOAD_DIR = tempfile.mkdtemp()  # Temporary directory for uploaded files
OUTPUT_DIR = tempfile.mkdtemp()  # Temporary directory for output files
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit for uploaded files
ALLOWED_EXTENSIONS = {".zip"}  # Allowed file extensions

# Utility function to validate and sanitize file names
def is_safe_file(filename):
    if not filename:
        return False
    if ".." in filename or filename.startswith("/"):
        return False
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS

# Utility function to concatenate text files in a zip archive
def process_zip_file(zip_path, output_path):
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            with open(output_path, "w", encoding="utf-8") as output_file:
                for file_info in zip_ref.infolist():
                    # Skip directories and non-text files
                    if file_info.is_dir() or not file_info.filename.endswith(".txt"):
                        continue
                    # Sanitize file name
                    if ".." in file_info.filename or file_info.filename.startswith("/"):
                        continue
                    # Extract and read the file
                    with zip_ref.open(file_info, "r") as file:
                        content = file.read().decode("utf-8", errors="ignore")
                        output_file.write(content + "\n")
    except (zipfile.BadZipFile, UnicodeDecodeError) as e:
        raise web.HTTPBadRequest(reason="Invalid zip file or file contents")

# Handler for the /convert endpoint
async def convert_zip_to_txt(request):
    reader = await request.multipart()
    field = await reader.next()
    if field.name != "file":
        raise web.HTTPBadRequest(reason="Invalid form field")
    
    # Save the uploaded file to a temporary location
    filename = field.filename
    if not is_safe_file(filename):
        raise web.HTTPBadRequest(reason="Invalid file name or type")
    
    temp_zip_path = os.path.join(UPLOAD_DIR, filename)
    size = 0
    with open(temp_zip_path, "wb") as temp_file:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_FILE_SIZE:
                raise web.HTTPBadRequest(reason="File size exceeds limit")
            temp_file.write(chunk)
    
    # Process the zip file and generate the output text file
    output_filename = os.path.splitext(filename)[0] + ".txt"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    try:
        process_zip_file(temp_zip_path, output_path)
    except web.HTTPBadRequest as e:
        os.remove(temp_zip_path)
        raise e
    
    # Return the generated text file as a response
    return web.FileResponse(output_path, headers={"Content-Type": "text/plain"})

# Create the web application and define routes
app = web.Application()
app.router.add_post("/convert", convert_zip_to_txt)

# Start the web server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)