const express = require('express');
const multer = require('multer');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const app = express();
const PORT = 5000;

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            profile_page TEXT,
            profile_photo BLOB
        )`, (err) => {
            if (err) {
                console.error(err.message);
            }
        });
    }
});

// Set up multer for file uploads with file type validation
const storage = multer.memoryStorage();
const upload = multer({
    storage: storage,
    fileFilter: (req, file, cb) => {
        if (file.mimetype === 'text/html' || file.mimetype === 'image/png') {
            cb(null, true);
        } else {
            cb(new Error('Invalid file type. Only HTML and PNG files are allowed.'), false);
        }
    },
    limits: { fileSize: 5 * 1024 * 1024 } // Limit file size to 5MB
});

// Add a new user profile
app.post('/add_profile', upload.fields([{ name: 'profile_page' }, { name: 'profile_photo' }]), (req, res) => {
    const { username } = req.body;
    const profilePage = req.files['profile_page'] ? req.files['profile_page'][0].buffer.toString('utf-8') : null;
    const profilePhoto = req.files['profile_photo'] ? req.files['profile_photo'][0].buffer : null;

    if (!username || !profilePage || !profilePhoto) {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)`, [username, profilePage, profilePhoto], function(err) {
        if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
                return res.status(403).send('Profile already exists, creation forbidden');
            }
            return res.status(400).send('Invalid input');
        }
        res.status(201).send('Profile created successfully');
    });
});

// Get user profile
app.get('/profile/:username', (req, res) => {
    const { username } = req.params;

    db.get(`SELECT profile_page FROM profiles WHERE username = ?`, [username], (err, row) => {
        if (err || !row) {
            return res.status(404).send('Profile not found');
        }
        res.status(200).send(row.profile_page);
    });
});

// Get user profile photo
app.get('/profile-photo/:username', (req, res) => {
    const { username } = req.params;

    db.get(`SELECT profile_photo FROM profiles WHERE username = ?`, [username], (err, row) => {
        if (err || !row) {
            return res.status(404).send('Profile photo not found');
        }
        res.set('Content-Type', 'image/png');
        res.status(200).send(row.profile_photo);
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});