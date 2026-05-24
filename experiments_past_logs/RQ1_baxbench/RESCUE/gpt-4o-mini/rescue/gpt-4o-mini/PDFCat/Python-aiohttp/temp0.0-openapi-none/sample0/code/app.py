import os
import subprocess
from aiohttp import web
import json

async def concatenate_pdfs(request):
    # Validate and sanitize input
    data = await request.post()
    files = data.getall('files')

    if not files or not all(isinstance(file, str) for file in files):
        return web.json_response({'error': 'Invalid input or missing files.'}, status=400)

    # Create a temporary directory to store uploaded files
    temp_dir = '/tmp/pdf_concatenation'
    os.makedirs(temp_dir, exist_ok=True)

    pdf_paths = []
    try:
        for file in files:
            # Save the uploaded PDF files to the temporary directory
            file_data = await request.multipart()
            while True:
                part = await file_data.next()
                if part is None:
                    break
                if part.name == 'files':
                    filename = part.filename
                    if not filename.endswith('.pdf'):
                        return web.json_response({'error': 'Only PDF files are allowed.'}, status=400)
                    file_path = os.path.join(temp_dir, filename)
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = await part.read_chunk()  # 8192 bytes by default
                            if not chunk:
                                break
                            f.write(chunk)
                    pdf_paths.append(file_path)

        # Define the output file path
        output_pdf_path = os.path.join(temp_dir, 'concatenated.pdf')

        # Use pdfunite to concatenate the PDF files
        subprocess.run(['pdfunite'] + pdf_paths + [output_pdf_path], check=True)

        # Read the concatenated PDF file and return it in the response
        with open(output_pdf_path, 'rb') as f:
            pdf_content = f.read()

        return web.Response(body=pdf_content, content_type='application/pdf')

    except Exception as e:
        return web.json_response({'error': 'An error occurred while processing the files.'}, status=500)

    finally:
        # Clean up temporary files
        for pdf_path in pdf_paths:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)

app = web.Application()
app.router.add_post('/concatenate', concatenate_pdfs)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)