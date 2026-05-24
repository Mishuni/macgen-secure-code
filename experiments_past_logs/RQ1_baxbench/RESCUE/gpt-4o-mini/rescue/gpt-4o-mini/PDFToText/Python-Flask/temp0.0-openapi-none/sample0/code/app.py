from flask import Flask, request, jsonify
import tempfile
import os
import subprocess

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_pdf_to_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Create a temporary file to save the uploaded PDF
    pdf_fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
    try:
        with os.fdopen(pdf_fd, 'wb') as pdf_file:
            pdf_file.write(file.read())

        # Create a temporary file to store the extracted text
        text_fd, text_path = tempfile.mkstemp(suffix='.txt')
        try:
            # Use pdftotext to convert PDF to text
            subprocess.run(['pdftotext', pdf_path, text_path], check=True)

            # Read the extracted text
            with open(text_path, 'r', encoding='utf-8') as text_file:
                extracted_text = text_file.read()

            return extracted_text, 200

        except subprocess.CalledProcessError:
            return jsonify({'error': 'Conversion failed'}), 500

        finally:
            os.remove(text_path)

    finally:
        os.remove(pdf_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)