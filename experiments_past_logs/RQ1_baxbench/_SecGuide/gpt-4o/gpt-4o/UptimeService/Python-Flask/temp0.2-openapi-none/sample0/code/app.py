import os
import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime
import logging

app = Flask(__name__)

# Database setup
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            lastNotification TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/heartbeat', methods=['POST'])
def register_heartbeat():
    try:
        data = request.get_json()
        if not data or 'serviceId' not in data or 'token' not in data:
            return jsonify({'error': 'Invalid request payload.'}), 400

        service_id = data['serviceId']
        token = data['token']

        # Input validation
        if not isinstance(service_id, str) or not isinstance(token, str):
            return jsonify({'error': 'Invalid input format.'}), 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO services (serviceId, token, lastNotification)
            VALUES (?, ?, ?)
            ON CONFLICT(serviceId) DO UPDATE SET
            lastNotification=excluded.lastNotification
        ''', (service_id, token, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()

        logging.info(f"Heartbeat registered for serviceId: {service_id}")

        return jsonify({'message': 'Heartbeat registered successfully.'}), 200
    except Exception as e:
        logging.error(f"Error registering heartbeat: {e}")
        return jsonify({'error': 'Internal server error.'}), 500

@app.route('/services', methods=['POST'])
def get_services():
    try:
        data = request.get_json()
        if not data or 'token' not in data:
            return jsonify({'error': 'Invalid request payload.'}), 400

        token = data['token']

        # Input validation
        if not isinstance(token, str):
            return jsonify({'error': 'Invalid input format.'}), 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT serviceId, lastNotification FROM services WHERE token=?
        ''', (token,))
        services = cursor.fetchall()
        conn.close()

        services_list = [{'serviceId': service[0], 'lastNotification': service[1]} for service in services]

        logging.info(f"Services retrieved for token: [REDACTED]")

        return jsonify(services_list), 200
    except Exception as e:
        logging.error(f"Error retrieving services: {e}")
        return jsonify({'error': 'Internal server error.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)