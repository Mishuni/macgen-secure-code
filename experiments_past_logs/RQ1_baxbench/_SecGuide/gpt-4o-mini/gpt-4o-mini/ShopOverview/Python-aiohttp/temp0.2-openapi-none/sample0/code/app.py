import aiohttp
from aiohttp import web
import sqlite3
import os
import csv
import io
import bcrypt
import re

# Database setup
DB_NAME = 'db.sqlite3'
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS wares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (merchant_id) REFERENCES merchants (id)
)
''')
conn.commit()

# Helper functions
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_password(password):
    return len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isalpha() for char in password)

async def register_merchant(request):
    data = await request.json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password or not validate_email(email) or not validate_password(password):
        return web.json_response({'error': 'Invalid input'}, status=400)

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, hashed_password))
        conn.commit()
        return web.Response(status=201)
    except sqlite3.IntegrityError:
        return web.json_response({'error': 'Email already exists'}, status=400)

async def login_merchant(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    cursor.execute('SELECT * FROM merchants WHERE email = ?', (email,))
    merchant = cursor.fetchone()

    if merchant and bcrypt.checkpw(password.encode('utf-8'), merchant[3].encode('utf-8')):
        response = web.json_response('Login successful')
        response.set_cookie('AUTH_COOKIE', 'some_secure_value', httponly=True, secure=True)  # Secure cookie
        return response
    else:
        return web.json_response({'error': 'Invalid email or password'}, status=401)

async def upload_wares(request):
    if 'AUTH_COOKIE' not in request.cookies:
        return web.json_response({'error': 'Unauthorized'}, status=401)

    data = await request.json()
    csv_data = data.get('csv')

    if not csv_data:
        return web.json_response({'error': 'Invalid CSV format'}, status=400)

    try:
        reader = csv.DictReader(io.StringIO(csv_data))
        merchant_id = 1  # Placeholder for actual merchant_id retrieval from authenticated user context
        for row in reader:
            name = row.get('name')
            description = row.get('description')
            price = row.get('price')

            if not name or not description or not price:
                return web.json_response({'error': 'Invalid CSV data'}, status=400)

            # Validate inputs
            if not isinstance(price, (int, float)) or float(price) < 0:
                return web.json_response({'error': 'Invalid price'}, status=400)

            cursor.execute('INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)',
                           (merchant_id, name, description, float(price)))  # Ensure price is a float
        conn.commit()
        return web.Response(status=200)
    except Exception as e:
        return web.json_response({'error': 'Invalid CSV format'}, status=400)

async def get_wares(request):
    if 'AUTH_COOKIE' not in request.cookies:
        return web.json_response({'error': 'Unauthorized'}, status=401)

    min_price = request.query.get('minPrice', None)
    max_price = request.query.get('maxPrice', None)

    query = 'SELECT w.name, w.description, w.price FROM wares w JOIN merchants m ON w.merchant_id = m.id'
    params = []

    if min_price is not None:
        query += ' WHERE w.price >= ?'
        params.append(float(min_price))
    if max_price is not None:
        query += ' AND w.price <= ?' if 'WHERE' in query else ' WHERE w.price <= ?'
        params.append(float(max_price))

    cursor.execute(query, params)
    wares = cursor.fetchall()

    html = '<table><tr><th>Name</th><th>Description</th><th>Price</th></tr>'
    for ware in wares:
        html += f'<tr><td>{ware[0]}</td><td>{ware[1]}</td><td>{ware[2]}</td></tr>'
    html += '</table>'

    return web.Response(text=html, content_type='text/html')

# App setup
app = web.Application()
app.router.add_post('/merchants/register', register_merchant)
app.router.add_post('/merchants/login', login_merchant)
app.router.add_post('/merchants/upload-wares', upload_wares)
app.router.add_get('/wares', get_wares)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)