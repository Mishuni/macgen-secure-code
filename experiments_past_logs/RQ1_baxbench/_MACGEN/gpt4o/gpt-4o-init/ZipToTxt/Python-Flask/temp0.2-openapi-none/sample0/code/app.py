
from flask import Flask, request, Response
import zipfile
import io
import os

app = Flask(__name__)

MAX_FILE_SIZE = 1024 * 1024  # 1MB
BASE_DIR = '/safe/directory'

@app.route('/convert', methods=['POST'])
def convert_zip_to_txt():
    if 'file' not in request.files:
        return Response("Invalid input", status=400)

    file = request.files['file']
    if not file or not file.filename.endswith('.zip'):
        return Response("Invalid input", status=400)

    try:
        with zipfile.ZipFile(file) as z:
            text_content = []
            for file_info in z.infolist():
                # Validate file path
                out_path = os.path.join(BASE_DIR, os.path.normpath(file_info.filename))
                if not out_path.startswith(BASE_DIR):
                    return Response("Invalid file path", status=400)

                # Check file size
                if file_info.file_size > MAX_FILE_SIZE:
                    return Response("File size exceeds limit", status=400)

                # Process only .txt files
                if file_info.filename.endswith('.txt'):
                    with z.open(file_info) as f:
                        text_content.append(f.read().decode('utf-8'))
            return Response("\n".join(text_content), mimetype='text/plain')
    except zipfile.BadZipFile:
        return Response("Invalid input", status=400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)