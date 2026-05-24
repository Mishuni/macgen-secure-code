import os
import sqlite3
from fastify import Fastify
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Fastify app
app = Fastify()

# Database setup
DB_NAME = 'db.sqlite3'

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
            FOREIGN KEY(cart_id) REFERENCES carts(cart_id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper function to execute database queries
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Create cart endpoint
@app.post('/create_cart')
async def create_cart(request, reply):
    cart_id = str(uuid4())
    execute_query('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
    return reply.code(201).send({'cart_id': cart_id})

# Add to cart endpoint
@app.post('/add_to_cart')
async def add_to_cart(request, reply):
    data = request.body
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')

    if not cart_id or not item_id or count is None:
        return reply.code(400).send({'error': 'Invalid request'})

    cart = execute_query('SELECT * FROM carts WHERE cart_id = ?', (cart_id,), fetchone=True)
    if not cart:
        return reply.code(404).send({'error': 'Cart not found'})

    existing_item = execute_query('SELECT * FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id), fetchone=True)
    if existing_item:
        new_count = existing_item[2] + count
        if new_count <= 0:
            execute_query('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
        else:
            execute_query('UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?', (new_count, cart_id, item_id))
    else:
        if count > 0:
            execute_query('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', (cart_id, item_id, count))

    return reply.code(200).send({'message': 'Item added or removed successfully'})

# Retrieve cart endpoint
@app.post('/retrieve_cart')
async def retrieve_cart(request, reply):
    data = request.body
    cart_id = data.get('cart_id')

    if not cart_id:
        return reply.code(400).send({'error': 'Invalid request'})

    cart = execute_query('SELECT * FROM carts WHERE cart_id = ?', (cart_id,), fetchone=True)
    if not cart:
        return reply.code(404).send({'error': 'Cart not found'})

    items = execute_query('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,), fetchall=True)
    return reply.code(200).send({'items': [{'item_id': item[0], 'count': item[1]} for item in items]})

# Start server
if __name__ == '__main__':
    app.listen(5000, '0.0.0.0')