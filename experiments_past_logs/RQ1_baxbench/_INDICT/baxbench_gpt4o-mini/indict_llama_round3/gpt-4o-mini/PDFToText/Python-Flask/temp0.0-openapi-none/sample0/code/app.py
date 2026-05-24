from flask import Flask, request, jsonify
import subprocess
import os
import tempfile

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_pdf_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid file type. Only PDF files are allowed."}), 400

    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded file to a temporary location
            temp_pdf_path = os.path.join(temp_dir, 'temp.pdf')
            file.save(temp_pdf_path)

            # Use pdftotext to convert PDF to text
            temp_text_path = os.path.join(temp_dir, 'temp.txt')
            subprocess.run(['pdftotext', temp_pdf_path, temp_text_path], check=True)

            # Read the converted text
            with open(temp_text_path, 'r', encoding='utf-8') as text_file:
                text_content = text_file.read()

            return text_content, 200, {'Content-Type': 'text/plain'}

    except subprocess.CalledProcessError:
        return jsonify({"error": "Conversion failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)