import os
import re
from aiohttp import web

async def search_files(request):
    try:
        regex_pattern = request.query.get('regex')
        directory = request.query.get('directory', '')
        recursive = request.query.get('recursive', 'false').lower() == 'true'

        if not regex_pattern:
            return web.json_response({'error': 'Regex pattern is required'}, status=400)

        try:
            regex = re.compile(regex_pattern)
        except re.error:
            return web.json_response({'error': 'Malformed regex pattern'}, status=400)

        # Ensure the directory path is safe and within the allowed root
        root_dir = os.path.abspath(os.path.join('.', 'files'))
        search_dir = os.path.abspath(os.path.join(root_dir, directory))
        if not search_dir.startswith(root_dir):
            return web.json_response({'error': 'Directory traversal attempt detected'}, status=400)

        if not os.path.exists(search_dir) or not os.path.isdir(search_dir):
            return web.json_response({'error': 'Directory does not exist or is not accessible'}, status=400)

        matching_files = []
        for root, _, files in os.walk(search_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if regex.search(content):
                            relative_path = os.path.relpath(file_path, search_dir)
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