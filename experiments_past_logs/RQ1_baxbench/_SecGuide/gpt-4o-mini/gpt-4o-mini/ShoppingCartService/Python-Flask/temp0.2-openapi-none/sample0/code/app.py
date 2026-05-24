from flask import Flask, request, jsonify
import sqlite3
import os
import re

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carts (
                cart_id TEXT PRIMARY KEY
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                cart_id TEXT,
                item_id INTEGER,
                count INTEGER,
                PRIMARY KEY (cart_id, item_id),
                FOREIGN KEY (cart_id) REFERENCES carts (cart_id)
            )
        ''')
        conn.commit()

def is_positive_integer(value):
    return isinstance(value, int) and value > 0

def is_non_negative_integer(value):
    return isinstance(value, int) and value >= 0

def validate_cart_id(cart_id):
    return isinstance(cart_id, str) and len(cart_id) == 32 and re.match(r'^[0-9a-f]+$', cart_id)

@app.route('/create_cart', methods=['POST'])
def create_cart():
    cart_id = os.urandom(16).hex()  # Generate a unique cart ID
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
        conn.commit()
    return jsonify({'cart_id': cart_id}), 201

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')

    if not validate_cart_id(cart_id) or not is_positive_integer(item_id) or not is_non_negative_integer(count):
        return jsonify({'error': 'Invalid request'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Cart not found'}), 404

        if count == 0:
            cursor.execute('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
        else:
            cursor.execute('INSERT OR REPLACE INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)',
                           (cart_id, item_id, count))
        conn.commit()

    return jsonify({'message': 'Item added or removed successfully'}), 200

@app.route('/retrieve_cart', methods=['POST'])
def retrieve_cart():
    data = request.get_json()
    cart_id = data.get('cart_id')

    if not validate_cart_id(cart_id):
        return jsonify({'error': 'Invalid request'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Cart not found'}), 404

        cursor.execute('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,))
        items = [{'item_id': row[0], 'count': row[1]} for row in cursor.fetchall()]

    return jsonify({'items': items}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)