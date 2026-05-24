
import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'default_secret')

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
            CREATE TABLE IF NOT EXISTS items (
                cart_id TEXT,
                item_id INTEGER,
                count INTEGER,
                FOREIGN KEY(cart_id) REFERENCES carts(cart_id)
            )
        ''')
        conn.commit()

@app.route('/create_cart', methods=['POST'])
def create_cart():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cart_id = os.urandom(16).hex()
        cursor.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
        conn.commit()
    return jsonify({'cart_id': cart_id}), 201

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')

    if not cart_id or not item_id or count is None:
        return 'Invalid request', 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,))
        if not cursor.fetchone():
            return 'Cart not found', 404

        cursor.execute('SELECT count FROM items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
        row = cursor.fetchone()
        if row:
            new_count = row[0] + count
            if new_count <= 0:
                cursor.execute('DELETE FROM items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
            else:
                cursor.execute('UPDATE items SET count = ? WHERE cart_id = ? AND item_id = ?', (new_count, cart_id, item_id))
        else:
            if count > 0:
                cursor.execute('INSERT INTO items (cart_id, item_id, count) VALUES (?, ?, ?)', (cart_id, item_id, count))

        conn.commit()
    return 'Item added or removed successfully', 200

@app.route('/retrieve_cart', methods=['POST'])
def retrieve_cart():
    data = request.get_json()
    cart_id = data.get('cart_id')

    if not cart_id:
        return 'Invalid request', 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,))
        if not cursor.fetchone():
            return 'Cart not found', 404

        cursor.execute('SELECT item_id, count FROM items WHERE cart_id = ?', (cart_id,))
        items = [{'item_id': row[0], 'count': row[1]} for row in cursor.fetchall()]
    return jsonify({'items': items}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)