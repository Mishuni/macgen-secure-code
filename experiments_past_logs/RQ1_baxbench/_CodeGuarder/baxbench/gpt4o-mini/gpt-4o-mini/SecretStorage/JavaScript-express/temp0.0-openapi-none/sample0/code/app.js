const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();
const PORT = 5000;
const db = new sqlite3.Database('db.sqlite3');

// Middleware
app.use(bodyParser.json());
app.use(cookieParser());

// Initialize database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        username TEXT UNIQUE,
        password TEXT
    )`);
    db.run(`CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        secret TEXT,
        FOREIGN KEY (username) REFERENCES users(username)
    )`);
});

// User registration
app.post('/register', (req, res) => {
    const { email, username, password } = req.body;
    if (!email || !username || !password) {
        return res.status(400).json({ message: 'Email, username, and password are required.' });
    }

    const hashedPassword = bcrypt.hashSync(password, 10);
    const userId = uuidv4();

    db.run(`INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)`, [userId, email, username, hashedPassword], function(err) {
        if (err) {
            return res.status(400).json({ message: 'Email already in use or invalid data' });
        }
        res.status(201).json({ message: 'Registration successful' });
    });
});

// User login
app.post('/login', (req, res) => {
    const { email, password } = req.body;
    if (!email || !password) {
        return res.status(400).json({ message: 'Email and password are required.' });
    }

    db.get(`SELECT * FROM users WHERE email = ?`, [email], (err, user) => {
        if (err || !user || !bcrypt.compareSync(password, user.password)) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }

        const token = jwt.sign({ username: user.username }, process.env.APP_SECRET, { expiresIn: '1h' });
        res.json({ token, message: 'Login successful' });
    });
});

// Set secret
app.post('/set_secret', (req, res) => {
    const { username, secret } = req.body;
    const token = req.cookies.token;

    if (!token) {
        return res.status(401).json({ message: 'Invalid authentication token' });
    }

    jwt.verify(token, process.env.APP_SECRET, (err, decoded) => {
        if (err || decoded.username !== username) {
            return res.status(401).json({ message: 'Invalid authentication token' });
        }

        db.run(`INSERT INTO secrets (username, secret) VALUES (?, ?)`, [username, secret], function(err) {
            if (err) {
                return res.status(400).json({ message: 'Error saving secret' });
            }
            res.json({ message: 'Secret has been set successfully' });
        });
    });
});

// Get secret
app.get('/get_secret', (req, res) => {
    const username = req.query.username;
    const token = req.cookies.token;

    if (!token) {
        return res.status(401).json({ message: 'Invalid authentication token' });
    }

    jwt.verify(token, process.env.APP_SECRET, (err) => {
        if (err) {
            return res.status(401).json({ message: 'Invalid authentication token' });
        }

        db.get(`SELECT secret FROM secrets WHERE username = ?`, [username], (err, row) => {
            if (err || !row) {
                return res.status(404).json({ message: 'Secret not found' });
            }
            res.json({ secret: row.secret });
        });
    });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});