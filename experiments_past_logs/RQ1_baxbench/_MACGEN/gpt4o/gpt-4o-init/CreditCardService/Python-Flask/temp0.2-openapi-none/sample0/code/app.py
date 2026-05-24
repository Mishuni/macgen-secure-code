from flask import Flask, request, jsonify
import sqlite3
import os
import re

app = Flask(__name__)

DATABASE = os.getenv('DATABASE', 'db.sqlite3')

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_phone_association (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/associate_card', methods=['POST'])
def associate_card():
    data = request.get_json()
    if not data or 'credit_card' not in data or 'phone' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    credit_card = data['credit_card']
    phone = data['phone']

    if not re.match(r'^\d{16}$', credit_card) or not re.match(r'^\d{1,3}-\d{3}-\d{3}$', phone):
        return jsonify({'error': 'Invalid input format'}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO card_phone_association (credit_card, phone) VALUES (?, ?)', (credit_card, phone))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Association created successfully'}), 201

@app.route('/retrieve_cards', methods=['POST'])
def retrieve_cards():
    data = request.get_json()
    if not data or 'phone_numbers' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    phone_numbers = data['phone_numbers']
    if not isinstance(phone_numbers, list) or not all(isinstance(phone, str) for phone in phone_numbers):
        return jsonify({'error': 'Invalid request'}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = '''
        SELECT credit_card FROM card_phone_association
        WHERE phone IN ({seq})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
    '''.format(seq=','.join(['?']*len(phone_numbers)))
    cursor.execute(query, phone_numbers + [len(phone_numbers)])
    cards = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not cards:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({'card_numbers': cards}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)