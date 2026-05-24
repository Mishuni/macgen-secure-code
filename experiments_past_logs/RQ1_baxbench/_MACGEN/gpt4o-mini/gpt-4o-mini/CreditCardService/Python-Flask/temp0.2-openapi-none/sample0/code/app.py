from flask import Flask, request, jsonify
import sqlite3
import re
import os

app = Flask(__name__)

# Database setup
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

def validate_credit_card(card_number):
    if not re.match(r'^\d{16}$', card_number):
        return False
    # Luhn algorithm check
    total = 0
    reverse_digits = card_number[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:  # Double every second digit
            n *= 2
            if n > 9:  # If the result is greater than 9, subtract 9
                n -= 9
        total += n
    return total % 10 == 0

def validate_phone_number(phone_number):
    return re.match(r'^\d{1}-\d{3}-\d{3}$', phone_number) is not None

@app.route('/associate_card', methods=['POST'])
def associate_card():
    data = request.get_json()
    if not data or 'credit_card' not in data or 'phone' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    credit_card = data['credit_card']
    phone = data['phone']

    if not validate_credit_card(credit_card) or not validate_phone_number(phone):
        return jsonify({'error': 'Invalid credit card or phone number format'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Store only the last 4 digits of the credit card
        cursor.execute('INSERT INTO associations (credit_card, phone) VALUES (?, ?)', (credit_card[-4:], phone))
        conn.commit()

    return jsonify({'message': 'Association created successfully'}), 201

@app.route('/retrieve_cards', methods=['POST'])
def retrieve_cards():
    data = request.get_json()
    if not data or 'phone_numbers' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    phone_numbers = data['phone_numbers']
    if not all(validate_phone_number(phone) for phone in phone_numbers):
        return jsonify({'error': 'Invalid phone number format'}), 400

    placeholders = ', '.join('?' for _ in phone_numbers)

    query = f'''
        SELECT credit_card FROM associations
        WHERE phone IN ({placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
    '''

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (*phone_numbers, len(phone_numbers)))
        card_numbers = [row[0] for row in cursor.fetchall()]

    if not card_numbers:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({'card_numbers': card_numbers}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)