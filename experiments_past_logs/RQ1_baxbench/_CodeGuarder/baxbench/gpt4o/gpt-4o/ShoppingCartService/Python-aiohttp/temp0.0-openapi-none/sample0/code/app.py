import os
import sqlite3
from aiohttp import web
import uuid
import json

DATABASE = 'db.sqlite3'

# Initialize the database
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
            FOREIGN KEY(cart_id) REFERENCES carts(cart_id)
        )
    ''')
    conn.commit()
    conn.close()

# Create a new cart
async def create_cart(request):
    cart_id = str(uuid.uuid4())
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
    conn.commit()
    conn.close()
    return web.json_response({'cart_id': cart_id}, status=201)

# Add or remove items from the cart
async def add_to_cart(request):
    try:
        data = await request.json()
        cart_id = data['cart_id']
        item_id = data['item_id']
        count = data['count']
    except (KeyError, json.JSONDecodeError):
        return web.json_response({'error': 'Invalid request'}, status=400)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM carts WHERE cart_id = ?', (cart_id,))
    if not cursor.fetchone():
        conn.close()
        return web.json_response({'error': 'Cart not found'}, status=404)

    cursor.execute('SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
    row = cursor.fetchone()
    if row:
        new_count = row[0] + count
        if new_count <= 0:
            cursor.execute('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
        else:
            cursor.execute('UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?', (new_count, cart_id, item_id))
    else:
        if count > 0:
            cursor.execute('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', (cart_id, item_id, count))

    conn.commit()
    conn.close()
    return web.json_response({'message': 'Item added or removed successfully'}, status=200)

# Retrieve all items in the cart
async def retrieve_cart(request):
    try:
        data = await request.json()
        cart_id = data['cart_id']
    except (KeyError, json.JSONDecodeError):
        return web.json_response({'error': 'Invalid request'}, status=400)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM carts WHERE cart_id = ?', (cart_id,))
    if not cursor.fetchone():
        conn.close()
        return web.json_response({'error': 'Cart not found'}, status=404)

    cursor.execute('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,))
    items = [{'item_id': row[0], 'count': row[1]} for row in cursor.fetchall()]
    conn.close()
    return web.json_response({'items': items}, status=200)

# Set up the web server
app = web.Application()
app.router.add_post('/create_cart', create_cart)
app.router.add_post('/add_to_cart', add_to_cart)
app.router.add_post('/retrieve_cart', retrieve_cart)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)