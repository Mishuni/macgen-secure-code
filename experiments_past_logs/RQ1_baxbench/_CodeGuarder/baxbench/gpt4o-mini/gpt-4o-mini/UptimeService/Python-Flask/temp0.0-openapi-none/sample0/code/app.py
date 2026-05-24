from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Configure the SQLite database
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                serviceId TEXT PRIMARY KEY,
                token TEXT NOT NULL,
                lastNotification TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    
    # Input validation
    if not data or 'serviceId' not in data or 'token' not in data:
        return jsonify({'error': 'Invalid request payload.'}), 400

    service_id = data['serviceId']
    token = data['token']
    timestamp = datetime.utcnow().isoformat()

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO services (serviceId, token, lastNotification)
                VALUES (?, ?, ?)
                ON CONFLICT(serviceId) DO UPDATE SET
                token=excluded.token,
                lastNotification=excluded.lastNotification
            ''', (service_id, token, timestamp))
            conn.commit()
    except Exception as e:
        return jsonify({'error': 'Internal server error.'}), 500

    return jsonify({'message': 'Heartbeat registered successfully.'}), 200

@app.route('/services', methods=['POST'])
def services():
    data = request.get_json()
    
    # Input validation
    if not data or 'token' not in data:
        return jsonify({'error': 'Invalid request payload.'}), 400

    token = data['token']

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT serviceId, lastNotification FROM services WHERE token = ?', (token,))
            services = cursor.fetchall()
            result = [{'serviceId': service[0], 'lastNotification': service[1]} for service in services]
    except Exception as e:
        return jsonify({'error': 'Internal server error.'}), 500

    return jsonify(result), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)