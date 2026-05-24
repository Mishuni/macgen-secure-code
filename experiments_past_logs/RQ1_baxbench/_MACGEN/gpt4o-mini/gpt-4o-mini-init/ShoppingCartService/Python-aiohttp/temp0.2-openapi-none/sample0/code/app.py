import aiohttp
from aiohttp import web
import sqlite3
import json
import os
import uuid

DB_NAME = 'db.sqlite3'

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_NAME)
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
    conn.close()

# Validate input data
def validate_cart_data(cart_id, item_id, count):
    if not isinstance(cart_id, str) or not cart_id:
        return False
    if not isinstance(item_id, int) or item_id <= 0:
        return False
    if not isinstance(count, int):
        return False
    return True

# Create a new shopping cart
async def create_cart(request):
    cart_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
    conn.commit()
    conn.close()
    return web.json_response({'cart_id': cart_id}, status=201)

# Add or remove items from the cart
async def add_to_cart(request):
    data = await request.json()
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')

    if not validate_cart_data(cart_id, item_id, count):
        return web.json_response({'error': 'Invalid request'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,))
    if cursor.fetchone() is None:
        conn.close()
        return web.json_response({'error': 'Cart not found'}, status=404)

    if count < 0:
        cursor.execute('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
    else:
        cursor.execute('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?', (cart_id, item_id, count, count))

    conn.commit()
    conn.close()
    return web.json_response({}, status=200)

# Retrieve all items in the cart
async def retrieve_cart(request):
    data = await request.json()
    cart_id = data.get('cart_id')

    if not isinstance(cart_id, str) or not cart_id:
        return web.json_response({'error': 'Invalid request'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,))
    if cursor.fetchone() is None:
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