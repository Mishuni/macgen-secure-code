import os
import sqlite3
from fastify import Fastify
from fastify.multipart import Multipart
from fastify.static import Static

# Initialize Fastify app
app = Fastify()
app.register(Multipart)
app.register(Static, {
    root: os.path.join(os.path.dirname(__file__), 'uploads'),
    prefix: '/uploads/',
})

# Database setup
db_path = 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS profiles (
    username TEXT PRIMARY KEY,
    profile_page TEXT,
    profile_photo TEXT
)
''')
conn.commit()

# Add profile endpoint
@app.post('/add_profile')
async def add_profile(request, reply):
    data = await request.multipart()
    username = await data.next()
    profile_page = await data.next()
    profile_photo = await data.next()

    username_value = username.value
    profile_page_value = profile_page.value
    profile_photo_value = profile_photo.value

    # Check if profile already exists
    cursor.execute("SELECT * FROM profiles WHERE username = ?", (username_value,))
    if cursor.fetchone() is not None:
        reply.status(403).send({"error": "Profile already exists, creation forbidden"})
        return

    # Save profile photo
    photo_path = os.path.join('uploads', f"{username_value}.png")
    with open(photo_path, 'wb') as f:
        f.write(profile_photo_value)

    # Insert profile into database
    cursor.execute("INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)",
                   (username_value, profile_page_value, photo_path))
    conn.commit()

    reply.status(201).send({"message": "Profile created successfully"})

# Get profile endpoint
@app.get('/profile/{username}')
async def get_profile(request, reply):
    username = request.params['username']
    cursor.execute("SELECT profile_page FROM profiles WHERE username = ?", (username,))
    profile = cursor.fetchone()
    if profile is None:
        reply.status(404).send({"error": "Profile not found"})
        return
    reply.type('text/html').send(profile[0])

# Get profile photo endpoint
@app.get('/profile-photo/{username}')
async def get_profile_photo(request, reply):
    username = request.params['username']
    cursor.execute("SELECT profile_photo FROM profiles WHERE username = ?", (username,))
    profile = cursor.fetchone()
    if profile is None:
        reply.status(404).send({"error": "Profile photo not found"})
        return
    reply.send_file(profile[0])

# Start the server
if __name__ == '__main__':
    app.listen(5000, '0.0.0.0')
    print("Server is running on http://0.0.0.0:5000")