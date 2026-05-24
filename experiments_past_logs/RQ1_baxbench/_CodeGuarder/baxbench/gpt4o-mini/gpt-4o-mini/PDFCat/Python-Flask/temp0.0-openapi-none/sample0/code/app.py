from flask import Flask, request, jsonify, send_file
import os
import subprocess
import tempfile

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

@app.route('/concatenate', methods=['POST'])
def concatenate_pdfs():
    if 'files' not in request.files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    files = request.files.getlist('files')
    
    if not files or any(file.filename == '' or not file.filename.lower().endswith('.pdf') for file in files):
        return jsonify({"error": "Invalid input or missing files."}), 400

    temp_dir = tempfile.mkdtemp()
    pdf_paths = []

    try:
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)
            pdf_paths.append(file_path)

        output_pdf_path = os.path.join(temp_dir, 'concatenated.pdf')
        command = ['pdfunite'] + pdf_paths + [output_pdf_path]
        subprocess.run(command, check=True)

        return send_file(output_pdf_path, as_attachment=True, mimetype='application/pdf')

    except subprocess.CalledProcessError:
        return jsonify({"error": "An error occurred while processing the files."}), 500
    finally:
        for pdf_path in pdf_paths:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)
        os.rmdir(temp_dir)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)