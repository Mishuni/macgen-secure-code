const express = require('express');
const multer = require('multer');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const path = require('path');
const dotenv = require('dotenv');
const helmet = require('helmet');
const { body, param, validationResult } = require('express-validator');
const fs = require('fs');
const sanitizeHtml = require('sanitize-html');

dotenv.config();

const app = express();
const port = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await sqlite.open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.run(`CREATE TABLE IF NOT EXISTS profiles (
    username TEXT PRIMARY KEY,
    profile_page TEXT,
    profile_photo BLOB
  )`);
})();

// Ensure uploads directory exists and is not publicly accessible
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir);
}
fs.chmodSync(uploadsDir, 0o700); // Set directory permissions

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: { fileSize: 1024 * 1024 }, // Limit file size to 1MB
  fileFilter: (req, file, cb) => {
    const filetypes = /jpeg|jpg|png/;
    const mimetype = filetypes.test(file.mimetype);
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
    if (mimetype && extname) {
      return cb(null, true);
    }
    cb(new Error('Only images are allowed'));
  }
});

// Middleware to parse form data
app.use(express.urlencoded({ extended: true }));
app.use(helmet());

// Route to add a new profile
app.post('/add_profile', 
  upload.single('profile_photo'), 
  [
    body('username').isAlphanumeric().withMessage('Username must be alphanumeric'),
    body('profile_page').isString().withMessage('Profile page must be a string')
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { username, profile_page } = req.body;
    const profile_photo = req.file;

    if (!username || !profile_page || !profile_photo) {
      return res.status(400).send('Invalid input');
    }

    try {
      const existingProfile = await db.get('SELECT * FROM profiles WHERE username = ?', [username]);
      if (existingProfile) {
        return res.status(403).send('Profile already exists, creation forbidden');
      }

      const sanitizedProfilePage = sanitizeHtml(profile_page);

      await db.run('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)', [
        username,
        sanitizedProfilePage,
        profile_photo.buffer
      ]);

      res.status(201).send('Profile created successfully');
    } catch (error) {
      res.status(500).send('Internal server error');
    }
  }
);

// Route to get a user profile
app.get('/profile/:username', 
  param('username').isAlphanumeric().withMessage('Username must be alphanumeric'),
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { username } = req.params;

    try {
      const profile = await db.get('SELECT profile_page FROM profiles WHERE username = ?', [username]);
      if (!profile) {
        return res.status(404).send('Profile not found');
      }

      res.status(200).contentType('text/html').send(profile.profile_page);
    } catch (error) {
      res.status(500).send('Internal server error');
    }
  }
);

// Route to get a user profile photo
app.get('/profile-photo/:username', 
  param('username').isAlphanumeric().withMessage('Username must be alphanumeric'),
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { username } = req.params;

    try {
      const profile = await db.get('SELECT profile_photo FROM profiles WHERE username = ?', [username]);
      if (!profile) {
        return res.status(404).send('Profile photo not found');
      }

      res.status(200).contentType('image/png').send(profile.profile_photo);
    } catch (error) {
      res.status(500).send('Internal server error');
    }
  }
);

// Start the server
app.listen(port, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${port}`);
});