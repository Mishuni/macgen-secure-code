import aiohttp
from aiohttp import web
import sqlite3
import os
import csv

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
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            merchant_id INTEGER,
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
        return web.json_response({'error': 'Invalid input'}, status=400)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, password))
        conn.commit()
        return web.json_response({'message': 'Merchant registered successfully'}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({'error': 'Email already exists'}, status=400)
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
        response = web.json_response({'message': 'Login successful'}, status=200)
        response.set_cookie('AUTH_COOKIE', 'some_auth_value')  # Simulated cookie
        return response
    else:
        return web.json_response({'error': 'Invalid email or password'}, status=401)

# Upload wares
async def upload_wares(request):
    if 'AUTH_COOKIE' not in request.cookies:
        return web.json_response({'error': 'Unauthorized'}, status=401)

    data = await request.json()
    csv_data = data.get('csv')

    if not csv_data:
        return web.json_response({'error': 'Invalid CSV format'}, status=400)

    try:
        reader = csv.reader(csv_data.splitlines())
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        for row in reader:
            if len(row) != 3:
                return web.json_response({'error': 'Invalid CSV format'}, status=400)
            name, description, price = row
            cursor.execute('INSERT INTO wares (name, description, price) VALUES (?, ?, ?)', (name, description, float(price)))
        conn.commit()
        return web.json_response({'message': 'Wares uploaded successfully'}, status=200)
    except Exception as e:
        return web.json_response({'error': 'Invalid CSV format'}, status=400)
    finally:
        conn.close()

# Retrieve wares
async def get_wares(request):
    if 'AUTH_COOKIE' not in request.cookies:
        return web.json_response({'error': 'Unauthorized'}, status=401)

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

# Create the app and routes
app = web.Application()
app.router.add_post('/merchants/register', register)
app.router.add_post('/merchants/login', login)
app.router.add_post('/merchants/upload-wares', upload_wares)
app.router.add_get('/wares', get_wares)

# Initialize the database and run the app
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)