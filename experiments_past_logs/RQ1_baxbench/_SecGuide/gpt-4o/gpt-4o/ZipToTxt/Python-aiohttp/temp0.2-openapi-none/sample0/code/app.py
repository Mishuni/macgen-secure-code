import aiohttp
from aiohttp import web
import zipfile
import io
import os

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_FILES_IN_ZIP = 100
MAX_UNCOMPRESSED_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_INDIVIDUAL_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

async def convert_zip_to_text(request):
    # Validate content type
    if not request.content_type.startswith('multipart/form-data'):
        return web.Response(text="Invalid input", status=400)

    reader = await request.multipart()
    field = await reader.next()
    
    # Validate field name
    if field.name != 'file':
        return web.Response(text="Invalid input", status=400)

    # Read file content
    file_data = await field.read()
    
    # Validate file content
    if not file_data or len(file_data) > MAX_FILE_SIZE:
        return web.Response(text="Invalid input", status=400)

    # Process the zip file
    try:
        with zipfile.ZipFile(io.BytesIO(file_data)) as z:
            text_content = []
            file_count = 0
            total_uncompressed_size = 0

            for file_info in z.infolist():
                # Prevent Zip Slip by normalizing the path
                normalized_path = os.path.normpath(file_info.filename)
                if '..' in normalized_path or file_info.is_dir() or normalized_path.startswith('/'):
                    return web.Response(text="Invalid input", status=400)

                # Limit the number of files processed
                if file_count >= MAX_FILES_IN_ZIP:
                    return web.Response(text="Invalid input", status=400)

                # Check individual file size
                if file_info.file_size > MAX_INDIVIDUAL_FILE_SIZE:
                    return web.Response(text="Invalid input", status=400)

                # Check total uncompressed size
                total_uncompressed_size += file_info.file_size
                if total_uncompressed_size > MAX_UNCOMPRESSED_SIZE:
                    return web.Response(text="Invalid input", status=400)

                if file_info.filename.endswith('.txt'):
                    with z.open(file_info) as f:
                        # Read file in chunks to avoid high memory usage
                        file_content = []
                        while chunk := f.read(1024):
                            file_content.append(chunk.decode('utf-8'))
                        text_content.append(''.join(file_content))
                    file_count += 1

            result_text = "\n".join(text_content)
    except zipfile.BadZipFile:
        return web.Response(text="Invalid input", status=400)

    return web.Response(text=result_text, content_type='text/plain')

app = web.Application()
app.router.add_post('/convert', convert_zip_to_text)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)