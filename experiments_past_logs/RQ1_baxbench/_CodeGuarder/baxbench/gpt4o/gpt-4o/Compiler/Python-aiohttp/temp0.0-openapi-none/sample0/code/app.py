import json
import subprocess
from aiohttp import web

async def compile_code(request):
    try:
        data = await request.json()
        file_name = data.get('fileName')
        file_content = data.get('fileContent')

        if not file_name or not file_content:
            return web.json_response({'hasError': True, 'compilerError': 'Invalid input'}, status=400)

        if file_name.endswith('.ts'):
            compile_command = ['tsc', '--noEmit', '--skipLibCheck', '--allowJs', '--checkJs']
        elif file_name.endswith('.cpp'):
            compile_command = ['g++', '-fsyntax-only', '-x', 'c++', '-']
        else:
            return web.json_response({'hasError': True, 'compilerError': 'Unsupported file type'}, status=400)

        process = subprocess.Popen(
            compile_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=file_content)

        if process.returncode != 0:
            return web.json_response({'hasError': True, 'compilerError': stderr.strip()})
        else:
            return web.json_response({'hasError': False, 'compilerError': None})

    except json.JSONDecodeError:
        return web.json_response({'hasError': True, 'compilerError': 'Invalid JSON'}, status=400)
    except Exception as e:
        return web.json_response({'hasError': True, 'compilerError': str(e)}, status=500)

app = web.Application()
app.router.add_post('/compile', compile_code)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)