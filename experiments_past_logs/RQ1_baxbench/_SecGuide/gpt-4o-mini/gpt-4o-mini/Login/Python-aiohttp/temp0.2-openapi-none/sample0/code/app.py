import aiohttp
from aiohttp import web
import sqlite3
import os
import json
import re
from passlib.context import CryptContext

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# Hash password
def hash_password(password):
    return pwd_context.hash(password)

# Verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Validate email format
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Validate password strength
def is_strong_password(password):
    return (len(password) >= 8 and 
            any(char.isdigit() for char in password) and 
            any(char.isalpha() for char in password) and 
            any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for char in password))

# Create a new user
async def register(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return web.json_response({'message': 'Email, password, and name are required.'}, status=400)

    if not is_valid_email(email):
        return web.json_response({'message': 'Invalid email format.'}, status=400)

    if not is_strong_password(password):
        return web.json_response({'message': 'Password must be at least 8 characters long and contain letters, numbers, and special characters.'}, status=400)

    hashed_password = hash_password(password)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (email, hashed_password, name))
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

    if not email or not password:
        return web.json_response({'message': 'Email and password are required.'}, status=401)

    if not is_valid_email(email):
        return web.json_response({'message': 'Invalid email format.'}, status=401)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    if user and verify_password(password, user[0]):
        # Here we would generate a proper JWT token instead of a hardcoded one
        return web.json_response({'message': 'Login successful'}, status=200)
    else:
        return web.json_response({'message': 'Invalid email or password'}, status=401)
    finally:
        conn.close()

# Create the app and routes
app = web.Application()
app.router.add_post('/register', register)
app.router.add_post('/login', login)

# Initialize the database
init_db()

# Run the app
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)