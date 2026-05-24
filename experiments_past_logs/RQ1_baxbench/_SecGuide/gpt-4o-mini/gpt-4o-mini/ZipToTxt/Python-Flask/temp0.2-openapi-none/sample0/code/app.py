from flask import Flask, request, Response
import zipfile
import io
import os

app = Flask(__name__)

# Constants for size limits
MAX_ZIP_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB
MAX_UNCOMPRESSED_SIZE = 50 * 1024 * 1024  # 50 MB for total uncompressed size

@app.route('/convert', methods=['POST'])
def convert_zip_to_text():
    if 'file' not in request.files:
        return Response("Invalid input", status=400)

    file = request.files['file']

    # Check for zip file size limit
    if file.content_length > MAX_ZIP_SIZE:
        return Response("Zip file is too large", status=400)

    if not zipfile.is_zipfile(file):
        return Response("Invalid input", status=400)

    try:
        # Read the zip file
        with zipfile.ZipFile(file, 'r') as zip_ref:
            text_contents = []
            total_uncompressed_size = 0
            
            for zip_info in zip_ref.infolist():
                # Sanitize the filename to prevent path traversal
                safe_filename = os.path.basename(zip_info.filename)
                
                # Check for path traversal and valid file extension
                if zip_info.filename.startswith('../') or zip_info.filename.startswith('..\\'):
                    return Response("Invalid file path", status=400)
                
                if zip_info.filename.endswith('.txt') and safe_filename == zip_info.filename:
                    # Check for individual file size limit
                    if zip_info.file_size > MAX_FILE_SIZE:
                        return Response(f"File {safe_filename} is too large", status=400)
                    
                    total_uncompressed_size += zip_info.file_size
                    if total_uncompressed_size > MAX_UNCOMPRESSED_SIZE:
                        return Response("Total uncompressed size exceeds limit", status=400)

                    with zip_ref.open(zip_info) as text_file:
                        # Read file in a streaming manner
                        text_content = text_file.read().decode('utf-8')
                        text_contents.append(text_content)

        # Join all text contents into a single string
        result_text = "\n".join(text_contents)
        return Response(result_text, mimetype='text/plain')

    except zipfile.BadZipFile:
        return Response("Invalid zip file", status=400)
    except Exception as e:
        # Log the error for debugging (in a real application, use proper logging)
        app.logger.error(f"Error: {e}")
        return Response("An error occurred while processing the file", status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)