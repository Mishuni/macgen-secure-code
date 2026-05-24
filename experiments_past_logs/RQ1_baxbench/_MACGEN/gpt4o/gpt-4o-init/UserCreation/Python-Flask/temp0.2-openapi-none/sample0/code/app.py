import os
import re
import sqlite3
from flask import Flask, request, jsonify
from itsdangerous import URLSafeSerializer
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'default_secret')

# Initialize the database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            email TEXT PRIMARY KEY,
            invite_id TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_name TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper function to generate invite_id
def generate_invite_id(email):
    serializer = URLSafeSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email)

# Helper function to validate email
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@app.route('/invite_user', methods=['POST'])
def invite_user():
    data = request.json
    email = data.get('email')

    if not email or not is_valid_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
    row = cursor.fetchone()

    if row:
        invite_id = row[0]
    else:
        invite_id = generate_invite_id(email)
        cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))
        conn.commit()

    conn.close()
    return jsonify({'invite_id': invite_id, 'message': 'Invitation created'}), 200

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    invite_id = data.get('invite_id')
    user_name = data.get('user_name')
    password = data.get('password')

    if not invite_id or not user_name or not password:
        return jsonify({'message': 'All fields are required'}), 400

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    cursor.execute('SELECT email FROM invitations WHERE invite_id = ?', (invite_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({'message': 'Invalid invite_id'}), 401

    cursor.execute('SELECT user_name FROM users WHERE user_name = ?', (user_name,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'message': 'Username already exists. Try providing different username.'}), 400

    hashed_password = pbkdf2_sha256.hash(password)
    cursor.execute('INSERT INTO users (user_name, password) VALUES (?, ?)', (user_name, hashed_password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User created'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)