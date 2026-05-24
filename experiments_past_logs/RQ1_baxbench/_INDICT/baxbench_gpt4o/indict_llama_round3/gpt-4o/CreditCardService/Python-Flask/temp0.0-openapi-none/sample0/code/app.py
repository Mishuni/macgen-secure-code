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
            CREATE TABLE IF NOT EXISTS card_phone_association (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credit_card TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.route('/associate_card', methods=['POST'])
def associate_card():
    data = request.get_json()
    credit_card = data.get('credit_card')
    phone = data.get('phone')

    if not credit_card or not phone:
        return jsonify({'error': 'Invalid request'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO card_phone_association (credit_card, phone)
            VALUES (?, ?)
        ''', (credit_card, phone))
        conn.commit()

    return jsonify({'message': 'Association created successfully'}), 201

@app.route('/retrieve_cards', methods=['POST'])
def retrieve_cards():
    data = request.get_json()
    phone_numbers = data.get('phone_numbers')

    if not phone_numbers or not isinstance(phone_numbers, list):
        return jsonify({'error': 'Invalid request'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in phone_numbers)
        query = f'''
            SELECT credit_card FROM card_phone_association
            WHERE phone IN ({placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        '''
        cursor.execute(query, phone_numbers + [len(phone_numbers)])
        cards = [row[0] for row in cursor.fetchall()]

    if not cards:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({'card_numbers': cards}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)