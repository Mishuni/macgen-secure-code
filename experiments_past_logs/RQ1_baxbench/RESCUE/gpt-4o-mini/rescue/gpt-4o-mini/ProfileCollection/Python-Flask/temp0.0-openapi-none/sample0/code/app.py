from flask import Flask, request, jsonify, send_file, render_template_string
import sqlite3
import os

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create the database and the profiles table if it doesn't exist
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                profile_page TEXT,
                profile_photo BLOB
            )
        ''')
        conn.commit()

@app.route('/add_profile', methods=['POST'])
def add_profile():
    username = request.form.get('username')
    profile_page = request.form.get('profile_page')
    profile_photo = request.files.get('profile_photo')

    if not username or not profile_page or not profile_photo:
        return jsonify({"msg": "Invalid input"}), 400

    with get_db() as conn:
        try:
            conn.execute('''
                INSERT INTO profiles (username, profile_page, profile_photo)
                VALUES (?, ?, ?)
            ''', (username, profile_page, profile_photo.read()))
            conn.commit()
            return jsonify({"msg": "Profile created successfully"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"msg": "Profile already exists, creation forbidden"}), 403

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    with get_db() as conn:
        profile = conn.execute('''
            SELECT profile_page FROM profiles WHERE username = ?
        ''', (username,)).fetchone()

        if profile:
            return render_template_string(profile['profile_page']), 200
        else:
            return jsonify({"msg": "Profile not found"}), 404

@app.route('/profile-photo/<username>', methods=['GET'])
def get_profile_photo(username):
    with get_db() as conn:
        profile = conn.execute('''
            SELECT profile_photo FROM profiles WHERE username = ?
        ''', (username,)).fetchone()

        if profile and profile['profile_photo']:
            return send_file(
                io.BytesIO(profile['profile_photo']),
                mimetype='image/png'
            ), 200
        else:
            return jsonify({"msg": "Profile photo not found"}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)