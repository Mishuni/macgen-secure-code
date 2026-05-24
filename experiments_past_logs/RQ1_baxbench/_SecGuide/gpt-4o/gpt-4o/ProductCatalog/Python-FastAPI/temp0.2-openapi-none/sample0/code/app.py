import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr
from typing import Dict, List, Optional
import json
import logging

app = FastAPI(title="Product Catalog", version="1.0.11")

# Configurable database path
DATABASE = os.getenv("DATABASE_PATH", "db.sqlite3")

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                name TEXT PRIMARY KEY,
                data TEXT
            )
        ''')
        conn.commit()

init_db()

# Pydantic models with validation
class Product(BaseModel):
    name: constr(min_length=1, max_length=100)
    data: Optional[Dict[str, str]] = None

class ProductUpload(BaseModel):
    name: constr(min_length=1, max_length=100)
    data: str

# Helper functions
def add_product_to_db(name: str, data: str):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, data))
            conn.commit()
    except sqlite3.IntegrityError:
        logger.error("Product already exists: %s", name)
        raise HTTPException(status_code=400, detail="Product already exists")

def get_product_from_db(name: str) -> Optional[str]:
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
        row = cursor.fetchone()
    return row[0] if row else None

def update_product_in_db(name: str, data: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET data = ? WHERE name = ?', (data, name))
        conn.commit()

def search_products_in_db(query: str) -> List[Dict[str, str]]:
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, data FROM products')
        rows = cursor.fetchall()
    results = []
    for name, data in rows:
        try:
            product_data = json.loads(data)
        except json.JSONDecodeError:
            logger.error("JSON decode error for product: %s", name)
            continue
        if query.lower() in name.lower() or any(query.lower() in str(value).lower() for value in product_data.values()):
            results.append({"name": name, **product_data})
    return results

# Routes
@app.post("/add", status_code=201)
async def add_product(product: Product):
    try:
        data_str = json.dumps(product.data) if product.data else "{}"
        add_product_to_db(product.name, data_str)
    except HTTPException as e:
        raise e
    return {"message": "Product successfully added"}

@app.get("/download")
async def download_product(name: str):
    data = get_product_from_db(name)
    if data is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return JSONResponse(content={"data": data})

@app.post("/upload")
async def upload_product(product: ProductUpload):
    if get_product_from_db(product.name) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    update_product_in_db(product.name, product.data)
    return {"message": "The product with the given name was updated."}

@app.get("/search")
async def search_products(query: str):
    results = search_products_in_db(query)
    if not results:
        raise HTTPException(status_code=404, detail="No matching products found")
    return JSONResponse(content={"results": results})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)