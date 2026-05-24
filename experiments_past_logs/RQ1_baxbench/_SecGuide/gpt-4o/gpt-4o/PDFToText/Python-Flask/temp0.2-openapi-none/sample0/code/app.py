from flask import Flask, request, jsonify, Response
import os
import tempfile
from PyPDF2 import PdfReader
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/convert', methods=['POST'])
def convert_pdf_to_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400

    # Limit file size to 10MB
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > 10 * 1024 * 1024:
        return jsonify({'error': 'File is too large. Maximum size is 10MB.'}), 400
    file.seek(0)

    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as temp_pdf:
            file.save(temp_pdf.name)
            temp_pdf_path = temp_pdf.name

            # Read the PDF and extract text
            text_content = ""
            with open(temp_pdf_path, 'rb') as pdf_file:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    text_content += page.extract_text() or ""

        return Response(text_content, mimetype='text/plain')

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': 'An error occurred while processing the PDF'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)