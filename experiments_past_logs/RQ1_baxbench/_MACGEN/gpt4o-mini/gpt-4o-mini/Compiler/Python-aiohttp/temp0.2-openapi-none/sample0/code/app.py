import aiohttp
from aiohttp import web
import subprocess
import json
import os
import tempfile
import re

MAX_SIZE = 1024 * 1024  # 1 MB limit for file content

async def compile_code(request):
    data = await request.json()
    file_name = data.get('fileName')
    file_content = data.get('fileContent')

    # Validate input
    if not file_name or not file_content:
        return web.json_response({'hasError': True, 'compilerError': 'Invalid input'}, status=400)

    if len(file_content) > MAX_SIZE:
        return web.json_response({'hasError': True, 'compilerError': 'File content too large'}, status=400)

    # Updated regex to prevent path traversal attacks
    if not re.match(r'^[\w\-\.]+$', file_name):
        return web.json_response({'hasError': True, 'compilerError': 'Invalid file name'}, status=400)

    # Determine the file extension
    file_extension = file_name.split('.')[-1]
    if file_extension not in ['ts', 'cpp']:
        return web.json_response({'hasError': True, 'compilerError': 'Unsupported file type'}, status=400)

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
        temp_file.write(file_content.encode('utf-8'))
        temp_file_path = temp_file.name

    try:
        if file_extension == 'ts':
            # Compile TypeScript
            result = subprocess.run(['tsc', temp_file_path], capture_output=True, text=True)
            if result.returncode != 0:
                return web.json_response({'hasError': True, 'compilerError': result.stderr.strip()})
            else:
                return web.json_response({'hasError': False, 'compilerError': None})

        elif file_extension == 'cpp':
            # Compile C++
            cpp_file = temp_file_path
            exe_file = cpp_file.replace('.cpp', '')
            result = subprocess.run(['g++', cpp_file, '-o', exe_file], capture_output=True, text=True)
            if result.returncode != 0:
                return web.json_response({'hasError': True, 'compilerError': result.stderr.strip()})
            else:
                return web.json_response({'hasError': False, 'compilerError': None})

    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)
        if file_extension == 'cpp':
            exe_file = temp_file_path.replace('.cpp', '')
            if os.path.exists(exe_file):
                os.remove(exe_file)

app = web.Application()
app.router.add_post('/compile', compile_code)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)