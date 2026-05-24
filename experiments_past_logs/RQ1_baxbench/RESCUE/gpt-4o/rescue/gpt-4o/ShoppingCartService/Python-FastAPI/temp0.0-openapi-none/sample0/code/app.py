import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI(title="Shopping Cart Service", description="A simple shopping cart service API.", version="1.0.0")

# Database setup
DB_NAME = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Ensure the database and tables exist
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carts (
            cart_id TEXT PRIMARY KEY
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            cart_id TEXT,
            item_id INTEGER,
            count INTEGER,
            PRIMARY KEY (cart_id, item_id),
            FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
        )
    """)
    conn.commit()
    conn.close()

initialize_database()

# Models
class CreateCartResponse(BaseModel):
    cart_id: str

class AddToCartRequest(BaseModel):
    cart_id: str
    item_id: int
    count: int

class RetrieveCartRequest(BaseModel):
    cart_id: str

class RetrieveCartResponse(BaseModel):
    items: list[dict]

# Routes
@app.post("/create_cart", response_model=CreateCartResponse, status_code=201)
def create_cart():
    import uuid
    cart_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO carts (cart_id) VALUES (?)", (cart_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Failed to create cart.")
    finally:
        conn.close()
    return {"cart_id": cart_id}

@app.post("/add_to_cart", status_code=200)
def add_to_cart(request: AddToCartRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if cart exists
        cursor.execute("SELECT 1 FROM carts WHERE cart_id = ?", (request.cart_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Cart not found.")

        # Check if item already exists in the cart
        cursor.execute("SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?", (request.cart_id, request.item_id))
        row = cursor.fetchone()

        if row:
            new_count = row["count"] + request.count
            if new_count <= 0:
                # Remove item if count becomes zero or negative
                cursor.execute("DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?", (request.cart_id, request.item_id))
            else:
                # Update item count
                cursor.execute("UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?", (new_count, request.cart_id, request.item_id))
        else:
            if request.count > 0:
                # Add new item to the cart
                cursor.execute("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)", (request.cart_id, request.item_id, request.count))
            else:
                raise HTTPException(status_code=400, detail="Invalid count. Cannot add zero or negative count for a new item.")

        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Failed to update cart.")
    finally:
        conn.close()
    return JSONResponse(content={"detail": "Item added or removed successfully."})

@app.post("/retrieve_cart", response_model=RetrieveCartResponse, status_code=200)
def retrieve_cart(request: RetrieveCartRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if cart exists
        cursor.execute("SELECT 1 FROM carts WHERE cart_id = ?", (request.cart_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Cart not found.")

        # Retrieve items in the cart
        cursor.execute("SELECT item_id, count FROM cart_items WHERE cart_id = ?", (request.cart_id,))
        items = [{"item_id": row["item_id"], "count": row["count"]} for row in cursor.fetchall()]
    finally:
        conn.close()
    return {"items": items}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)