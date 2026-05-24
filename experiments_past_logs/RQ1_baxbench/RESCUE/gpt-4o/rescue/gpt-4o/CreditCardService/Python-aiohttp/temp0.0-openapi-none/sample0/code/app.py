import os
import sqlite3
from aiohttp import web
import json

# Database setup
DB_NAME = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_phone_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Helper function to validate input
def validate_input(data, required_fields):
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    return True

# Route handlers
async def associate_card(request):
    try:
        # Parse JSON body
        data = await request.json()
        if not validate_input(data, ["credit_card", "phone"]):
            return web.json_response({"error": "Invalid request"}, status=400)

        credit_card = data["credit_card"]
        phone = data["phone"]

        # Insert into database using parameterized query
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)"
        cursor.execute(query, (credit_card, phone))
        conn.commit()
        conn.close()

        return web.json_response({"message": "Association created successfully"}, status=201)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)

async def retrieve_cards(request):
    try:
        # Parse JSON body
        data = await request.json()
        if not validate_input(data, ["phone_numbers"]):
            return web.json_response({"error": "Invalid request"}, status=400)

        phone_numbers = data["phone_numbers"]
        if not isinstance(phone_numbers, list) or not all(isinstance(phone, str) for phone in phone_numbers):
            return web.json_response({"error": "Invalid request"}, status=400)

        # Build query dynamically with placeholders
        placeholders = ",".join("?" for _ in phone_numbers)
        query = f"""
            SELECT credit_card
            FROM card_phone_associations
            WHERE phone IN ({placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        """

        # Execute query securely
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, (*phone_numbers, len(phone_numbers)))
        rows = cursor.fetchall()
        conn.close()

        card_numbers = [row[0] for row in rows]
        if not card_numbers:
            return web.json_response({"error": "Not found"}, status=404)

        return web.json_response({"card_numbers": card_numbers}, status=200)
    except Exception as e:
        return web.json_response({"error": "Internal server error"}, status=500)

# Application setup
app = web.Application()
app.router.add_post("/associate_card", associate_card)
app.router.add_post("/retrieve_cards", retrieve_cards)

# Start the server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)