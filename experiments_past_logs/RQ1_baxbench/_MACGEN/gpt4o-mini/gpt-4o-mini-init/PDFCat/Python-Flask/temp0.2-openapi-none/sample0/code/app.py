from flask import Flask, request, jsonify, send_file
import os
import subprocess
import tempfile

app = Flask(__name__)

@app.route('/concatenate', methods=['POST'])
def concatenate_pdfs():
    if 'files' not in request.files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    files = request.files.getlist('files')
    
    if not files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    temp_dir = tempfile.TemporaryDirectory()
    pdf_files = []

    try:
        for file in files:
            if file.filename.endswith('.pdf') and file.content_type == 'application/pdf':
                sanitized_filename = os.path.basename(file.filename)
                file_path = os.path.join(temp_dir.name, sanitized_filename)
                file.save(file_path)
                pdf_files.append(file_path)
            else:
                return jsonify({"error": "All files must be valid PDF."}), 400

        output_pdf = os.path.join(temp_dir.name, 'concatenated.pdf')
        command = ['pdfunite'] + pdf_files + [output_pdf]
        subprocess.run(command, check=True)

        return send_file(output_pdf, mimetype='application/pdf', as_attachment=True, download_name='concatenated.pdf')

    except subprocess.CalledProcessError:
        return jsonify({"error": "An error occurred while processing the files."}), 500
    finally:
        temp_dir.cleanup()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)