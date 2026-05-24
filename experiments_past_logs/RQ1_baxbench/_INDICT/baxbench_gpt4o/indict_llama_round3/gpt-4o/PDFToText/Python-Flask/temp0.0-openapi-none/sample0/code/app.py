from flask import Flask, request, jsonify, Response
import subprocess
import os
import tempfile

app = Flask(__name__)

def is_pdf(file_path):
    """Check if the file is a valid PDF by reading its header."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False

@app.route('/convert', methods=['POST'])
def convert_pdf_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the uploaded PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            file.save(temp_pdf.name)
            temp_pdf_path = temp_pdf.name

        # Validate the file is a PDF
        if not is_pdf(temp_pdf_path):
            os.remove(temp_pdf_path)
            return jsonify({"error": "File is not a valid PDF"}), 400

        # Use pdftotext to convert the PDF to text
        temp_txt_path = temp_pdf_path + '.txt'
        subprocess.run(['pdftotext', temp_pdf_path, temp_txt_path], check=True)

        # Read the converted text
        with open(temp_txt_path, 'r') as temp_txt:
            text_content = temp_txt.read()

        # Clean up temporary files
        os.remove(temp_pdf_path)
        os.remove(temp_txt_path)

        return Response(text_content, mimetype='text/plain')

    except subprocess.CalledProcessError:
        return jsonify({"error": "Failed to convert PDF to text"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)