from flask import Flask, request, Response
import zipfile
import os

app = Flask(__name__)

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_UNCOMPRESSED_SIZE = 20 * 1024 * 1024  # 20 MB
MAX_FILES = 100  # Maximum number of files

@app.route('/convert', methods=['POST'])
def convert_zip_to_text():
    if 'file' not in request.files:
        return Response(status=400)

    file = request.files['file']

    if file.content_length > MAX_UPLOAD_SIZE:
        return Response(status=400)

    if not zipfile.is_zipfile(file):
        return Response(status=400)

    try:
        total_uncompressed_size = 0
        file_count = 0
        text_contents = []

        with zipfile.ZipFile(file) as z:
            for entry in z.infolist():
                # Validate file path
                if not entry.filename.startswith('/') and '..' not in entry.filename:
                    if entry.file_size > 0 and entry.filename.endswith('.txt'):
                        if file_count >= MAX_FILES:
                            return Response(status=400)

                        entry_uncompressed_size = entry.file_size
                        if total_uncompressed_size + entry_uncompressed_size > MAX_UNCOMPRESSED_SIZE:
                            return Response(status=400)

                        with z.open(entry) as f:
                            text_contents.append(f.read().decode('utf-8'))
                            total_uncompressed_size += entry_uncompressed_size
                            file_count += 1

        result = "\n".join(text_contents)
        return Response(result, mimetype='text/plain')
    except Exception:
        return Response(status=400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)