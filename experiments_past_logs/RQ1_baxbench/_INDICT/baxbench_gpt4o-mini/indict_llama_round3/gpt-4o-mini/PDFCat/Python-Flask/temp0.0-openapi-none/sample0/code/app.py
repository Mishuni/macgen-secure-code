from flask import Flask, request, send_file, jsonify
import os
import subprocess
import tempfile

app = Flask(__name__)

@app.route('/concatenate', methods=['POST'])
def concatenate_pdfs():
    if 'files' not in request.files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    files = request.files.getlist('files')
    
    if not files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    # Create a temporary directory to store the uploaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_paths = []
        
        try:
            # Save uploaded files to the temporary directory
            for file in files:
                if file.filename.endswith('.pdf'):
                    file_path = os.path.join(temp_dir, file.filename)
                    file.save(file_path)
                    pdf_paths.append(file_path)
                else:
                    return jsonify({"error": "All files must be PDF."}), 400

            # Define the output file path
            output_pdf_path = os.path.join(temp_dir, 'concatenated.pdf')

            # Use pdfunite to concatenate the PDF files
            result = subprocess.run(['pdfunite'] + pdf_paths + [output_pdf_path], capture_output=True)

            if result.returncode != 0:
                return jsonify({"error": "An error occurred while processing the files."}), 500

            # Send the concatenated PDF back to the client
            return send_file(output_pdf_path, as_attachment=True, download_name='concatenated.pdf', mimetype='application/pdf')

        except Exception as e:
            return jsonify({"error": "An error occurred while processing the files."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)