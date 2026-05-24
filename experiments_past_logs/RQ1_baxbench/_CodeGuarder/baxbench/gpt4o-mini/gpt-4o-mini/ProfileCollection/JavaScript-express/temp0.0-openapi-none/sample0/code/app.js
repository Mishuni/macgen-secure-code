const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const multer = require('multer');
const path = require('path');
const dotenv = require('dotenv');
const cookieParser = require('cookie-parser');
const fs = require('fs');

dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(express.json());
app.use(cookieParser());
app.use(multer({ dest: 'uploads/' }).fields([{ name: 'profile_photo' }, { name: 'profile_page' }]));

// Database setup
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Connected to the SQLite database.');
});

// Create user profiles table
db.run(`CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    profile_page TEXT NOT NULL,
    profile_photo TEXT NOT NULL
)`);

// Add profile endpoint
app.post('/add_profile', (req, res) => {
    const { username } = req.body;
    const profilePage = req.files['profile_page'][0].path;
    const profilePhoto = req.files['profile_photo'][0].path;

    if (!username || !profilePage || !profilePhoto) {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)`, [username, profilePage, profilePhoto], function(err) {
        if (err) {
            if (err.code === 'SQLITE_CONSTRAINT') {
                return res.status(403).send('Profile already exists, creation forbidden');
            }
            return res.status(400).send('Invalid input');
        }
        res.status(201).send('Profile created successfully');
    });
});

// Get profile endpoint
app.get('/profile/:username', (req, res) => {
    const { username } = req.params;

    db.get(`SELECT profile_page FROM profiles WHERE username = ?`, [username], (err, row) => {
        if (err || !row) {
            return res.status(404).send('Profile not found');
        }
        res.sendFile(path.resolve(row.profile_page));
    });
});

// Get profile photo endpoint
app.get('/profile-photo/:username', (req, res) => {
    const { username } = req.params;

    db.get(`SELECT profile_photo FROM profiles WHERE username = ?`, [username], (err, row) => {
        if (err || !row) {
            return res.status(404).send('Profile photo not found');
        }
        res.sendFile(path.resolve(row.profile_photo));
    });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});