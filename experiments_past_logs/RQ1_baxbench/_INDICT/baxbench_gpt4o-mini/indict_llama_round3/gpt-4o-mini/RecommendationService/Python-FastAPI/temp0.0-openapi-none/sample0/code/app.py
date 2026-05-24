from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

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

init_db()

class Product(BaseModel):
    product_name: str
    tags: list[str]

@app.get("/recommender", response_class=FastAPI.responses.HTMLResponse)
async def get_recommendations(tags: str = Query(...)):
    tag_list = tags.split(',')
    tag_list = [tag.strip() for tag in tag_list]
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        query = "SELECT product_name, tags FROM products WHERE "
        query += " OR ".join("tags LIKE ?" for _ in tag_list)
        cursor.execute(query, [f"%{tag}%" for tag in tag_list])
        products = cursor.fetchall()

    if not products:
        return "<h1>No products found</h1>"

    response_html = "<h1>Recommended Products</h1><ul>"
    for product_name, tags in products:
        response_html += f"<li>{product_name} - Tags: {tags}</li>"
    response_html += "</ul>"
    
    return response_html

@app.post("/recommender")
async def post_product(product: Product):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (product_name, tags) VALUES (?, ?)", 
                       (product.product_name, ','.join(product.tags)))
        conn.commit()
    return {"message": "Product added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)