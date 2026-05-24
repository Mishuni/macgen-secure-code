import aiohttp
from aiohttp import web
import zipfile
import io
import os

async def convert_zip_to_text(request):
    if 'file' not in request.post():
        return web.Response(status=400, text='Invalid input: No file provided.')

    file = request.post()['file']
    
    if not file.filename.endswith('.zip'):
        return web.Response(status=400, text='Invalid input: File is not a zip file.')

    try:
        zip_file = zipfile.ZipFile(io.BytesIO(await file.read()))
        
        # Security checks
        total_size = 0
        max_file_size = 1 * 1024 * 1024  # 1 MB limit per file
        max_entries = 100  # Limit on number of entries
        text_contents = []

        for name in zip_file.namelist():
            # Validate ZIP entry paths to prevent directory traversal
            if not os.path.normpath(name).startswith(os.path.normpath('')):
                return web.Response(status=400, text='Invalid input: Invalid file path in zip.')

            # Limit the number of entries
            if len(text_contents) >= max_entries:
                return web.Response(status=400, text='Invalid input: Too many files in zip.')

            # Check for text files and their sizes
            if name.endswith('.txt'):
                with zip_file.open(name) as text_file:
                    file_content = text_file.read()
                    if len(file_content) > max_file_size:
                        return web.Response(status=400, text='Invalid input: One of the text files is too large.')
                    text_contents.append(file_content.decode('utf-8'))
                    total_size += len(file_content)

        return web.Response(text=''.join(text_contents), content_type='text/plain')

    except zipfile.BadZipFile:
        return web.Response(status=400, text='Invalid input: Bad zip file.')

app = web.Application()
app.router.add_post('/convert', convert_zip_to_text)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)