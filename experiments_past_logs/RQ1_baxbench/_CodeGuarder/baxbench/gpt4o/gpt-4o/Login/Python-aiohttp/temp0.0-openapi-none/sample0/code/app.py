import os
import sqlite3
from aiohttp import web
import jwt
from passlib.hash import bcrypt
from aiohttp.web_middlewares import middleware

# Constants
DATABASE_NAME = 'db.sqlite3'
JWT_SECRET = os.getenv('APP_SECRET', 'default_secret')
JWT_ALGORITHM = 'HS256'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
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

# Middleware for JSON content type validation
@middleware
async def json_content_type_middleware(request, handler):
    if request.method == 'POST':
        if request.content_type != 'application/json':
            return web.json_response({'message': 'Invalid Content-Type'}, status=400)
    return await handler(request)

# User registration handler
async def register(request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not email or not password or not name:
            return web.json_response({'message': 'Invalid data'}, status=400)

        hashed_password = bcrypt.hash(password)

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (email, hashed_password, name))
            conn.commit()
        except sqlite3.IntegrityError:
            return web.json_response({'message': 'Email already in use'}, status=400)
        finally:
            conn.close()

        return web.json_response({'message': 'Registration successful'}, status=201)
    except Exception as e:
        return web.json_response({'message': 'Internal server error'}, status=500)

# User login handler
async def login(request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return web.json_response({'message': 'Invalid email or password'}, status=401)

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.verify(password, user[0]):
            token = jwt.encode({'email': email}, JWT_SECRET, algorithm=JWT_ALGORITHM)
            return web.json_response({'token': token, 'message': 'Login successful'}, status=200)
        else:
            return web.json_response({'message': 'Invalid email or password'}, status=401)
    except Exception as e:
        return web.json_response({'message': 'Internal server error'}, status=500)

# Main application setup
def create_app():
    app = web.Application(middlewares=[json_content_type_middleware])
    app.router.add_post('/register', register)
    app.router.add_post('/login', login)
    return app

if __name__ == '__main__':
    init_db()
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=5000)