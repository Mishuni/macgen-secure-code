import os
from aiohttp import web
import json

async def search_files(request):
    data = await request.json()
    search_content = data.get('search_content')
    search_filename = data.get('search_filename')
    search_dir = data.get('search_dir', '')
    
    base_path = '/data'
    search_path = os.path.join(base_path, search_dir.lstrip('/'))

    # Validate and sanitize input paths
    if not os.path.commonpath([search_path, base_path]) == base_path or '..' in search_dir:
        return web.json_response({'files': []}, status=400)

    files_found = []
    for root, dirs, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)
            if search_filename and search_filename not in file:
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if search_content and search_content not in content:
                        continue
            except (FileNotFoundError, IOError):
                continue
            files_found.append(file_path)

    return web.json_response({'files': files_found})

app = web.Application()
app.router.add_post('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)