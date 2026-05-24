import os
import sqlite3
from flask import Flask, request, jsonify, abort

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET', 'default_secret')

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
    data = request.get_json()
    if not data or 'timestamp' not in data:
        abort(400, description="Invalid request: 'timestamp' is required.")
    
    timestamp = data['timestamp']
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        conn.commit()
    
    return jsonify({"message": "Click registered successfully"}), 201

@app.route('/clicks', methods=['GET'])
def retrieve_clicks():
    date = request.args.get('date')
    direction = request.args.get('direction')

    if not date or direction not in ["<", ">", "<=", ">="]:
        abort(400, description="Invalid request: 'date' and 'direction' are required.")

    query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (date,))
        clicks = cursor.fetchall()

    if not clicks:
        abort(404, description="No clicks found.")

    result = [{"id": click[0], "timestamp": click[1]} for click in clicks]
    return jsonify(result), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)