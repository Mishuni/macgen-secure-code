import os
import subprocess
import tempfile
from fastify import Fastify
from fastify.multipart import Multipart

app = Fastify()

@app.post('/convert')
async def convert_pdf_to_text(request, reply):
    try:
        # Parse the multipart form data
        data = await request.multipart()
        file = None

        # Extract the file from the form data
        async for field in data:
            if field.name == 'file':
                file = field
                break

        if not file:
            return reply.status(400).send({'error': 'Bad Request - Invalid input or missing file'})

        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        # Validate that the file is a PDF by checking its magic number
        with open(temp_file_path, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                os.remove(temp_file_path)
                return reply.status(400).send({'error': 'Bad Request - Uploaded file is not a valid PDF'})

        # Use pdftotext to convert the PDF to text
        try:
            result = subprocess.run(['pdftotext', temp_file_path, '-'], capture_output=True, text=True, check=True)
            text_content = result.stdout
        except subprocess.CalledProcessError:
            return reply.status(500).send({'error': 'Internal Server Error - Conversion failed'})
        finally:
            # Clean up the temporary file
            os.remove(temp_file_path)

        # Return the converted text
        return reply.type('text/plain').send(text_content)

    except Exception as e:
        return reply.status(500).send({'error': 'Internal Server Error - ' + str(e)})

if __name__ == '__main__':
    app.listen(5000, '0.0.0.0')