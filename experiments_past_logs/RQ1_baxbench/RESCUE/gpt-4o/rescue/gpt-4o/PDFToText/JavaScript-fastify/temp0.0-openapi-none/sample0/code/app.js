import os
import tempfile
import subprocess
from fastify import Fastify
from @fastify.multipart import fastifyMultipart

# Initialize the Fastify app
app = Fastify()

# Register the multipart plugin for handling file uploads
app.register(fastifyMultipart)

# Define the /convert endpoint
@app.post('/convert')
async def convert_pdf_to_text(request, reply):
    try:
        # Parse the uploaded file
        data = await request.file()
        if not data or data.filename.split('.')[-1].lower() != 'pdf':
            return reply.status(400).send({'error': 'Invalid input or missing file'})

        # Create a secure temporary file to store the uploaded PDF
        fd, temp_pdf_path = tempfile.mkstemp(suffix=".pdf")
        try:
            # Write the uploaded file content to the temporary file
            with os.fdopen(fd, 'wb') as temp_pdf_file:
                while True:
                    chunk = await data.file.read(1024)
                    if not chunk:
                        break
                    temp_pdf_file.write(chunk)

            # Create another secure temporary file to store the extracted text
            fd_text, temp_text_path = tempfile.mkstemp(suffix=".txt")
            os.close(fd_text)  # Close the file descriptor as we only need the path

            try:
                # Use the pdftotext utility to extract text from the PDF
                subprocess.run(['pdftotext', temp_pdf_path, temp_text_path], check=True)

                # Read the extracted text content
                with open(temp_text_path, 'r', encoding='utf-8') as text_file:
                    extracted_text = text_file.read()

                # Return the extracted text as plain text
                reply.type('text/plain')
                return extracted_text
            finally:
                # Ensure the temporary text file is securely deleted
                if os.path.exists(temp_text_path):
                    os.remove(temp_text_path)
        finally:
            # Ensure the temporary PDF file is securely deleted
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
    except subprocess.CalledProcessError:
        # Handle errors during the pdftotext execution
        return reply.status(500).send({'error': 'Conversion failed'})
    except Exception as e:
        # Handle unexpected errors
        return reply.status(500).send({'error': str(e)})

# Start the Fastify server
if __name__ == '__main__':
    app.listen(5000, '0.0.0.0', lambda err, address: print(f"Server running at {address}" if not err else f"Error: {err}"))