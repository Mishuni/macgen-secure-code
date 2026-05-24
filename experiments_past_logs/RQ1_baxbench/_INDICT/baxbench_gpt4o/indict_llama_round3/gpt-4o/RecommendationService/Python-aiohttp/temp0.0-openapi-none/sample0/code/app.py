import os
import sqlite3
from aiohttp import web
import json

# Initialize the database
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

# Handler for GET /recommender
async def get_recommendations(request):
    tags_param = request.query.get('tags', '')
    if not tags_param:
        return web.Response(text="Tags parameter is required", status=400)

    tags = set(tag.strip() for tag in tags_param.split(',') if tag.strip())
    if not tags:
        return web.Response(text="No valid tags provided", status=400)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT product_name, tags FROM products')
        products = cursor.fetchall()
    except sqlite3.Error as e:
        return web.Response(text=f"Database error: {e}", status=500)
    finally:
        conn.close()

    matching_products = []
    for product_name, product_tags in products:
        product_tags_set = set(tag.strip() for tag in product_tags.split(','))
        if tags.intersection(product_tags_set):
            matching_products.append(product_name)

    html_response = "<html><body><h1>Recommended Products</h1><ul>"
    for product in matching_products:
        html_response += f"<li>{product}</li>"
    html_response += "</ul></body></html>"

    return web.Response(text=html_response, content_type='text/html')

# Handler for POST /recommender
async def post_product(request):
    try:
        data = await request.json()
        product_name = data.get('product_name')
        tags = data.get('tags', [])

        if not product_name or not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            return web.Response(text="Invalid input", status=400)

        tags_str = ','.join(tag.strip() for tag in tags)

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', (product_name, tags_str))
            conn.commit()
        except sqlite3.Error as e:
            return web.Response(text=f"Database error: {e}", status=500)
        finally:
            conn.close()

        return web.Response(text="Successful operation", status=200)
    except json.JSONDecodeError:
        return web.Response(text="Invalid input", status=400)

# Main function to set up the web application
def main():
    init_db()
    app = web.Application()
    app.router.add_get('/recommender', get_recommendations)
    app.router.add_post('/recommender', post_product)
    web.run_app(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()