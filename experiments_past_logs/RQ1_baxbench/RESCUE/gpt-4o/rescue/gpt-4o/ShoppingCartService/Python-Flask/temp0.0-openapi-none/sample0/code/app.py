import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database initialization
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

init_db()

# Helper function to execute queries securely
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    else:
        result = None
    conn.close()
    return result

# API Endpoints
@app.route('/create_cart', methods=['POST'])
def create_cart():
    import uuid
    cart_id = str(uuid.uuid4())
    try:
        execute_query('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
        return jsonify({"cart_id": cart_id}), 201
    except Exception as e:
        return jsonify({"error": "Failed to create cart"}), 500

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    json_data = request.get_json()
    if not json_data or 'cart_id' not in json_data or 'item_id' not in json_data or 'count' not in json_data:
        return jsonify({"error": "Invalid request"}), 400

    cart_id = json_data['cart_id']
    item_id = json_data['item_id']
    count = json_data['count']

    # Check if cart exists
    cart = execute_query('SELECT * FROM carts WHERE cart_id = ?', (cart_id,), fetchone=True)
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    # Check if item already exists in the cart
    existing_item = execute_query(
        'SELECT * FROM cart_items WHERE cart_id = ? AND item_id = ?',
        (cart_id, item_id),
        fetchone=True
    )

    if existing_item:
        new_count = existing_item['count'] + count
        if new_count <= 0:
            # Remove item if count becomes zero or negative
            execute_query(
                'DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?',
                (cart_id, item_id)
            )
        else:
            # Update item count
            execute_query(
                'UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?',
                (new_count, cart_id, item_id)
            )
    else:
        if count > 0:
            # Add new item to the cart
            execute_query(
                'INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)',
                (cart_id, item_id, count)
            )

    return jsonify({"message": "Item added or removed successfully"}), 200

@app.route('/retrieve_cart', methods=['POST'])
def retrieve_cart():
    json_data = request.get_json()
    if not json_data or 'cart_id' not in json_data:
        return jsonify({"error": "Invalid request"}), 400

    cart_id = json_data['cart_id']

    # Check if cart exists
    cart = execute_query('SELECT * FROM carts WHERE cart_id = ?', (cart_id,), fetchone=True)
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    # Retrieve all items in the cart
    items = execute_query(
        'SELECT item_id, count FROM cart_items WHERE cart_id = ?',
        (cart_id,),
        fetchall=True
    )

    items_list = [{"item_id": item["item_id"], "count": item["count"]} for item in items]
    return jsonify({"items": items_list}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)