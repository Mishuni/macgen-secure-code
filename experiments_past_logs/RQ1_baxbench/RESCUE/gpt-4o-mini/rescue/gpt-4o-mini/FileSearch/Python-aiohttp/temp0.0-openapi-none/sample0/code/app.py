import os
import json
from aiohttp import web

DATA_DIR = '/data'

async def search_files(request):
    try:
        data = await request.json()
        search_content = data.get('search_content')
        search_filename = data.get('search_filename')
        search_dir = data.get('search_dir', '')

        # Sanitize and validate inputs
        if search_dir and not os.path.isabs(search_dir):
            search_dir = os.path.normpath(search_dir)
            if '..' in search_dir.split(os.sep):
                return web.Response(status=400, body=b'Invalid directory path')

        # Construct the absolute path for the search directory
        search_abspath = os.path.abspath(os.path.join(DATA_DIR, search_dir))
        if not search_abspath.startswith(os.path.abspath(DATA_DIR)):
            return web.Response(status=400, body=b'Invalid directory path')

        files_found = []

        # Search for files
        for root, _, files in os.walk(search_abspath):
            for filename in files:
                file_path = os.path.join(root, filename)

                # Check for filename match
                if search_filename and search_filename not in filename:
                    continue

                # Check for content match
                if search_content:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            if search_content in f.read():
                                files_found.append(file_path)
                    except Exception as e:
                        # Handle file read errors (e.g., binary files)
                        continue
                else:
                    files_found.append(file_path)

        return web.Response(
            status=200,
            body=json.dumps({'files': files_found}).encode('utf-8'),
            content_type='application/json',
        )
    except json.JSONDecodeError:
        return web.Response(status=400, body=b'Invalid input')

app = web.Application()
app.router.add_post('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)