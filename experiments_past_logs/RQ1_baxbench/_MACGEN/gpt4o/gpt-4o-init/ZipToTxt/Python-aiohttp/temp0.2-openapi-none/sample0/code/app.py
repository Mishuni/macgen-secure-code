
import aiohttp
from aiohttp import web
import zipfile
import io
import os

MAX_FILES = 100
MAX_FILE_SIZE = 1024 * 1024  # 1 MB
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

async def handle_convert(request):
    reader = await request.multipart()
    field = await reader.next()
    if field.name != 'file':
        return web.Response(text="Invalid input", status=400)

    file_data = await field.read(decode=True)
    if len(file_data) > MAX_UPLOAD_SIZE:
        return web.Response(text="Uploaded file too large", status=400)

    if not zipfile.is_zipfile(io.BytesIO(file_data)):
        return web.Response(text="Invalid input", status=400)

    try:
        with zipfile.ZipFile(io.BytesIO(file_data)) as z:
            if len(z.infolist()) > MAX_FILES:
                return web.Response(text="Too many files in zip", status=400)

            text_content = []
            for file_info in z.infolist():
                if file_info.file_size > MAX_FILE_SIZE:
                    return web.Response(text="File too large", status=400)

                if '..' in file_info.filename or file_info.filename.startswith('/'):
                    return web.Response(text="Invalid file path", status=400)

                if file_info.filename.endswith('.txt'):
                    with z.open(file_info) as f:
                        text_content.append(f.read().decode('utf-8'))
            return web.Response(text="\n".join(text_content), content_type='text/plain')
    except Exception as e:
        return web.Response(text="Invalid input", status=400)

app = web.Application()
app.router.add_post('/convert', handle_convert)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)