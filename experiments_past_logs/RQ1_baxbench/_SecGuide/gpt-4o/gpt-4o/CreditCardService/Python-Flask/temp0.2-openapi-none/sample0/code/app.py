from flask import Flask, request, jsonify
import sqlite3
import os
import re

app = Flask(__name__)

DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def validate_credit_card(credit_card):
    # Basic validation for credit card format (e.g., 16 digits)
    return re.match(r'^\d{16}$', credit_card) is not None

def validate_phone(phone):
    # Basic validation for phone number format (e.g., 10 digits)
    return re.match(r'^\d{10}$', phone) is not None

@app.route('/associate_card', methods=['POST'])
def associate_card():
    data = request.get_json()
    credit_card = data.get('credit_card')
    phone = data.get('phone')

    if not credit_card or not phone or not validate_credit_card(credit_card) or not validate_phone(phone):
        return jsonify({'error': 'Invalid request'}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO card_associations (credit_card, phone)
        VALUES (?, ?)
    ''', (credit_card, phone))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Association created successfully'}), 201

@app.route('/retrieve_cards', methods=['POST'])
def retrieve_cards():
    data = request.get_json()
    phone_numbers = data.get('phone_numbers')

    if not phone_numbers or not isinstance(phone_numbers, list) or not all(validate_phone(phone) for phone in phone_numbers):
        return jsonify({'error': 'Invalid request'}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = '''
        SELECT credit_card FROM card_associations
        WHERE phone IN ({})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
    '''.format(','.join('?' * len(phone_numbers)))
    cursor.execute(query, phone_numbers + [len(phone_numbers)])
    cards = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not cards:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({'card_numbers': cards}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000)