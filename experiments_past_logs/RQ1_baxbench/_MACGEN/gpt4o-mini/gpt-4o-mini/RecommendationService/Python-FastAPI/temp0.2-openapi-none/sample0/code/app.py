from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, constr, conlist
import sqlite3
import os

app = FastAPI()

DATABASE = 'db.sqlite3'

# Create the SQLite database and products table if it doesn't exist
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
    product_name: constr(min_length=1)  # Non-empty string
    tags: conlist(constr(min_length=1), min_items=1)  # List of non-empty strings

@app.post("/recommender", status_code=200)
async def post_product(product: Product):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', 
                       (product.product_name, ','.join(product.tags)))
        conn.commit()
    return {"message": "Product added successfully"}

@app.get("/recommender", response_class=FastAPI.responses.HTMLResponse)
async def get_recommendations(tags: str = Query(...)):
    tag_list = tags.split(',')
    query = "SELECT product_name, tags FROM products WHERE tags LIKE ?"
    results = []
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        for tag in tag_list:
            cursor.execute(query, ('%' + tag.strip() + '%',))
            results.extend(cursor.fetchall())
    
    if not results:
        return "<h1>No products found</h1>"
    
    html_response = "<h1>Recommended Products</h1><ul>"
    for product_name, tags in results:
        html_response += f"<li>{product_name} - Tags: {tags}</li>"
    html_response += "</ul>"
    
    return html_response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)