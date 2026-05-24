from flask import Flask, request, send_file, jsonify
import os
import tempfile
import PyPDF2
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set a maximum file size limit (e.g., 10MB per file)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

@app.route('/concatenate', methods=['POST'])
def concatenate_pdfs():
    if 'files' not in request.files:
        return jsonify({'error': 'Invalid input or missing files.'}), 400

    files = request.files.getlist('files')
    if not files or len(files) < 2:
        return jsonify({'error': 'Invalid input or missing files.'}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        input_file_paths = []

        try:
            for file in files:
                # Secure the filename
                filename = secure_filename(file.filename)
                if not filename.endswith('.pdf'):
                    return jsonify({'error': 'All files must be PDFs.'}), 400

                temp_file_path = os.path.join(temp_dir, filename)
                file.save(temp_file_path)
                input_file_paths.append(temp_file_path)

                # Verify the file is a valid PDF
                try:
                    with open(temp_file_path, 'rb') as f:
                        PyPDF2.PdfReader(f)
                except PyPDF2.errors.PdfReadError:
                    return jsonify({'error': 'One or more files are not valid PDFs.'}), 400

            output_file_path = os.path.join(temp_dir, 'concatenated.pdf')

            # Concatenate PDFs using PyPDF2
            pdf_writer = PyPDF2.PdfWriter()
            for input_file_path in input_file_paths:
                with open(input_file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in range(len(pdf_reader.pages)):
                        pdf_writer.add_page(pdf_reader.pages[page])

            with open(output_file_path, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)

            return send_file(output_file_path, as_attachment=True, mimetype='application/pdf')

        except PyPDF2.errors.PdfReadError as e:
            app.logger.error(f"PDF read error: {e}")
            return jsonify({'error': 'An error occurred while reading the PDF files.'}), 400
        except Exception as e:
            # Log the exception for debugging purposes
            app.logger.error(f"An error occurred: {e}")
            return jsonify({'error': 'An error occurred while processing the files.'}), 500

if __name__ == '__main__':
    # Ensure the application is not run in debug mode in production
    app.run(host='0.0.0.0', port=5000, debug=False)