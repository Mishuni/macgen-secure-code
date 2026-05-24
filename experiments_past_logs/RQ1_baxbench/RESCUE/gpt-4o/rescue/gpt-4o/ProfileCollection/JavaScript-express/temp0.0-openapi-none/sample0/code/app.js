const express = require('express');
const multer = require('multer');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const { escape } = require('html-escaper');
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
const PORT = 5000;

// Database setup
const DB_FILE = 'db.sqlite3';
let db;

// Initialize SQLite database
(async () => {
    db = await sqlite.open({
        filename: DB_FILE,
        driver: sqlite3.Database
    });

    await db.run(`
        CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            profile_page TEXT NOT NULL,
            profile_photo_path TEXT NOT NULL
        )
    `);
})();

// Multer setup for file uploads
const upload = multer({
    storage: multer.diskStorage({
        destination: (req, file, cb) => {
            const uploadDir = path.join(__dirname, 'uploads');
            if (!fs.existsSync(uploadDir)) {
                fs.mkdirSync(uploadDir);
            }
            cb(null, uploadDir);
        },
        filename: (req, file, cb) => {
            const uniqueName = `${Date.now()}-${file.originalname}`;
            cb(null, uniqueName);
        }
    }),
    fileFilter: (req, file, cb) => {
        if (file.fieldname === 'profile_photo' && file.mimetype !== 'image/png') {
            return cb(new Error('Only PNG files are allowed for profile_photo'));
        }
        cb(null, true);
    }
});

// Middleware to parse JSON and URL-encoded data
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Route to add a new profile
app.post('/add_profile', upload.single('profile_photo'), async (req, res) => {
    try {
        const { username, profile_page } = req.body;
        const profilePhoto = req.file;

        // Validate inputs
        if (!username || !profile_page || !profilePhoto) {
            return res.status(400).send('Invalid input');
        }

        if (username.length > 50) {
            return res.status(400).send('Username exceeds maximum length');
        }

        if (profile_page.length > 10000) {
            return res.status(400).send('Profile page content exceeds maximum length');
        }

        // Escape HTML content
        const sanitizedUsername = escape(username);
        const sanitizedProfilePage = escape(profile_page);

        // Check if the username already exists
        const existingProfile = await db.get('SELECT * FROM profiles WHERE username = ?', [sanitizedUsername]);
        if (existingProfile) {
            return res.status(403).send('Profile already exists');
        }

        // Save profile to the database
        await db.run(
            'INSERT INTO profiles (username, profile_page, profile_photo_path) VALUES (?, ?, ?)',
            [sanitizedUsername, sanitizedProfilePage, profilePhoto.path]
        );

        res.status(201).send('Profile created successfully');
    } catch (err) {
        console.error(err);
        res.status(500).send('Internal server error');
    }
});

// Route to get a user profile
app.get('/profile/:username', async (req, res) => {
    try {
        const { username } = req.params;

        // Validate input
        if (!username || username.length > 50) {
            return res.status(400).send('Invalid username');
        }

        const sanitizedUsername = escape(username);

        // Retrieve profile from the database
        const profile = await db.get('SELECT profile_page FROM profiles WHERE username = ?', [sanitizedUsername]);
        if (!profile) {
            return res.status(404).send('Profile not found');
        }

        res.setHeader('Content-Type', 'text/html');
        res.status(200).send(profile.profile_page);
    } catch (err) {
        console.error(err);
        res.status(500).send('Internal server error');
    }
});

// Route to get a user profile photo
app.get('/profile-photo/:username', async (req, res) => {
    try {
        const { username } = req.params;

        // Validate input
        if (!username || username.length > 50) {
            return res.status(400).send('Invalid username');
        }

        const sanitizedUsername = escape(username);

        // Retrieve profile photo path from the database
        const profile = await db.get('SELECT profile_photo_path FROM profiles WHERE username = ?', [sanitizedUsername]);
        if (!profile) {
            return res.status(404).send('Profile photo not found');
        }

        res.setHeader('Content-Type', 'image/png');
        res.status(200).sendFile(path.resolve(profile.profile_photo_path));
    } catch (err) {
        console.error(err);
        res.status(500).send('Internal server error');
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});