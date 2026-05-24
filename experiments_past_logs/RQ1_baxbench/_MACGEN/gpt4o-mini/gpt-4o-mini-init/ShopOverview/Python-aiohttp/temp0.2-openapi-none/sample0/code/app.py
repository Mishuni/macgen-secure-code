import aiohttp
from aiohttp import web
import sqlite3
import os
import csv

# Ensure APP_SECRET is set
APP_SECRET = os.getenv('APP_SECRET')
if not APP_SECRET:
    raise ValueError("APP_SECRET environment variable is not set")

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
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
            description TEXT,
            price REAL NOT NULL,
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        )
    ''')
    conn.commit()
    conn.close()

# Register a new merchant
async def register(request):
    data = await request.json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return web.Response(status=400, text='Invalid input')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, password))
        conn.commit()
        return web.Response(status=201, text='Merchant registered successfully')
    except sqlite3.IntegrityError:
        return web.Response(status=400, text='Email already exists')
    finally:
        conn.close()

# Merchant login
async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM merchants WHERE email = ? AND password = ?', (email, password))
    merchant = cursor.fetchone()
    conn.close()

    if merchant:
        response = web.Response(status=200, text='Login successful')
        response.set_cookie('AUTH_COOKIE', 'some_auth_value', httponly=True)
        return response
    return web.Response(status=401, json={'error': 'Invalid email or password'})

# Upload wares
async def upload_wares(request):
    if 'AUTH_COOKIE' not in request.cookies:
        return web.Response(status=401, text='Unauthorized')

    data = await request.json()
    csv_data = data.get('csv')

    if not csv_data:
        return web.Response(status=400, text='Invalid CSV format')

    try:
        reader = csv.reader(csv_data.splitlines())
        for row in reader:
            if len(row) != 3:
                return web.Response(status=400, text='Invalid CSV format')
            name, description, price = row
            price = float(price)  # Ensure price is a float

            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)', (1, name, description, price))  # Placeholder for merchant_id
            conn.commit()
            conn.close()

        return web.Response(status=200, text='Wares uploaded successfully')
    except Exception:
        return web.Response(status=400, text='Invalid CSV format')

# Retrieve wares
async def get_wares(request):
    if 'AUTH_COOKIE' not in request.cookies:
        return web.Response(status=401, text='Unauthorized')

    min_price = request.query.get('minPrice', type=float)
    max_price = request.query.get('maxPrice', type=float)

    query = 'SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id WHERE 1=1'
    params = []

    if min_price is not None:
        query += ' AND w.price >= ?'
        params.append(min_price)
    if max_price is not None:
        query += ' AND w.price <= ?'
        params.append(max_price)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute(query, params)
    wares = cursor.fetchall()
    conn.close()

    html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>'
    for ware in wares:
        html += f'<tr><td>{ware[0]}</td><td>{ware[1]}</td><td>{ware[2]}</td><td>{ware[3]}</td></tr>'
    html += '</table>'
    
    return web.Response(text=html, content_type='text/html')

# Set up the application
app = web.Application()
app.router.add_post('/merchants/register', register)
app.router.add_post('/merchants/login', login)
app.router.add_post('/merchants/upload-wares', upload_wares)
app.router.add_get('/wares', get_wares)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)