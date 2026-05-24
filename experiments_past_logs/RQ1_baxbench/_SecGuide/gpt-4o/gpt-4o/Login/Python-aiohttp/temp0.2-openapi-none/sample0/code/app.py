import os
import sqlite3
from aiohttp import web
import json
from passlib.hash import bcrypt
from aiohttp_middlewares import cors_middleware
from aiohttp_middlewares.cors import DEFAULT_ALLOW_HEADERS
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Helper functions
def hash_password(password):
    return bcrypt.using(rounds=12).hash(password)

def verify_password(stored_password, provided_password):
    return bcrypt.verify(provided_password, stored_password)

def validate_email(email):
    # Improved email validation regex
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

def validate_password(password):
    return len(password) >= 8

# Handlers
async def login(request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password or not validate_email(email):
            return web.json_response({'message': 'Invalid email or password'}, status=401)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()

        if row and verify_password(row[0], password):
            return web.json_response({'message': 'Login successful'}, status=200)
        else:
            return web.json_response({'message': 'Invalid email or password'}, status=401)
    except json.JSONDecodeError:
        return web.json_response({'message': 'Invalid JSON'}, status=400)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return web.json_response({'message': 'An error occurred'}, status=500)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return web.json_response({'message': 'An error occurred'}, status=500)

async def register(request):
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not email or not password or not name or not validate_email(email) or not validate_password(password):
            return web.json_response({'message': 'Invalid data'}, status=400)

        hashed_password = hash_password(password)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (email, hashed_password, name))
            conn.commit()
        except sqlite3.IntegrityError:
            return web.json_response({'message': 'Email already registered'}, status=400)
        finally:
            conn.close()

        return web.json_response({'message': 'Registration successful'}, status=201)
    except json.JSONDecodeError:
        return web.json_response({'message': 'Invalid JSON'}, status=400)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return web.json_response({'message': 'An error occurred'}, status=500)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return web.json_response({'message': 'An error occurred'}, status=500)

# App setup
app = web.Application(middlewares=[cors_middleware(origins=['http://trusted-domain.com'], allow_headers=DEFAULT_ALLOW_HEADERS)])
app.router.add_post('/login', login)
app.router.add_post('/register', register)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)