import os
import sqlite3
from aiohttp import web
import jwt
from passlib.hash import bcrypt
from aiohttp.web_middlewares import middleware
from datetime import datetime, timedelta
import ssl

# Constants
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')
APP_SECRET = os.getenv('APP_SECRET')
if not APP_SECRET:
    raise EnvironmentError("APP_SECRET environment variable not set")

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
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

# Middleware for JWT authentication
@middleware
async def auth_middleware(request, handler):
    if request.path in ['/register', '/login']:
        return await handler(request)
    
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        return web.json_response({'message': 'Authentication required'}, status=401)
    
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, APP_SECRET, algorithms=['HS256'])
        request['user'] = payload
    except (IndexError, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return web.json_response({'message': 'Invalid or expired authentication token'}, status=401)
    
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
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', (email, username, hashed_password))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Email or username already in use'}, status=400)

    return web.json_response({'message': 'Registration successful'}, status=201)

# User login
async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return web.json_response({'message': 'Invalid email or password'}, status=401)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()

    if row and bcrypt.verify(password, row[0]):
        token = jwt.encode({'email': email, 'exp': datetime.utcnow() + timedelta(hours=1)}, APP_SECRET, algorithm='HS256')
        return web.json_response({'token': token, 'message': 'Login successful'}, status=200)
    
    return web.json_response({'message': 'Invalid email or password'}, status=401)

# Set secret
async def set_secret(request):
    data = await request.json()
    secret = data.get('secret')

    if not secret:
        return web.json_response({'message': 'Invalid data'}, status=400)

    username = request['user']['email']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO secrets (username, secret) VALUES (?, ?)', (username, secret))
    conn.commit()
    conn.close()

    return web.json_response({'message': 'Secret has been set successfully'}, status=200)

# Get secret
async def get_secret(request):
    username = request['user']['email']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT secret FROM secrets WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return web.json_response({'secret': row[0]}, status=200)
    
    return web.json_response({'message': 'Secret not found'}, status=404)

# Create app and routes
app = web.Application(middlewares=[auth_middleware])
app.router.add_post('/register', register)
app.router.add_post('/login', login)
app.router.add_post('/set_secret', set_secret)
app.router.add_get('/get_secret', get_secret)

# Initialize database and run app
init_db()

# SSL context for HTTPS
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile='path/to/certfile', keyfile='path/to/keyfile')

web.run_app(app, host='0.0.0.0', port=5000, ssl_context=ssl_context)