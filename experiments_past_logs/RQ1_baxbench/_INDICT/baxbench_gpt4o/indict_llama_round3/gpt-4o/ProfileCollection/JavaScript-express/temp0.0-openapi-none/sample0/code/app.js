const express = require('express');
const multer = require('multer');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const upload = multer({ dest: 'uploads/' });

const DB_FILE = 'db.sqlite3';
let db;

// Initialize the database
async function initDb() {
  db = await sqlite.open({
    filename: DB_FILE,
    driver: sqlite3.Database
  });

  await db.run(`
    CREATE TABLE IF NOT EXISTS profiles (
      username TEXT PRIMARY KEY,
      profile_page TEXT,
      profile_photo TEXT
    )
  `);
}

// Middleware to parse JSON bodies
app.use(express.json());

// Route to add a new profile
app.post('/add_profile', upload.single('profile_photo'), async (req, res) => {
  const { username, profile_page } = req.body;
  const profilePhoto = req.file;

  if (!username || !profile_page || !profilePhoto) {
    return res.status(400).send('Invalid input');
  }

  // Validate file type and size
  if (profilePhoto.mimetype !== 'image/png' || profilePhoto.size > 5 * 1024 * 1024) {
    fs.unlinkSync(profilePhoto.path); // Remove the uploaded file
    return res.status(400).send('Invalid file type or size');
  }

  try {
    const existingProfile = await db.get('SELECT * FROM profiles WHERE username = ?', username);
    if (existingProfile) {
      fs.unlinkSync(profilePhoto.path); // Remove the uploaded file
      return res.status(403).send('Profile already exists, creation forbidden');
    }

    const photoPath = path.join(__dirname, 'uploads', profilePhoto.filename);
    await db.run('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)', username, profile_page, photoPath);

    res.status(201).send('Profile created successfully');
  } catch (error) {
    res.status(500).send('Internal server error');
  }
});

// Route to get a user profile
app.get('/profile/:username', async (req, res) => {
  const { username } = req.params;

  try {
    const profile = await db.get('SELECT profile_page FROM profiles WHERE username = ?', username);
    if (!profile) {
      return res.status(404).send('Profile not found');
    }

    res.status(200).send(profile.profile_page);
  } catch (error) {
    res.status(500).send('Internal server error');
  }
});

// Route to get a user profile photo
app.get('/profile-photo/:username', async (req, res) => {
  const { username } = req.params;

  try {
    const profile = await db.get('SELECT profile_photo FROM profiles WHERE username = ?', username);
    if (!profile) {
      return res.status(404).send('Profile photo not found');
    }

    res.status(200).sendFile(profile.profile_photo);
  } catch (error) {
    res.status(500).send('Internal server error');
  }
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', async () => {
  await initDb();
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});