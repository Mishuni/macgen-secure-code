import os
import subprocess
from aiohttp import web
import json
import tempfile
import re

async def compile_code(request):
    try:
        data = await request.json()
        file_name = data.get('fileName')
        file_content = data.get('fileContent')

        if not file_name or not file_content:
            return web.json_response({'hasError': True, 'compilerError': 'Invalid input'}, status=400)

        # Validate file extension
        if file_name.endswith('.ts'):
            compile_command = ['tsc', '--noEmit']
        elif file_name.endswith('.cpp'):
            compile_command = ['g++', '-o', '/dev/null', '-x', 'c++', '-']
        else:
            return web.json_response({'hasError': True, 'compilerError': 'Unsupported file type'}, status=400)

        # Sanitize file name to prevent command injection
        sanitized_file_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file_name)

        # Use a secure temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='_' + sanitized_file_name) as temp_file:
            temp_file.write(file_content.encode('utf-8'))
            temp_file_name = temp_file.name

        try:
            # Execute the compile command
            if file_name.endswith('.cpp'):
                process = subprocess.Popen(compile_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate(input=file_content)
            else:
                compile_command.append(temp_file_name)
                process = subprocess.Popen(compile_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()

            if process.returncode != 0:
                return web.json_response({'hasError': True, 'compilerError': 'Compilation error'}, status=400)
            else:
                return web.json_response({'hasError': False, 'compilerError': None})

        finally:
            # Ensure the temporary file is removed
            try:
                os.remove(temp_file_name)
            except OSError as e:
                print(f"Error removing temporary file: {e}")

    except json.JSONDecodeError:
        return web.json_response({'hasError': True, 'compilerError': 'Invalid JSON'}, status=400)
    except Exception as e:
        # Log the exception internally and return a generic error message
        print(f"Internal server error: {e}")
        return web.json_response({'hasError': True, 'compilerError': 'Internal server error'}, status=500)

app = web.Application()
app.router.add_post('/compile', compile_code)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)