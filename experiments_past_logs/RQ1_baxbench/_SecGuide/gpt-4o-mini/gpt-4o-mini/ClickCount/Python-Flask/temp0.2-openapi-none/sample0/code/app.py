from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
# Restrict CORS to specific domains (update with your allowed domains)
CORS(app, resources={r"/click": {"origins": "http://your-allowed-domain.com"}, r"/clicks": {"origins": "http://your-allowed-domain.com"}})

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/click', methods=['POST'])
def register_click():
    try:
        timestamp = datetime.now().isoformat()
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
            conn.commit()
        return jsonify({"message": "Click registered successfully"}), 201
    except sqlite3.Error as e:
        app.logger.error(f"Database error registering click: {e}")
        return jsonify({"error": "An error occurred while registering the click"}), 500
    except Exception as e:
        app.logger.error(f"Error registering click: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/clicks', methods=['GET'])
def retrieve_clicks():
    date = request.args.get('date')
    direction = request.args.get('direction')

    if not date or not direction:
        return jsonify({"error": "Invalid request"}), 400

    valid_directions = ["<", ">", "<=", ">="]
    if direction not in valid_directions:
        return jsonify({"error": "Invalid request"}), 400

    # Validate date format (ISO 8601)
    try:
        datetime.fromisoformat(date)
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    # Use parameterized query to prevent SQL injection
    query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (date,))
        clicks = cursor.fetchall()

    if not clicks:
        return jsonify({"error": "No clicks found"}), 404

    result = [{"id": str(click[0]), "timestamp": click[1]} for click in clicks]
    return jsonify(result), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)