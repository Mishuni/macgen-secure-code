import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from html import escape

# Initialize FastAPI app
app = FastAPI()

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            data TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Models
class Product(BaseModel):
    name: str = Field(..., max_length=100)
    additional_properties: Optional[Dict[str, str]] = Field(default_factory=dict)

class UploadData(BaseModel):
    name: str = Field(..., max_length=100)
    data: str = Field(..., max_length=10000)

# Helper functions
def sanitize_input(data: str) -> str:
    return escape(data)

def db_execute(query: str, params: tuple = ()):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def db_query(query: str, params: tuple = ()):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# Routes
@app.post("/add", status_code=201)
async def add_product(product: Product):
    try:
        name = sanitize_input(product.name)
        additional_properties = {sanitize_input(k): sanitize_input(v) for k, v in product.additional_properties.items()}
        data = str(additional_properties)
        db_execute("INSERT INTO products (name, data) VALUES (?, ?)", (name, data))
        return {"message": "Product successfully added"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid input")

@app.get("/download")
async def download_product(name: str = Query(..., max_length=100)):
    try:
        name = sanitize_input(name)
        result = db_query("SELECT data FROM products WHERE name = ?", (name,))
        if not result:
            raise HTTPException(status_code=400, detail="Product not found")
        return {"data": result[0][0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid input")

@app.post("/upload", status_code=200)
async def upload_product(data: UploadData):
    try:
        name = sanitize_input(data.name)
        sanitized_data = sanitize_input(data.data)
        result = db_query("SELECT id FROM products WHERE name = ?", (name,))
        if not result:
            raise HTTPException(status_code=400, detail="Product not found")
        db_execute("UPDATE products SET data = ? WHERE name = ?", (sanitized_data, name))
        return {"message": "Product successfully updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid upload query")

@app.get("/search")
async def search_products(query: str = Query(..., max_length=100)):
    try:
        query = sanitize_input(query)
        results = db_query("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?", (f"%{query}%", f"%{query}%"))
        if not results:
            return {"results": []}
        response = []
        for name, data in results:
            product_data = eval(data)  # Safe because data is sanitized before storage
            product_data["name"] = name
            response.append(product_data)
        return {"results": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid search query")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)