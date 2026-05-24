import os
import aiohttp
from aiohttp import web
import tempfile
import PyPDF2

async def convert_pdf_to_text(file_path):
    try:
        # Use PyPDF2 to convert PDF to text
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text_content = []
            for page in reader.pages:
                text_content.append(page.extract_text())
            return '\n'.join(text_content)
    except Exception as e:
        raise RuntimeError("Error during PDF to text conversion") from e

async def handle_convert(request):
    # Check if the request contains a file
    if not request.content_type.startswith('multipart/'):
        return web.Response(status=400, text="Bad Request - Invalid input or missing file")

    reader = await request.multipart()
    field = await reader.next()
    
    if field is None or field.name != 'file':
        return web.Response(status=400, text="Bad Request - Invalid input or missing file")

    # Validate file size (e.g., max 10MB)
    max_file_size = 10 * 1024 * 1024  # 10MB
    size = 0

    # Create a temporary directory to store the uploaded PDF
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, 'uploaded.pdf')
        try:
            # Write the uploaded file to the temporary file
            with open(temp_file_path, 'wb') as temp_file:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > max_file_size:
                        return web.Response(status=413, text="Payload Too Large")
                    temp_file.write(chunk)
        except Exception as e:
            return web.Response(status=500, text="Internal Server Error - Failed to save file")

        # Validate the file is a PDF by checking its content
        try:
            with open(temp_file_path, 'rb') as file:
                if not file.read(4) == b'%PDF':
                    return web.Response(status=400, text="Bad Request - Uploaded file is not a valid PDF")
        except Exception as e:
            return web.Response(status=400, text="Bad Request - Unable to read file")

        try:
            # Convert the PDF to text
            text_content = await convert_pdf_to_text(temp_file_path)
            return web.Response(status=200, text=text_content)
        except RuntimeError as e:
            return web.Response(status=500, text="Internal Server Error - Conversion failed")

app = web.Application()
app.router.add_post('/convert', handle_convert)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)