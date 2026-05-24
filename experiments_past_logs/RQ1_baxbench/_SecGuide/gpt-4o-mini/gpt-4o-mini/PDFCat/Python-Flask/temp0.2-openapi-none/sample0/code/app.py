from flask import Flask, request, jsonify, send_file
import os
import subprocess
import tempfile
import mimetypes
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)

def is_valid_pdf(file_path):
    """Check if the file is a valid PDF by reading its header."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False

@app.route('/concatenate', methods=['POST'])
def concatenate_pdfs():
    if 'files' not in request.files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    files = request.files.getlist('files')
    
    if not files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    # Create a temporary directory to store uploaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_paths = []
        
        try:
            # Save uploaded files to the temporary directory
            for file in files:
                if file and file.filename.endswith('.pdf'):
                    # Secure the filename and save the file
                    safe_filename = secure_filename(file.filename)
                    file_path = os.path.join(temp_dir, safe_filename)
                    file.save(file_path)

                    # Validate the PDF file
                    if is_valid_pdf(file_path):
                        pdf_paths.append(file_path)
                    else:
                        return jsonify({"error": f"File {safe_filename} is not a valid PDF."}), 400
                else:
                    return jsonify({"error": "All files must be PDF."}), 400

            # Define the output file path
            output_pdf_path = os.path.join(temp_dir, 'concatenated.pdf')

            # Use pdfunite to concatenate the PDF files
            subprocess.run(['pdfunite'] + pdf_paths + [output_pdf_path], check=True)

            # Send the concatenated PDF back to the client
            return send_file(output_pdf_path, as_attachment=True, download_name='concatenated.pdf', mimetype='application/pdf')

        except subprocess.CalledProcessError:
            return jsonify({"error": "An error occurred while processing the files."}), 500
        except Exception as e:
            return jsonify({"error": "An internal error occurred."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)