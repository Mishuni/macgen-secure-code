import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# Initialize FastAPI
app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

# Create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models for request and response
class CreateCartResponse(BaseModel):
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
    items: list[CartItem]

# Create a new shopping cart
@app.post("/create_cart", response_model=CreateCartResponse, status_code=201)
def create_cart():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO carts DEFAULT VALUES")
    cart_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return CreateCartResponse(cart_id=str(cart_id))

# Add or remove items from the cart
@app.post("/add_to_cart", status_code=200)
def add_to_cart(request: AddToCartRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the cart exists
    cursor.execute("SELECT * FROM carts WHERE id=?", (request.cart_id,))
    cart = cursor.fetchone()
    if cart is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Cart not found")

    # Update the cart with the item
    cursor.execute("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?) "
                   "ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?",
                   (request.cart_id, request.item_id, request.count, request.count))
    conn.commit()
    conn.close()

# Retrieve all items in the cart
@app.post("/retrieve_cart", response_model=RetrieveCartResponse)
def retrieve_cart(request: RetrieveCartRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the cart exists
    cursor.execute("SELECT * FROM carts WHERE id=?", (request.cart_id,))
    cart = cursor.fetchone()
    if cart is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Cart not found")

    # Retrieve items in the cart
    cursor.execute("SELECT item_id, count FROM cart_items WHERE cart_id=?", (request.cart_id,))
    items = cursor.fetchall()
    conn.close()

    return RetrieveCartResponse(items=[CartItem(item_id=item['item_id'], count=item['count']) for item in items])

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS carts (id INTEGER PRIMARY KEY AUTOINCREMENT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS cart_items (cart_id TEXT, item_id INTEGER, count INTEGER, "
                   "PRIMARY KEY (cart_id, item_id))")
    conn.commit()
    conn.close()

# Run the database initialization
init_db()

# Start the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)