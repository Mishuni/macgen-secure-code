from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
SONG_DIRECTORY = '/var/songs'

@app.route('/download', methods=['POST'])
def download_song():
    if not request.is_json:
        return jsonify({'error': 'Invalid input'}), 400
    
    filename = secure_filename(request.json.get('filename', ''))
    
    if not filename:
        return jsonify({'error': 'Invalid input'}), 400
    
    file_path = os.path.join(SONG_DIRECTORY, filename)
    
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File does not exist'}), 404
    
    return send_file(file_path, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)