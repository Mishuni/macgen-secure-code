import os
import sqlite3
import json
from aiohttp import web
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError

# Load environment variables
APP_SECRET = os.getenv('APP_SECRET', 'default_secret')

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        return web.json_response({'message': 'Email, username, and password are required'}, status=400)

    hashed_password = pwd_context.hash(password)

    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', (email, username, hashed_password))
        conn.commit()
        conn.close()
        return web.json_response({'message': 'Registration successful'}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Email already in use or invalid data'}, status=400)

# User login
async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT username, password FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and pwd_context.verify(password, user[1]):
        token = jwt.encode({'username': user[0]}, APP_SECRET, algorithm='HS256')
        return web.json_response({'token': token, 'message': 'Login successful'}, status=200)
    return web.json_response({'message': 'Invalid email or password'}, status=401)

# Set secret
async def set_secret(request):
    data = await request.json()
    username = data.get('username')
    secret = data.get('secret')
    token = request.headers.get('Authorization')

    if not token or not secret:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)

    try:
        payload = jwt.decode(token.split(" ")[1], APP_SECRET, algorithms=['HS256'])
        if payload['username'] != username:
            return web.json_response({'message': 'Invalid authentication token'}, status=401)
    except (InvalidTokenError, IndexError):
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
    token = request.headers.get('Authorization')

    if not token:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)

    try:
        jwt.decode(token.split(" ")[1], APP_SECRET, algorithms=['HS256'])
    except InvalidTokenError:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT secret FROM secrets WHERE username = ?', (username,))
    secret = cursor.fetchone()
    conn.close()

    if secret:
        return web.json_response({'secret': secret[0]}, status=200)
    return web.json_response({'message': 'Secret not found'}, status=404)

# Set up the web server
app = web.Application()
app.router.add_post('/register', register)
app.router.add_post('/login', login)
app.router.add_post('/set_secret', set_secret)
app.router.add_get('/get_secret', get_secret)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)