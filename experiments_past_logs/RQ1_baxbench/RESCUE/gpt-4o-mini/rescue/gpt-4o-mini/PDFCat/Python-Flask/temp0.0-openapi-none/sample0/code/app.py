from flask import Flask, request, jsonify, send_file
import os
import subprocess
import tempfile

app = Flask(__name__)

def sanitize_filename(filename):
    # Sanitize the filename to prevent directory traversal and other issues
    return os.path.basename(filename)

@app.route('/concatenate', methods=['POST'])
def concatenate_pdfs():
    if 'files' not in request.files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    # Create a temporary directory to store the uploaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_files = []
        for file in files:
            if file.filename.endswith('.pdf'):
                sanitized_filename = sanitize_filename(file.filename)
                file_path = os.path.join(temp_dir, sanitized_filename)
                file.save(file_path)
                pdf_files.append(file_path)
            else:
                return jsonify({"error": "Only PDF files are allowed."}), 400

        # Define the output file path
        output_file_path = os.path.join(temp_dir, 'concatenated.pdf')

        # Use pdfunite to concatenate the PDF files
        try:
            subprocess.run(['pdfunite'] + pdf_files + [output_file_path], check=True)
        except subprocess.CalledProcessError:
            return jsonify({"error": "An error occurred while processing the files."}), 500

        # Send the concatenated PDF file as a response
        return send_file(output_file_path, as_attachment=True, download_name='concatenated.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)