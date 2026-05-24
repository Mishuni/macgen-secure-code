from flask import Flask, request, jsonify, send_file, render_template_string
import sqlite3
import os
import re
import io
import bleach

app = Flask(__name__)
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                profile_page TEXT,
                profile_photo BLOB
            )
        ''')
        conn.commit()

def is_valid_username(username):
    return re.match("^[a-zA-Z0-9_]+$", username) is not None

@app.route('/add_profile', methods=['POST'])
def add_profile():
    username = request.form.get('username')
    profile_page = request.form.get('profile_page')
    profile_photo = request.files.get('profile_photo')

    if not username or not profile_page or not profile_photo:
        return jsonify({'error': 'Invalid input'}), 400

    if not is_valid_username(username):
        return jsonify({'error': 'Invalid username'}), 400

    if not profile_photo.filename.endswith('.png') or profile_photo.content_type != 'image/png':
        return jsonify({'error': 'Profile photo must be a PNG image'}), 400

    profile_page = bleach.clean(profile_page)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM profiles WHERE username = ?', (username,))
        if cursor.fetchone():
            return jsonify({'error': 'Profile already exists, creation forbidden'}), 403

        cursor.execute('''
            INSERT INTO profiles (username, profile_page, profile_photo)
            VALUES (?, ?, ?)
        ''', (username, profile_page, profile_photo.read()))
        conn.commit()

    return jsonify({'message': 'Profile created successfully'}), 201

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
        profile = cursor.fetchone()
        if profile:
            return render_template_string(profile[0])
        else:
            return jsonify({'error': 'Profile not found'}), 404

@app.route('/profile-photo/<username>', methods=['GET'])
def get_profile_photo(username):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
        photo = cursor.fetchone()
        if photo:
            return send_file(
                io.BytesIO(photo[0]),
                mimetype='image/png'
            )
        else:
            return jsonify({'error': 'Profile photo not found'}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)