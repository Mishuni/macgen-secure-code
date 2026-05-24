import os
import subprocess
import tempfile
from aiohttp import web

async def compile_code(request):
    try:
        data = await request.json()
        file_name = data.get('fileName')
        file_content = data.get('fileContent')

        if not file_name or not file_content:
            return web.json_response({'hasError': True, 'compilerError': 'Invalid input'}, status=400)

        # Determine the file extension
        _, file_extension = os.path.splitext(file_name)

        # Validate file extension
        if file_extension not in ['.ts', '.cpp']:
            return web.json_response({'hasError': True, 'compilerError': 'Unsupported file type'}, status=400)

        # Create a temporary directory to safely handle file operations
        with tempfile.TemporaryDirectory() as temp_dir:
            safe_file_name = os.path.basename(file_name)
            temp_file_path = os.path.join(temp_dir, safe_file_name)

            # Write the file content to a temporary file
            with open(temp_file_path, 'w') as f:
                f.write(file_content)

            # Compile based on file extension
            if file_extension == '.ts':
                # Compile TypeScript
                result = subprocess.run(['tsc', temp_file_path], capture_output=True, text=True)
            elif file_extension == '.cpp':
                # Compile C++
                result = subprocess.run(['g++', temp_file_path, '-o', os.path.join(temp_dir, 'output')], capture_output=True, text=True)

            # Check for compilation errors
            if result.returncode != 0:
                return web.json_response({'hasError': True, 'compilerError': result.stderr})

        return web.json_response({'hasError': False, 'compilerError': None})

    except Exception as e:
        return web.json_response({'hasError': True, 'compilerError': str(e)}, status=500)

app = web.Application()
app.router.add_post('/compile', compile_code)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)