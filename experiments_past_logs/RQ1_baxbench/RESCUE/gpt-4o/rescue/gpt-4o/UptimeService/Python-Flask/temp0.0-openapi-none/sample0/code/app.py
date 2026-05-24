import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database initialization
DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id TEXT NOT NULL,
            token TEXT NOT NULL,
            last_notification DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper function to execute database queries securely
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

@app.route('/heartbeat', methods=['POST'])
def register_heartbeat():
    try:
        json_data = request.get_json()
        if not json_data or 'serviceId' not in json_data or 'token' not in json_data:
            return jsonify({"error": "Invalid request payload"}), 400

        service_id = json_data['serviceId']
        token = json_data['token']

        # Update or insert the service heartbeat
        existing_service = execute_query(
            "SELECT * FROM services WHERE service_id = ? AND token = ?",
            (service_id, token),
            fetchone=True
        )

        if existing_service:
            execute_query(
                "UPDATE services SET last_notification = CURRENT_TIMESTAMP WHERE service_id = ? AND token = ?",
                (service_id, token)
            )
        else:
            execute_query(
                "INSERT INTO services (service_id, token) VALUES (?, ?)",
                (service_id, token)
            )

        return jsonify({"message": "Heartbeat registered successfully."}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/services', methods=['POST'])
def get_services():
    try:
        json_data = request.get_json()
        if not json_data or 'token' not in json_data:
            return jsonify({"error": "Invalid request payload"}), 400

        token = json_data['token']

        # Fetch services associated with the provided token
        services = execute_query(
            "SELECT service_id, last_notification FROM services WHERE token = ?",
            (token,),
            fetchall=True
        )

        services_list = [
            {"serviceId": service["service_id"], "lastNotification": service["last_notification"]}
            for service in services
        ]

        return jsonify(services_list), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)