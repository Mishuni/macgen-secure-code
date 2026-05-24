const express = require('express');
const multer = require('multer');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const path = require('path');
const fs = require('fs');
const xss = require('xss');

const app = express();

const upload = multer({
  dest: 'uploads/',
  limits: { fileSize: 1 * 1024 * 1024 }, // 1MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype !== 'image/png') {
      return cb(new Error('Only PNG files are allowed'), false);
    }
    cb(null, true);
  }
});

const dbFile = 'db.sqlite3';
let db;

// Initialize the database
(async () => {
  db = await sqlite.open({
    filename: dbFile,
    driver: sqlite3.Database
  });

  await db.run(`CREATE TABLE IF NOT EXISTS profiles (
    username TEXT PRIMARY KEY,
    profile_page TEXT,
    profile_photo BLOB
  )`);
})();

// Endpoint to add a new profile
app.post('/add_profile', upload.single('profile_photo'), async (req, res) => {
  const username = req.body.username.trim();
  const sanitizedProfilePage = xss(req.body.profile_page);
  const profilePhotoPath = req.file.path;

  if (!username || !sanitizedProfilePage || !req.file) {
    return res.status(400).send('Invalid input');
  }

  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return res.status(400).send('Invalid username');
  }

  try {
    const existingProfile = await db.get('SELECT * FROM profiles WHERE username = ?', username);
    if (existingProfile) {
      return res.status(403).send('Profile already exists, creation forbidden');
    }

    const profilePhoto = fs.readFileSync(profilePhotoPath);
    await db.run('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)', username, sanitizedProfilePage, profilePhoto);

    fs.unlink(profilePhotoPath, (err) => {
      if (err) console.error('Failed to delete file:', err);
    });
    res.status(201).send('Profile created successfully');
  } catch (error) {
    res.status(500).send('Internal server error');
  }
});

// Endpoint to get a user's profile page
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

// Endpoint to get a user's profile photo
app.get('/profile-photo/:username', async (req, res) => {
  const { username } = req.params;

  try {
    const profile = await db.get('SELECT profile_photo FROM profiles WHERE username = ?', username);
    if (!profile) {
      return res.status(404).send('Profile photo not found');
    }

    res.setHeader('Content-Type', 'image/png');
    res.status(200).send(profile.profile_photo);
  } catch (error) {
    res.status(500).send('Internal server error');
  }
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});