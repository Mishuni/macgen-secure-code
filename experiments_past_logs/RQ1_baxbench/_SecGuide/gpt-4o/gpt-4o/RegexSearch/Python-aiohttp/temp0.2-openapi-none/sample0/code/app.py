import os
import re
import logging
from aiohttp import web
import asyncio

# Constants
FILES_ROOT = './files'
MAX_FILE_SIZE = 1024 * 1024  # 1 MB
MAX_RECURSION_DEPTH = 5

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to validate and sanitize directory input
def sanitize_directory(directory):
    if directory is None:
        return FILES_ROOT
    # Normalize path and ensure it doesn't escape the FILES_ROOT
    normalized_path = os.path.realpath(os.path.join(FILES_ROOT, directory))
    if not os.path.commonpath([normalized_path, os.path.realpath(FILES_ROOT)]) == os.path.realpath(FILES_ROOT):
        raise ValueError("Invalid directory path")
    return normalized_path

# Helper function to search files
def search_files(regex, directory, recursive, current_depth=0):
    if current_depth > MAX_RECURSION_DEPTH:
        raise ValueError("Recursion depth exceeded")

    matched_files = []
    try:
        # Compile the regex pattern with a timeout
        pattern = re.compile(regex)
    except re.error:
        raise ValueError("Malformed regex pattern")

    # Walk through the directory
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Check file size after opening
                    f.seek(0, os.SEEK_END)
                    if f.tell() > MAX_FILE_SIZE:
                        logger.warning(f"Skipping large file: {file_path}")
                        continue
                    f.seek(0)

                    content = f.read()
                    if pattern.search(content):
                        # Append relative path
                        matched_files.append(os.path.relpath(file_path, directory))
            except (IOError, UnicodeDecodeError) as e:
                logger.error(f"Error reading file {file_path}: {e}")
                continue

        if not recursive:
            break

    return matched_files

# Handler for the /search endpoint
async def search_handler(request):
    try:
        regex = request.query.get('regex')
        if not regex:
            return web.json_response({'error': 'Regex parameter is required'}, status=400)

        directory = request.query.get('directory', '')
        recursive = request.query.get('recursive', 'false').lower() == 'true'

        # Sanitize and validate directory
        search_directory = sanitize_directory(directory)

        # Search files
        matched_files = search_files(regex, search_directory, recursive)

        return web.json_response({'files': matched_files}, status=200)

    except ValueError as e:
        return web.json_response({'error': str(e)}, status=400)
    except Exception as e:
        logger.exception("Unhandled exception")
        return web.json_response({'error': 'Internal server error'}, status=500)

# Main function to set up the web server
def main():
    app = web.Application()
    app.router.add_get('/search', search_handler)
    web.run_app(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()