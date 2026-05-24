import os
import re
import subprocess
from aiohttp import web

SAFE_DIR = '/tmp/safe_directory'

# Ensure the safe directory exists
os.makedirs(SAFE_DIR, exist_ok=True)

async def compile_code(request):
    try:
        data = await request.json()
        file_name = data.get('fileName')
        file_content = data.get('fileContent')

        # Validate file name
        if not file_name or not re.match(r'^[\w\-]+\.(ts|cpp)$', file_name):
            return web.json_response({'hasError': True, 'compilerError': 'Invalid file name'}, status=400)

        # Determine file path
        file_path = os.path.join(SAFE_DIR, file_name)

        # Write file content to the safe directory
        with open(file_path, 'w') as f:
            f.write(file_content)

        # Determine the compiler based on file extension
        if file_name.endswith('.ts'):
            result = subprocess.run(['tsc', file_path], capture_output=True, text=True, shell=False)
        elif file_name.endswith('.cpp'):
            result = subprocess.run(['g++', file_path, '-o', os.path.join(SAFE_DIR, 'output')], capture_output=True, text=True, shell=False)
        else:
            return web.json_response({'hasError': True, 'compilerError': 'Unsupported file type'}, status=400)

        # Check for compilation errors
        if result.returncode != 0:
            return web.json_response({'hasError': True, 'compilerError': result.stderr.strip()})

        return web.json_response({'hasError': False, 'compilerError': None})

    except Exception as e:
        return web.json_response({'hasError': True, 'compilerError': str(e)}, status=500)

app = web.Application()
app.router.add_post('/compile', compile_code)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)