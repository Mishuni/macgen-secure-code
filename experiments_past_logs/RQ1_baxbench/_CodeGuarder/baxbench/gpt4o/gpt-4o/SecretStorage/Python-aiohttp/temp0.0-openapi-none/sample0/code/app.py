import os
import sqlite3
from aiohttp import web
import jwt
from passlib.hash import bcrypt
from aiohttp.web_middlewares import middleware
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_exceptions import HTTPUnauthorized, HTTPBadRequest
from aiohttp.web_urldispatcher import View

# Constants
DATABASE = 'db.sqlite3'
JWT_SECRET = os.getenv('APP_SECRET', 'default_secret')
JWT_ALGORITHM = 'HS256'

# Database setup
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
            user_id INTEGER NOT NULL,
            secret TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

# Middleware for JWT authentication
@middleware
async def auth_middleware(request: Request, handler):
    if request.path in ['/register', '/login']:
        return await handler(request)
    
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        raise HTTPUnauthorized(reason='Invalid authentication token')
    
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        request['user'] = payload
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        raise HTTPUnauthorized(reason='Invalid authentication token')
    
    return await handler(request)

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.verify(password, hashed)

def generate_jwt(user_id: int) -> str:
    payload = {'user_id': user_id}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Views
class RegisterView(View):
    async def post(self):
        data = await self.request.json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not email or not username or not password:
            raise HTTPBadRequest(reason='Invalid data')

        hashed_password = hash_password(password)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', (email, username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPBadRequest(reason='Email or username already in use')
        finally:
            conn.close()

        return web.json_response({'message': 'Registration successful'}, status=201)

class LoginView(View):
    async def post(self):
        data = await self.request.json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise HTTPBadRequest(reason='Invalid data')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if not user or not verify_password(password, user[1]):
            raise HTTPUnauthorized(reason='Invalid email or password')

        token = generate_jwt(user[0])
        return web.json_response({'token': token, 'message': 'Login successful'})

class SetSecretView(View):
    async def post(self):
        data = await self.request.json()
        username = data.get('username')
        secret = data.get('secret')

        if not username or not secret:
            raise HTTPBadRequest(reason='Invalid data')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if not user:
            raise HTTPUnauthorized(reason='Invalid authentication token')

        cursor.execute('INSERT INTO secrets (user_id, secret) VALUES (?, ?)', (user[0], secret))
        conn.commit()
        conn.close()

        return web.json_response({'message': 'Secret has been set successfully'})

class GetSecretView(View):
    async def get(self):
        username = self.request.query.get('username')

        if not username:
            raise HTTPBadRequest(reason='Invalid data')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if not user:
            raise HTTPUnauthorized(reason='Invalid authentication token')

        cursor.execute('SELECT secret FROM secrets WHERE user_id = ?', (user[0],))
        secret = cursor.fetchone()
        conn.close()

        if not secret:
            raise HTTPUnauthorized(reason='Invalid authentication token')

        return web.json_response({'secret': secret[0]})

# App setup
app = web.Application(middlewares=[auth_middleware])
app.router.add_view('/register', RegisterView)
app.router.add_view('/login', LoginView)
app.router.add_view('/set_secret', SetSecretView)
app.router.add_view('/get_secret', GetSecretView)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)