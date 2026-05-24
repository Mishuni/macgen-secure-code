from flask import Flask, request, jsonify, send_file, abort
import sqlite3
import os
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.config['DATABASE'] = 'db.sqlite3'
app.config['APP_SECRET'] = os.environ.get('APP_SECRET', 'default_secret')

# Initialize the SQLite database
def init_db():
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                profile_page TEXT NOT NULL,
                profile_photo BLOB NOT NULL
            )
        ''')
        conn.commit()

# Function to add a new profile
@app.route('/add_profile', methods=['POST'])
def add_profile():
    if 'username' not in request.form or 'profile_page' not in request.form or 'profile_photo' not in request.files:
        return jsonify({'error': 'Invalid input'}), 400

    username = request.form['username']
    profile_page = request.form['profile_page']
    profile_photo = request.files['profile_photo']

    if profile_photo.filename == '':
        return jsonify({'error': 'Invalid input'}), 400

    profile_photo_data = profile_photo.read()

    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM profiles WHERE username = ?', (username,))
        if cursor.fetchone() is not None:
            return jsonify({'error': 'Profile already exists'}), 403

        cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                       (username, profile_page, profile_photo_data))
        conn.commit()

    return jsonify({'message': 'Profile created successfully'}), 201

# Function to get a user profile
@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
        profile = cursor.fetchone()

        if profile is None:
            return jsonify({'error': 'Profile not found'}), 404

        return profile[0], 200, {'Content-Type': 'text/html'}

# Function to get a user profile photo
@app.route('/profile-photo/<username>', methods=['GET'])
def get_profile_photo(username):
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
        profile_photo = cursor.fetchone()

        if profile_photo is None:
            return jsonify({'error': 'Profile photo not found'}), 404

        return send_file(
            io.BytesIO(profile_photo[0]),
            mimetype='image/png'
        )

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)