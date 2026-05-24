import os
import json
from aiohttp import web
import aiofiles

async def search_files(request):
    try:
        data = await request.json()
        search_content = data.get('search_content')
        search_filename = data.get('search_filename')
        search_dir = data.get('search_dir', '')

        base_path = '/data'
        search_path = os.path.join(base_path, search_dir.lstrip('/'))

        # Validate the search directory
        if not os.path.exists(search_path) or not os.path.isdir(search_path):
            return web.json_response({'files': []}, status=400)

        matched_files = set()

        # Walk through the directory
        for root, _, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)

                # Check for filename match
                if search_filename and search_filename in file:
                    matched_files.add(file_path)

                # Check for content match
                if search_content:
                    try:
                        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                            content = await f.read()
                            if search_content in content:
                                matched_files.add(file_path)
                    except (IOError, UnicodeDecodeError):
                        continue

        return web.json_response({'files': list(matched_files)})

    except json.JSONDecodeError:
        return web.json_response({'error': 'Invalid input'}, status=400)

app = web.Application()
app.router.add_post('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)