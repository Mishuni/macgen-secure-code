import aiohttp
from aiohttp import web
import os
import subprocess
import tempfile

async def concatenate_pdfs(request):
    # Check if the request has files
    data = await request.post()
    if 'files' not in data or not data['files']:
        return web.json_response({'error': 'Invalid input or missing files.'}, status=400)

    # Create a temporary directory to store uploaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_files = data['files']
        
        # Save uploaded files to the temporary directory
        file_paths = []
        for i, pdf_file in enumerate(pdf_files):
            # Validate file type
            if not pdf_file.filename.lower().endswith('.pdf'):
                return web.json_response({'error': 'Only PDF files are allowed.'}, status=400)
            
            file_path = os.path.join(temp_dir, f'file_{i}.pdf')
            with open(file_path, 'wb') as f:
                f.write(await pdf_file.read())
            file_paths.append(file_path)

        # Define the output file path
        output_file_path = os.path.join(temp_dir, 'concatenated.pdf')

        # Use pdfunite to concatenate the PDF files
        try:
            subprocess.run(['pdfunite'] + file_paths + [output_file_path], check=True)
        except subprocess.CalledProcessError:
            return web.json_response({'error': 'An error occurred while processing the files.'}, status=500)

        # Read the concatenated PDF file and return it in the response
        with open(output_file_path, 'rb') as f:
            pdf_data = f.read()

        return web.Response(body=pdf_data, content_type='application/pdf')

app = web.Application()
app.router.add_post('/concatenate', concatenate_pdfs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)