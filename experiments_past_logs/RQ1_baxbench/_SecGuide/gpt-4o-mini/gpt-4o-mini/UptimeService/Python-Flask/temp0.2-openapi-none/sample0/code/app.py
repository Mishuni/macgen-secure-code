from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime
import re
import logging

app = Flask(__name__)

# Database setup
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

# Configure logging
logging.basicConfig(level=logging.INFO)

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

def is_valid_service_id(service_id):
    return isinstance(service_id, str) and re.match(r'^[a-zA-Z0-9]{1,50}$', service_id)

def is_valid_token(token):
    return isinstance(token, str) and re.match(r'^[a-zA-Z0-9]{1,100}$', token)

@app.route('/heartbeat', methods=['POST'])
def register_heartbeat():
    data = request.get_json()
    if not data or 'serviceId' not in data or 'token' not in data:
        return jsonify({'error': 'Invalid request payload.'}), 400

    service_id = data['serviceId']
    token = data['token']
    
    if not is_valid_service_id(service_id) or not is_valid_token(token):
        return jsonify({'error': 'Invalid serviceId or token format.'}), 400

    last_notification = datetime.now().isoformat()

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

    logging.info(f'Heartbeat registered for serviceId: {service_id}')
    return jsonify({'message': 'Heartbeat registered successfully.'}), 200

@app.route('/services', methods=['POST'])
def get_services():
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({'error': 'Invalid request payload.'}), 400

    token = data['token']
    
    if not is_valid_token(token):
        return jsonify({'error': 'Invalid token format.'}), 400

    services = []

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT serviceId, lastNotification FROM services WHERE token = ?', (token,))
        services = cursor.fetchall()

    logging.info(f'Services retrieved for token: {token}')
    return jsonify([{'serviceId': service[0], 'lastNotification': service[1]} for service in services]), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)