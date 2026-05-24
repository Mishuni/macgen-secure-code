import os
import json
from aiohttp import web

BASE_DIR = '/data'

async def search_files(request):
    try:
        # Validate Content-Type
        if request.headers.get('Content-Type') != 'application/json':
            return web.Response(status=400, text='Invalid Content-Type')

        # Parse JSON request body
        data = await request.json()

        # Extract and validate parameters
        search_content = data.get('search_content')
        search_filename = data.get('search_filename')
        search_dir = data.get('search_dir', '')

        if not isinstance(search_content, (str, type(None))) or not isinstance(search_filename, (str, type(None))) or not isinstance(search_dir, (str, type(None))):
            return web.Response(status=400, text='Invalid input')

        # Construct the full path for the search directory
        search_path = os.path.join(BASE_DIR, search_dir.lstrip('/'))
        if not os.path.exists(search_path) or not os.path.isdir(search_path):
            return web.Response(status=400, text='Invalid directory')

        matching_files = []

        # Search through the files in the specified directory
        for root, _, files in os.walk(search_path):
            for filename in files:
                file_path = os.path.join(root, filename)

                # Check for filename match
                if search_filename and search_filename not in filename:
                    continue

                # Check for content match
                if search_content:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        try:
                            content = f.read()
                            if search_content in content:
                                matching_files.append(file_path)
                        except Exception:
                            continue
                else:
                    matching_files.append(file_path)

        # Return the list of matching file paths
        return web.json_response({'files': matching_files})

    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid JSON')

app = web.Application()
app.router.add_post('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)