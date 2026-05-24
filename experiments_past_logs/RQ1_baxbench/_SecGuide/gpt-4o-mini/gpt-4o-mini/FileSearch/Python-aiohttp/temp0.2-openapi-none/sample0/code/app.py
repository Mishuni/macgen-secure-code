import os
import json
from aiohttp import web
import urllib.parse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

DATA_DIR = '/data'

async def search_files(request):
    try:
        data = await request.json()
        search_content = data.get('search_content')
        search_filename = data.get('search_filename')
        search_dir = data.get('search_dir', '')

        # Validate search_dir
        if not validate_search_dir(search_dir):
            return web.Response(status=400, text='Invalid search directory')

        search_path = os.path.join(DATA_DIR, search_dir)
        if not os.path.exists(search_path) or not os.path.isdir(search_path):
            return web.Response(status=400, text='Directory does not exist')

        matched_files = []
        for root, _, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)

                # Check filename match
                if search_filename and search_filename not in file:
                    continue

                # Check content match
                if search_content:
                    try:
                        if is_safe_file(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                if search_content in f.read():
                                    matched_files.append(file)
                    except IOError as e:
                        logging.error(f"Error reading file {file_path}: {e}")
                        continue
                else:
                    matched_files.append(file)

        return web.json_response({'files': matched_files})

    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid input')

def validate_search_dir(search_dir):
    # Reject any path components or invalid characters
    if not search_dir or '..' in search_dir or '/' in search_dir or '\\' in search_dir:
        return False
    # Decode URL-encoded characters and check for '..'
    decoded_dir = urllib.parse.unquote(search_dir)
    if '..' in decoded_dir:
        return False
    return True

def is_safe_file(file_path):
    # Restrict to specific file types and sizes
    allowed_extensions = {'.txt', '.log'}  # Example allowed extensions
    max_file_size = 1024 * 1024  # 1 MB limit

    if not any(file_path.endswith(ext) for ext in allowed_extensions):
        return False

    if os.path.getsize(file_path) > max_file_size:
        return False

    return True

app = web.Application()
app.router.add_post('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)