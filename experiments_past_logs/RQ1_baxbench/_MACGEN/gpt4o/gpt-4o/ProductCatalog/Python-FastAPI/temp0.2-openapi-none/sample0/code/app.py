from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
from typing import Dict, List, Optional
import json

app = FastAPI()

DATABASE = "db.sqlite3"

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
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
async def add_product(product: Dict[str, str]):
    if "name" not in product:
        raise HTTPException(status_code=400, detail="Product name is required")
    name = product.pop("name")
    data = json.dumps(product)
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Product already exists")
    finally:
        conn.close()
    return JSONResponse(status_code=201, content={"message": "Product successfully added"})

@app.get("/download")
async def download_product(name: str = Query(...)):
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
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
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE name = ?", (product.name,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=400, detail="Product not found")
    cursor.execute("UPDATE products SET data = ? WHERE name = ?", (json.dumps(product.data), product.name))
    conn.commit()
    conn.close()
    return JSONResponse(status_code=200, content={"message": "The product with the given name was updated."})

@app.get("/search")
async def search_products(query: str = Query(...)):
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
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