from flask import Flask, request, jsonify
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                invite_id TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

def is_valid_email(email):
    # More robust regex for validating an email
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

def is_strong_password(password):
    # Check for minimum length and complexity
    return len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isalpha() for char in password)

@app.route('/invite_user', methods=['POST'])
def invite_user():
    data = request.get_json()
    email = data.get('email')

    if not email or not is_valid_email(email):
        return jsonify({"message": "A valid email is required."}), 400

    invite_id = os.urandom(16).hex()  # Generate a random invite_id

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
        existing_invite = cursor.fetchone()

        if existing_invite:
            invite_id = existing_invite[0]
        else:
            cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))
            conn.commit()

    return jsonify({"invite_id": invite_id, "message": "Invitation email prepared."}), 200

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    invite_id = data.get('invite_id')
    user_name = data.get('user_name')
    password = data.get('password')

    if not invite_id or not user_name or not password:
        return jsonify({"message": "Invite ID, username, and password are required."}), 400

    if len(user_name) < 3 or len(user_name) > 20:
        return jsonify({"message": "Username must be between 3 and 20 characters."}), 400

    if not is_strong_password(password):
        return jsonify({"message": "Password must be at least 8 characters long and contain both letters and numbers."}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM invitations WHERE invite_id = ?', (invite_id,))
        invitation = cursor.fetchone()

        if not invitation:
            return jsonify({"message": "Invalid invite_id."}), 401

        hashed_password = generate_password_hash(password)

        try:
            cursor.execute('INSERT INTO users (user_name, password) VALUES (?, ?)', (user_name, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            return jsonify({"message": "Username already exists. Please choose a different username."}), 400

    return jsonify({"message": "User created."}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)