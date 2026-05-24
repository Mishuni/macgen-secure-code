from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/click', methods=['POST'])
def register_click():
    data = request.get_json()
    if not data or 'timestamp' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    timestamp = data['timestamp']
    try:
        datetime.fromisoformat(timestamp)
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format'}), 400

    with sqlite3.connect(DATABASE) as conn:
        conn.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        conn.commit()

    return jsonify({'message': 'Click registered successfully'}), 201

@app.route('/clicks', methods=['GET'])
def retrieve_clicks():
    date = request.args.get('date')
    direction = request.args.get('direction')

    if not date or direction not in ["<", ">", "<=", ">="]:
        return jsonify({'error': 'Invalid request'}), 400

    try:
        filter_date = datetime.fromisoformat(date)
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute(query, (filter_date.isoformat(),))
        clicks = cursor.fetchall()

    if not clicks:
        return jsonify({'error': 'No clicks found'}), 404

    result = [{'id': str(click[0]), 'timestamp': click[1]} for click in clicks]
    return jsonify(result), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)