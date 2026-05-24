import os
import sqlite3
from aiohttp import web
import json
from passlib.hash import bcrypt
import jwt
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
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

# Security setup
APP_SECRET = os.environ.get('APP_SECRET', 'default_secret')
fernet_key = fernet.Fernet.generate_key()
secret_key = fernet.Fernet(fernet_key)

# Helper functions
def hash_password(password):
    return bcrypt.hash(password)

def verify_password(password, hashed):
    return bcrypt.verify(password, hashed)

def create_jwt_token(email):
    return jwt.encode({'email': email}, APP_SECRET, algorithm='HS256')

def decode_jwt_token(token):
    try:
        return jwt.decode(token, APP_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Middleware
async def auth_middleware(app, handler):
    async def middleware_handler(request):
        if request.path in ['/merchants/register', '/merchants/login']:
            return await handler(request)
        session = await get_session(request)
        if 'user' not in session:
            return web.json_response({'error': 'Unauthorized'}, status=401)
        return await handler(request)
    return middleware_handler

# Handlers
async def register_merchant(request):
    data = await request.json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return web.json_response({'error': 'Invalid input'}, status=400)

    hashed_password = hash_password(password)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return web.json_response({'error': 'Email already registered'}, status=400)
    finally:
        conn.close()

    return web.json_response({'message': 'Merchant registered successfully'}, status=201)

async def login_merchant(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return web.json_response({'error': 'Invalid input'}, status=400)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM merchants WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()

    if row and verify_password(password, row[0]):
        session = await get_session(request)
        session['user'] = email
        return web.json_response({'message': 'Login successful'}, status=200)
    else:
        return web.json_response({'error': 'Invalid email or password'}, status=401)

async def upload_wares(request):
    session = await get_session(request)
    email = session.get('user')

    data = await request.json()
    csv_data = data.get('csv')

    if not csv_data:
        return web.json_response({'error': 'Invalid CSV format'}, status=400)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM merchants WHERE email = ?', (email,))
    merchant_id = cursor.fetchone()[0]

    wares = []
    for line in csv_data.splitlines():
        name, description, price = line.split(',')
        wares.append((merchant_id, name.strip(), description.strip(), float(price.strip())))

    cursor.executemany('INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)', wares)
    conn.commit()
    conn.close()

    return web.json_response({'message': 'Wares uploaded successfully'}, status=200)

async def retrieve_wares(request):
    min_price = request.query.get('minPrice')
    max_price = request.query.get('maxPrice')

    query = 'SELECT wares.name, wares.price, wares.description, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1'
    params = []

    if min_price:
        query += ' AND wares.price >= ?'
        params.append(float(min_price))
    if max_price:
        query += ' AND wares.price <= ?'
        params.append(float(max_price))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    html = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>'
    for row in rows:
        html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>'
    html += '</table>'

    return web.Response(text=html, content_type='text/html')

# App setup
app = web.Application(middlewares=[session_middleware(EncryptedCookieStorage(secret_key)), auth_middleware])
app.router.add_post('/merchants/register', register_merchant)
app.router.add_post('/merchants/login', login_merchant)
app.router.add_post('/merchants/upload-wares', upload_wares)
app.router.add_get('/wares', retrieve_wares)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)