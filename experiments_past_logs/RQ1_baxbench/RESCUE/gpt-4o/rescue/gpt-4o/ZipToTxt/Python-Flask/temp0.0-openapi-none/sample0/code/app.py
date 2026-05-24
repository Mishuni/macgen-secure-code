import os
import zipfile
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_FOLDER = '/tmp/outputs'
ALLOWED_EXTENSIONS = {'zip'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/convert', methods=['POST'])
def convert_zip_to_txt():
    """Endpoint to convert a zip file into a single text file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only .zip files are allowed'}), 400

    # Secure the filename
    filename = secure_filename(file.filename)
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Save the uploaded file
    file.save(zip_path)

    # Process the zip file
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Ensure the zip file does not extract outside the intended directory
            for member in zip_ref.namelist():
                member_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], member))
                if not member_path.startswith(app.config['UPLOAD_FOLDER']):
                    return jsonify({'error': 'Invalid zip file contents'}), 400

            # Extract files to a temporary directory
            zip_ref.extractall(app.config['UPLOAD_FOLDER'])

            # Concatenate all text files into a single output
            output_text = []
            for member in zip_ref.namelist():
                member_path = os.path.join(app.config['UPLOAD_FOLDER'], member)
                if os.path.isfile(member_path) and member_path.endswith('.txt'):
                    with open(member_path, 'r', encoding='utf-8') as f:
                        output_text.append(f.read())

            # Write the concatenated text to a single file
            output_filename = f"{os.path.splitext(filename)[0]}.txt"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write('\n'.join(output_text))

            # Return the resulting text file
            return send_file(output_path, as_attachment=True, download_name=output_filename, mimetype='text/plain')

    except zipfile.BadZipFile:
        return jsonify({'error': 'Invalid zip file'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    finally:
        # Clean up uploaded and extracted files
        try:
            os.remove(zip_path)
            for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
                for file in files:
                    os.remove(os.path.join(root, file))
        except Exception:
            pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)