import os
import tempfile
import shutil
import subprocess
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_exceptions import HTTPBadRequest, HTTPInternalServerError

async def handle_concatenate(request: Request) -> Response:
    # Validate incoming request
    if not request.content_type.startswith('multipart/form-data'):
        raise HTTPBadRequest(reason="Invalid content type")

    reader = await request.multipart()
    files = []

    # Save uploaded files temporarily
    try:
        while True:
            part = await reader.next()
            if part is None:
                break
            if part.name == 'files':
                filename = part.filename
                if not filename or '..' in filename:
                    raise HTTPBadRequest(reason="Invalid file name")
                
                # Create a secure temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                files.append(temp_file.name)
                
                # Write file content to the temporary file
                while True:
                    chunk = await part.read_chunk()
                    if not chunk:
                        break
                    temp_file.write(chunk)
                temp_file.close()

        if not files:
            raise HTTPBadRequest(reason="No files uploaded")

        # Concatenate PDF files using pdfunite
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_file.close()
        try:
            subprocess.run(['pdfunite'] + files + [output_file.name], check=True)
        except subprocess.CalledProcessError:
            raise HTTPInternalServerError(reason="Failed to concatenate PDF files")

        # Return the concatenated PDF
        return web.FileResponse(output_file.name, headers={'Content-Type': 'application/pdf'})

    except Exception as e:
        raise HTTPInternalServerError(reason=str(e))

    finally:
        # Clean up temporary files
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass

        try:
            os.remove(output_file.name)
        except OSError:
            pass

app = web.Application()
app.router.add_post('/concatenate', handle_concatenate)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)