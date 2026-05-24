import os
import sqlite3
from aiohttp import web
import json

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Helper function to execute database queries securely
def execute_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
        result = cursor.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result

# Handlers
async def get_recommendations(request):
    tags = request.query.get('tags')
    if not tags:
        return web.Response(text="Tags parameter is required", status=400)

    # Split tags and prepare for SQL query
    tag_list = [tag.strip() for tag in tags.split(",")]
    placeholders = ",".join("?" for _ in tag_list)

    # Securely query the database
    query = f"""
        SELECT product_name, tags FROM products
        WHERE EXISTS (
            SELECT 1 FROM json_each(products.tags)
            WHERE json_each.value IN ({placeholders})
        )
    """
    results = execute_query(query, tag_list, fetch=True)

    # Format results into HTML
    html_results = "<ul>"
    for product_name, tags in results:
        html_results += f"<li>{product_name} - Tags: {tags}</li>"
    html_results += "</ul>"

    return web.Response(text=html_results, content_type="text/html")

async def post_product(request):
    try:
        data = await request.json()
        product_name = data.get("product_name")
        tags = data.get("tags")

        if not product_name or not tags or not isinstance(tags, list):
            return web.Response(text="Invalid input", status=400)

        # Convert tags to JSON string for storage
        tags_json = json.dumps(tags)

        # Securely insert into the database
        query = "INSERT INTO products (product_name, tags) VALUES (?, ?)"
        execute_query(query, (product_name, tags_json))

        return web.Response(text="Product added successfully", status=200)
    except Exception as e:
        return web.Response(text="Invalid input", status=400)

# Application setup
app = web.Application()
app.router.add_get('/recommender', get_recommendations)
app.router.add_post('/recommender', post_product)

# Start the web server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)