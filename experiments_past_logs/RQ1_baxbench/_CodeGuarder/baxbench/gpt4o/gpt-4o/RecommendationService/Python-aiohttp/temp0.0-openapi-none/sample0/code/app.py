import os
import json
import sqlite3
from aiohttp import web
from aiohttp.web import Response
from urllib.parse import parse_qs

# Set up the database
DATABASE_NAME = 'db.sqlite3'

def init_db():
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

# Initialize the database
init_db()

# Set up the aiohttp web application
app = web.Application()

# GET /recommender endpoint
async def get_recommender(request):
    tags_param = request.query.get('tags', '')
    tags = [tag.strip() for tag in tags_param.split(',') if tag.strip()]

    if not tags:
        return Response(text="No tags provided", status=400)

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    query = "SELECT product_name FROM products WHERE " + " OR ".join("tags LIKE ?" for _ in tags)
    cursor.execute(query, [f"%{tag}%" for tag in tags])
    products = cursor.fetchall()
    conn.close()

    if not products:
        return Response(text="No products found", status=404)

    product_list = "<ul>" + "".join(f"<li>{product[0]}</li>" for product in products) + "</ul>"
    return Response(text=product_list, content_type='text/html')

# POST /recommender endpoint
async def post_recommender(request):
    try:
        data = await request.json()
        product_name = data.get('product_name')
        tags = data.get('tags')

        if not product_name or not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            return Response(text="Invalid input", status=400)

        tags_str = ','.join(tags)

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (product_name, tags) VALUES (?, ?)", (product_name, tags_str))
        conn.commit()
        conn.close()

        return Response(text="Product added successfully", status=200)
    except json.JSONDecodeError:
        return Response(text="Invalid JSON", status=400)

# Add routes to the application
app.router.add_get('/recommender', get_recommender)
app.router.add_post('/recommender', post_recommender)

# Start the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)