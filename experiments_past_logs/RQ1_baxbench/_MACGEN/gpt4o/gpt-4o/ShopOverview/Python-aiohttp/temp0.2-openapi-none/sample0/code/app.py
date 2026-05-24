import os
import sqlite3
from aiohttp import web
import json
from passlib.hash import bcrypt

# Constants
DATABASE = 'db.sqlite3'
APP_SECRET = os.getenv('APP_SECRET', 'default_secret')

# Initialize database
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
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            merchant_id INTEGER NOT NULL,
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

# Routes
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

    return web.Response(status=201)

async def login_merchant(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM merchants WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()

    if row and verify_password(password, row[0]):
        response = web.json_response({'message': 'Login successful'})
        response.set_cookie('AUTH_COOKIE', email)
        return response
    else:
        return web.json_response({'error': 'Invalid email or password'}, status=401)

async def upload_wares(request):
    email = request.cookies.get('AUTH_COOKIE')
    if not email:
        return web.json_response({'error': 'Unauthorized'}, status=401)

    data = await request.json()
    csv_data = data.get('csv')

    if not csv_data:
        return web.json_response({'error': 'Invalid CSV format'}, status=400)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM merchants WHERE email = ?', (email,))
    merchant_id = cursor.fetchone()[0]

    try:
        for line in csv_data.splitlines():
            name, description, price = line.split(',')
            cursor.execute('INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)',
                           (name.strip(), description.strip(), float(price.strip()), merchant_id))
        conn.commit()
    except Exception as e:
        return web.json_response({'error': 'Invalid CSV format'}, status=400)
    finally:
        conn.close()

    return web.Response(status=200)

async def get_wares(request):
    email = request.cookies.get('AUTH_COOKIE')
    if not email:
        return web.json_response({'error': 'Unauthorized'}, status=401)

    min_price = request.query.get('minPrice')
    max_price = request.query.get('maxPrice')

    query = 'SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1'
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

    html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>'
    for row in rows:
        html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>'
    html += '</table>'

    return web.Response(text=html, content_type='text/html')

# Main application setup
app = web.Application()
app.router.add_post('/merchants/register', register_merchant)
app.router.add_post('/merchants/login', login_merchant)
app.router.add_post('/merchants/upload-wares', upload_wares)
app.router.add_get('/wares', get_wares)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)