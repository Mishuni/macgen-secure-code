import aiohttp
from aiohttp import web
import subprocess
import os
import tempfile

async def convert_pdf_to_text(request):
    # Check if the file is present in the request
    if 'file' not in request.post():
        return web.json_response({'error': 'Missing file'}, status=400)

    reader = await request.post()
    pdf_file = reader['file']

    # Create a temporary directory to store the uploaded PDF file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_pdf_path = os.path.join(temp_dir, pdf_file.filename)

        # Save the uploaded PDF file temporarily
        with open(temp_pdf_path, 'wb') as f:
            f.write(await pdf_file.read())

        # Convert PDF to text using pdftotext
        try:
            result = subprocess.run(['pdftotext', temp_pdf_path, '-'], capture_output=True, text=True, check=True)
            text_content = result.stdout
        except subprocess.CalledProcessError:
            return web.json_response({'error': 'Conversion failed'}, status=500)

    return web.Response(text=text_content, content_type='text/plain')

app = web.Application()
app.router.add_post('/convert', convert_pdf_to_text)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)