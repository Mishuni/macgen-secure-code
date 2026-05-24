from flask import Flask, request, send_file, jsonify
import os
import subprocess
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/concatenate', methods=['POST'])
def concatenate_pdfs():
    if 'files' not in request.files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    files = request.files.getlist('files')
    if not files or len(files) < 2:
        return jsonify({"error": "Invalid input or missing files."}), 400

    temp_dir = tempfile.mkdtemp()
    input_file_paths = []

    try:
        for file in files:
            if file.filename == '':
                return jsonify({"error": "Invalid input or missing files."}), 400
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({"error": "Only PDF files are allowed."}), 400
            filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            input_file_paths.append(file_path)

        output_file_path = os.path.join(temp_dir, 'concatenated.pdf')
        command = ['pdfunite'] + input_file_paths + [output_file_path]

        result = subprocess.run(command, capture_output=True, check=True)
        
        return send_file(output_file_path, as_attachment=True, mimetype='application/pdf')

    except subprocess.CalledProcessError:
        return jsonify({"error": "An error occurred while processing the files."}), 500

    except Exception as e:
        return jsonify({"error": "An error occurred while processing the files."}), 500

    finally:
        for file_path in input_file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        os.rmdir(temp_dir)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)