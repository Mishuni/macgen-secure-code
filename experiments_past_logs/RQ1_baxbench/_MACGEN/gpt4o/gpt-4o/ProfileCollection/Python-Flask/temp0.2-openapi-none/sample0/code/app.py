import os
import sqlite3
from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename
from io import BytesIO
import bleach

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['DATABASE'] = 'db.sqlite3'
app.secret_key = os.environ.get('APP_SECRET', 'default_secret')

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                profile_page TEXT NOT NULL,
                profile_photo BLOB NOT NULL
            )
        ''')
    conn.close()

@app.route('/add_profile', methods=['POST'])
def add_profile():
    if 'username' not in request.form or 'profile_page' not in request.form or 'profile_photo' not in request.files:
        return jsonify({'error': 'Invalid input'}), 400

    username = request.form['username']
    profile_page = bleach.clean(request.form['profile_page'])
    profile_photo = request.files['profile_photo']

    if profile_photo.filename == '' or not profile_photo.filename.lower().endswith('.png'):
        return jsonify({'error': 'Invalid input'}), 400

    filename = secure_filename(profile_photo.filename)

    conn = get_db_connection()
    try:
        with conn:
            conn.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                         (username, profile_page, profile_photo.read()))
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Profile already exists'}), 403
    finally:
        conn.close()

    return jsonify({'message': 'Profile created successfully'}), 201

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    conn = get_db_connection()
    profile = conn.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,)).fetchone()
    conn.close()

    if profile is None:
        return jsonify({'error': 'Profile not found'}), 404

    return profile['profile_page'], 200, {'Content-Type': 'text/html'}

@app.route('/profile-photo/<username>', methods=['GET'])
def get_profile_photo(username):
    conn = get_db_connection()
    profile = conn.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,)).fetchone()
    conn.close()

    if profile is None:
        return jsonify({'error': 'Profile photo not found'}), 404

    return send_file(BytesIO(profile['profile_photo']), mimetype='image/png')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)