import os
import re
from aiohttp import web

async def search_files(request):
    regex_pattern = request.query.get('regex')
    directory = request.query.get('directory', '')
    recursive = request.query.get('recursive', 'false').lower() == 'true'

    # Validate regex with a timeout
    try:
        re.compile(regex_pattern)
    except re.error:
        return web.json_response({'error': 'Invalid regex pattern.'}, status=400)

    # Validate directory path
    if not validate_directory(directory):
        return web.json_response({'error': 'Invalid directory path.'}, status=400)

    # Set the root directory
    root_directory = os.path.abspath('./files')
    search_directory = os.path.abspath(os.path.join(root_directory, directory))

    # Ensure the search directory is within the root directory
    if not search_directory.startswith(root_directory):
        return web.json_response({'error': 'Invalid directory path.'}, status=400)

    # Check if the directory exists
    if not os.path.exists(search_directory) or not os.path.isdir(search_directory):
        return web.json_response({'error': 'Directory does not exist or is not accessible.'}, status=400)

    matched_files = []
    
    # Search files
    if recursive:
        for dirpath, _, filenames in os.walk(search_directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if match_file(file_path, regex_pattern):
                    matched_files.append(os.path.relpath(file_path, root_directory))
    else:
        for filename in os.listdir(search_directory):
            file_path = os.path.join(search_directory, filename)
            if os.path.isfile(file_path) and match_file(file_path, regex_pattern):
                matched_files.append(os.path.relpath(file_path, root_directory))

    return web.json_response({'files': matched_files})

def match_file(file_path, regex_pattern):
    # Limit file size to prevent memory issues
    max_file_size = 1024 * 1024  # 1 MB
    if os.path.getsize(file_path) > max_file_size:
        return False

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        return re.search(regex_pattern, content) is not None

def validate_directory(directory):
    # Reject single path components and validate the directory
    if not directory or '..' in directory or '/' in directory or '\\' in directory:
        return False
    return True

app = web.Application()
app.router.add_get('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)