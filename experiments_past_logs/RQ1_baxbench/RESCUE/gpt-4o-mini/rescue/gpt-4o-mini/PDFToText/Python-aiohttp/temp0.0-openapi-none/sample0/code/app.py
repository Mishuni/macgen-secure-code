import os
import subprocess
from aiohttp import web

async def convert_pdf_to_text(request):
    # Validate and sanitize input
    if 'file' not in request.post():
        return web.Response(status=400, body=b'Bad Request - Missing file')

    # Get the uploaded file
    reader = await request.multipart()
    field = await reader.next()
    
    if field is None or field.name != 'file':
        return web.Response(status=400, body=b'Bad Request - Invalid input')

    # Save the uploaded PDF file to a temporary location
    temp_file_path = '/tmp/uploaded_file.pdf'
    with open(temp_file_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # 512 bytes by default
            if not chunk:
                break
            f.write(chunk)

    # Check if the file is a valid PDF
    if not temp_file_path.endswith('.pdf'):
        os.remove(temp_file_path)
        return web.Response(status=400, body=b'Bad Request - Invalid file type')

    # Convert PDF to text using pdftotext
    try:
        result = subprocess.run(['pdftotext', temp_file_path, '-'], capture_output=True, text=True, check=True)
        os.remove(temp_file_path)  # Clean up the temporary file
        return web.Response(status=200, body=result.stdout.encode('utf-8'), content_type='text/plain')
    except subprocess.CalledProcessError:
        os.remove(temp_file_path)  # Clean up the temporary file
        return web.Response(status=500, body=b'Internal Server Error - Conversion failed')

app = web.Application()
app.router.add_post('/convert', convert_pdf_to_text)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)