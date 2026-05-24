import os
import sqlite3
from aiohttp import web
import json

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                tags TEXT NOT NULL
            )
        ''')
        conn.commit()

# Initialize the database
init_db()

# Web application setup
app = web.Application()

# Helper function to parse tags
def parse_tags(tags_str):
    return [tag.strip() for tag in tags_str.split(',') if tag.strip()]

# GET /recommender
async def get_recommendations(request):
    tags = request.query.get('tags', '')
    if not tags:
        return web.Response(status=400, text="Tags parameter is required")

    tags_list = parse_tags(tags)
    if not tags_list:
        return web.Response(status=400, text="Invalid tags format")

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        query = "SELECT product_name FROM products WHERE " + " OR ".join(["tags LIKE ?"] * len(tags_list))
        params = [f"%{tag}%" for tag in tags_list]
        cursor.execute(query, params)
        products = cursor.fetchall()

    response_html = "<html><body><ul>"
    for product in products:
        response_html += f"<li>{product[0]}</li>"
    response_html += "</ul></body></html>"

    return web.Response(content_type='text/html', text=response_html)

# POST /recommender
async def post_product(request):
    try:
        data = await request.json()
        product_name = data.get('product_name')
        tags = data.get('tags', [])

        if not product_name or not isinstance(tags, list):
            return web.Response(status=400, text="Invalid input")

        tags_str = ','.join(tags)

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', (product_name, tags_str))
            conn.commit()

        return web.Response(status=200, text="Product added successfully")
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")

# Register routes
app.router.add_get('/recommender', get_recommendations)
app.router.add_post('/recommender', post_product)

# Start the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)