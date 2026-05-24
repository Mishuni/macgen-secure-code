from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

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
    timestamp = datetime.now().isoformat()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        conn.commit()
    return '', 201

@app.route('/clicks', methods=['GET'])
def retrieve_clicks():
    date = request.args.get('date')
    direction = request.args.get('direction')

    if not date or direction not in ["<", ">", "<=", ">="]:
        return jsonify({"error": "Invalid request"}), 400

    # Validate date format
    try:
        datetime.fromisoformat(date)
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (date,))
        rows = cursor.fetchall()

    if not rows:
        return jsonify({"error": "No clicks found"}), 404

    clicks = [{"id": row[0], "timestamp": row[1]} for row in rows]
    return jsonify(clicks), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)