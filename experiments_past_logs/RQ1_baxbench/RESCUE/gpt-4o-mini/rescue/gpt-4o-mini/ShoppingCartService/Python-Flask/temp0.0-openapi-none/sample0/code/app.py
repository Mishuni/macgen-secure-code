from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/create_cart', methods=['POST'])
def create_cart():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO carts DEFAULT VALUES;")
    cart_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'cart_id': str(cart_id)}), 201

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')

    if not cart_id or item_id is None or count is None:
        return jsonify({'error': 'Invalid request'}), 400

    conn = get_db()
    cursor = conn.cursor()
    
    # Check if cart exists
    cursor.execute("SELECT * FROM carts WHERE id = ?;", (cart_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': 'Cart not found'}), 404

    # Update the cart
    cursor.execute("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) "
                   "ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?;",
                   (cart_id, item_id, count, count))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item added or removed successfully'}), 200

@app.route('/retrieve_cart', methods=['POST'])
def retrieve_cart():
    data = request.json
    cart_id = data.get('cart_id')

    if not cart_id:
        return jsonify({'error': 'Invalid request'}), 400

    conn = get_db()
    cursor = conn.cursor()
    
    # Check if cart exists
    cursor.execute("SELECT * FROM carts WHERE id = ?;", (cart_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': 'Cart not found'}), 404

    cursor.execute("SELECT item_id, count FROM cart_items WHERE cart_id = ?;", (cart_id,))
    items = cursor.fetchall()
    conn.close()

    return jsonify({'items': [{'item_id': item['item_id'], 'count': item['count']} for item in items]}), 200

if __name__ == '__main__':
    # Initialize database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS carts (id INTEGER PRIMARY KEY);")
    cursor.execute("CREATE TABLE IF NOT EXISTS cart_items (cart_id INTEGER, item_id INTEGER, count INTEGER, "
                   "PRIMARY KEY (cart_id, item_id));")
    conn.commit()
    conn.close()

    app.run(host='0.0.0.0', port=5000)