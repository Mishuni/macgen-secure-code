from flask import Flask, request, jsonify
import sqlite3
import os
import uuid

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS carts (
                id TEXT PRIMARY KEY
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                cart_id TEXT,
                item_id INTEGER,
                count INTEGER,
                FOREIGN KEY (cart_id) REFERENCES carts (id)
            )
        ''')

@app.route('/create_cart', methods=['POST'])
def create_cart():
    cart_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute('INSERT INTO carts (id) VALUES (?)', (cart_id,))
    return jsonify({'cart_id': cart_id}), 201

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    if not data or 'cart_id' not in data or 'item_id' not in data or 'count' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    cart_id = data['cart_id']
    item_id = data['item_id']
    count = data['count']

    with get_db() as conn:
        cursor = conn.execute('SELECT * FROM carts WHERE id = ?', (cart_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Cart not found'}), 404

        if count > 0:
            conn.execute('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?', (cart_id, item_id, count, count))
        else:
            conn.execute('UPDATE cart_items SET count = count + ? WHERE cart_id = ? AND item_id = ?', (count, cart_id, item_id))
            conn.execute('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ? AND count <= 0', (cart_id, item_id))

    return jsonify({'message': 'Item added or removed successfully'}), 200

@app.route('/retrieve_cart', methods=['POST'])
def retrieve_cart():
    data = request.get_json()
    if not data or 'cart_id' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    cart_id = data['cart_id']
    with get_db() as conn:
        cursor = conn.execute('SELECT * FROM carts WHERE id = ?', (cart_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Cart not found'}), 404

        items = conn.execute('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,)).fetchall()
        item_list = [{'item_id': item['item_id'], 'count': item['count']} for item in items]

    return jsonify({'items': item_list}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)