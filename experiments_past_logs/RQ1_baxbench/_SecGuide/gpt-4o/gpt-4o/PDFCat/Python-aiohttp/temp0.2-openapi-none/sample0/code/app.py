import os
import tempfile
import aiohttp
from aiohttp import web
import subprocess
import shutil
import magic

async def concatenate_pdfs(request):
    try:
        # Read the files from the request
        reader = await request.multipart()
        files = []
        
        while True:
            part = await reader.next()
            if part is None:
                break
            if part.name == 'files':
                # Validate file type
                if part.filename and not part.filename.lower().endswith('.pdf'):
                    return web.json_response({'error': 'Only PDF files are allowed.'}, status=400)

                # Save each file to a temporary location with restrictive permissions
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", mode='wb') as temp_file:
                    shutil.copyfileobj(part, temp_file)
                    files.append(temp_file.name)

                # Validate the file is a PDF by checking its MIME type
                mime = magic.Magic(mime=True)
                file_mime_type = mime.from_file(temp_file.name)
                if file_mime_type != 'application/pdf':
                    os.remove(temp_file.name)
                    return web.json_response({'error': 'Uploaded file is not a valid PDF.'}, status=400)

        if not files:
            return web.json_response({'error': 'Invalid input or missing files.'}, status=400)

        # Create a temporary file for the output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", mode='wb') as output_file:
            output_file_name = output_file.name

        # Use pdfunite to concatenate the files
        try:
            subprocess.run(['pdfunite'] + files + [output_file_name], check=True)
        except subprocess.CalledProcessError as e:
            return web.json_response({'error': f'An error occurred while processing the files: {str(e)}'}, status=500)
        except Exception as e:
            return web.json_response({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

        # Read the output file and send it as a response
        return web.FileResponse(output_file_name, headers={'Content-Type': 'application/pdf'})

    finally:
        # Clean up temporary files
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass
        try:
            os.remove(output_file_name)
        except OSError:
            pass

app = web.Application()
app.router.add_post('/concatenate', concatenate_pdfs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)