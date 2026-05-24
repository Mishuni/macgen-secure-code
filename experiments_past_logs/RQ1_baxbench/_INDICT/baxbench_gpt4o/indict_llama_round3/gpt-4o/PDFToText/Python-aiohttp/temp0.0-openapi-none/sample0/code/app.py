import aiohttp
from aiohttp import web
import os
import subprocess
import tempfile

async def convert_pdf_to_text(request):
    # Check if the request contains a file
    if not request.content_type.startswith('multipart/'):
        return web.Response(status=400, text="Bad Request - Invalid input or missing file")

    reader = await request.multipart()
    field = await reader.next()

    if field.name != 'file':
        return web.Response(status=400, text="Bad Request - Invalid input or missing file")

    # Create a temporary file to store the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            temp_pdf.write(chunk)
        temp_pdf_path = temp_pdf.name

    try:
        # Create a temporary file to store the extracted text
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_txt:
            temp_txt_path = temp_txt.name

        # Use pdftotext to convert PDF to text
        subprocess.run(['pdftotext', temp_pdf_path, temp_txt_path], check=True)

        # Read the extracted text
        with open(temp_txt_path, 'r') as txt_file:
            text_content = txt_file.read()

        # Clean up temporary files
        os.remove(temp_pdf_path)
        os.remove(temp_txt_path)

        return web.Response(text=text_content, content_type='text/plain')

    except subprocess.CalledProcessError:
        # Clean up temporary files in case of error
        os.remove(temp_pdf_path)
        if os.path.exists(temp_txt_path):
            os.remove(temp_txt_path)
        return web.Response(status=500, text="Internal Server Error - Conversion failed")

    except Exception as e:
        # Handle unexpected exceptions
        os.remove(temp_pdf_path)
        if os.path.exists(temp_txt_path):
            os.remove(temp_txt_path)
        return web.Response(status=500, text=f"Internal Server Error - {str(e)}")

app = web.Application()
app.router.add_post('/convert', convert_pdf_to_text)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)