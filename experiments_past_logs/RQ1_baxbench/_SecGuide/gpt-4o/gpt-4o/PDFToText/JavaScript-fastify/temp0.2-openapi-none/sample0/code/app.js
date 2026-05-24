import os
import tempfile
from fastify import Fastify
from @fastify.multipart import fastifyMultipart
from PyPDF2 import PdfReader

app = Fastify()

# Register the multipart plugin
app.register(fastifyMultipart)

@app.post('/convert')
async def convert_pdf_to_text(request, reply):
    try:
        # Parse the multipart form data
        data = await request.file()
        if not data or data.fieldname != 'file':
            return reply.status(400).send({'error': 'Bad Request - Invalid input or missing file'})

        # Validate file size (e.g., max 5MB)
        max_file_size = 5 * 1024 * 1024  # 5MB
        if data.file.size > max_file_size:
            return reply.status(400).send({'error': 'Bad Request - File too large'})

        # Validate file type (e.g., only allow PDFs)
        if not data.filename.lower().endswith('.pdf'):
            return reply.status(400).send({'error': 'Bad Request - Only PDF files are allowed'})

        # Use a secure method to handle temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            file_path = temp_file.name
            while True:
                chunk = await data.file.read(1024)
                if not chunk:
                    break
                temp_file.write(chunk)

        # Use PyPDF2 to convert PDF to text
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                text_content = ''
                for page in reader.pages:
                    text_content += page.extract_text() or ''
        except Exception:
            return reply.status(500).send({'error': 'Internal Server Error - Conversion failed'})

        # Clean up temporary files
        os.remove(file_path)

        # Return the text content
        return reply.type('text/plain').send(text_content)

    except Exception as e:
        return reply.status(500).send({'error': 'Internal Server Error - An unexpected error occurred'})

if __name__ == '__main__':
    app.listen(5000, '127.0.0.1')