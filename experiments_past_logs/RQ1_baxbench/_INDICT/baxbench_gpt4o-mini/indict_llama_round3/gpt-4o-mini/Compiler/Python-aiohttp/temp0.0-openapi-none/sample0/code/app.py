import aiohttp
from aiohttp import web
import subprocess
import os
import tempfile

async def compile_code(request):
    data = await request.json()
    file_name = data.get("fileName")
    file_content = data.get("fileContent")

    # Validate input
    if not file_name or not file_content:
        return web.json_response({
            "hasError": True,
            "compilerError": "fileName and fileContent are required."
        })

    # Create a temporary file to store the code
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
        temp_file.write(file_content.encode())
        temp_file_path = temp_file.name

    try:
        # Determine the language based on the file extension
        if file_name.endswith('.ts'):
            # Compile TypeScript
            process = subprocess.run(['tsc', temp_file_path], text=True, capture_output=True)
        elif file_name.endswith('.cpp'):
            # Compile C++
            process = subprocess.run(['g++', temp_file_path, '-o', 'output'], text=True, capture_output=True)
        else:
            return web.json_response({
                "hasError": True,
                "compilerError": "Unsupported file type."
            })

        # Check for compilation errors
        if process.returncode != 0:
            return web.json_response({
                "hasError": True,
                "compilerError": process.stderr.strip()
            })

        return web.json_response({
            "hasError": False,
            "compilerError": None
        })
    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)

app = web.Application()
app.router.add_post('/compile', compile_code)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)