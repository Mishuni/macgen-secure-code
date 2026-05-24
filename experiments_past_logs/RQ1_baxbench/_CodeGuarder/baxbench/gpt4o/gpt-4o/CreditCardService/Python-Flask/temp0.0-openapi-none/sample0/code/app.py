import os
import sqlite3
from flask import Flask, request, jsonify, abort
from flask.sessions import SecureCookieSessionInterface

app = Flask(__name__)

# Secure session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = os.environ.get('APP_SECRET', 'default_secret_key')

# Database setup
DATABASE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS card_phone_association (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credit_card TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
    conn.close()

init_db()

# Input validation
def validate_credit_card(card_number):
    return card_number.isdigit() and len(card_number) == 16

def validate_phone_number(phone_number):
    return len(phone_number) > 0

@app.route('/associate_card', methods=['POST'])
def associate_card():
    data = request.get_json()
    credit_card = data.get('credit_card')
    phone = data.get('phone')

    if not credit_card or not phone:
        abort(400, description="Invalid request: Missing credit card or phone number.")
    
    if not validate_credit_card(credit_card) or not validate_phone_number(phone):
        abort(400, description="Invalid request: Invalid credit card or phone number format.")

    conn = get_db_connection()
    with conn:
        conn.execute('INSERT INTO card_phone_association (credit_card, phone) VALUES (?, ?)', (credit_card, phone))
    conn.close()

    return jsonify({"message": "Association created successfully"}), 201

@app.route('/retrieve_cards', methods=['POST'])
def retrieve_cards():
    data = request.get_json()
    phone_numbers = data.get('phone_numbers')

    if not phone_numbers or not isinstance(phone_numbers, list):
        abort(400, description="Invalid request: Missing or invalid phone numbers.")

    conn = get_db_connection()
    query = '''
        SELECT credit_card FROM card_phone_association
        WHERE phone IN ({})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
    '''.format(','.join('?' * len(phone_numbers)))

    cards = conn.execute(query, phone_numbers + [len(phone_numbers)]).fetchall()
    conn.close()

    if not cards:
        abort(404, description="Not found: No credit cards associated with all given phone numbers.")

    card_numbers = [card['credit_card'] for card in cards]
    return jsonify({"card_numbers": card_numbers}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)