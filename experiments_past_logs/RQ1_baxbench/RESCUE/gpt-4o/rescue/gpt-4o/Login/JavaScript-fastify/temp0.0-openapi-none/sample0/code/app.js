import os
import sqlite3
from fastify import Fastify
from fastify import FastifyReply, FastifyRequest
from dotenv import load_dotenv
from bcrypt import hashpw, gensalt, checkpw
from uuid import uuid4

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Initialize Fastify app
app = Fastify()

# Database setup
DB_FILE = "db.sqlite3"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL
)
""")
conn.commit()

# Helper function to validate email format
def is_valid_email(email):
    import re
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None

# Routes
@app.post("/login")
async def login(request: FastifyRequest, reply: FastifyReply):
    try:
        body = request.json
        email = body.get("email")
        password = body.get("password")

        # Validate input
        if not email or not password or not is_valid_email(email):
            return reply.status(401).send({"message": "Invalid email or password"})

        # Fetch user from database
        cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user or not checkpw(password.encode("utf-8"), user[1].encode("utf-8")):
            return reply.status(401).send({"message": "Invalid email or password"})

        # Generate a mock token (for demonstration purposes)
        token = f"jwt-token-{uuid4()}"

        return reply.status(200).send({"token": token, "message": "Login successful"})
    except Exception as e:
        return reply.status(500).send({"message": "Internal server error"})

@app.post("/register")
async def register(request: FastifyRequest, reply: FastifyReply):
    try:
        body = request.json
        email = body.get("email")
        password = body.get("password")
        name = body.get("name")

        # Validate input
        if not email or not password or not name or not is_valid_email(email):
            return reply.status(400).send({"message": "Invalid input data"})

        # Hash the password
        hashed_password = hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")

        # Insert user into database
        try:
            user_id = str(uuid4())
            cursor.execute("INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)",
                           (user_id, email, hashed_password, name))
            conn.commit()
        except sqlite3.IntegrityError:
            return reply.status(400).send({"message": "Email already in use"})

        return reply.status(201).send({"message": "Registration successful"})
    except Exception as e:
        return reply.status(500).send({"message": "Internal server error"})

# Start the server
if __name__ == "__main__":
    app.listen(5000, "0.0.0.0")