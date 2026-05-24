from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                serviceId TEXT PRIMARY KEY,
                token TEXT NOT NULL,
                lastNotification DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

@app.route('/heartbeat', methods=['POST'])
def register_heartbeat():
    json_data = request.get_json()
    
    if not json_data or 'serviceId' not in json_data or 'token' not in json_data:
        return jsonify({"msg": "Invalid request payload."}), 400

    service_id = json_data['serviceId']
    token = json_data['token']

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO services (serviceId, token, lastNotification)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(serviceId) DO UPDATE SET
            token = excluded.token,
            lastNotification = CURRENT_TIMESTAMP
        ''', (service_id, token))
        conn.commit()

    return jsonify({"msg": "Heartbeat registered successfully."}), 200

@app.route('/services', methods=['POST'])
def get_services():
    json_data = request.get_json()
    
    if not json_data or 'token' not in json_data:
        return jsonify({"msg": "Invalid request payload."}), 400

    token = json_data['token']

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT serviceId, lastNotification FROM services WHERE token = ?
        ''', (token,))
        services = cursor.fetchall()

    service_list = [{"serviceId": service[0], "lastNotification": service[1]} for service in services]

    return jsonify(service_list), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)