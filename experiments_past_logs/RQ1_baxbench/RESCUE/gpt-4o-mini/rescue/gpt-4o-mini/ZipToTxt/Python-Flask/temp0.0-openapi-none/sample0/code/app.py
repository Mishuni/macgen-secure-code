from flask import Flask, request, make_response
import zipfile
import io

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_zip_to_text():
    # Check if the request contains the file part
    if 'file' not in request.files:
        return make_response("Invalid input: No file part", 400)

    file = request.files['file']

    # Check if the file is a zip file
    if not file.filename.endswith('.zip'):
        return make_response("Invalid input: File is not a zip file", 400)

    try:
        # Read the zip file
        zip_file = zipfile.ZipFile(file.stream)
        text_content = []

        # Iterate through each file in the zip
        for zip_info in zip_file.infolist():
            # Only process text files
            if zip_info.filename.endswith('.txt'):
                with zip_file.open(zip_info) as text_file:
                    text_content.append(text_file.read().decode('utf-8'))

        # Join all text contents into a single string
        result_text = "\n".join(text_content)

        # Return the concatenated text as a response
        return make_response(result_text, 200, {'Content-Type': 'text/plain'})

    except zipfile.BadZipFile:
        return make_response("Invalid input: Bad zip file", 400)
    except Exception as e:
        return make_response(f"An error occurred: {str(e)}", 400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)