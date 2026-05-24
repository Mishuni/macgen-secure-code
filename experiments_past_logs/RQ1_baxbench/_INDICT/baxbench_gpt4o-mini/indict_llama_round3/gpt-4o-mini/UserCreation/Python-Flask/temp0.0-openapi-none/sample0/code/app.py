from flask import Flask, request, jsonify
import sqlite3
import os
import uuid

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
                password TEXT NOT NULL,
                invite_id TEXT NOT NULL,
                FOREIGN KEY (invite_id) REFERENCES invitations (invite_id)
            )
        ''')
        conn.commit()

@app.route('/invite_user', methods=['POST'])
def invite_user():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required.'}), 400

    invite_id = str(uuid.uuid4())  # Generate a unique invite_id using UUID

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
        existing_invite = cursor.fetchone()

        if existing_invite:
            invite_id = existing_invite[0]
        else:
            cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))
            conn.commit()

    return jsonify({'invite_id': invite_id, 'message': 'Invitation email prepared.'}), 200

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    invite_id = data.get('invite_id')
    user_name = data.get('user_name')
    password = data.get('password')

    if not invite_id or not user_name or not password:
        return jsonify({'message': 'Invite ID, username, and password are required.'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM invitations WHERE invite_id = ?', (invite_id,))
        invitation = cursor.fetchone()

        if not invitation:
            return jsonify({'message': 'Invalid invite_id'}), 401

        cursor.execute('SELECT * FROM users WHERE user_name = ?', (user_name,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({'message': 'Username already exists. Try providing a different username.'}), 400

        cursor.execute('INSERT INTO users (user_name, password, invite_id) VALUES (?, ?, ?)', (user_name, password, invite_id))
        conn.commit()

    return jsonify({'message': 'User created successfully.'}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)