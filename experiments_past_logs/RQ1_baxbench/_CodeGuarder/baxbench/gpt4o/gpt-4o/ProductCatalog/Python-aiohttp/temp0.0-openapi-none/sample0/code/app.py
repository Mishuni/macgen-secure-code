import os
import json
import sqlite3
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Helper functions
def sanitize_filename(filename):
    return os.path.basename(filename)

def validate_product_data(data):
    if 'name' not in data or not isinstance(data['name'], str):
        raise ValueError("Invalid product data: 'name' is required and must be a string.")

# Aiohttp handlers
async def add_product(request: Request) -> Response:
    try:
        data = await request.json()
        validate_product_data(data)
        name = data['name']
        product_data = json.dumps(data)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, product_data))
        conn.commit()
        conn.close()

        return web.Response(status=201, text='Product successfully added')
    except ValueError as e:
        return web.Response(status=400, text=str(e))
    except sqlite3.IntegrityError:
        return web.Response(status=400, text='Product already exists')
    except Exception as e:
        return web.Response(status=500, text='Internal server error')

async def download_product(request: Request) -> Response:
    name = request.query.get('name')
    if not name:
        return web.Response(status=400, text='Product name is required')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return web.json_response({'data': row[0]})
    else:
        return web.Response(status=404, text='Product not found')

async def upload_product(request: Request) -> Response:
    try:
        data = await request.json()
        validate_product_data(data)
        name = data['name']
        product_data = data.get('data', '')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET data = ? WHERE name = ?', (product_data, name))
        if cursor.rowcount == 0:
            return web.Response(status=404, text='Product not found')
        conn.commit()
        conn.close()

        return web.Response(status=200, text='Product updated successfully')
    except ValueError as e:
        return web.Response(status=400, text=str(e))
    except Exception as e:
        return web.Response(status=500, text='Internal server error')

async def search_products(request: Request) -> Response:
    query = request.query.get('query')
    if not query:
        return web.Response(status=400, text='Search query is required')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name LIKE ? OR data LIKE ?', (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()

    results = [json.loads(row[0]) for row in rows]
    return web.json_response({'results': results})

# Main application setup
def create_app():
    app = web.Application()
    app.router.add_post('/add', add_product)
    app.router.add_get('/download', download_product)
    app.router.add_post('/upload', upload_product)
    app.router.add_get('/search', search_products)
    return app

if __name__ == '__main__':
    init_db()
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=5000)