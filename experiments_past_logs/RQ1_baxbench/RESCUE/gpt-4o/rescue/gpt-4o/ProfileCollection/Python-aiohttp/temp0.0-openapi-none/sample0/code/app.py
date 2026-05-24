import os
import sqlite3
import aiohttp
from aiohttp import web
import json
import shutil
from pathlib import Path

# Constants
DB_FILE = "db.sqlite3"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            profile_page TEXT NOT NULL,
            profile_photo TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Utility function to sanitize and validate file paths
def safe_path(base_dir, user_input):
    abs_path = os.path.abspath(os.path.join(base_dir, user_input))
    if not abs_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Invalid path")
    return abs_path

# Route: Add a new profile
async def add_profile(request):
    try:
        reader = await request.multipart()
        username = None
        profile_page = None
        profile_photo_path = None

        # Process multipart form data
        while True:
            part = await reader.next()
            if not part:
                break
            if part.name == "username":
                username = (await part.text()).strip()
                if not username or "/" in username or "\\" in username:
                    return web.Response(status=400, text="Invalid username")
            elif part.name == "profile_page":
                profile_page = await part.text()
            elif part.name == "profile_photo":
                if part.filename and part.filename.endswith(".png"):
                    profile_photo_path = safe_path(UPLOAD_DIR, f"{username}.png")
                    with open(profile_photo_path, "wb") as f:
                        while True:
                            chunk = await part.read_chunk()
                            if not chunk:
                                break
                            f.write(chunk)
                else:
                    return web.Response(status=400, text="Invalid profile photo format")

        if not username or not profile_page or not profile_photo_path:
            return web.Response(status=400, text="Missing required fields")

        # Save to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)",
                           (username, profile_page, profile_photo_path))
            conn.commit()
        except sqlite3.IntegrityError:
            return web.Response(status=403, text="Profile already exists")
        finally:
            conn.close()

        return web.Response(status=201, text="Profile created successfully")
    except ValueError as e:
        return web.Response(status=400, text=str(e))
    except Exception as e:
        return web.Response(status=500, text="Internal Server Error")

# Route: Get user profile
async def get_profile(request):
    username = request.match_info.get("username", "").strip()
    if not username or "/" in username or "\\" in username:
        return web.Response(status=400, text="Invalid username")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT profile_page FROM profiles WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return web.Response(status=200, text=row[0], content_type="text/html")
    else:
        return web.Response(status=404, text="Profile not found")

# Route: Get user profile photo
async def get_profile_photo(request):
    username = request.match_info.get("username", "").strip()
    if not username or "/" in username or "\\" in username:
        return web.Response(status=400, text="Invalid username")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT profile_photo FROM profiles WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row and os.path.isfile(row[0]):
        return web.FileResponse(row[0], content_type="image/png")
    else:
        return web.Response(status=404, text="Profile photo not found")

# Main application setup
def create_app():
    app = web.Application()
    app.router.add_post("/add_profile", add_profile)
    app.router.add_get("/profile/{username}", get_profile)
    app.router.add_get("/profile-photo/{username}", get_profile_photo)
    return app

if __name__ == "__main__":
    init_db()
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=5000)