from flask import Flask, request, jsonify
import subprocess
import os
import uuid
import tempfile

app = Flask(__name__)

# Define a maximum file size (e.g., 5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@app.route('/convert', methods=['POST'])
def convert_pdf_to_text():
    if 'file' not in request.files:
        return jsonify({'error': 'Bad Request - Invalid input or missing file'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Bad Request - Invalid input or missing file'}), 400

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Bad Request - Only PDF files are allowed'}), 400

    # Validate file size
    if file.content_length > MAX_FILE_SIZE:
        return jsonify({'error': 'Bad Request - File is too large'}), 400

    # Create a secure temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_pdf_path = temp_file.name
        file.save(temp_pdf_path)

    try:
        # Use pdftotext to convert PDF to text
        result = subprocess.run(['pdftotext', temp_pdf_path, '-'], capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            return jsonify({'error': 'Internal Server Error - Conversion failed'}), 500

        # Return the converted text
        return result.stdout, 200

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Internal Server Error - Conversion timed out'}), 500

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)