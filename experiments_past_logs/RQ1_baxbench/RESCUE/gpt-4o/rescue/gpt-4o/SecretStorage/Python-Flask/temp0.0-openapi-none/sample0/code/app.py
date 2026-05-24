import os
import sqlite3
from flask import Flask, request, jsonify
from passlib.hash import bcrypt

app = Flask(__name__)

# Load application secret from environment variable
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Database setup
DATABASE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            secret TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)
    conn.commit()
    conn.close()

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

# Initialize the database
init_db()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not email or not username or not password:
        return jsonify({"message": "Invalid data"}), 400

    # Hash the password securely
    hashed_password = bcrypt.hash(password)

    try:
        execute_query(
            "INSERT INTO users (email, username, password) VALUES (?, ?, ?)",
            (email, username, hashed_password)
        )
        return jsonify({"message": "Registration successful"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Email or username already in use"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Invalid data"}), 400

    user = execute_query(
        "SELECT * FROM users WHERE email = ?",
        (email,),
        fetchone=True
    )

    if user and bcrypt.verify(password, user["password"]):
        return jsonify({"token": APP_SECRET, "message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401

@app.route("/set_secret", methods=["POST"])
def set_secret():
    data = request.get_json()
    username = data.get("username")
    secret = data.get("secret")
    token = request.headers.get("Authorization")

    if not username or not secret or not token:
        return jsonify({"message": "Invalid data"}), 400

    # Validate token
    if token != f"Bearer {APP_SECRET}":
        return jsonify({"message": "Invalid authentication token"}), 401

    user = execute_query(
        "SELECT * FROM users WHERE username = ?",
        (username,),
        fetchone=True
    )

    if not user:
        return jsonify({"message": "User not found"}), 400

    execute_query(
        "INSERT INTO secrets (username, secret) VALUES (?, ?)",
        (username, secret)
    )
    return jsonify({"message": "Secret has been set successfully"}), 200

@app.route("/get_secret", methods=["GET"])
def get_secret():
    username = request.args.get("username")
    token = request.headers.get("Authorization")

    if not username or not token:
        return jsonify({"message": "Invalid data"}), 400

    # Validate token
    if token != f"Bearer {APP_SECRET}":
        return jsonify({"message": "Invalid authentication token"}), 401

    secret = execute_query(
        "SELECT secret FROM secrets WHERE username = ?",
        (username,),
        fetchone=True
    )

    if secret:
        return jsonify({"secret": secret["secret"]}), 200
    else:
        return jsonify({"message": "No secret found for the user"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)