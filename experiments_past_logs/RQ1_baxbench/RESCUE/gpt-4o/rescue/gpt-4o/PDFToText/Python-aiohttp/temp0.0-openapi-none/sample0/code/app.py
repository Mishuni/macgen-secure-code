import os
import tempfile
import subprocess
from aiohttp import web
import aiohttp
import asyncio

# Define constants
STORAGE_DIR = tempfile.gettempdir()  # Use a temporary directory for file storage
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit for uploaded files

# Utility function to sanitize file names
def sanitize_filename(filename):
    return os.path.basename(filename)

# Route handler for PDF to Text conversion
async def convert_pdf_to_text(request):
    try:
        # Ensure the request is multipart/form-data
        if not request.content_type.startswith("multipart/form-data"):
            return web.Response(status=400, text="Invalid content type. Expected multipart/form-data.")

        # Parse the incoming request
        reader = await request.multipart()
        field = await reader.next()

        # Ensure the field is named "file"
        if field.name != "file":
            return web.Response(status=400, text="Invalid field name. Expected 'file'.")

        # Get the filename and sanitize it
        filename = sanitize_filename(field.filename)
        if not filename:
            return web.Response(status=400, text="Missing or invalid file name.")

        # Ensure the file is a PDF
        if not filename.lower().endswith(".pdf"):
            return web.Response(status=400, text="Invalid file type. Only PDF files are allowed.")

        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join(STORAGE_DIR, filename)
        with open(temp_file_path, "wb") as temp_file:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                if temp_file.tell() + len(chunk) > MAX_FILE_SIZE:
                    return web.Response(status=400, text="File size exceeds the maximum allowed limit of 10 MB.")
                temp_file.write(chunk)

        # Ensure the file is within the allowed directory
        if not os.path.abspath(temp_file_path).startswith(STORAGE_DIR):
            return web.Response(status=400, text="Invalid file path.")

        # Convert the PDF to text using the `pdftotext` utility
        output_text = ""
        try:
            result = subprocess.run(
                ["pdftotext", temp_file_path, "-"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            output_text = result.stdout
        except subprocess.CalledProcessError as e:
            return web.Response(status=500, text="Failed to convert PDF to text.")

        # Clean up the temporary file
        os.remove(temp_file_path)

        # Return the extracted text as plain text
        return web.Response(
            status=200,
            text=output_text,
            content_type="text/plain"
        )

    except Exception as e:
        # Handle unexpected errors
        return web.Response(status=500, text="An unexpected error occurred.")

# Create the web application and define routes
app = web.Application()
app.router.add_post("/convert", convert_pdf_to_text)

# Start the web server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)