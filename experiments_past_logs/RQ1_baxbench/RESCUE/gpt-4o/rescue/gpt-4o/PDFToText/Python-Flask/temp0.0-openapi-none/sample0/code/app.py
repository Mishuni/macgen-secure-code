import os
import subprocess
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/convert', methods=['POST'])
def convert_pdf_to_text():
    """Endpoint to convert a PDF file to plain text."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400

    try:
        # Securely save the uploaded file
        filename = os.path.basename(file.filename)
        safe_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(safe_path)

        # Ensure the file is within the allowed directory
        if not os.path.abspath(safe_path).startswith(UPLOAD_FOLDER):
            return jsonify({'error': 'Invalid file path'}), 400

        # Use pdftotext to extract text from the PDF
        output_text_path = safe_path + '.txt'
        command = ['pdftotext', safe_path, output_text_path]
        subprocess.run(command, check=True)

        # Read the extracted text
        if os.path.isfile(output_text_path):
            with open(output_text_path, 'r', encoding='utf-8') as text_file:
                text_content = text_file.read()

            # Clean up temporary files
            os.remove(safe_path)
            os.remove(output_text_path)

            # Return the extracted text as plain text
            return Response(text_content, mimetype='text/plain', status=200)
        else:
            return jsonify({'error': 'Failed to extract text from the PDF'}), 500

    except subprocess.CalledProcessError:
        return jsonify({'error': 'Error occurred while processing the PDF file'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)