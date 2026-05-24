
import os
import subprocess
import tempfile
from aiohttp import web

async def handle_convert(request):
    reader = await request.multipart()
    field = await reader.next()
    
    if field is None or field.name != 'file':
        return web.Response(status=400, text="Bad Request - Missing file")
    
    # Create a temporary file to store the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            temp_pdf.write(chunk)
        temp_pdf_path = temp_pdf.name
    
    try:
        # Validate if the file is a valid PDF
        if not is_valid_pdf(temp_pdf_path):
            return web.Response(status=400, text="Bad Request - Invalid PDF file")
        
        # Convert PDF to text using pdftotext
        result = subprocess.run(['pdftotext', temp_pdf_path, '-'], capture_output=True, text=True, check=True)
        return web.Response(status=200, text=result.stdout)
    
    except subprocess.CalledProcessError:
        return web.Response(status=500, text="Internal Server Error - Conversion failed")
    
    finally:
        # Ensure the temporary file is removed
        os.remove(temp_pdf_path)

def is_valid_pdf(file_path):
    # Check the magic number for PDF files
    with open(file_path, 'rb') as f:
        return f.read(4) == b'%PDF'

app = web.Application()
app.router.add_post('/convert', handle_convert)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)