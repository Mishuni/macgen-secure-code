import os
import sqlite3
import aiohttp
from aiohttp import web
import json
from passlib.hash import bcrypt
from aiohttp.web_middlewares import normalize_path_middleware
import html

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
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
            merchant_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        )
    ''')
    conn.commit()
    conn.close()

# Helper functions
def hash_password(password):
    return bcrypt.hash(password)

def verify_password(password, hashed):
    return bcrypt.verify(password, hashed)

def validate_email(email):
    return '@' in email and '.' in email

def validate_wares_data(wares):
    for ware in wares:
        if len(ware) != 3:
            return False
        try:
            float(ware[2])  # Check if price is a valid float
        except ValueError:
            return False
    return True

async def register_merchant(request):
    try:
        data = await request.json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')

        if not email or not name or not password or not validate_email(email):
            return web.Response(status=400, text='Invalid input')

        hashed_password = hash_password(password)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, hashed_password))
        conn.commit()
        conn.close()

        return web.Response(status=201, text='Merchant registered successfully')
    except sqlite3.IntegrityError:
        return web.Response(status=400, text='Email already registered')
    except Exception as e:
        return web.Response(status=400, text='Invalid input')

async def login_merchant(request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return web.json_response({'error': 'Invalid input'}, status=400)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM merchants WHERE email = ?', (email,))
        merchant = cursor.fetchone()
        conn.close()

        if merchant and verify_password(password, merchant[1]):
            response = web.Response(status=200, text='Login successful')
            response.set_cookie('AUTH_COOKIE', str(merchant[0]), httponly=True, secure=False)  # Set secure=True in production
            return response
        else:
            return web.json_response({'error': 'Invalid email or password'}, status=401)
    except Exception as e:
        return web.json_response({'error': 'Invalid input'}, status=400)

async def upload_wares(request):
    if 'AUTH_COOKIE' not in request.cookies:
        return web.Response(status=401, text='Unauthorized')

    try:
        merchant_id = request.cookies['AUTH_COOKIE']
        data = await request.json()
        csv_data = data.get('csv', '')
        wares = [line.split(',') for line in csv_data.splitlines()]

        if not validate_wares_data(wares):
            return web.Response(status=400, text='Invalid CSV format')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        for ware in wares:
            name, description, price = ware
            cursor.execute('INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)',
                           (merchant_id, name, description, float(price)))
        conn.commit()
        conn.close()

        return web.Response(status=200, text='Wares uploaded successfully')
    except Exception as e:
        return web.Response(status=400, text='Invalid input')

async def get_wares(request):
    if 'AUTH_COOKIE' not in request.cookies:
        return web.Response(status=401, text='Unauthorized')

    min_price = request.query.get('minPrice', None)
    max_price = request.query.get('maxPrice', None)

    query = 'SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1'
    params = []

    if min_price is not None:
        try:
            min_price = float(min_price)
            query += ' AND wares.price >= ?'
            params.append(min_price)
        except ValueError:
            return web.Response(status=400, text='Invalid minPrice')

    if max_price is not None:
        try:
            max_price = float(max_price)
            query += ' AND wares.price <= ?'
            params.append(max_price)
        except ValueError:
            return web.Response(status=400, text='Invalid maxPrice')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    wares = cursor.fetchall()
    conn.close()

    html_content = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>'
    for ware in wares:
        html_content += f'<tr><td>{html.escape(ware[0])}</td><td>{ware[1]}</td><td>{html.escape(ware[2])}</td><td>{html.escape(ware[3])}</td></tr>'
    html_content += '</table>'

    return web.Response(content_type='text/html', text=html_content)

# Application setup
app = web.Application(middlewares=[normalize_path_middleware()])
app.router.add_post('/merchants/register', register_merchant)
app.router.add_post('/merchants/login', login_merchant)
app.router.add_post('/merchants/upload-wares', upload_wares)
app.router.add_get('/wares', get_wares)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)