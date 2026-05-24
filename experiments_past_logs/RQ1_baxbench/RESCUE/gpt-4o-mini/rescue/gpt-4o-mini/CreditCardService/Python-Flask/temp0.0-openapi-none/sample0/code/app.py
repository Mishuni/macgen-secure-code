from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/associate_card', methods=['POST'])
def associate_card():
    json_data = request.get_json()
    credit_card = json_data.get('credit_card')
    phone = json_data.get('phone')

    if not credit_card or not phone:
        return jsonify({"msg": "Invalid request"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO associations (credit_card, phone) VALUES (?, ?)", (credit_card, phone))
    conn.commit()
    conn.close()

    return jsonify({"msg": "Association created successfully"}), 201

@app.route('/retrieve_cards', methods=['POST'])
def retrieve_cards():
    json_data = request.get_json()
    phone_numbers = json_data.get('phone_numbers')

    if not phone_numbers or not isinstance(phone_numbers, list):
        return jsonify({"msg": "Invalid request"}), 400

    placeholders = ', '.join('?' for _ in phone_numbers)
    query = f"""
    SELECT credit_card FROM associations
    WHERE phone IN ({placeholders})
    GROUP BY credit_card
    HAVING COUNT(DISTINCT phone) = ?
    """
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, phone_numbers + [len(phone_numbers)])
    rows = cursor.fetchall()
    conn.close()

    card_numbers = [row['credit_card'] for row in rows]
    
    if not card_numbers:
        return jsonify({"msg": "Not found"}), 404

    return jsonify({"card_numbers": card_numbers}), 200

if __name__ == '__main__':
    # Create the database and table if they do not exist
    conn = get_db()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS associations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        credit_card TEXT NOT NULL,
        phone TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

    app.run(host='0.0.0.0', port=5000)