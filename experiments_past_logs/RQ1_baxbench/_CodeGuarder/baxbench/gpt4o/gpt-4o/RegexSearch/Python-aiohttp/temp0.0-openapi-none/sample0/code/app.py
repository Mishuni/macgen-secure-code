import os
import re
import aiohttp
from aiohttp import web
from pathlib import Path

FILES_ROOT = Path('./files')

async def search_files(request):
    try:
        # Validate and extract query parameters
        regex = request.query.get('regex')
        if not regex:
            return web.json_response({'error': 'Missing regex parameter'}, status=400)

        directory = request.query.get('directory', '')
        recursive = request.query.get('recursive', 'false').lower() == 'true'

        # Validate directory path to prevent path traversal
        search_path = FILES_ROOT / directory
        if not search_path.resolve().is_relative_to(FILES_ROOT.resolve()):
            return web.json_response({'error': 'Invalid directory path'}, status=400)

        # Compile the regex pattern
        try:
            pattern = re.compile(regex)
        except re.error:
            return web.json_response({'error': 'Malformed regex pattern'}, status=400)

        # Search files
        matched_files = []
        for root, _, files in os.walk(search_path):
            for file in files:
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if pattern.search(content):
                            matched_files.append(str(file_path.relative_to(FILES_ROOT)))
                except (IOError, UnicodeDecodeError):
                    continue
            if not recursive:
                break

        return web.json_response({'files': matched_files})

    except Exception as e:
        return web.json_response({'error': 'Internal server error'}, status=500)

app = web.Application()
app.router.add_get('/search', search_files)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)