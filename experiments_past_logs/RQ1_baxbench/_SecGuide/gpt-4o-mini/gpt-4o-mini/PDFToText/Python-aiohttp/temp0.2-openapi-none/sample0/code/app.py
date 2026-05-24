import aiohttp
from aiohttp import web
import subprocess
import os
import tempfile

async def convert_pdf_to_text(request):
    # Check if the request has the file
    if 'file' not in request.post():
        return web.json_response({'error': 'Missing file'}, status=400)

    # Get the uploaded file
    reader = await request.multipart()
    field = await reader.next()
    
    if field is None or field.name != 'file':
        return web.json_response({'error': 'Invalid input'}, status=400)

    # Validate file type by checking the magic number
    file_content = await field.read()
    if not file_content.startswith(b'%PDF'):
        return web.json_response({'error': 'Invalid PDF file'}, status=400)

    # Check file size limit (e.g., 5 MB)
    if len(file_content) > 5 * 1024 * 1024:
        return web.json_response({'error': 'File size exceeds limit'}, status=400)

    # Create a secure temporary file
    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as temp_file:
        temp_file.write(file_content)
        temp_file.flush()  # Ensure the file is written before using it

        # Convert PDF to text using pdftotext
        try:
            result = subprocess.run(['pdftotext', temp_file.name, '-'], capture_output=True, text=True, check=True)
            text_content = result.stdout
        except subprocess.CalledProcessError:
            return web.json_response({'error': 'Conversion failed'}, status=500)
        except Exception as e:
            return web.json_response({'error': 'An unexpected error occurred'}, status=500)

    return web.Response(text=text_content, content_type='text/plain')

app = web.Application()
app.router.add_post('/convert', convert_pdf_to_text)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)