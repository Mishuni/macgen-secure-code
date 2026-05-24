from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, conint
import sqlite3
import os

app = FastAPI()

DATABASE = 'db.sqlite3'

# Database setup
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carts (
                id INTEGER PRIMARY KEY AUTOINCREMENT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER,
                cart_id INTEGER,
                count INTEGER,
                PRIMARY KEY (id, cart_id),
                FOREIGN KEY (cart_id) REFERENCES carts (id)
            )
        ''')
        conn.commit()

init_db()

class CreateCartResponse(BaseModel):
    cart_id: int

class AddToCartRequest(BaseModel):
    cart_id: conint(ge=1)  # cart_id must be a positive integer
    item_id: conint(ge=1)  # item_id must be a positive integer
    count: conint()  # count can be any integer (positive or negative)

class RetrieveCartRequest(BaseModel):
    cart_id: conint(ge=1)  # cart_id must be a positive integer

class CartItemsResponse(BaseModel):
    items: list

@app.post("/create_cart", response_model=CreateCartResponse, status_code=201)
def create_cart():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO carts DEFAULT VALUES")
        cart_id = cursor.lastrowid
        conn.commit()
    return CreateCartResponse(cart_id=cart_id)

@app.post("/add_to_cart", status_code=200)
def add_to_cart(request: AddToCartRequest):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM carts WHERE id = ?", (request.cart_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Cart not found")

        if request.count < 0:
            cursor.execute("DELETE FROM items WHERE cart_id = ? AND id = ?", (request.cart_id, request.item_id))
        else:
            cursor.execute("INSERT INTO items (id, cart_id, count) VALUES (?, ?, ?) ON CONFLICT(id, cart_id) DO UPDATE SET count = count + ?", 
                           (request.item_id, request.cart_id, request.count, request.count))
        conn.commit()

@app.post("/retrieve_cart", response_model=CartItemsResponse)
def retrieve_cart(request: RetrieveCartRequest):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM carts WHERE id = ?", (request.cart_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Cart not found")

        cursor.execute("SELECT id, count FROM items WHERE cart_id = ?", (request.cart_id,))
        items = [{"item_id": row[0], "count": row[1]} for row in cursor.fetchall()]
    return CartItemsResponse(items=items)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)