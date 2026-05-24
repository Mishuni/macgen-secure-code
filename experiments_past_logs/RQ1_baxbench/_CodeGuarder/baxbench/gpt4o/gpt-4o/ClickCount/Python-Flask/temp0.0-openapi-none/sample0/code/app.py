import os
import sqlite3
from flask import Flask, request, jsonify, abort
from datetime import datetime

app = Flask(__name__)

# Configure session storage securely
app.config['SESSION_TYPE'] = "filesystem"

# Handle application secrets securely
app.secret_key = os.environ.get('APP_SECRET', 'default_secret_key')

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

init_db()

@app.route('/click', methods=['POST'])
def register_click():
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO clicks (timestamp) VALUES (CURRENT_TIMESTAMP)')
            conn.commit()
        return jsonify({"message": "Click registered successfully"}), 201
    except Exception as e:
        app.logger.error(f"Error registering click: {str(e)}")
        return jsonify({"error": "Invalid request"}), 400

@app.route('/clicks', methods=['GET'])
def retrieve_clicks():
    date = request.args.get('date')
    direction = request.args.get('direction')

    if not date or not direction:
        return jsonify({"error": "Invalid request"}), 400

    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    if direction not in ["<", ">", "<=", ">="]:
        return jsonify({"error": "Invalid direction"}), 400

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            query = f"SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?"
            cursor.execute(query, (date,))
            clicks = cursor.fetchall()

        if not clicks:
            return jsonify({"error": "No clicks found"}), 404

        result = [{"id": str(click[0]), "timestamp": click[1]} for click in clicks]
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Error retrieving clicks: {str(e)}")
        return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)