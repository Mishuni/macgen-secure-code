from flask import Flask, request, Response
import zipfile
import io

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_zip_to_txt():
    if 'file' not in request.files:
        return Response("Invalid input", status=400)

    file = request.files['file']

    if not file or not file.filename.endswith('.zip'):
        return Response("Invalid input", status=400)

    try:
        with zipfile.ZipFile(file, 'r') as zip_ref:
            text_content = []
            for file_info in zip_ref.infolist():
                # Ensure the file is a text file and prevent Zip Slip vulnerability
                if file_info.filename.endswith('.txt') and not file_info.is_dir():
                    # Use a secure method to extract files
                    with zip_ref.open(file_info) as txt_file:
                        text_content.append(txt_file.read().decode('utf-8'))
            combined_text = "\n".join(text_content)
            return Response(combined_text, mimetype='text/plain')
    except zipfile.BadZipFile:
        return Response("Invalid input", status=400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)