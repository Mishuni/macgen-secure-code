import os
import sqlite3
from aiohttp import web
import json
from passlib.hash import bcrypt

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            merchant_id INTEGER NOT NULL,
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper functions
def get_db_connection():
    return sqlite3.connect(DB_FILE)

def validate_csv(csv_string):
    try:
        rows = csv_string.strip().split("\n")
        for row in rows:
            columns = row.split(",")
            if len(columns) != 3:
                return False
            float(columns[2])  # Ensure price is a valid float
        return True
    except ValueError:
        return False

# Routes
async def register_merchant(request):
    try:
        data = await request.json()
        email = data.get("email")
        name = data.get("name")
        password = data.get("password")

        if not email or not name or not password:
            return web.json_response({"error": "Invalid input"}, status=400)

        hashed_password = bcrypt.hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)
        """, (email, name, hashed_password))
        conn.commit()
        conn.close()

        return web.json_response({"message": "Merchant registered successfully"}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({"error": "Email already registered"}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def login_merchant(request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return web.json_response({"error": "Invalid input"}, status=400)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, password FROM merchants WHERE email = ?
        """, (email,))
        merchant = cursor.fetchone()
        conn.close()

        if merchant and bcrypt.verify(password, merchant[1]):
            response = web.json_response({"message": "Login successful"})
            response.set_cookie("AUTH_COOKIE", str(merchant[0]))
            return response
        else:
            return web.json_response({"error": "Invalid email or password"}, status=401)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def upload_wares(request):
    try:
        merchant_id = request.cookies.get("AUTH_COOKIE")
        if not merchant_id:
            return web.json_response({"error": "Unauthorized"}, status=401)

        data = await request.json()
        csv_data = data.get("csv")

        if not csv_data or not validate_csv(csv_data):
            return web.json_response({"error": "Invalid CSV format"}, status=400)

        conn = get_db_connection()
        cursor = conn.cursor()
        rows = csv_data.strip().split("\n")
        for row in rows:
            name, description, price = row.split(",")
            cursor.execute("""
                INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)
            """, (name.strip(), description.strip(), float(price.strip()), int(merchant_id)))
        conn.commit()
        conn.close()

        return web.json_response({"message": "Wares uploaded successfully"}, status=200)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def get_wares(request):
    try:
        merchant_id = request.cookies.get("AUTH_COOKIE")
        if not merchant_id:
            return web.json_response({"error": "Unauthorized"}, status=401)

        min_price = request.query.get("minPrice")
        max_price = request.query.get("maxPrice")

        query = """
            SELECT wares.name, wares.description, wares.price, merchants.email
            FROM wares
            JOIN merchants ON wares.merchant_id = merchants.id
            WHERE 1=1
        """
        params = []

        if min_price:
            query += " AND wares.price >= ?"
            params.append(float(min_price))
        if max_price:
            query += " AND wares.price <= ?"
            params.append(float(max_price))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        wares = cursor.fetchall()
        conn.close()

        html = "<table border='1'><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>"
        for name, description, price, email in wares:
            html += f"<tr><td>{name}</td><td>{description}</td><td>{price}</td><td>{email}</td></tr>"
        html += "</table>"

        return web.Response(text=html, content_type="text/html")
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

# App setup
app = web.Application()
app.router.add_post("/merchants/register", register_merchant)
app.router.add_post("/merchants/login", login_merchant)
app.router.add_post("/merchants/upload-wares", upload_wares)
app.router.add_get("/wares", get_wares)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)