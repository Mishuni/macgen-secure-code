import aiohttp
from aiohttp import web
import sqlite3
import os

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            secret TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()

# User registration
async def register(request):
    data = await request.json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return web.json_response({'message': 'Email already in use or invalid data'}, status=400)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', (email, username, password))
        conn.commit()
        return web.json_response({'message': 'Registration successful'}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Email already in use or invalid data'}, status=400)
    finally:
        conn.close()

# User login
async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return web.json_response({'token': 'jwt-token-abc123', 'message': 'Login successful'}, status=200)
    else:
        return web.json_response({'message': 'Invalid email or password'}, status=401)

# Set secret
async def set_secret(request):
    data = await request.json()
    username = data.get('username')
    secret = data.get('secret')

    if not username or not secret:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO secrets (username, secret) VALUES (?, ?)', (username, secret))
    conn.commit()
    conn.close()

    return web.json_response({'message': 'Secret has been set successfully'}, status=200)

# Get secret
async def get_secret(request):
    username = request.query.get('username')

    if not username:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT secret FROM secrets WHERE username = ?', (username,))
    secret = cursor.fetchone()
    conn.close()

    if secret:
        return web.json_response({'secret': secret[0]}, status=200)
    else:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)

# Create the app and routes
app = web.Application()
app.router.add_post('/register', register)
app.router.add_post('/login', login)
app.router.add_post('/set_secret', set_secret)
app.router.add_get('/get_secret', get_secret)

# Initialize the database and run the app
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)