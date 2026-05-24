
import os
import jwt
import sqlite3
from aiohttp import web
from passlib.hash import bcrypt
from aiohttp.web_middlewares import middleware

APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Database setup
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
    user_id INTEGER NOT NULL,
    secret TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')
conn.commit()

# Middleware for JWT authentication
@middleware
async def auth_middleware(request, handler):
    if request.path in ['/register', '/login']:
        return await handler(request)
    
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)
    
    try:
        token = auth_header.split(" ")[1]
        jwt.decode(token, APP_SECRET, algorithms=["HS256"])
    except (IndexError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return web.json_response({'message': 'Invalid authentication token'}, status=401)
    
    return await handler(request)

# Register a new user
async def register(request):
    data = await request.json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return web.json_response({'message': 'Invalid data'}, status=400)

    hashed_password = bcrypt.hash(password)
    try:
        cursor.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', (email, username, hashed_password))
        conn.commit()
        return web.json_response({'message': 'Registration successful'}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Email already in use or invalid data'}, status=400)

# User login
async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    cursor.execute('SELECT id, password FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    if user and bcrypt.verify(password, user[1]):
        token = jwt.encode({'user_id': user[0]}, APP_SECRET, algorithm="HS256")
        return web.json_response({'token': token, 'message': 'Login successful'}, status=200)
    else:
        return web.json_response({'message': 'Invalid email or password'}, status=401)

# Set secret
async def set_secret(request):
    data = await request.json()
    username = data.get('username')
    secret = data.get('secret')

    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    if user:
        cursor.execute('INSERT INTO secrets (user_id, secret) VALUES (?, ?)', (user[0], secret))
        conn.commit()
        return web.json_response({'message': 'Secret has been set successfully'}, status=200)
    else:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)

# Get secret
async def get_secret(request):
    username = request.query.get('username')

    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    if user:
        cursor.execute('SELECT secret FROM secrets WHERE user_id = ?', (user[0],))
        secret = cursor.fetchone()
        if secret:
            return web.json_response({'secret': secret[0]}, status=200)
        else:
            return web.json_response({'message': 'No secret found'}, status=404)
    else:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)

# Setup application and routes
app = web.Application(middlewares=[auth_middleware])
app.router.add_post('/register', register)
app.router.add_post('/login', login)
app.router.add_post('/set_secret', set_secret)
app.router.add_get('/get_secret', get_secret)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)