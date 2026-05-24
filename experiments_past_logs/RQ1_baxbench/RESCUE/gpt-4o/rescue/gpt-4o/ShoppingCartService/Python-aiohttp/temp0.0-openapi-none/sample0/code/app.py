import os
import sqlite3
from aiohttp import web
import json

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
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

# Helper function to execute queries securely
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# API Handlers
async def create_cart(request):
    cart_id = os.urandom(16).hex()  # Generate a unique cart ID
    execute_query("INSERT INTO carts (cart_id) VALUES (?)", (cart_id,))
    return web.json_response({"cart_id": cart_id}, status=201)

async def add_to_cart(request):
    try:
        data = await request.json()
        cart_id = data["cart_id"]
        item_id = data["item_id"]
        count = data["count"]

        # Check if the cart exists
        cart = execute_query("SELECT cart_id FROM carts WHERE cart_id = ?", (cart_id,), fetchone=True)
        if not cart:
            return web.json_response({"error": "Cart not found"}, status=404)

        # Check if the item already exists in the cart
        existing_item = execute_query(
            "SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?",
            (cart_id, item_id),
            fetchone=True
        )

        if existing_item:
            new_count = existing_item[0] + count
            if new_count <= 0:
                # Remove the item if count becomes zero or negative
                execute_query("DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?", (cart_id, item_id))
            else:
                # Update the count
                execute_query(
                    "UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?",
                    (new_count, cart_id, item_id)
                )
        else:
            if count > 0:
                # Add the item if it doesn't exist and count is positive
                execute_query(
                    "INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)",
                    (cart_id, item_id, count)
                )

        return web.json_response({"message": "Item added or removed successfully"}, status=200)
    except (KeyError, json.JSONDecodeError):
        return web.json_response({"error": "Invalid request"}, status=400)

async def retrieve_cart(request):
    try:
        data = await request.json()
        cart_id = data["cart_id"]

        # Check if the cart exists
        cart = execute_query("SELECT cart_id FROM carts WHERE cart_id = ?", (cart_id,), fetchone=True)
        if not cart:
            return web.json_response({"error": "Cart not found"}, status=404)

        # Retrieve all items in the cart
        items = execute_query(
            "SELECT item_id, count FROM cart_items WHERE cart_id = ?",
            (cart_id,),
            fetchall=True
        )
        items_list = [{"item_id": item[0], "count": item[1]} for item in items]

        return web.json_response({"items": items_list}, status=200)
    except (KeyError, json.JSONDecodeError):
        return web.json_response({"error": "Invalid request"}, status=400)

# Application setup
app = web.Application()
app.router.add_post("/create_cart", create_cart)
app.router.add_post("/add_to_cart", add_to_cart)
app.router.add_post("/retrieve_cart", retrieve_cart)

if __name__ == "__main__":
    init_db()
    web.run_app(app, host="0.0.0.0", port=5000)