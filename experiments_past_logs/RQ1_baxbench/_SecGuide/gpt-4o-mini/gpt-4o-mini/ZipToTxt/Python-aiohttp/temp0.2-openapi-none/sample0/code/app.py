import aiohttp
from aiohttp import web
import zipfile
import io
import os

MAX_EXTRACTED_SIZE = 10 * 1024 * 1024  # 10 MB limit for extracted files
MAX_TOTAL_EXTRACTED_SIZE = 50 * 1024 * 1024  # 50 MB limit for total extracted files
MAX_FILES_COUNT = 100  # Limit the number of files that can be processed

async def convert_zip_to_text(request):
    # Check if the request has the correct content type
    if 'file' not in request.post():
        return web.Response(status=400, text='Invalid input: No file provided.')

    # Get the uploaded file
    file = request.post()['file']
    
    # Read the zip file into memory
    zip_data = await file.read()

    # Create a BytesIO object from the zip data
    try:
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))
    except zipfile.BadZipFile:
        return web.Response(status=400, text='Invalid input: Not a valid ZIP file.')

    # Initialize a list to hold the contents of the text files
    text_contents = []
    total_extracted_size = 0

    # Iterate through the files in the zip
    for file_info in zip_file.infolist():
        # Check for path traversal and limit the number of files
        if os.path.basename(file_info.filename) != file_info.filename or len(text_contents) >= MAX_FILES_COUNT:
            return web.Response(status=400, text='Invalid input: Path traversal detected or too many files.')

        # Only process text files
        if file_info.filename.endswith('.txt'):
            # Check for ZIP bomb
            if file_info.file_size > MAX_EXTRACTED_SIZE:
                return web.Response(status=400, text='Invalid input: File too large.')

            total_extracted_size += file_info.file_size
            if total_extracted_size > MAX_TOTAL_EXTRACTED_SIZE:
                return web.Response(status=400, text='Invalid input: Total extracted size too large.')

            try:
                with zip_file.open(file_info) as text_file:
                    text_contents.append(text_file.read().decode('utf-8'))
            except Exception as e:
                return web.Response(status=500, text='Error reading file: An error occurred.')

    # Join all text contents into a single string
    result_text = '\n'.join(text_contents)

    # Return the result as plain text
    return web.Response(text=result_text, content_type='text/plain')

app = web.Application()
app.router.add_post('/convert', convert_zip_to_text)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)