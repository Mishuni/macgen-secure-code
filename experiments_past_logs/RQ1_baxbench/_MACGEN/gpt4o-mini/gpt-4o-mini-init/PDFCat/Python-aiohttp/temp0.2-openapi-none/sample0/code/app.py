import aiohttp
from aiohttp import web
import subprocess
import os
import tempfile

async def concatenate_pdfs(request):
    # Check if files are provided
    data = await request.post()
    files = data.getall('files')
    if not files:
        return web.json_response({'error': 'Invalid input or missing files.'}, status=400)
    
    # Limit the number of uploaded files
    if len(files) > 10:  # Example limit
        return web.json_response({'error': 'Too many files uploaded.'}, status=400)
    
    # Create a temporary directory to store uploaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_files = []
        for file in files:
            # Validate filename
            filename = os.path.basename(file.filename)
            if not filename.endswith('.pdf'):
                return web.json_response({'error': 'Invalid file type.'}, status=400)
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(await file.read())
            pdf_files.append(file_path)
        
        # Prepare the output file path
        output_file = os.path.join(temp_dir, 'concatenated.pdf')
        
        # Use safe command execution
        command = ['pdfunite'] + pdf_files + [output_file]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            return web.json_response({'error': 'An error occurred while processing the files.'}, status=500)
        
        # Return the concatenated PDF
        return web.FileResponse(output_file, media_type='application/pdf')

app = web.Application()
app.router.add_post('/concatenate', concatenate_pdfs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)