import os
import re
from aiohttp import web

async def search_files(request):
    regex_pattern = request.query.get('regex')
    directory = request.query.get('directory', '')
    recursive = request.query.get('recursive', 'false').lower() == 'true'

    if not regex_pattern:
        return web.json_response({'error': 'Regex pattern is required.'}, status=400)

    # Validate regex
    try:
        re.compile(regex_pattern)
    except re.error:
        return web.json_response({'error': 'Invalid regex pattern.'}, status=400)

    # Set the root directory
    root_directory = './files'
    search_directory = os.path.join(root_directory, directory)

    # Prevent directory traversal attacks
    if not os.path.commonpath([search_directory, root_directory]) == root_directory:
        return web.json_response({'error': 'Invalid directory path.'}, status=400)

    # Check if the directory exists
    if not os.path.exists(search_directory) or not os.path.isdir(search_directory):
        return web.json_response({'error': 'Directory does not exist or is inaccessible.'}, status=400)

    matched_files = []

    # Function to search files
    async def search_in_directory(path):
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path) and recursive:
                await search_in_directory(full_path)
            elif os.path.isfile(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                        if re.search(regex_pattern, content):
                            relative_path = os.path.relpath(full_path, root_directory)
                            matched_files.append(relative_path)
                except Exception:
                    continue

    await search_in_directory(search_directory)

    return web.json_response({'files': matched_files})

app = web.Application()
app.router.add_get('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)