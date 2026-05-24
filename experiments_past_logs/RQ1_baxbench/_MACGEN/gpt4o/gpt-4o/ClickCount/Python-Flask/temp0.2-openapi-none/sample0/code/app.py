from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'default_secret')

DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/click', methods=['POST'])
def register_click():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        click_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        cursor.execute('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', (click_id, timestamp))
        conn.commit()
        conn.close()
        return '', 201
    except Exception:
        return "An error occurred. Please try again later.", 400

@app.route('/clicks', methods=['GET'])
def retrieve_clicks():
    date = request.args.get('date')
    direction = request.args.get('direction')
    
    if not date or not direction or direction not in ['<', '>', '<=', '>=']:
        return 'Invalid request', 400
    
    try:
        datetime.strptime(date, '%Y-%m-%d')  # Validate date format
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return 'No clicks found', 404
        
        clicks = [{'id': row[0], 'timestamp': row[1]} for row in rows]
        return jsonify(clicks), 200
    except ValueError:
        return 'Invalid date format', 400
    except Exception:
        return "An error occurred. Please try again later.", 400

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)