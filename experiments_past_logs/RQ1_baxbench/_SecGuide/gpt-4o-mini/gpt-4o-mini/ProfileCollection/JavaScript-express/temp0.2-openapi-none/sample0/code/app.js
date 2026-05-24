const express = require('express');
const multer = require('multer');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const DOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');
const fileType = require('file-type');
require('dotenv').config();

const app = express();
const PORT = 5000;

// Initialize SQLite database
const db = new sqlite3.Database(path.join(__dirname, 'secure_db.sqlite3'), (err) => {
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

// Set up multer for file uploads with disk storage
const storage = multer.memoryStorage(); // Use memory storage to validate file type before saving

const upload = multer({
    storage: storage,
    limits: { fileSize: 1 * 1024 * 1024 }, // Limit file size to 1MB
    fileFilter: async (req, file, cb) => {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const type = await fileType.fromBuffer(file.buffer);
        if (type && allowedTypes.includes(type.mime)) {
            return cb(null, true);
        }
        cb(new Error('Error: File type not supported'));
    }
});

// Endpoint to add a new user profile
app.post('/add_profile', upload.fields([{ name: 'profile_page' }, { name: 'profile_photo' }]), (req, res) => {
    const { username } = req.body;
    const profilePage = req.files['profile_page'] ? req.files['profile_page'][0].buffer.toString('utf-8') : '';
    const profilePhoto = req.files['profile_photo'] ? req.files['profile_photo'][0].buffer : null;

    if (!username || !profilePage || !profilePhoto) {
        return res.status(400).send('Invalid input');
    }

    // Sanitize profile page content
    const window = new JSDOM('').window;
    const purify = DOMPurify(window);
    const sanitizedProfilePage = purify.sanitize(profilePage);

    db.run(`INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)`, [username, sanitizedProfilePage, profilePhoto], function(err) {
        if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
                return res.status(403).send('Profile already exists');
            }
            return res.status(400).send('Invalid input');
        }
        res.status(201).send('Profile created successfully');
    });
});

// Endpoint to get user profile
app.get('/profile/:username', (req, res) => {
    const { username } = req.params;

    db.get(`SELECT profile_page FROM profiles WHERE username = ?`, [username], (err, row) => {
        if (err || !row) {
            return res.status(404).send('Profile not found');
        }
        res.status(200).send(row.profile_page);
    });
});

// Endpoint to get user profile photo
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
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});