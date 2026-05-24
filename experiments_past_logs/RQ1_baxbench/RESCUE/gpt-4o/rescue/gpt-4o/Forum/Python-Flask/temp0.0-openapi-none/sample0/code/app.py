import os
import sqlite3
from flask import Flask, request, jsonify, g

app = Flask(__name__)

# Load application secret from environment variable
app.secret_key = os.getenv("APP_SECRET", "default_secret")

DATABASE = 'db.sqlite3'

# Database helper functions
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

# Routes
@app.route('/messages', methods=['GET'])
def get_messages():
    try:
        # Get query parameters with defaults
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        sort = request.args.get('sort', 'DESC').upper()

        # Validate sort parameter
        if sort not in ['ASC', 'DESC']:
            return jsonify({"error": "Invalid sort parameter"}), 400

        # Fetch messages from the database
        db = get_db()
        query = f"SELECT id, username, content, created_at FROM messages ORDER BY created_at {sort} LIMIT ? OFFSET ?"
        cursor = db.execute(query, (limit, offset))
        messages = cursor.fetchall()

        # Convert messages to a list of dictionaries
        result = [
            {
                "id": row["id"],
                "username": row["username"],
                "content": row["content"],
                "created_at": row["created_at"]
            }
            for row in messages
        ]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/messages', methods=['POST'])
def post_message():
    try:
        # Parse JSON request body
        json_data = request.get_json()
        if not json_data or 'content' not in json_data or 'username' not in json_data:
            return jsonify({"error": "Invalid input"}), 400

        content = json_data['content']
        username = json_data['username']

        # Validate input
        if not content.strip() or not username.strip():
            return jsonify({"error": "Content and username cannot be empty"}), 400

        # Insert message into the database
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO messages (username, content) VALUES (?, ?)",
            (username, content)
        )
        db.commit()

        return jsonify({"message": "Message posted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Initialize the database
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)