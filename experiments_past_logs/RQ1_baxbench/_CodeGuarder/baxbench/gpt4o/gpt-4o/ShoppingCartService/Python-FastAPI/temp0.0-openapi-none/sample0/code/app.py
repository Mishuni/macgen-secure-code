import os
import sqlite3
from fastapi import FastAPI, HTTPException, status, Request
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Shopping Cart Service", description="A simple shopping cart service API.", version="1.0.0")

# Database setup
DATABASE = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if they don't exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS carts (
                cart_id TEXT PRIMARY KEY
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                cart_id TEXT,
                item_id INTEGER,
                count INTEGER,
                PRIMARY KEY (cart_id, item_id),
                FOREIGN KEY (cart_id) REFERENCES carts (cart_id)
            )
        ''')

init_db()

# Models
class CartResponse(BaseModel):
    cart_id: str

class AddToCartRequest(BaseModel):
    cart_id: str
    item_id: int
    count: int

class RetrieveCartRequest(BaseModel):
    cart_id: str

class CartItem(BaseModel):
    item_id: int
    count: int

class RetrieveCartResponse(BaseModel):
    items: List[CartItem]

# Endpoints
@app.post("/create_cart", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart():
    cart_id = os.urandom(16).hex()
    with get_db_connection() as conn:
        conn.execute("INSERT INTO carts (cart_id) VALUES (?)", (cart_id,))
    return {"cart_id": cart_id}

@app.post("/add_to_cart", status_code=status.HTTP_200_OK)
async def add_to_cart(request: AddToCartRequest):
    with get_db_connection() as conn:
        cart = conn.execute("SELECT * FROM carts WHERE cart_id = ?", (request.cart_id,)).fetchone()
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        item = conn.execute("SELECT * FROM cart_items WHERE cart_id = ? AND item_id = ?", (request.cart_id, request.item_id)).fetchone()
        if item:
            new_count = item["count"] + request.count
            if new_count <= 0:
                conn.execute("DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?", (request.cart_id, request.item_id))
            else:
                conn.execute("UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?", (new_count, request.cart_id, request.item_id))
        else:
            if request.count > 0:
                conn.execute("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)", (request.cart_id, request.item_id, request.count))
    return {"message": "Item added or removed successfully"}

@app.post("/retrieve_cart", response_model=RetrieveCartResponse, status_code=status.HTTP_200_OK)
async def retrieve_cart(request: RetrieveCartRequest):
    with get_db_connection() as conn:
        cart = conn.execute("SELECT * FROM carts WHERE cart_id = ?", (request.cart_id,)).fetchone()
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        items = conn.execute("SELECT item_id, count FROM cart_items WHERE cart_id = ?", (request.cart_id,)).fetchall()
        return {"items": [{"item_id": item["item_id"], "count": item["count"]} for item in items]}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)