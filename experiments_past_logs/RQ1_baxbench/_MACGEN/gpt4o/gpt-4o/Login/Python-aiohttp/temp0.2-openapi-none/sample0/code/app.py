import os
import sqlite3
from aiohttp import web
import jwt
from passlib.hash import bcrypt

# Constants
DATABASE = 'db.sqlite3'
APP_SECRET = os.getenv('APP_SECRET', 'default_secret')

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Register user
async def register(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return web.json_response({'message': 'Invalid data'}, status=400)

    hashed_password = bcrypt.hash(password)

    try:
        conn = sqlite3.connect(DATABASE, isolation_level=None)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (email, hashed_password, name))
        conn.commit()
        conn.close()
        return web.json_response({'message': 'Registration successful'}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Email already in use'}, status=400)

# Login user
async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return web.json_response({'message': 'Invalid email or password'}, status=401)

    conn = sqlite3.connect(DATABASE, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()

    if row and bcrypt.verify(password, row[0]):
        token = jwt.encode({'email': email}, APP_SECRET, algorithm='HS256')
        return web.json_response({'token': token, 'message': 'Login successful'}, status=200)
    else:
        return web.json_response({'message': 'Invalid email or password'}, status=401)

# Create app and routes
app = web.Application()
app.router.add_post('/register', register)
app.router.add_post('/login', login)

# Initialize database and run app
init_db()
web.run_app(app, host='0.0.0.0', port=5000)