import os
from aiohttp import web

async def search_files(request):
    try:
        data = await request.json()
    except Exception:
        return web.json_response({'error': 'Invalid input'}, status=400)

    search_content = data.get('search_content')
    search_filename = data.get('search_filename')
    search_dir = data.get('search_dir', '')

    if not (search_content or search_filename):
        return web.json_response({'error': 'Invalid input'}, status=400)

    base_dir = '/data'
    search_path = os.path.join(base_dir, search_dir.lstrip('/'))

    # Ensure the search path is within the base directory to prevent directory traversal
    if not os.path.commonpath([base_dir, search_path]).startswith(base_dir):
        return web.json_response({'error': 'Invalid directory path'}, status=400)

    if not os.path.exists(search_path):
        return web.json_response({'files': []})

    matching_files = []

    for root, _, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)
            if search_filename and file == search_filename:
                matching_files.append(file_path)
            elif search_content:
                try:
                    # Check file size before reading to prevent large file issues
                    if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10 MB limit
                        continue
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        if search_content in f.read():
                            matching_files.append(file_path)
                except Exception:
                    continue

    return web.json_response({'files': matching_files})

app = web.Application()
app.router.add_post('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)