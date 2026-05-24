import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['DATABASE'] = 'db.sqlite3'
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET', 'default_secret')

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                invite_id TEXT UNIQUE NOT NULL,
                used INTEGER DEFAULT 0
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/invite_user', methods=['POST'])
def invite_user():
    data = request.get_json()
    email = data.get('email')

    if not email or '@' not in email:
        return jsonify({'message': 'Invalid email format.'}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
        invitation = cursor.fetchone()

        if invitation:
            invite_id = invitation['invite_id']
        else:
            invite_id = os.urandom(16).hex()  # Generate a unique invite ID
            cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))

        conn.commit()

    return jsonify({'invite_id': invite_id, 'message': 'Invitation email prepared.'}), 200

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    invite_id = data.get('invite_id')
    username = data.get('user_name')
    password = data.get('password')

    if not invite_id or not username or not password:
        return jsonify({'message': 'All fields are required.'}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM invitations WHERE invite_id = ? AND used = 0', (invite_id,))
        invitation = cursor.fetchone()

        if not invitation:
            return jsonify({'message': 'Invalid invite_id'}), 401

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            return jsonify({'message': 'Username already exists. Try providing a different username.'}), 400

        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        cursor.execute('UPDATE invitations SET used = 1 WHERE id = ?', (invitation['id'],))
        conn.commit()

    return jsonify({'message': 'User created successfully.'}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)