import os
import shutil
import tempfile
from fastify import Fastify
from uuid import uuid4
from subprocess import run, CalledProcessError
from @fastify.multipart import fastifyMultipart

# Initialize Fastify app
app = Fastify()

# Register multipart plugin
app.register(fastifyMultipart)

# Define constants
UPLOAD_DIR = "/tmp/pdf_uploads"
CONCATENATED_DIR = "/tmp/pdf_concatenated"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CONCATENATED_DIR, exist_ok=True)

# Utility function to sanitize file names
def sanitize_filename(filename):
    return os.path.basename(filename)

# Route for PDF concatenation
@app.post('/concatenate')
async def concatenate_pdfs(request, reply):
    try:
        # Parse multipart form data
        data = await request.file()
        files = data.files.getall('files')

        # Validate input
        if not files or len(files) < 2:
            return reply.status(400).send({"error": "Invalid input or missing files."})

        # Save uploaded files securely
        uploaded_files = []
        for file in files:
            filename = sanitize_filename(file.filename)
            if not filename.endswith('.pdf'):
                return reply.status(400).send({"error": "All files must be PDFs."})
            file_path = os.path.join(UPLOAD_DIR, f"{uuid4()}_{filename}")
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            uploaded_files.append(file_path)

        # Generate output file path
        output_file = os.path.join(CONCATENATED_DIR, f"{uuid4()}_concatenated.pdf")

        # Concatenate PDFs using pdfunite
        try:
            run(['pdfunite', *uploaded_files, output_file], check=True)
        except CalledProcessError:
            return reply.status(500).send({"error": "An error occurred while processing the files."})

        # Return concatenated PDF
        with open(output_file, 'rb') as f:
            pdf_data = f.read()

        # Clean up temporary files
        for file_path in uploaded_files:
            os.remove(file_path)
        os.remove(output_file)

        return reply
            .header('Content-Type', 'application/pdf')
            .header('Content-Disposition', 'attachment; filename="concatenated.pdf"')
            .send(pdf_data)

    except Exception as e:
        return reply.status(500).send({"error": "An unexpected error occurred."})

# Start the server
if __name__ == '__main__':
    app.listen(5000, '0.0.0.0')