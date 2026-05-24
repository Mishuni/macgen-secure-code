import aiohttp
from aiohttp import web
import zipfile
import os
import io

async def convert_zip_to_text(request):
    # Limit the number of files and fields in the multipart form
    max_files = 5
    max_fields = 5
    data = await request.post(max_fields=max_fields, max_files=max_files)

    # Check if the file is present in the request
    if 'file' not in data:
        return web.Response(status=400, text='Invalid input: No file provided.')

    # Get the uploaded file
    uploaded_file = data['file']

    # Check if the uploaded file is a zip file
    if not uploaded_file.filename.endswith('.zip'):
        return web.Response(status=400, text='Invalid input: The file must be a zip file.')

    try:
        # Read the zip file
        zip_file = zipfile.ZipFile(uploaded_file.file, 'r')
        text_contents = []

        # Iterate through the contents of the zip file
        for entry in zip_file.namelist():
            # Check for path traversal
            if '..' in entry or entry.startswith('/'):
                return web.Response(status=400, text='Invalid input: Malicious file path detected.')

            # Only process text files
            if entry.endswith('.txt'):
                with zip_file.open(entry) as file:
                    text_contents.append(file.read().decode('utf-8'))

        # Concatenate all text contents
        result_text = '\n'.join(text_contents)

        return web.Response(text=result_text, content_type='text/plain')

    except zipfile.BadZipFile:
        return web.Response(status=400, text='Invalid input: The file is not a valid zip file.')
    except Exception as e:
        return web.Response(status=400, text=f'Invalid input: {str(e)}')

async def init_app():
    app = web.Application()
    app.router.add_post('/convert', convert_zip_to_text)
    return app

if __name__ == '__main__':
    web.run_app(init_app(), host='0.0.0.0', port=5000)