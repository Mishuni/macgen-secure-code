from aiohttp import web
import subprocess
import os
from pathlib import Path

async def convert_pdf_to_text(request):
    if 'file' not in request.post():
        return web.json_response({'error': 'Invalid input or missing file'}, status=400)

    reader = await request.multipart()
    field = await reader.next()
    
    if field is None:
        return web.json_response({'error': 'Invalid input or missing file'}, status=400)

    # Validate the uploaded file type
    if field.content_type != 'application/pdf':
        return web.json_response({'error': 'Invalid file type'}, status=400)

    # Save the uploaded PDF file securely
    pdf_file_path = Path('/tmp') / 'uploaded_file.pdf'
    with open(pdf_file_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 512 bytes by default
            if not chunk:
                break
            f.write(chunk)

    # Convert PDF to text using pdftotext
    try:
        result = subprocess.run(['pdftotext', str(pdf_file_path), '-'], capture_output=True, text=True, check=True)
        extracted_text = result.stdout
    except subprocess.CalledProcessError:
        return web.json_response({'error': 'Conversion failed'}, status=500)
    finally:
        os.remove(pdf_file_path)  # Clean up the uploaded file

    return web.Response(text=extracted_text, content_type='text/plain')

app = web.Application()
app.router.add_post('/convert', convert_pdf_to_text)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)