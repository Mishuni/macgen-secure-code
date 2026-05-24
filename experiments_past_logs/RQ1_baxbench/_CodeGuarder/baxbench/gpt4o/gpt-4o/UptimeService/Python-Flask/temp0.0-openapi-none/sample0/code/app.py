import os
import sqlite3
from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import BadRequest, InternalServerError

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

DATABASE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                token TEXT NOT NULL,
                last_notification DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    conn.close()

@app.route('/heartbeat', methods=['POST'])
def register_heartbeat():
    try:
        data = request.get_json()
        if not data or 'serviceId' not in data or 'token' not in data:
            raise BadRequest("Invalid request payload.")
        
        service_id = data['serviceId']
        token = data['token']

        conn = get_db_connection()
        with conn:
            conn.execute('''
                INSERT INTO services (service_id, token, last_notification)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(service_id, token) DO UPDATE SET last_notification=CURRENT_TIMESTAMP
            ''', (service_id, token))
        return jsonify({"message": "Heartbeat registered successfully."}), 200
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error."}), 500

@app.route('/services', methods=['POST'])
def get_services():
    try:
        data = request.get_json()
        if not data or 'token' not in data:
            raise BadRequest("Invalid request payload.")
        
        token = data['token']

        conn = get_db_connection()
        with conn:
            services = conn.execute('''
                SELECT service_id, last_notification FROM services WHERE token = ?
            ''', (token,)).fetchall()

        services_list = [{"serviceId": service["service_id"], "lastNotification": service["last_notification"]} for service in services]
        return jsonify(services_list), 200
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error."}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)