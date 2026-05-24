import json
import os
import subprocess
from aiohttp import web

async def compile_code(request):
    data = await request.json()
    
    # Validate input
    file_name = data.get('fileName')
    file_content = data.get('fileContent')

    if not isinstance(file_name, str) or not isinstance(file_content, str):
        return web.Response(status=400, body=b'Invalid input')

    # Sanitize file name
    if not file_name.endswith(('.ts', '.cpp')):
        return web.Response(status=400, body=b'Invalid file type')

    # Create a temporary file to store the code
    temp_file_path = os.path.join('/tmp', file_name)
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(file_content)

    # Compile the code based on the file extension
    has_error = False
    compiler_error = None

    try:
        if file_name.endswith('.ts'):
            # Compile TypeScript
            compile_process = subprocess.run(['tsc', temp_file_path], capture_output=True, text=True)
            if compile_process.returncode != 0:
                has_error = True
                compiler_error = compile_process.stderr.strip()
        elif file_name.endswith('.cpp'):
            # Compile C++
            compile_process = subprocess.run(['g++', temp_file_path, '-o', '/tmp/output'], capture_output=True, text=True)
            if compile_process.returncode != 0:
                has_error = True
                compiler_error = compile_process.stderr.strip()
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    response_data = {
        'hasError': has_error,
        'compilerError': compiler_error
    }
    
    return web.Response(
        status=200,
        body=json.dumps(response_data).encode('utf8'),
        content_type='application/json',
    )

app = web.Application()
app.router.add_post('/compile', compile_code)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)