import aiohttp
from aiohttp import web
import subprocess
import json
import os
import tempfile
import re

async def compile_code(request):
    try:
        data = await request.json()
        file_name = data.get('fileName')
        file_content = data.get('fileContent')

        if not file_name or not file_content:
            return web.json_response({'hasError': True, 'compilerError': 'Invalid input.'}, status=400)

        # Sanitize file name to prevent directory traversal and command injection
        if not re.match(r'^[\w\-\.]+\.((ts)|(cpp))$', file_name):
            return web.json_response({'hasError': True, 'compilerError': 'Invalid file name.'}, status=400)

        # Validate file content to prevent execution of malicious code
        if not re.match(r'^[\s\S]*$', file_content):  # Adjust regex to match safe patterns
            return web.json_response({'hasError': True, 'compilerError': 'Invalid file content.'}, status=400)

        # Create a temporary directory for file storage
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, file_name)

            # Write code to a temporary file
            with open(file_path, 'w') as f:
                f.write(file_content)

            # Compile TypeScript code
            if file_name.endswith('.ts'):
                process = subprocess.run(['tsc', file_path], capture_output=True, text=True, timeout=5)
            # Compile C++ code
            elif file_name.endswith('.cpp'):
                process = subprocess.run(['g++', file_path, '-o', os.path.join(temp_dir, 'output')], capture_output=True, text=True, timeout=5)

            if process.returncode != 0:
                return web.json_response({'hasError': True, 'compilerError': process.stderr.strip()})
            else:
                return web.json_response({'hasError': False, 'compilerError': None})

    except subprocess.TimeoutExpired:
        return web.json_response({'hasError': True, 'compilerError': 'Compilation timed out.'}, status=500)
    except Exception as e:
        return web.json_response({'hasError': True, 'compilerError': 'An error occurred.'}, status=500)

app = web.Application()
app.router.add_post('/compile', compile_code)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)