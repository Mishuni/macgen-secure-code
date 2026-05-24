from flask import Flask, request, jsonify, abort
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set a limit on the maximum file size for uploads (e.g., 10MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Allowed extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/convert', methods=['POST'])
def convert_pdf_to_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join('/tmp', filename)

    try:
        file.save(input_path)

        # Use pdftotext to convert PDF to text
        output_path = input_path + '.txt'
        result = subprocess.run(['pdftotext', input_path, output_path], check=True)

        with open(output_path, 'r') as output_file:
            text_content = output_file.read()

        os.remove(input_path)
        os.remove(output_path)

        return text_content, 200, {'Content-Type': 'text/plain'}

    except subprocess.CalledProcessError:
        return jsonify({'error': 'Failed to convert PDF'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)