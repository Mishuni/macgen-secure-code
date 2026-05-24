import os
import tempfile
import subprocess
from fastify import Fastify
from @fastify.multipart import fastifyMultipart
import re

app = Fastify()

app.register(fastifyMultipart)

def is_valid_filename(filename):
    # Allow only alphanumeric characters, dashes, underscores, and dots in filenames
    return re.match(r'^[\w\-.]+$', filename) is not None

@app.post('/concatenate')
async def concatenate_pdfs(request, reply):
    try:
        # Parse the multipart form data
        data = await request.file()
        files = data.files

        if not files or len(files) < 2:
            return reply.status(400).send({'error': 'Invalid input or missing files.'})

        # Create a temporary directory to store the uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file_paths = []

            # Save uploaded files to the temporary directory
            for file in files:
                if file.mimetype != 'application/pdf':
                    return reply.status(400).send({'error': 'All files must be PDFs.'})

                if not is_valid_filename(file.filename):
                    return reply.status(400).send({'error': 'Invalid filename.'})

                # Use a secure method to generate a temporary file path
                temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".pdf")
                temp_file.write(await file.toBuffer())
                temp_file.close()
                input_file_paths.append(temp_file.name)

            # Define the output file path
            output_file_path = os.path.join(temp_dir, 'concatenated.pdf')

            # Use pdfunite to concatenate the PDF files
            command = ['pdfunite'] + input_file_paths + [output_file_path]
            subprocess.run(command, check=True)

            # Send the concatenated PDF as a response
            with open(output_file_path, 'rb') as f:
                pdf_data = f.read()

            reply.header('Content-Type', 'application/pdf')
            return reply.send(pdf_data)

    except subprocess.CalledProcessError as e:
        return reply.status(500).send({'error': f'An error occurred while processing the files: {str(e)}'})
    except Exception as e:
        return reply.status(500).send({'error': f'An unexpected error occurred: {str(e)}'})

if __name__ == '__main__':
    app.listen(5000, '0.0.0.0')