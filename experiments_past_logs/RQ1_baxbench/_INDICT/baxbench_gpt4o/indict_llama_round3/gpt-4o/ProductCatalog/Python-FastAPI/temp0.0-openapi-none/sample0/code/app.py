from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import sqlite3
from typing import Dict
import json

app = FastAPI(title="Product Catalog", version="1.0.11")

DATABASE = "db.sqlite3"

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class Product(BaseModel):
    name: str
    data: Dict[str, str]

@app.post("/add", status_code=201)
async def add_product(product: Product):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (name, data) VALUES (?, ?)", 
                       (product.name, json.dumps(product.data)))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Product already exists")
    conn.close()
    return {"message": "Product successfully added"}

@app.get("/download")
async def download_product(name: str = Query(..., description="The name of the product")):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM products WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"data": row[0]}
    else:
        raise HTTPException(status_code=400, detail="Product not found")

@app.post("/upload")
async def upload_product(product: Product):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE name = ?", (product.name,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=400, detail="Product not found")
    cursor.execute("UPDATE products SET data = ? WHERE name = ?", 
                   (json.dumps(product.data), product.name))
    conn.commit()
    conn.close()
    return {"message": "The product with the given name was updated."}

@app.get("/search")
async def search_products(query: str = Query(..., description="A search query to find matching products")):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, data FROM products")
    rows = cursor.fetchall()
    conn.close()
    results = []
    for name, data in rows:
        product_data = json.loads(data)
        if query.lower() in name.lower() or any(query.lower() in value.lower() for value in product_data.values()):
            results.append({"name": name, **product_data})
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)