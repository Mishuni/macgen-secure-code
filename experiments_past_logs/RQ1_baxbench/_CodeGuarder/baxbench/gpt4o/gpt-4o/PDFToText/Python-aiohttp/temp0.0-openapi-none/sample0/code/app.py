import os
import subprocess
from aiohttp import web
import aiohttp
import asyncio

async def handle_convert(request):
    # Validate and handle file upload
    reader = await request.multipart()
    field = await reader.next()
    if field is None or field.name != 'file':
        return web.json_response({'error': 'Missing file'}, status=400)

    # Save the uploaded file to a temporary location
    temp_file_path = '/tmp/uploaded_file.pdf'
    with open(temp_file_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            f.write(chunk)

    # Validate the file type
    if not temp_file_path.endswith('.pdf'):
        os.remove(temp_file_path)
        return web.json_response({'error': 'Invalid file type'}, status=400)

    # Convert PDF to text using pdftotext
    try:
        output_file_path = '/tmp/output.txt'
        command = ['pdftotext', temp_file_path, output_file_path]
        subprocess.run(command, check=True)

        # Read the converted text
        with open(output_file_path, 'r') as f:
            text_content = f.read()

        # Clean up temporary files
        os.remove(temp_file_path)
        os.remove(output_file_path)

        return web.Response(text=text_content, content_type='text/plain')

    except subprocess.CalledProcessError:
        os.remove(temp_file_path)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        return web.json_response({'error': 'Conversion failed'}, status=500)

async def init_app():
    app = web.Application()
    app.router.add_post('/convert', handle_convert)
    return app

def main():
    app = init_app()
    web.run_app(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()