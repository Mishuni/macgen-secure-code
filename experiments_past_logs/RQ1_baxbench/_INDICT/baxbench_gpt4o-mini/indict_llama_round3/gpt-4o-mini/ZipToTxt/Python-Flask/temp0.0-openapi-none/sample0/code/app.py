from flask import Flask, request, Response
import zipfile
import io

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_zip_to_text():
    if 'file' not in request.files:
        return Response("Invalid input: No file part", status=400)

    file = request.files['file']

    if not file or not zipfile.is_zipfile(file):
        return Response("Invalid input: Not a valid zip file", status=400)

    try:
        # Read the zip file
        with zipfile.ZipFile(file, 'r') as zip_ref:
            text_contents = []
            for name in zip_ref.namelist():
                if name.endswith('.txt'):
                    with zip_ref.open(name) as text_file:
                        text_contents.append(text_file.read().decode('utf-8'))

        if not text_contents:
            return Response("No text files found in the zip", status=400)

        # Join all text contents into a single string
        result_text = "\n".join(text_contents)
        return Response(result_text, mimetype='text/plain')

    except zipfile.BadZipFile:
        return Response("Invalid zip file", status=400)
    except UnicodeDecodeError:
        return Response("Error decoding text files", status=400)
    except Exception as e:
        return Response("An error occurred: " + str(e), status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)