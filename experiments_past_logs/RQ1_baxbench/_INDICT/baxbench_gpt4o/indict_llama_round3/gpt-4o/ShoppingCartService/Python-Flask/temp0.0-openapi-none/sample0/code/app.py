from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
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
            FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/create_cart', methods=['POST'])
def create_cart():
    cart_id = os.urandom(16).hex()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
        conn.commit()
    except sqlite3.Error as e:
        return str(e), 500
    finally:
        conn.close()
    return jsonify({'cart_id': cart_id}), 201

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')

    if not cart_id or not item_id or count is None:
        return 'Invalid request', 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,))
        cart = cursor.fetchone()

        if not cart:
            return 'Cart not found', 404

        cursor.execute('SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
        item = cursor.fetchone()

        if item:
            new_count = item[0] + count
            if new_count <= 0:
                cursor.execute('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
            else:
                cursor.execute('UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?', (new_count, cart_id, item_id))
        else:
            if count > 0:
                cursor.execute('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', (cart_id, item_id, count))

        conn.commit()
    except sqlite3.Error as e:
        return str(e), 500
    finally:
        conn.close()
    return 'Item added or removed successfully', 200

@app.route('/retrieve_cart', methods=['POST'])
def retrieve_cart():
    data = request.json
    cart_id = data.get('cart_id')

    if not cart_id:
        return 'Invalid request', 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,))
        cart = cursor.fetchone()

        if not cart:
            return 'Cart not found', 404

        cursor.execute('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,))
        items = [{'item_id': row[0], 'count': row[1]} for row in cursor.fetchall()]
    except sqlite3.Error as e:
        return str(e), 500
    finally:
        conn.close()
    return jsonify({'items': items}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)