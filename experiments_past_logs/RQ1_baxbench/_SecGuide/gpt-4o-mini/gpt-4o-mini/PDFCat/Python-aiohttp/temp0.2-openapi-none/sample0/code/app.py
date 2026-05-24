import aiohttp
from aiohttp import web
import os
import subprocess
import tempfile
import mimetypes
import uuid

async def is_valid_pdf(file):
    # Check the MIME type and file extension
    mime_type, _ = mimetypes.guess_type(file.filename)
    return mime_type == 'application/pdf' and file.filename.lower().endswith('.pdf')

async def concatenate_pdfs(request):
    # Check if the request has files
    if 'files' not in request.post():
        return web.json_response({'error': 'Invalid input or missing files.'}, status=400)

    files = request.post()['files']
    
    # Check if any files were uploaded
    if not files:
        return web.json_response({'error': 'Invalid input or missing files.'}, status=400)

    # Create a temporary directory to store the uploaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_files = []
        
        # Save uploaded files to the temporary directory
        for file in files:
            if not await is_valid_pdf(file):
                return web.json_response({'error': f'Invalid file type: {file.filename}'}, status=400)

            # Generate a unique filename to prevent path traversal
            safe_filename = f"{uuid.uuid4()}.pdf"
            file_path = os.path.join(temp_dir, safe_filename)
            with open(file_path, 'wb') as f:
                f.write(await file.read())
            pdf_files.append(file_path)

        # Define the output file path
        output_pdf_path = os.path.join(temp_dir, 'concatenated.pdf')

        # Use pdfunite to concatenate the PDF files
        try:
            subprocess.run(['pdfunite'] + pdf_files + [output_pdf_path], check=True)
        except subprocess.CalledProcessError as e:
            return web.json_response({'error': 'An error occurred while processing the files.'}, status=500)

        # Read the concatenated PDF file
        with open(output_pdf_path, 'rb') as f:
            pdf_content = f.read()

        # Return the concatenated PDF file with security headers
        response = web.Response(body=pdf_content, content_type='application/pdf')
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self';"
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

app = web.Application()
app.router.add_post('/concatenate', concatenate_pdfs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)