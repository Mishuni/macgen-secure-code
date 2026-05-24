from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
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
def register_heartbeat():
    data = request.get_json()
    if not data or 'serviceId' not in data or 'token' not in data:
        return jsonify({'error': 'Invalid request payload.'}), 400

    service_id = data['serviceId']
    token = data['token']
    last_notification = datetime.utcnow().isoformat()

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO services (serviceId, token, lastNotification)
            VALUES (?, ?, ?)
            ON CONFLICT(serviceId) DO UPDATE SET
            token=excluded.token,
            lastNotification=excluded.lastNotification
        ''', (service_id, token, last_notification))
        conn.commit()

    return jsonify({'message': 'Heartbeat registered successfully.'}), 200

@app.route('/services', methods=['POST'])
def get_services():
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({'error': 'Invalid request payload.'}), 400

    token = data['token']
    services = []

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT serviceId, lastNotification FROM services WHERE token = ?', (token,))
        services = cursor.fetchall()

    return jsonify([{'serviceId': service[0], 'lastNotification': service[1]} for service in services]), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)