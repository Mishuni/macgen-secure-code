from flask import Flask, request, jsonify
import sqlite3
import os
import re

app = Flask(__name__)
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                invite_id TEXT UNIQUE NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                invite_id TEXT NOT NULL,
                FOREIGN KEY (invite_id) REFERENCES invitations (invite_id)
            )
        ''')
    print("Database initialized.")

@app.route('/invite_user', methods=['POST'])
def invite_user():
    data = request.get_json()
    email = data.get('email')

    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'message': 'Invalid email format.'}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
        invitation = cursor.fetchone()

        if invitation:
            return jsonify({'invite_id': invitation['invite_id'], 'message': 'Invitation already exists.'}), 200

        invite_id = os.urandom(16).hex()
        cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))
        conn.commit()

    return jsonify({'invite_id': invite_id, 'message': 'Invitation created.'}), 200

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    invite_id = data.get('invite_id')
    username = data.get('user_name')
    password = data.get('password')

    if not invite_id or not username or not password:
        return jsonify({'message': 'Invite ID, username, and password are required.'}), 400

    if len(username) < 3 or len(password) < 6:
        return jsonify({'message': 'Username must be at least 3 characters and password at least 6 characters long.'}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM invitations WHERE invite_id = ?', (invite_id,))
        invitation = cursor.fetchone()

        if not invitation:
            return jsonify({'message': 'Invalid invite_id.'}), 401

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            return jsonify({'message': 'Username already exists. Try providing a different username.'}), 400

        cursor.execute('INSERT INTO users (username, password, invite_id) VALUES (?, ?, ?)', (username, password, invite_id))
        conn.commit()

    return jsonify({'message': 'User created.'}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)