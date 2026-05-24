import os
import json
import sqlite3
from fastify import Fastify

app = Fastify()

DATABASE = 'db.sqlite3'

# Initialize the database
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

init_db()

@app.post('/add')
async def add_product(request, reply):
    try:
        product = request.body
        name = product.get('name')
        if not name:
            return reply.code(400).send({'error': 'Product name is required'})

        # Remove the name from the product data to store the rest as JSON
        product_data = {k: v for k, v in product.items() if k != 'name'}
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, json.dumps(product_data)))
        conn.commit()
        conn.close()
        return reply.code(201).send({'message': 'Product successfully added'})
    except sqlite3.IntegrityError:
        return reply.code(400).send({'error': 'Product with this name already exists'})
    except Exception as e:
        return reply.code(500).send({'error': 'Internal server error'})

@app.get('/download')
async def download_product(request, reply):
    try:
        name = request.query.get('name')
        if not name:
            return reply.code(400).send({'error': 'Product name is required'})

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return reply.code(200).send({'data': row[0]})
        else:
            return reply.code(404).send({'error': 'Product not found'})
    except Exception as e:
        return reply.code(500).send({'error': 'Internal server error'})

@app.post('/upload')
async def upload_product(request, reply):
    try:
        product = request.body
        name = product.get('name')
        data = product.get('data')
        if not name or not data:
            return reply.code(400).send({'error': 'Product name and data are required'})

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET data = ? WHERE name = ?', (data, name))
        if cursor.rowcount == 0:
            return reply.code(404).send({'error': 'Product not found'})
        conn.commit()
        conn.close()
        return reply.code(200).send({'message': 'Product successfully updated'})
    except Exception as e:
        return reply.code(500).send({'error': 'Internal server error'})

@app.get('/search')
async def search_products(request, reply):
    try:
        query = request.query.get('query')
        if not query:
            return reply.code(400).send({'error': 'Search query is required'})

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', (f'%{query}%', f'%{query}%'))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            product_data = json.loads(row[1])
            product_data['name'] = row[0]
            results.append(product_data)

        return reply.code(200).send({'results': results})
    except Exception as e:
        return reply.code(500).send({'error': 'Internal server error'})

if __name__ == '__main__':
    app.listen(5000, '0.0.0.0')