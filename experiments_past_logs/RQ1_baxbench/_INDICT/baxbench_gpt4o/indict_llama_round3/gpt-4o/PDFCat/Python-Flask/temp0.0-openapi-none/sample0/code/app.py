from flask import Flask, request, send_file, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename
import tempfile
import shutil
import uuid

app = Flask(__name__)

@app.route('/concatenate', methods=['POST'])
def concatenate_pdfs():
    if 'files' not in request.files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    files = request.files.getlist('files')
    if not files or len(files) < 2:
        return jsonify({"error": "Invalid input or missing files."}), 400

    temp_dir = tempfile.mkdtemp()
    try:
        file_paths = []

        for file in files:
            # Generate a unique filename to avoid conflicts
            unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            file_path = os.path.join(temp_dir, unique_filename)
            file.save(file_path)
            file_paths.append(file_path)

        # Concatenate PDFs using pdfunite
        output_file = os.path.join(temp_dir, 'concatenated.pdf')
        subprocess.run(['pdfunite'] + file_paths + [output_file], check=True)

        # Send the concatenated PDF back to the client
        return send_file(output_file, as_attachment=True, mimetype='application/pdf')

    except subprocess.CalledProcessError:
        return jsonify({"error": "An error occurred while processing the files."}), 500

    finally:
        # Clean up temporary files
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)