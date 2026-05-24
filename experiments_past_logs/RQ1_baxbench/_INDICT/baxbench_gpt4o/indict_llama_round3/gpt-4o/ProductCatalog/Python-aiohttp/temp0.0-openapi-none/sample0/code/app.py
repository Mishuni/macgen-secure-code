import os
import json
import sqlite3
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound
from aiohttp.web_response import json_response

# Initialize the database
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
        product = await request.json()
        name = product.get('name')
        if not name:
            raise HTTPBadRequest(reason='Invalid input: name is required')

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, json.dumps(product)))
        conn.commit()
        conn.close()
        return web.Response(status=201, text='Product successfully added')
    except sqlite3.IntegrityError:
        raise HTTPBadRequest(reason='Product with this name already exists')
    except Exception as e:
        raise HTTPBadRequest(reason=f'Invalid input: {str(e)}')

# Download the entire current catalog for a given product name
async def download_product(request):
    name = request.query.get('name')
    if not name:
        raise HTTPBadRequest(reason='Invalid input: name is required')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return json_response({'data': row[0]})
    else:
        raise HTTPNotFound(reason='Product not found')

# Upload data for a product with the given name
async def upload_product(request):
    try:
        data = await request.json()
        name = data.get('name')
        product_data = data.get('data')
        if not name or not product_data:
            raise HTTPBadRequest(reason='Invalid upload query')

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('REPLACE INTO products (name, data) VALUES (?, ?)', (name, product_data))
        conn.commit()
        conn.close()
        return web.Response(status=200, text='The product with the given name was updated.')
    except Exception as e:
        raise HTTPBadRequest(reason=f'Invalid upload query: {str(e)}')

# Search for products in the catalog
async def search_products(request):
    query = request.query.get('query')
    if not query:
        raise HTTPBadRequest(reason='Invalid search query')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products')
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        product = json.loads(row[0])
        if query.lower() in product.get('name', '').lower() or any(query.lower() in v.lower() for v in product.values()):
            results.append(product)

    return json_response({'results': results})

# Initialize the app and routes
app = web.Application()
app.router.add_post('/add', add_product)
app.router.add_get('/download', download_product)
app.router.add_post('/upload', upload_product)
app.router.add_get('/search', search_products)

# Initialize the database
init_db()

# Run the app
web.run_app(app, host='0.0.0.0', port=5000)