import os
import aiohttp
from aiohttp import web
import tempfile
import subprocess

async def concatenate_pdfs(request):
    try:
        reader = await request.multipart()
        files = []

        while True:
            part = await reader.next()
            if part is None:
                break
            if part.name == 'files':
                # Ensure the file is a PDF by checking the content type
                if part.headers.get('Content-Type') != 'application/pdf':
                    return web.json_response({'error': 'All files must be PDFs.'}, status=400)
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=tempfile.gettempdir())
                files.append(temp_file.name)
                while True:
                    chunk = await part.read_chunk()
                    if not chunk:
                        break
                    temp_file.write(chunk)
                temp_file.close()

        if not files:
            return web.json_response({'error': 'Invalid input or missing files.'}, status=400)

        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=tempfile.gettempdir())
        output_file.close()

        try:
            # Use subprocess.run safely by ensuring files are valid PDFs
            subprocess.run(['pdfunite'] + files + [output_file.name], check=True)
        except subprocess.CalledProcessError:
            return web.json_response({'error': 'An error occurred while processing the files.'}, status=500)

        with open(output_file.name, 'rb') as f:
            concatenated_pdf = f.read()

        for file in files:
            os.remove(file)
        os.remove(output_file.name)

        return web.Response(body=concatenated_pdf, content_type='application/pdf')

    except Exception as e:
        return web.json_response({'error': 'An error occurred while processing the files.'}, status=500)

app = web.Application()
app.router.add_post('/concatenate', concatenate_pdfs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)