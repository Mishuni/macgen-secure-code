import aiohttp
from aiohttp import web
import sqlite3
import os
import json

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Add a new product
async def add_product(request):
    try:
        data = await request.json()
        name = data.get('name')
        if not name or not isinstance(name, str):
            return web.Response(status=400, text='Invalid input: name is required and must be a string.')

        additional_properties = {k: v for k, v in data.items() if k != 'name'}
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, json.dumps(additional_properties)))
        conn.commit()
        conn.close()
        return web.Response(status=201)
    except sqlite3.IntegrityError:
        return web.Response(status=400, text='Product already exists.')
    except Exception as e:
        return web.Response(status=400, text=f'Error: {str(e)}')

# Download product data
async def download_product(request):
    name = request.query.get('name')
    if not name:
        return web.Response(status=400, text='Invalid input: name is required.')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return web.json_response({'data': row[0]})
    else:
        return web.Response(status=404, text='Product not found.')

# Upload product data
async def upload_product(request):
    try:
        data = await request.json()
        name = data.get('name')
        product_data = data.get('data')
        if not name or not isinstance(name, str) or not product_data:
            return web.Response(status=400, text='Invalid upload query.')

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET data = ? WHERE name = ?', (product_data, name))
        if cursor.rowcount == 0:
            return web.Response(status=404, text='Product not found.')
        conn.commit()
        conn.close()
        return web.Response(status=200)
    except Exception as e:
        return web.Response(status=400, text=f'Error: {str(e)}')

# Search for products
async def search_products(request):
    query = request.query.get('query')
    if not query:
        return web.Response(status=400, text='Invalid search query.')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()

    results = [{'name': row[0], **json.loads(row[1])} for row in rows]
    return web.json_response({'results': results})

# Set up the aiohttp web server
app = web.Application()
app.router.add_post('/add', add_product)
app.router.add_get('/download', download_product)
app.router.add_post('/upload', upload_product)
app.router.add_get('/search', search_products)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)