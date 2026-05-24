from flask import Flask, request, jsonify
import sqlite3
import os
import re

app = Flask(__name__)
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credit_card TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        conn.commit()

def is_valid_credit_card(card):
    return re.match(r'^\d{16}$', card) is not None

def is_valid_phone(phone):
    return re.match(r'^\d{1}-\d{3}-\d{3}$', phone) is not None

@app.route('/associate_card', methods=['POST'])
def associate_card():
    data = request.get_json()
    credit_card = data.get('credit_card')
    phone = data.get('phone')

    if not credit_card or not phone or not is_valid_credit_card(credit_card) or not is_valid_phone(phone):
        return jsonify({'error': 'Invalid request'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO associations (credit_card, phone) VALUES (?, ?)', (credit_card, phone))
        conn.commit()

    return jsonify({'message': 'Association created successfully'}), 201

@app.route('/retrieve_cards', methods=['POST'])
def retrieve_cards():
    data = request.get_json()
    phone_numbers = data.get('phone_numbers')

    if not phone_numbers or not isinstance(phone_numbers, list) or not all(is_valid_phone(phone) for phone in phone_numbers):
        return jsonify({'error': 'Invalid request'}), 400

    placeholders = ', '.join('?' for _ in phone_numbers)
    query = f'''
        SELECT credit_card FROM associations
        WHERE phone IN ({placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = {len(phone_numbers)}
    '''

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, phone_numbers)
        results = cursor.fetchall()

    card_numbers = [row[0] for row in results]

    if not card_numbers:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({'card_numbers': card_numbers}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)