import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

DATABASE = 'db.sqlite3'
APP_SECRET = os.getenv('APP_SECRET', 'default_secret')

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

@app.route('/heartbeat', methods=['POST'])
def register_heartbeat():
    try:
        data = request.json
        service_id = data.get('serviceId')
        token = data.get('token')

        if not service_id or not token:
            return jsonify({'error': 'Invalid request payload.'}), 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO services (serviceId, token, lastNotification)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(serviceId) DO UPDATE SET
            lastNotification = datetime('now')
        ''', (service_id, token))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Heartbeat registered successfully.'}), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error.'}), 500

@app.route('/services', methods=['POST'])
def get_services():
    try:
        data = request.json
        token = data.get('token')

        if not token:
            return jsonify({'error': 'Invalid request payload.'}), 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT serviceId, lastNotification FROM services WHERE token = ?
        ''', (token,))
        services = [{'serviceId': row[0], 'lastNotification': row[1]} for row in cursor.fetchall()]
        conn.close()

        return jsonify(services), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error.'}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)