from flask import Flask, request, jsonify, send_file
import os
import subprocess

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

@app.route('/convert', methods=['POST'])
def convert_pdf_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "File is not a PDF"}), 400

    # Save the file to a temporary location
    temp_file_path = os.path.join('/tmp', file.filename)
    file.save(temp_file_path)

    try:
        # Use pdftotext to convert PDF to text
        output_text_path = temp_file_path.replace('.pdf', '.txt')
        subprocess.run(['pdftotext', temp_file_path, output_text_path], check=True)

        # Read the extracted text
        with open(output_text_path, 'r') as text_file:
            extracted_text = text_file.read()

        # Clean up temporary files
        os.remove(temp_file_path)
        os.remove(output_text_path)

        return extracted_text, 200

    except subprocess.CalledProcessError:
        return jsonify({"error": "Conversion failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)