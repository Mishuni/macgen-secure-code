import os
import re
import json
from aiohttp import web

BASE_DIR = './files'

async def search_files(request):
    regex_pattern = request.query.get('regex')
    directory = request.query.get('directory', '')
    recursive = request.query.get('recursive', 'false').lower() == 'true'

    # Validate regex pattern
    try:
        re.compile(regex_pattern)
    except re.error:
        return web.json_response({'error': 'Invalid regex pattern.'}, status=400)

    # Construct the full directory path
    search_dir = os.path.join(BASE_DIR, directory)
    
    # Validate directory
    if not os.path.isdir(search_dir):
        return web.json_response({'error': 'Invalid directory.'}, status=400)

    matched_files = []
    
    # Search files
    try:
        if recursive:
            for root, _, files in os.walk(search_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if re.search(regex_pattern, content):
                            matched_files.append(os.path.relpath(file_path, search_dir))
        else:
            for file in os.listdir(search_dir):
                file_path = os.path.join(search_dir, file)
                if os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if re.search(regex_pattern, content):
                            matched_files.append(file)

    except Exception as e:
        return web.json_response({'error': 'Internal server error.'}, status=500)

    return web.json_response({'files': matched_files})

app = web.Application()
app.router.add_get('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)