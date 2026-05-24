import os
import aiohttp
from aiohttp import web
import logging
import re

# Constants
DATA_DIR = '/data'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_INPUT_SIZE = 1024  # 1 KB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to validate and sanitize input
def validate_and_sanitize_input(search_dir, search_filename, search_content):
    if search_dir:
        # Ensure the search_dir is a safe path
        search_dir = os.path.normpath(search_dir)
        full_path = os.path.abspath(os.path.join(DATA_DIR, search_dir))
        if not full_path.startswith(os.path.abspath(DATA_DIR)):
            raise ValueError("Invalid search directory path.")
    
    if search_filename:
        # Ensure the search_filename is a safe filename
        if not re.match(r'^[\w\-.]+$', search_filename):
            raise ValueError("Invalid search filename.")
    
    return search_dir, search_filename, search_content

# Function to search files
async def search_files(search_dir, search_filename, search_content):
    search_dir = os.path.join(DATA_DIR, search_dir) if search_dir else DATA_DIR
    result_files = []

    for root, _, files in os.walk(search_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                continue
            if search_filename and search_filename in file:
                result_files.append(os.path.relpath(file_path, DATA_DIR))
            elif search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if search_content in line:
                                result_files.append(os.path.relpath(file_path, DATA_DIR))
                                break
                except (UnicodeDecodeError, IOError):
                    continue

    return result_files

# Handler for the /search endpoint
async def search_handler(request):
    try:
        data = await request.json()
        if len(str(data)) > MAX_INPUT_SIZE:
            return web.json_response({'error': 'Input size too large'}, status=400)

        search_content = data.get('search_content')
        search_filename = data.get('search_filename')
        search_dir = data.get('search_dir')

        # Validate and sanitize input
        search_dir, search_filename, search_content = validate_and_sanitize_input(
            search_dir, search_filename, search_content
        )

        # Perform the search
        files = await search_files(search_dir, search_filename, search_content)
        return web.json_response({'files': files})

    except ValueError as e:
        return web.json_response({'error': str(e)}, status=400)
    except Exception as e:
        logger.exception("Exception occurred")
        return web.json_response({'error': 'Internal server error'}, status=500)

# Middleware to add security headers
@web.middleware
async def security_headers_middleware(request, handler):
    response = await handler(request)
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response

# Main function to set up the app and routes
def main():
    app = web.Application(middlewares=[security_headers_middleware])
    app.router.add_post('/search', search_handler)
    web.run_app(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()