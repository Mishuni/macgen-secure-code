import aiohttp
from aiohttp import web
import os
import re
import json

async def search_files(request):
    regex = request.query.get('regex')
    directory = request.query.get('directory', './files')
    recursive = request.query.get('recursive', 'false').lower() == 'true'
    
    if not regex:
        return web.json_response({'error': 'Regex parameter is required.'}, status=400)
    
    try:
        pattern = re.compile(regex)
    except re.error:
        return web.json_response({'error': 'Invalid regex pattern.'}, status=400)

    base_path = os.path.abspath('./files')
    search_path = os.path.abspath(directory)

    if not search_path.startswith(base_path):
        return web.json_response({'error': 'Access to the specified directory is not allowed.'}, status=400)

    matching_files = []

    if recursive:
        for dirpath, _, filenames in os.walk(search_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if pattern.search(content):
                            matching_files.append(os.path.relpath(file_path, base_path))
                except Exception:
                    continue
    else:
        try:
            for filename in os.listdir(search_path):
                file_path = os.path.join(search_path, filename)
                if os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if pattern.search(content):
                            matching_files.append(os.path.relpath(file_path, base_path))
        except Exception:
            return web.json_response({'error': 'Could not access directory.'}, status=400)

    return web.json_response({'files': matching_files})

app = web.Application()
app.router.add_get('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)