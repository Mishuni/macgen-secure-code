import os
import subprocess
from aiohttp import web

async def concatenate_pdfs(request):
    # Validate input
    if 'files' not in request.post() or not request.post()['files']:
        return web.json_response({'error': 'Invalid input or missing files.'}, status=400)

    files = request.post()['files']
    
    # Limit the number of files to prevent resource exhaustion
    if len(files) > 10:
        return web.json_response({'error': 'Too many files. Maximum allowed is 10.'}, status=400)

    pdf_file_paths = []
    try:
        for file in files:
            # Save the uploaded files to a temporary location
            file_path = f"/tmp/{file.filename}"
            with open(file_path, 'wb') as f:
                f.write(await file.read())
            pdf_file_paths.append(file_path)

        # Define the output file path
        output_file_path = "/tmp/concatenated.pdf"

        # Use pdfunite to concatenate the PDF files
        command = ['pdfunite'] + pdf_file_paths + [output_file_path]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            return web.json_response({'error': 'An error occurred while processing the files.'}, status=500)

        # Return the concatenated PDF file
        with open(output_file_path, 'rb') as f:
            response = web.Response(body=f.read(), content_type='application/pdf')
            response.headers['Content-Disposition'] = 'attachment; filename="concatenated.pdf"'
            return response

    except Exception as e:
        return web.json_response({'error': 'An error occurred while processing the files.'}, status=500)

    finally:
        # Clean up temporary files
        for file_path in pdf_file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

app = web.Application()
app.router.add_post('/concatenate', concatenate_pdfs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)