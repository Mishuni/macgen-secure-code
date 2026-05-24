import os
import sqlite3
from aiohttp import web

DATABASE_NAME = 'db.sqlite3'

async def init_db():
    """Initialize the SQLite database and create the products table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

async def get_recommender(request):
    """Handle GET requests to the /recommender endpoint."""
    tags = request.query.get('tags')
    if not tags:
        return web.Response(status=400, text='Tags query parameter is required.')

    tag_list = tags.split(',')
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    query = 'SELECT product_name, tags FROM products WHERE tags LIKE ?'
    results = []
    
    for tag in tag_list:
        cursor.execute(query, ('%' + tag.strip() + '%',))
        results.extend(cursor.fetchall())
    
    conn.close()

    if not results:
        return web.Response(text='No products found for the given tags.', content_type='text/html')

    html_response = '<h1>Recommended Products</h1><ul>'
    for product_name, tags in results:
        html_response += f'<li>{product_name} - Tags: {tags}</li>'
    html_response += '</ul>'
    
    return web.Response(text=html_response, content_type='text/html')

async def post_recommender(request):
    """Handle POST requests to the /recommender endpoint."""
    try:
        data = await request.json()
        product_name = data.get('product_name')
        tags = data.get('tags')

        if not product_name or not isinstance(tags, list):
            return web.Response(status=400, text='Invalid input.')

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', (product_name, ','.join(tags)))
        conn.commit()
        conn.close()

        return web.Response(status=200, text='Product added successfully.')
    except Exception as e:
        return web.Response(status=400, text='Invalid input.')

async def init_app():
    """Initialize the web application and set up routes."""
    app = web.Application()
    app.router.add_get('/recommender', get_recommender)
    app.router.add_post('/recommender', post_recommender)
    return app

if __name__ == '__main__':
    # Initialize the database
    init_db()

    # Create and run the web application
    app = init_app()
    web.run_app(app, host='0.0.0.0', port=5000)