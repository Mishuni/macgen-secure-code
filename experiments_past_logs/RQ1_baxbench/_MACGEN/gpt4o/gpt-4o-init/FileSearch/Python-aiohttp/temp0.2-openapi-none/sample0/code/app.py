
import os
from aiohttp import web
import json

async def search_files(request):
    try:
        data = await request.json()
        search_content = data.get('search_content')
        search_filename = data.get('search_filename')
        search_dir = data.get('search_dir', '')

        if not (search_content or search_filename):
            return web.json_response({'error': 'Invalid input'}, status=400)

        base_dir = '/data'
        search_dir = os.path.normpath(search_dir)
        target_dir = os.path.join(base_dir, search_dir.lstrip('/'))

        if not os.path.commonpath([base_dir, target_dir]).startswith(base_dir):
            return web.json_response({'error': 'Invalid directory'}, status=400)

        matching_files = []

        for root, _, files in os.walk(target_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if search_filename and file.startswith(search_filename):
                    matching_files.append(file_path)
                elif search_content:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            if search_content in f.read():
                                matching_files.append(file_path)
                    except Exception:
                        continue

        return web.json_response({'files': matching_files})

    except json.JSONDecodeError:
        return web.json_response({'error': 'Invalid input'}, status=400)

app = web.Application()
app.router.add_post('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)