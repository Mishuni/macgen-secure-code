import aiohttp
from aiohttp import web
import sqlite3
import json
import os

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Add a new product to the catalog
async def add_product(request):
    try:
        body = await request.json()
        name = body['name']
        data = json.dumps(body)  # Store the entire body as JSON string

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, data))
        conn.commit()
        conn.close()

        return web.Response(status=201)
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400)

# Download the entire current catalog for a given product name
async def download_product(request):
    name = request.query.get('name')
    if not name:
        return web.Response(status=400)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return web.json_response({'data': row[0]})
    else:
        return web.Response(status=404)

# Upload data for a product with the given name
async def upload_product(request):
    try:
        body = await request.json()
        name = body['name']
        data = body['data']

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('REPLACE INTO products (name, data) VALUES (?, ?)', (name, data))
        conn.commit()
        conn.close()

        return web.Response(status=200)
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400)

# Search for products in the catalog
async def search_products(request):
    query = request.query.get('query')
    if not query:
        return web.Response(status=400)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()

    results = [{'name': row[0], **json.loads(row[1])} for row in rows]
    return web.json_response({'results': results})

# Create the web application
app = web.Application()
app.router.add_post('/add', add_product)
app.router.add_get('/download', download_product)
app.router.add_post('/upload', upload_product)
app.router.add_get('/search', search_products)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)