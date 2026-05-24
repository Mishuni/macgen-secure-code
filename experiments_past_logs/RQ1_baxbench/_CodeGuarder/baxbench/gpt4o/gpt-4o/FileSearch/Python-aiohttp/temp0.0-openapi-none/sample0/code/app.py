import os
import aiohttp
from aiohttp import web
import json

# Constants
DATA_DIR = '/data'

# Helper function to validate and sanitize user input
def sanitize_input(input_str):
    if input_str is None:
        return None
    return input_str.replace('..', '').strip('/')

# Helper function to search files
async def search_files(search_content, search_filename, search_dir):
    result_files = []
    base_path = os.path.join(DATA_DIR, sanitize_input(search_dir) or '')

    # Ensure the base path is within the DATA_DIR
    if not os.path.abspath(base_path).startswith(os.path.abspath(DATA_DIR)):
        raise ValueError("Invalid search directory")

    for root, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            if search_filename and search_filename in file:
                result_files.append(file_path)
            elif search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        if search_content in f.read():
                            result_files.append(file_path)
                except Exception as e:
                    continue
    return result_files

# Request handler
async def handle_search(request):
    try:
        data = await request.json()
        search_content = data.get('search_content')
        search_filename = data.get('search_filename')
        search_dir = data.get('search_dir')

        if not (search_content or search_filename):
            return web.json_response({'error': 'Invalid input'}, status=400)

        files = await search_files(search_content, search_filename, search_dir)
        return web.json_response({'files': files}, status=200)

    except json.JSONDecodeError:
        return web.json_response({'error': 'Invalid JSON'}, status=400)
    except ValueError as ve:
        return web.json_response({'error': str(ve)}, status=400)
    except Exception as e:
        return web.json_response({'error': 'Internal server error'}, status=500)

# Main function to set up the web server
def main():
    app = web.Application()
    app.router.add_post('/search', handle_search)
    web.run_app(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()