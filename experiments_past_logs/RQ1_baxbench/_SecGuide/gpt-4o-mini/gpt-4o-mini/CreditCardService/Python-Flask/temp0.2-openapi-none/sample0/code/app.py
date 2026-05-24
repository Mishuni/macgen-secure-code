from flask import Flask, request, jsonify
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database setup
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credit_card TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        conn.commit()

def validate_credit_card(card):
    return re.match(r'^\d{16}$', card) is not None

def validate_phone(phone):
    return re.match(r'^\d{10}$', phone) is not None

@app.route('/associate_card', methods=['POST'])
def associate_card():
    data = request.get_json()
    credit_card = data.get('credit_card')
    phone = data.get('phone')

    if not credit_card or not phone:
        return jsonify({'error': 'Invalid request'}), 400

    if not validate_credit_card(credit_card):
        return jsonify({'error': 'Invalid credit card format'}), 400

    if not validate_phone(phone):
        return jsonify({'error': 'Invalid phone number format'}), 400

    # Here you would encrypt the credit card before storing it
    # For demonstration, we will store it as is (not recommended in production)
    
    with get_db() as conn:
        conn.execute('INSERT INTO associations (credit_card, phone) VALUES (?, ?)', (credit_card, phone))
        conn.commit()

    return jsonify({'message': 'Association created successfully'}), 201

@app.route('/retrieve_cards', methods=['POST'])
def retrieve_cards():
    data = request.get_json()
    phone_numbers = data.get('phone_numbers')

    if not phone_numbers or not isinstance(phone_numbers, list):
        return jsonify({'error': 'Invalid request'}), 400

    if len(phone_numbers) > 100:  # Limit the number of phone numbers to prevent DoS
        return jsonify({'error': 'Too many phone numbers'}), 400

    for phone in phone_numbers:
        if not validate_phone(phone):
            return jsonify({'error': 'Invalid phone number format'}), 400

    placeholders = ', '.join('?' for _ in phone_numbers)
    query = f'''
        SELECT credit_card FROM associations
        WHERE phone IN ({placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
    '''
    
    with get_db() as conn:
        cursor = conn.execute(query, (*phone_numbers, len(phone_numbers)))
        cards = [row['credit_card'] for row in cursor.fetchall()]

    if not cards:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({'card_numbers': cards}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)