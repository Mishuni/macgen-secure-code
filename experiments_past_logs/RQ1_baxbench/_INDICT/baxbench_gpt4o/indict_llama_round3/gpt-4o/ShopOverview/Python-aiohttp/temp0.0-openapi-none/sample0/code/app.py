import os
import sqlite3
from aiohttp import web
import json
from passlib.hash import bcrypt

# Database setup
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
    merchant_id INTEGER NOT NULL,
    FOREIGN KEY (merchant_id) REFERENCES merchants (id)
)
''')

conn.commit()

# Helper functions
def get_merchant_by_email(email):
    cursor.execute('SELECT * FROM merchants WHERE email = ?', (email,))
    return cursor.fetchone()

def get_merchant_by_id(merchant_id):
    cursor.execute('SELECT * FROM merchants WHERE id = ?', (merchant_id,))
    return cursor.fetchone()

def add_merchant(email, name, password):
    hashed_password = bcrypt.hash(password)
    cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, hashed_password))
    conn.commit()

def add_ware(name, description, price, merchant_id):
    cursor.execute('INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)', (name, description, price, merchant_id))
    conn.commit()

def get_wares(min_price=None, max_price=None):
    query = 'SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id'
    params = []
    if min_price is not None:
        query += ' WHERE wares.price >= ?'
        params.append(min_price)
    if max_price is not None:
        if min_price is not None:
            query += ' AND wares.price <= ?'
        else:
            query += ' WHERE wares.price <= ?'
        params.append(max_price)
    cursor.execute(query, params)
    return cursor.fetchall()

# Routes
async def register_merchant(request):
    data = await request.json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return web.Response(status=400, text='Invalid input')

    if get_merchant_by_email(email):
        return web.Response(status=400, text='Merchant already exists')

    add_merchant(email, name, password)
    return web.Response(status=201, text='Merchant registered successfully')

async def login_merchant(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    merchant = get_merchant_by_email(email)
    if not merchant or not bcrypt.verify(password, merchant[3]):
        return web.json_response({'error': 'Invalid email or password'}, status=401)

    response = web.json_response('Login successful')
    response.set_cookie('AUTH_COOKIE', str(merchant[0]), httponly=True)
    return response

async def upload_wares(request):
    auth_cookie = request.cookies.get('AUTH_COOKIE')
    if not auth_cookie:
        return web.Response(status=401, text='Unauthorized')

    merchant = get_merchant_by_id(auth_cookie)
    if not merchant:
        return web.Response(status=401, text='Unauthorized')

    data = await request.json()
    csv_data = data.get('csv')
    if not csv_data:
        return web.Response(status=400, text='Invalid CSV format')

    try:
        lines = csv_data.splitlines()
        for line in lines:
            parts = line.split(',')
            if len(parts) != 3:
                raise ValueError('Invalid CSV format')
            name, description, price = parts
            add_ware(name.strip(), description.strip(), float(price.strip()), merchant[0])
    except Exception as e:
        return web.Response(status=400, text='Invalid CSV format')

    return web.Response(status=200, text='Wares uploaded successfully')

async def get_wares_handler(request):
    auth_cookie = request.cookies.get('AUTH_COOKIE')
    if not auth_cookie:
        return web.Response(status=401, text='Unauthorized')

    min_price = request.query.get('minPrice')
    max_price = request.query.get('maxPrice')

    try:
        min_price = float(min_price) if min_price else None
        max_price = float(max_price) if max_price else None
    except ValueError:
        return web.Response(status=400, text='Invalid price format')

    wares = get_wares(min_price, max_price)
    html_content = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>'
    for ware in wares:
        html_content += f'<tr><td>{ware[0]}</td><td>{ware[1]}</td><td>{ware[2]}</td><td>{ware[3]}</td></tr>'
    html_content += '</table>'

    return web.Response(content_type='text/html', text=html_content)

# App setup
app = web.Application()
app.add_routes([
    web.post('/merchants/register', register_merchant),
    web.post('/merchants/login', login_merchant),
    web.post('/merchants/upload-wares', upload_wares),
    web.get('/wares', get_wares_handler)
])

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)