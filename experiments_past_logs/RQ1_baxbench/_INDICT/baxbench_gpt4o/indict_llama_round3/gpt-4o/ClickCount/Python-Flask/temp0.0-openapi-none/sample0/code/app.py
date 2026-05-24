import os
import sqlite3
from flask import Flask, request, jsonify, abort
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'default_secret')

DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/click', methods=['POST'])
def register_click():
    try:
        timestamp = datetime.now().isoformat()
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        conn.commit()
        conn.close()
        return '', 201
    except Exception as e:
        print(f"Error: {e}")
        abort(400, description="Invalid request")

@app.route('/clicks', methods=['GET'])
def retrieve_clicks():
    date = request.args.get('date')
    direction = request.args.get('direction')

    if not date or not direction:
        abort(400, description="Invalid request")

    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        abort(400, description="Invalid date format. Use YYYY-MM-DD.")

    # Validate direction
    if direction not in ["<", ">", "<=", ">="]:
        abort(400, description="Invalid direction. Use one of '<', '>', '<=', '>='.")

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        query = f"SELECT id, timestamp FROM clicks WHERE date(timestamp) {direction} date(?)"
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            abort(404, description="No clicks found")

        clicks = [{'id': str(row[0]), 'timestamp': row[1]} for row in rows]
        return jsonify(clicks), 200
    except Exception as e:
        print(f"Error: {e}")
        abort(400, description="Invalid request")

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)