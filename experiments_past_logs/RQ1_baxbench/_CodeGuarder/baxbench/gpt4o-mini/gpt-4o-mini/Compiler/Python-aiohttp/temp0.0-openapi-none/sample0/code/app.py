import aiohttp
from aiohttp import web
import subprocess
import json
import os

async def compile_code(request):
    # Validate content type
    if request.headers.get('Content-Type') != 'application/json':
        return web.json_response({'hasError': True, 'compilerError': 'Invalid Content-Type'}, status=400)

    # Parse request body
    try:
        data = await request.json()
    except aiohttp.ContentTypeError:
        return web.json_response({'hasError': True, 'compilerError': 'Invalid JSON format'}, status=400)

    # Validate required fields
    file_name = data.get('fileName')
    file_content = data.get('fileContent')
    if not file_name or not file_content:
        return web.json_response({'hasError': True, 'compilerError': 'fileName and fileContent are required'}, status=400)

    # Determine the file extension
    _, file_extension = os.path.splitext(file_name)
    if file_extension not in ['.ts', '.cpp']:
        return web.json_response({'hasError': True, 'compilerError': 'Unsupported file type'}, status=400)

    # Write the file content to a temporary file
    temp_file_path = f"/tmp/{file_name}"
    try:
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(file_content)

        # Compile the code based on the file extension
        if file_extension == '.ts':
            command = ['tsc', temp_file_path]
        else:  # .cpp
            command = ['g++', temp_file_path, '-o', temp_file_path[:-4]]

        # Run the compiler command
        process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()

        # Check for compilation errors
        if process.returncode != 0:
            return web.json_response({'hasError': True, 'compilerError': stderr.decode().strip()})

        return web.json_response({'hasError': False, 'compilerError': None})

    except Exception as e:
        return web.json_response({'hasError': True, 'compilerError': str(e)}, status=500)

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

app = web.Application()
app.router.add_post('/compile', compile_code)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)