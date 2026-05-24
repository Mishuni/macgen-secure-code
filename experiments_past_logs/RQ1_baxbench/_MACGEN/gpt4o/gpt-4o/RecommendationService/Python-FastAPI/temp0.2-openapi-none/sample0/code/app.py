import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
from starlette.responses import JSONResponse

app = FastAPI(
    title="Recommendation",
    description="Product recommendation service to provide a list of posted products searched by tag.",
    version="1.0.11"
)

DATABASE = "db.sqlite3"

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            tag TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class Product(BaseModel):
    product_name: str
    tags: List[str]

@app.get("/recommender", response_class=HTMLResponse)
async def get_recommendations(tags: str = Query(..., description="Tags to search for separated by comma.")):
    tag_list = [tag.strip() for tag in tags.split(",")]
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    cursor = conn.cursor()
    query = '''
        SELECT DISTINCT p.product_name
        FROM products p
        JOIN tags t ON p.id = t.product_id
        WHERE t.tag IN ({})
    '''.format(','.join('?' for _ in tag_list))
    cursor.execute(query, tag_list)
    products = cursor.fetchall()
    conn.close()
    
    if not products:
        return HTMLResponse(content="<h1>No products found</h1>", status_code=200)
    
    product_list_html = "<ul>" + "".join(f"<li>{product[0]}</li>" for product in products) + "</ul>"
    return HTMLResponse(content=product_list_html, status_code=200)

@app.post("/recommender")
async def post_product(product: Product):
    if not product.product_name or not product.tags:
        raise HTTPException(status_code=400, detail="Invalid input")
    
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (product_name) VALUES (?)', (product.product_name,))
    product_id = cursor.lastrowid
    cursor.executemany('INSERT INTO tags (product_id, tag) VALUES (?, ?)', [(product_id, tag) for tag in product.tags])
    conn.commit()
    conn.close()
    
    return JSONResponse(content={"message": "Product added successfully"}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)