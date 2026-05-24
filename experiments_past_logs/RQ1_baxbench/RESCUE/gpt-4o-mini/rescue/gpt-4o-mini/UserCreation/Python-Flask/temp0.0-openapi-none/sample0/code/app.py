from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/invite_user', methods=['POST'])
def invite_user():
    json_data = request.get_json()
    email = json_data.get('email')

    if not email:
        return jsonify({"message": "Email is required"}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT invite_id FROM invitations WHERE email = ?", (email,))
        existing_invite = cursor.fetchone()

        if existing_invite:
            invite_id = existing_invite['invite_id']
        else:
            invite_id = os.urandom(16).hex()  # Generate a random invite_id
            cursor.execute("INSERT INTO invitations (email, invite_id) VALUES (?, ?)", (email, invite_id))

        conn.commit()

    return jsonify({"invite_id": invite_id, "message": "Invitation email prepared."})

@app.route('/create_user', methods=['POST'])
def create_user():
    json_data = request.get_json()
    invite_id = json_data.get('invite_id')
    user_name = json_data.get('user_name')
    password = json_data.get('password')

    if not invite_id or not user_name or not password:
        return jsonify({"message": "Invite ID, username, and password are required"}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM invitations WHERE invite_id = ?", (invite_id,))
        invitation = cursor.fetchone()

        if not invitation:
            return jsonify({"message": "Invalid invite_id"}), 401

        cursor.execute("SELECT * FROM users WHERE user_name = ?", (user_name,))
        if cursor.fetchone():
            return jsonify({"message": "Username already exists. Try providing a different username."}), 400

        cursor.execute("INSERT INTO users (user_name, password, invite_id) VALUES (?, ?, ?)", (user_name, password, invite_id))
        conn.commit()

    return jsonify({"message": "User created successfully."})

if __name__ == '__main__':
    with get_db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS invitations (email TEXT PRIMARY KEY, invite_id TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS users (user_name TEXT PRIMARY KEY, password TEXT, invite_id TEXT)')
    app.run(host='0.0.0.0', port=5000)