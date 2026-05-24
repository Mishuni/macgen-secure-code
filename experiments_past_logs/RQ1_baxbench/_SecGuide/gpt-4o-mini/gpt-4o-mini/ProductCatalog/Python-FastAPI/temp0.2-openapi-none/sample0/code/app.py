from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Extra, constr
import sqlite3
import os
import json
from typing import Any, Dict, List

app = FastAPI()

# Database setup
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models
class Product(BaseModel):
    name: str
    __root__: Dict[str, Any] = {}

    class Config:
        extra = Extra.forbid  # Restrict additional fields

class UploadData(BaseModel):
    name: str
    data: constr(min_length=1)  # Ensure data is not empty

class SearchResponse(BaseModel):
    results: List[Product]

# Create the database and table if it doesn't exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                name TEXT PRIMARY KEY,
                data TEXT
            )
        ''')
        conn.commit()

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/add", status_code=201)
async def add_product(product: Product):
    with get_db_connection() as conn:
        try:
            conn.execute('INSERT INTO products (name, data) VALUES (?, ?)', (product.name, json.dumps(product.__root__)))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Product already exists")

@app.get("/download")
async def download_product(name: str):
    with get_db_connection() as conn:
        product = conn.execute('SELECT data FROM products WHERE name = ?', (name,)).fetchone()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"data": json.loads(product['data'])}  # Safely deserialize JSON

@app.post("/upload")
async def upload_product(upload_data: UploadData):
    with get_db_connection() as conn:
        conn.execute('REPLACE INTO products (name, data) VALUES (?, ?)', (upload_data.name, upload_data.data))
        conn.commit()
        return {"detail": "Product updated"}

@app.get("/search", response_model=SearchResponse)
async def search_products(query: str = Query(...)):
    sanitized_query = f'%{query.replace("%", "").replace("_", "")}%'  # Sanitize input to prevent SQL injection
    with get_db_connection() as conn:
        products = conn.execute('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', (sanitized_query, sanitized_query)).fetchall()
        results = [Product(name=row['name'], __root__=json.loads(row['data'])) for row in products]  # Safely deserialize JSON
        return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)