from flask import Flask, request, jsonify
import subprocess
import tempfile
import os

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_pdf_to_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file.content_type != 'application/pdf':
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400

    try:
        # Create a secure temporary file for the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_pdf_path = temp_file.name
            file.save(temp_pdf_path)

        # Use pdftotext to convert PDF to text
        result = subprocess.run(['pdftotext', temp_pdf_path, '-'], capture_output=True, text=True)

        # Remove the temporary file
        os.remove(temp_pdf_path)

        if result.returncode != 0:
            return jsonify({'error': 'Conversion failed'}), 500

        return result.stdout, 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)