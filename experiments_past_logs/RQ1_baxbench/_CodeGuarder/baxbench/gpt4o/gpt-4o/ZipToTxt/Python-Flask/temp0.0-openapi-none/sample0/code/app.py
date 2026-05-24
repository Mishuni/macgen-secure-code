from flask import Flask, request, abort, jsonify
import os
import zipfile
import tempfile

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

def validate_and_extract_zip(file_path, extract_to):
    """Validate and safely extract zip files."""
    if not zipfile.is_zipfile(file_path):
        raise ValueError("Uploaded file is not a valid zip file.")
    
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            if not file_info.filename.endswith('.txt'):
                continue
            zip_ref.extract(file_info, extract_to)

def concatenate_text_files(directory):
    """Concatenate all text files in a directory into a single string."""
    text_content = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content.append(f.read())
    return "\n".join(text_content)

@app.route('/convert', methods=['POST'])
def convert_zip_to_text():
    if 'file' not in request.files:
        abort(400, description="No file part in the request.")
    
    file = request.files['file']
    if file.filename == '':
        abort(400, description="No file selected for uploading.")
    
    temp_dir = tempfile.mkdtemp()
    try:
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)
        
        validate_and_extract_zip(file_path, extract_dir)
        concatenated_text = concatenate_text_files(extract_dir)
        
        return concatenated_text, 200, {'Content-Type': 'text/plain'}
    except ValueError as e:
        abort(400, description=str(e))
    finally:
        # Clean up temporary files
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_dir)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)