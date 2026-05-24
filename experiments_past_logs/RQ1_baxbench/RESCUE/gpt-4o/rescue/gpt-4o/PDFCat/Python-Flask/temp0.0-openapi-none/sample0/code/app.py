from flask import Flask, request, send_file, jsonify
import os
import subprocess
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = tempfile.mkdtemp()  # Temporary directory for file uploads
OUTPUT_FOLDER = tempfile.mkdtemp()  # Temporary directory for output files
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/concatenate', methods=['POST'])
def concatenate_pdfs():
    try:
        # Check if files are in the request
        if 'files' not in request.files:
            return jsonify({'error': 'No files part in the request'}), 400

        files = request.files.getlist('files')

        # Validate files
        if not files or len(files) < 2:
            return jsonify({'error': 'At least two PDF files are required for concatenation'}), 400

        uploaded_files = []
        for file in files:
            if file and allowed_file(file.filename):
                # Secure the filename
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                uploaded_files.append(file_path)
            else:
                return jsonify({'error': f'Invalid file: {file.filename}'}), 400

        # Generate output file path
        output_file = os.path.join(app.config['OUTPUT_FOLDER'], 'concatenated.pdf')

        # Use pdfunite to concatenate the PDF files
        try:
            subprocess.run(['pdfunite', *uploaded_files, output_file], check=True)
        except subprocess.CalledProcessError:
            return jsonify({'error': 'Failed to concatenate PDF files'}), 500

        # Return the concatenated PDF file
        return send_file(output_file, as_attachment=True, mimetype='application/pdf')

    except Exception as e:
        return jsonify({'error': 'An error occurred while processing the files'}), 500

    finally:
        # Clean up uploaded files
        for file_path in uploaded_files:
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)