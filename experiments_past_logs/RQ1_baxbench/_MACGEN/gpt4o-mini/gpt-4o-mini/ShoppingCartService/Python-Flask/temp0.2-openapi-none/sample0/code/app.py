from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS carts (
                cart_id TEXT PRIMARY KEY
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                cart_id TEXT,
                item_id INTEGER,
                count INTEGER,
                PRIMARY KEY (cart_id, item_id),
                FOREIGN KEY (cart_id) REFERENCES carts (cart_id)
            )
        ''')

@app.route('/create_cart', methods=['POST'])
def create_cart():
    cart_id = str(len(get_db().execute('SELECT * FROM carts').fetchall()) + 1)
    with get_db() as conn:
        conn.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
    return jsonify({'cart_id': cart_id}), 201

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')

    if not cart_id or item_id is None or count is None or not isinstance(item_id, int) or item_id <= 0 or not isinstance(count, int):
        return jsonify({'error': 'Invalid request'}), 400

    with get_db() as conn:
        cart = conn.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,)).fetchone()
        if not cart:
            return jsonify({'error': 'Cart not found'}), 404

        if count < 0:
            conn.execute('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
        else:
            conn.execute('INSERT OR REPLACE INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)',
                         (cart_id, item_id, count))

    return jsonify({}), 200

@app.route('/retrieve_cart', methods=['POST'])
def retrieve_cart():
    data = request.json
    cart_id = data.get('cart_id')

    if not cart_id:
        return jsonify({'error': 'Invalid request'}), 400

    with get_db() as conn:
        cart = conn.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,)).fetchone()
        if not cart:
            return jsonify({'error': 'Cart not found'}), 404

        items = conn.execute('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,)).fetchall()
        item_list = [{'item_id': item['item_id'], 'count': item['count']} for item in items]

    return jsonify({'items': item_list}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)