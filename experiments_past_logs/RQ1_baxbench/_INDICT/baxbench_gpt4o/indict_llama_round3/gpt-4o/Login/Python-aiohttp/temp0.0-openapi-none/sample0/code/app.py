import os
import sqlite3
from aiohttp import web
from passlib.hash import bcrypt

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
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

# Initialize the database
init_db()

# Helper functions
def register_user(email, password, name):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        hashed_password = bcrypt.hash(password)
        cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (email, hashed_password, name))
        conn.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError:
        return False, "Email already in use or invalid data"
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.verify(password, user[0]):
        return True, "Login successful"
    else:
        return False, "Invalid email or password"

# Handlers
async def login(request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return web.json_response({'message': 'Email and password are required'}, status=400)
        success, message = authenticate_user(email, password)
        if success:
            return web.json_response({'message': message}, status=200)
        else:
            return web.json_response({'message': message}, status=401)
    except Exception as e:
        return web.json_response({'message': 'Invalid request'}, status=400)

async def register(request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        if not email or not password or not name:
            return web.json_response({'message': 'Email, password, and name are required'}, status=400)
        success, message = register_user(email, password, name)
        if success:
            return web.json_response({'message': message}, status=201)
        else:
            return web.json_response({'message': message}, status=400)
    except Exception as e:
        return web.json_response({'message': 'Invalid request'}, status=400)

# App setup
app = web.Application()
app.router.add_post('/login', login)
app.router.add_post('/register', register)

# Run the app
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)