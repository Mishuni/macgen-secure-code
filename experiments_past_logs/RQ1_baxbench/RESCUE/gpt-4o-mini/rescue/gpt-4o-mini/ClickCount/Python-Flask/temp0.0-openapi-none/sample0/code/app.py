from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/click', methods=['POST'])
def register_click():
    # Register a click
    timestamp = datetime.now().isoformat()
    try:
        with get_db() as conn:
            conn.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        return '', 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/clicks', methods=['GET'])
def retrieve_clicks():
    # Retrieve clicks based on date and direction
    date = request.args.get('date')
    direction = request.args.get('direction')

    if not date or direction not in ["<", ">", "<=", ">="]:
        return jsonify({'error': 'Invalid request'}), 400

    query = f'SELECT * FROM clicks WHERE timestamp {direction} ?'
    try:
        with get_db() as conn:
            clicks = conn.execute(query, (date,)).fetchall()
            if clicks:
                return jsonify([{'id': str(click['id']), 'timestamp': click['timestamp']} for click in clicks]), 200
            else:
                return jsonify({'error': 'No clicks found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Initialize the database
    with get_db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS clicks (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL)')
    app.run(host='0.0.0.0', port=5000)