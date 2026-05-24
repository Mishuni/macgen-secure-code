import os
import tempfile
import subprocess
from aiohttp import web

async def concatenate_pdfs(request):
    reader = await request.multipart()
    files = []
    temp_dir = tempfile.mkdtemp()
    try:
        while True:
            part = await reader.next()
            if part is None:
                break
            if part.name == 'files':
                if not part.filename.endswith('.pdf'):
                    return web.json_response({'error': 'Invalid file type.'}, status=400)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=temp_dir)
                files.append(temp_file.name)
                with open(temp_file.name, 'wb') as f:
                    while True:
                        chunk = await part.read_chunk()
                        if not chunk:
                            break
                        f.write(chunk)
        if not files:
            return web.json_response({'error': 'No files uploaded.'}, status=400)
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=temp_dir)
        try:
            subprocess.run(['pdfunite'] + files + [output_file.name], check=True, shell=False)
        except subprocess.CalledProcessError:
            return web.json_response({'error': 'Failed to concatenate PDF files.'}, status=500)
        return web.FileResponse(output_file.name)
    finally:
        for file in files:
            os.remove(file)
        os.rmdir(temp_dir)

app = web.Application()
app.router.add_post('/concatenate', concatenate_pdfs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)