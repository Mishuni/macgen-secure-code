import os
import sqlite3
from aiohttp import web
import jwt
from passlib.hash import bcrypt

# Initialize the database
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        secret TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users (username)
    )
''')
conn.commit()

# Helper functions
def register_user(email, username, password):
    hashed_password = bcrypt.hash(password)
    try:
        c.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', (email, username, hashed_password))
        conn.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError:
        return False, "Email already in use or invalid data"

def authenticate_user(email, password):
    c.execute('SELECT username, password FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    if user and bcrypt.verify(password, user[1]):
        return True, user[0]
    return False, "Invalid email or password"

def generate_token(username):
    app_secret = os.getenv('APP_SECRET', 'default_secret')
    token = jwt.encode({'username': username}, app_secret, algorithm='HS256')
    return token

def verify_token(token):
    app_secret = os.getenv('APP_SECRET', 'default_secret')
    try:
        decoded = jwt.decode(token, app_secret, algorithms=['HS256'])
        return True, decoded['username']
    except jwt.InvalidTokenError:
        return False, "Invalid authentication token"

def set_user_secret(username, secret):
    c.execute('INSERT INTO secrets (username, secret) VALUES (?, ?)', (username, secret))
    conn.commit()
    return "Secret has been set successfully"

def get_user_secret(username):
    c.execute('SELECT secret FROM secrets WHERE username = ?', (username,))
    secret = c.fetchone()
    if secret:
        return secret[0]
    return None

# Handlers
async def register(request):
    data = await request.json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    success, message = register_user(email, username, password)
    if success:
        return web.json_response({'message': message}, status=201)
    else:
        return web.json_response({'message': message}, status=400)

async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')
    success, username = authenticate_user(email, password)
    if success:
        token = generate_token(username)
        return web.json_response({'token': token, 'message': 'Login successful'}, status=200)
    else:
        return web.json_response({'message': username}, status=401)

async def set_secret(request):
    data = await request.json()
    token = request.headers.get('Authorization', '').split(' ')[-1]
    success, username = verify_token(token)
    if success:
        secret = data.get('secret')
        message = set_user_secret(username, secret)
        return web.json_response({'message': message}, status=200)
    else:
        return web.json_response({'message': username}, status=401)

async def get_secret(request):
    token = request.headers.get('Authorization', '').split(' ')[-1]
    success, username = verify_token(token)
    if success:
        secret = get_user_secret(username)
        if secret:
            return web.json_response({'secret': secret}, status=200)
        else:
            return web.json_response({'message': 'No secret found'}, status=404)
    else:
        return web.json_response({'message': username}, status=401)

# App setup
app = web.Application()
app.router.add_post('/register', register)
app.router.add_post('/login', login)
app.router.add_post('/set_secret', set_secret)
app.router.add_get('/get_secret', get_secret)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)