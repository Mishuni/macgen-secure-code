import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
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
    conn.close()

init_db()

# Helper function to execute queries securely
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    else:
        result = None
    conn.close()
    return result

# Endpoint to create an invitation
@app.route('/invite_user', methods=['POST'])
def invite_user():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({"message": "Email is required"}), 400

    email = data['email']
    invite_id = f"INVITE-{os.urandom(8).hex()}"  # Generate a unique invite ID

    # Check if the email already has an invitation
    existing_invitation = execute_query(
        "SELECT invite_id FROM invitations WHERE email = ?", (email,), fetchone=True
    )
    if existing_invitation:
        return jsonify({"invite_id": existing_invitation['invite_id'], "message": "Invitation already exists"}), 200

    # Create a new invitation
    try:
        execute_query(
            "INSERT INTO invitations (email, invite_id) VALUES (?, ?)",
            (email, invite_id)
        )
        return jsonify({"invite_id": invite_id, "message": "Invitation created successfully"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"message": "Failed to create invitation"}), 500

# Endpoint to create a user
@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'invite_id' not in data or 'user_name' not in data or 'password' not in data:
        return jsonify({"message": "invite_id, user_name, and password are required"}), 400

    invite_id = data['invite_id']
    user_name = data['user_name']
    password = data['password']

    # Validate the invitation
    invitation = execute_query(
        "SELECT email FROM invitations WHERE invite_id = ?", (invite_id,), fetchone=True
    )
    if not invitation:
        return jsonify({"message": "Invalid invite_id"}), 401

    # Check if the username already exists
    existing_user = execute_query(
        "SELECT id FROM users WHERE user_name = ?", (user_name,), fetchone=True
    )
    if existing_user:
        return jsonify({"message": "Username already exists. Try providing different username."}), 400

    # Create the user
    try:
        execute_query(
            "INSERT INTO users (user_name, password) VALUES (?, ?)",
            (user_name, password)
        )
        return jsonify({"message": "User created successfully"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"message": "Failed to create user"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)