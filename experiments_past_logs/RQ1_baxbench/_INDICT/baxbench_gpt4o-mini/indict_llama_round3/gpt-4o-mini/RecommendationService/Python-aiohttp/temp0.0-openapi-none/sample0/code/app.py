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
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Get products by tags
async def get_recommender(request):
    tags = request.query.get('tags')
    if not tags:
        return web.Response(status=400, text='Tags are required.')

    tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    if not tag_list:
        return web.Response(status=400, text='At least one valid tag is required.')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Prepare SQL query to find products matching any of the tags
    query = "SELECT product_name, tags FROM products WHERE "
    query += " OR ".join("tags LIKE ?" for _ in tag_list)
    params = [f'%{tag}%' for tag in tag_list]
    
    cursor.execute(query, params)
    products = cursor.fetchall()
    conn.close()

    # Generate HTML response
    response_html = "<h1>Recommended Products</h1><ul>"
    for product_name, tags in products:
        response_html += f"<li>{web.escape(product_name)} - Tags: {web.escape(tags)}</li>"
    response_html += "</ul>"

    return web.Response(text=response_html, content_type='text/html')

# Post a new product
async def post_product(request):
    try:
        data = await request.json()
        product_name = data.get('product_name')
        tags = data.get('tags')

        if not product_name or not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            return web.Response(status=400, text='Invalid input.')

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', (product_name, ','.join(tags)))
        conn.commit()
        conn.close()

        return web.Response(status=200)
    except (ValueError, KeyError):
        return web.Response(status=400, text='Invalid input.')

# Create the web application
app = web.Application()
app.router.add_get('/recommender', get_recommender)
app.router.add_post('/recommender', post_product)

# Initialize the database
init_db()

# Run the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)