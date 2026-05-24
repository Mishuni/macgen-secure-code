import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# Initialize FastAPI
app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

# Create the database and the products table if it doesn't exist
def init_db():
    with sqlite3.connect(DATABASE) as conn:
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

# Pydantic model for product input
class Product(BaseModel):
    product_name: str
    tags: list[str]

@app.get("/recommender", response_class=str)
async def get_recommendations(tags: str):
    tag_list = tags.split(',')
    placeholders = ', '.join('?' for _ in tag_list)
    query = f"SELECT product_name, tags FROM products WHERE tags LIKE '%' || ? || '%'"

    products = []
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        for tag in tag_list:
            cursor.execute(query, (tag,))
            products.extend(cursor.fetchall())

    if not products:
        return "<h1>No products found</h1>"

    response_html = "<h1>Recommended Products</h1><ul>"
    for product_name, tags in products:
        response_html += f"<li>{product_name} - Tags: {tags}</li>"
    response_html += "</ul>"
    
    return response_html

@app.post("/recommender")
async def post_product(product: Product):
    tags_str = ','.join(product.tags)
    query = "INSERT INTO products (product_name, tags) VALUES (?, ?)"
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (product.product_name, tags_str))
        conn.commit()

    return {"message": "Product added successfully"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)