import aiohttp
from aiohttp import web
import subprocess
import tempfile
import os

async def convert_pdf_to_text(request):
    if 'file' not in request.post():
        return web.json_response({'error': 'Missing file'}, status=400)

    pdf_file = request.post()['file']
    
    # Create a secure temporary file for the PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        temp_pdf.write(await pdf_file.read())
        temp_pdf_path = temp_pdf.name

    try:
        # Define the output text file path
        temp_text_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        temp_text_file.close()  # Close the file to allow pdftotext to write to it

        # Call pdftotext to convert the PDF to text
        result = subprocess.run(['pdftotext', temp_pdf_path, temp_text_file.name], capture_output=True, text=True)

        if result.returncode != 0:
            return web.json_response({'error': 'Conversion failed'}, status=500)

        # Read the converted text
        with open(temp_text_file.name, 'r') as f:
            converted_text = f.read()

        return web.Response(text=converted_text, content_type='text/plain')

    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

    finally:
        # Clean up temporary files
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        if os.path.exists(temp_text_file.name):
            os.remove(temp_text_file.name)

app = web.Application()
app.router.add_post('/convert', convert_pdf_to_text)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)