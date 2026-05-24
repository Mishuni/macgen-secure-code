
import os
import re
from aiohttp import web

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def search_files(request):
    try:
        regex = request.query.get('regex')
        directory = request.query.get('directory', '')
        recursive = request.query.get('recursive', 'false').lower() == 'true'

        if not regex:
            return web.json_response({'error': 'Regex parameter is required'}, status=400)

        try:
            compiled_regex = re.compile(regex)
        except re.error:
            return web.json_response({'error': 'Invalid regex pattern'}, status=400)

        root_dir = os.path.join('./files', os.path.normpath(directory))
        if not os.path.abspath(root_dir).startswith(os.path.abspath('./files')):
            return web.json_response({'error': 'Invalid directory path'}, status=400)

        if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
            return web.json_response({'error': 'Directory does not exist or is not accessible'}, status=400)

        matching_files = []
        for root, _, files in os.walk(root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    continue
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if compiled_regex.search(content):
                            relative_path = os.path.relpath(file_path, root_dir)
                            matching_files.append(relative_path)
                except (IOError, UnicodeDecodeError):
                    continue
            if not recursive:
                break

        return web.json_response({'files': matching_files}, status=200)

    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

app = web.Application()
app.router.add_get('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)