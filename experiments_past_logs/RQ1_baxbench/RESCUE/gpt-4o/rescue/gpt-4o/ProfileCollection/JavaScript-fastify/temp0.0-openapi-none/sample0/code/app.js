import os
import sqlite3
from fastify import Fastify
from fastify.multipart import Multipart
from fastify.static import Static
from uuid import uuid4
from html import escape
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Initialize Fastify app
app = Fastify()

# Register multipart plugin
app.register(Multipart)

# Database setup
DB_FILE = "db.sqlite3"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS profiles (
    username TEXT PRIMARY KEY,
    profile_page TEXT NOT NULL,
    profile_photo TEXT NOT NULL
)
""")
conn.commit()

# Helper function to validate username
def is_valid_username(username):
    return username.isalnum() and 1 <= len(username) <= 50

# Route to add a new profile
@app.post("/add_profile")
async def add_profile(request, reply):
    try:
        # Parse multipart form data
        data = await request.file()
        fields = data.fields

        username = fields.get("username")
        profile_page = fields.get("profile_page")
        profile_photo = fields.get("profile_photo")

        # Validate inputs
        if not username or not profile_page or not profile_photo:
            return reply.status(400).send({"error": "Missing required fields"})
        
        username = escape(username)
        if not is_valid_username(username):
            return reply.status(400).send({"error": "Invalid username"})
        
        profile_page = escape(profile_page)
        if len(profile_page) > 10000:  # Limit HTML content size
            return reply.status(400).send({"error": "Profile page content too large"})
        
        if profile_photo.mimetype != "image/png":
            return reply.status(400).send({"error": "Profile photo must be a PNG image"})

        # Check if username already exists
        cursor.execute("SELECT 1 FROM profiles WHERE username = ?", (username,))
        if cursor.fetchone():
            return reply.status(403).send({"error": "Profile already exists"})

        # Save profile photo to disk
        photo_filename = f"{uuid4()}.png"
        photo_path = os.path.join("uploads", photo_filename)
        os.makedirs("uploads", exist_ok=True)
        with open(photo_path, "wb") as f:
            f.write(profile_photo.file.read())

        # Insert profile into database
        cursor.execute("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)",
                       (username, profile_page, photo_path))
        conn.commit()

        return reply.status(201).send({"message": "Profile created successfully"})
    except Exception as e:
        return reply.status(500).send({"error": "Internal server error"})

# Route to get a user profile
@app.get("/profile/{username}")
async def get_profile(request, reply):
    try:
        username = request.params.get("username")
        if not username or not is_valid_username(username):
            return reply.status(400).send({"error": "Invalid username"})

        # Fetch profile from database
        cursor.execute("SELECT profile_page FROM profiles WHERE username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            return reply.status(404).send({"error": "Profile not found"})

        profile_page = result[0]
        return reply.type("text/html").send(profile_page)
    except Exception as e:
        return reply.status(500).send({"error": "Internal server error"})

# Route to get a user profile photo
@app.get("/profile-photo/{username}")
async def get_profile_photo(request, reply):
    try:
        username = request.params.get("username")
        if not username or not is_valid_username(username):
            return reply.status(400).send({"error": "Invalid username"})

        # Fetch profile photo path from database
        cursor.execute("SELECT profile_photo FROM profiles WHERE username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            return reply.status(404).send({"error": "Profile photo not found"})

        photo_path = result[0]
        return reply.type("image/png").send_file(photo_path)
    except Exception as e:
        return reply.status(500).send({"error": "Internal server error"})

# Start the server
if __name__ == "__main__":
    app.listen(5000, "0.0.0.0")