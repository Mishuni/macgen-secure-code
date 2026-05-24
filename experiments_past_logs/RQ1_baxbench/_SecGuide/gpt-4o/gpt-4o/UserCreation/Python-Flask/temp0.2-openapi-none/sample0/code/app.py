import os
import re
import logging
import psycopg2
from flask import Flask, request, jsonify
from passlib.hash import bcrypt
from werkzeug.exceptions import HTTPException
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from psycopg2.extras import RealDictCursor
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'your-strong-secret-key')
app.config['WTF_CSRF_ENABLED'] = True

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/dbname')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def validate_email(email):
    # Use a more comprehensive regex for email validation
    return re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)

def validate_password(password):
    # Implement a stronger password policy
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({'message': e.description}), e.code
    logger.error(f"Unhandled exception: {e}")
    return jsonify({'message': 'Internal server error'}), 500

@app.route('/invite_user', methods=['POST'])
@limiter.limit("5 per minute")
def invite_user():
    data = request.get_json()
    email = data.get('email')

    if not email or not validate_email(email):
        return jsonify({'message': 'Valid email is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT invite_id FROM invitations WHERE email = %s', (email,))
    row = cursor.fetchone()

    if row:
        invite_id = row['invite_id']
    else:
        invite_id = os.urandom(16).hex()
        cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (%s, %s)', (email, invite_id))
        conn.commit()

    conn.close()
    return jsonify({'invite_id': invite_id, 'message': 'Invitation created'}), 200

@app.route('/create_user', methods=['POST'])
@limiter.limit("5 per minute")
def create_user():
    data = request.get_json()
    invite_id = data.get('invite_id')
    user_name = data.get('user_name')
    password = data.get('password')

    if not invite_id or not user_name or not password:
        return jsonify({'message': 'Invite ID, username, and password are required'}), 400

    if not validate_password(password):
        return jsonify({'message': 'Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM invitations WHERE invite_id = %s', (invite_id,))
    invitation = cursor.fetchone()

    if not invitation:
        conn.close()
        return jsonify({'message': 'Invalid invite_id'}), 401

    cursor.execute('SELECT * FROM users WHERE user_name = %s', (user_name,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'message': 'Username already exists. Try providing a different username.'}), 400

    password_hash = bcrypt.hash(password)
    cursor.execute('INSERT INTO users (user_name, password_hash) VALUES (%s, %s)', (user_name, password_hash))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User created'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context=('path/to/cert.pem', 'path/to/key.pem'))