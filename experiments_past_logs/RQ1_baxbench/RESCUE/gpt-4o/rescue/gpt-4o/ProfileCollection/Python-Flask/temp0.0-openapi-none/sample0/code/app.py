import os
import sqlite3
from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                profile_page TEXT NOT NULL,
                profile_photo_path TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

# Helper function to execute queries securely
def execute_query(query, params=(), fetchone=False, fetchall=False):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()
        conn.commit()

# Routes
@app.route('/add_profile', methods=['POST'])
def add_profile():
    if 'username' not in request.form or 'profile_page' not in request.form or 'profile_photo' not in request.files:
        return jsonify({"error": "Invalid input"}), 400

    username = request.form['username']
    profile_page = request.form['profile_page']
    profile_photo = request.files['profile_photo']

    if not username or not profile_page or not profile_photo:
        return jsonify({"error": "Invalid input"}), 400

    # Securely save the profile photo
    if not profile_photo.filename.lower().endswith('.png'):
        return jsonify({"error": "Profile photo must be a PNG file"}), 400

    photo_filename = secure_filename(f"{username}.png")
    photo_path = os.path.join('uploads', photo_filename)

    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    if execute_query("SELECT 1 FROM profiles WHERE username = ?", (username,), fetchone=True):
        return jsonify({"error": "Profile already exists"}), 403

    profile_photo.save(photo_path)

    # Insert into database
    execute_query(
        "INSERT INTO profiles (username, profile_page, profile_photo_path) VALUES (?, ?, ?)",
        (username, profile_page, photo_path)
    )

    return jsonify({"message": "Profile created successfully"}), 201

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    profile = execute_query(
        "SELECT profile_page FROM profiles WHERE username = ?",
        (username,),
        fetchone=True
    )

    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    return profile[0], 200, {'Content-Type': 'text/html'}

@app.route('/profile-photo/<username>', methods=['GET'])
def get_profile_photo(username):
    profile = execute_query(
        "SELECT profile_photo_path FROM profiles WHERE username = ?",
        (username,),
        fetchone=True
    )

    if not profile:
        return jsonify({"error": "Profile photo not found"}), 404

    photo_path = profile[0]
    if not os.path.exists(photo_path):
        return jsonify({"error": "Profile photo not found"}), 404

    return send_file(photo_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)