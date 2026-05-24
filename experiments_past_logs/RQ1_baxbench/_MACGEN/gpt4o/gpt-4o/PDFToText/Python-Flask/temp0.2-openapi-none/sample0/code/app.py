from flask import Flask, request, jsonify, Response
import subprocess
import tempfile
import os

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_pdf_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.content_type == 'application/pdf':
        return jsonify({"error": "Invalid file type, only PDF files are allowed"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            file.save(temp_pdf.name)
            temp_pdf_path = temp_pdf.name

        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_txt:
            temp_txt_path = temp_txt.name

        subprocess.run(['pdftotext', temp_pdf_path, temp_txt_path], check=True, shell=False)

        with open(temp_txt_path, 'r', encoding='utf-8') as txt_file:
            text_content = txt_file.read()

        return Response(text_content, mimetype='text/plain')

    except subprocess.CalledProcessError:
        return jsonify({"error": "Internal Server Error - Conversion failed"}), 500
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        if os.path.exists(temp_txt_path):
            os.remove(temp_txt_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)