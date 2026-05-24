from flask import Flask, request, Response
from werkzeug.utils import secure_filename
import zipfile
import os
import io
import logging

app = Flask(__name__)

# Set a maximum file size limit (e.g., 10 MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a secure base directory for extraction
BASE_DIR = os.path.abspath("extracted_files")

def is_safe_path(base_path, path, follow_symlinks=True):
    # Resolve symbolic links
    if follow_symlinks:
        base_path = os.path.realpath(base_path)
        path = os.path.realpath(path)
    else:
        base_path = os.path.abspath(base_path)
        path = os.path.abspath(path)
    return os.path.commonpath([base_path]) == os.path.commonpath([base_path, path])

@app.route('/convert', methods=['POST'])
def convert_zip_to_txt():
    if 'file' not in request.files:
        return Response("Invalid input", status=400)

    file = request.files['file']
    if file.filename == '':
        return Response("Invalid input", status=400)

    filename = secure_filename(file.filename)
    if not filename.endswith('.zip'):
        return Response("Invalid input", status=400)

    try:
        with zipfile.ZipFile(file, 'r') as zip_ref:
            text_content = io.StringIO()
            for file_info in zip_ref.infolist():
                # Check for Zip Slip vulnerability
                extracted_path = os.path.join(BASE_DIR, file_info.filename)
                if not is_safe_path(BASE_DIR, extracted_path):
                    return Response("Invalid input", status=400)

                if file_info.filename.endswith('.txt'):
                    with zip_ref.open(file_info) as txt_file:
                        # Limit the size of the file being read
                        file_data = txt_file.read(1024 * 1024)  # Read up to 1 MB
                        text_content.write(file_data.decode('utf-8'))
                        text_content.write("\n")
            text_content.seek(0)
            return Response(text_content.read(), mimetype='text/plain')
    except zipfile.BadZipFile:
        return Response("Invalid input", status=400)
    except Exception as e:
        # Log the error for debugging purposes
        logger.error(f"Error processing file: {e}")
        return Response("Invalid input", status=400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)