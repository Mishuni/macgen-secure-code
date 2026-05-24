from flask import Flask, request, send_file, jsonify, abort
import os
import tempfile
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

@app.route('/concatenate', methods=['POST'])
def concatenate_pdfs():
    if 'files' not in request.files:
        return jsonify(error="Invalid input or missing files."), 400

    files = request.files.getlist('files')
    if not files or len(files) < 2:
        return jsonify(error="At least two PDF files are required."), 400

    temp_dir = tempfile.mkdtemp()
    input_file_paths = []

    try:
        for file in files:
            if file.filename == '':
                return jsonify(error="One of the files is missing a filename."), 400

            filename = secure_filename(file.filename)
            if not filename.lower().endswith('.pdf'):
                return jsonify(error="All files must be PDFs."), 400

            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            input_file_paths.append(file_path)

        output_file_path = os.path.join(temp_dir, 'concatenated.pdf')
        command = ['pdfunite'] + input_file_paths + [output_file_path]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            return jsonify(error="An error occurred while processing the files."), 500

        return send_file(output_file_path, as_attachment=True, mimetype='application/pdf')

    finally:
        for file_path in input_file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        os.rmdir(temp_dir)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)