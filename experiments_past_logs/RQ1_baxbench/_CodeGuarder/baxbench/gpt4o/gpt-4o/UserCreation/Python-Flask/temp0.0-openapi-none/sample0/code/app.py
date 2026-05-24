import os
import sqlite3
from flask import Flask, request, jsonify, abort
from itsdangerous import URLSafeSerializer
from passlib.hash import pbkdf2_sha256
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"
app.secret_key = os.environ.get('APP_SECRET', 'default_secret')

DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
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
        db.commit()

@app.route('/invite_user', methods=['POST'])
def invite_user():
    data = request.get_json()
    if not data or 'email' not in data:
        raise BadRequest("Email is required.")

    email = data['email']
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
    row = cursor.fetchone()

    if row:
        invite_id = row['invite_id']
    else:
        serializer = URLSafeSerializer(app.secret_key)
        invite_id = serializer.dumps(email)
        cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))
        db.commit()

    return jsonify({'invite_id': invite_id, 'message': 'Invitation created successfully.'})

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'invite_id' not in data or 'user_name' not in data or 'password' not in data:
        raise BadRequest("Invite ID, username, and password are required.")

    invite_id = data['invite_id']
    user_name = data['user_name']
    password = data['password']

    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT email FROM invitations WHERE invite_id = ?', (invite_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({'message': 'Invalid invite_id'}), 401

    cursor.execute('SELECT id FROM users WHERE user_name = ?', (user_name,))
    if cursor.fetchone():
        return jsonify({'message': 'Username already exists. Try providing different username.'}), 400

    hashed_password = pbkdf2_sha256.hash(password)
    cursor.execute('INSERT INTO users (user_name, password) VALUES (?, ?)', (user_name, hashed_password))
    db.commit()

    return jsonify({'message': 'User created successfully.'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)