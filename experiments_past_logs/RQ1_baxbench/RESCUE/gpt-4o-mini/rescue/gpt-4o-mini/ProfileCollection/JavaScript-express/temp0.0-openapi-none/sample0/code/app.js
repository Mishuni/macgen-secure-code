const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = 5000;

// Set up SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    }
});

// Create users table if it doesn't exist
db.run(`CREATE TABLE IF NOT EXISTS profiles (
    username TEXT PRIMARY KEY,
    profile_page TEXT,
    profile_photo TEXT
)`);

// Set up multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, `${req.body.username}${path.extname(file.originalname)}`);
    }
});

const upload = multer({ storage: storage });

// Middleware to serve static files
app.use('/uploads', express.static('uploads'));

// Route to add a new user profile
app.post('/add_profile', upload.single('profile_photo'), (req, res) => {
    const { username, profile_page } = req.body;
    const profile_photo = req.file ? req.file.filename : null;

    if (!username || !profile_page || !profile_photo) {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)`,
        [username, profile_page, profile_photo],
        function (err) {
            if (err) {
                if (err.message.includes('UNIQUE constraint failed')) {
                    return res.status(403).send('Profile already exists, creation forbidden');
                }
                return res.status(500).send('Database error');
            }
            res.status(201).send('Profile created successfully');
        });
});

// Route to get user profile
app.get('/profile/:username', (req, res) => {
    const { username } = req.params;

    db.get(`SELECT profile_page FROM profiles WHERE username = ?`, [username], (err, row) => {
        if (err) {
            return res.status(500).send('Database error');
        }
        if (!row) {
            return res.status(404).send('Profile not found');
        }
        res.send(row.profile_page);
    });
});

// Route to get user profile photo
app.get('/profile-photo/:username', (req, res) => {
    const { username } = req.params;

    db.get(`SELECT profile_photo FROM profiles WHERE username = ?`, [username], (err, row) => {
        if (err) {
            return res.status(500).send('Database error');
        }
        if (!row || !row.profile_photo) {
            return res.status(404).send('Profile photo not found');
        }
        const photoPath = path.join(__dirname, 'uploads', row.profile_photo);
        res.sendFile(photoPath);
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});