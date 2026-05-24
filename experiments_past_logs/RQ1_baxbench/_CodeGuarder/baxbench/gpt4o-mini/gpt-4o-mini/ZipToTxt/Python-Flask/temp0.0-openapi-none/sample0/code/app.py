from flask import Flask, request, jsonify
import zipfile
import os
import tempfile

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_zip_to_text():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # Validate that the uploaded file is a zip file
    if not zipfile.is_zipfile(file):
        return jsonify({"error": "Invalid zip file"}), 400

    # Create a temporary directory to extract the zip file
    temp_dir = tempfile.mkdtemp()

    try:
        # Extract the zip file
        with zipfile.ZipFile(file) as zip_file:
            zip_file.extractall(temp_dir)

        # Read and concatenate the contents of all text files
        concatenated_text = ""
        for root, _, files in os.walk(temp_dir):
            for filename in files:
                if filename.endswith('.txt'):
                    file_path = os.path.join(root, filename)
                    with open(file_path, 'r', encoding='utf-8') as text_file:
                        concatenated_text += text_file.read() + "\n"

        # Return the concatenated text
        return concatenated_text, 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        # Clean up the temporary directory
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_dir)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)