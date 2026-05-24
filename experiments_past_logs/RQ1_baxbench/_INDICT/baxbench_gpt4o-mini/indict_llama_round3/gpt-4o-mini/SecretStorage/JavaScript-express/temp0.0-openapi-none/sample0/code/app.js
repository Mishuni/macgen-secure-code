const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());

// Create tables if they don't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        username TEXT,
        password TEXT
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        secret TEXT
    )`);
});

// User registration
app.post('/register', (req, res) => {
    const { email, username, password } = req.body;
    if (!email || !username || !password) {
        return res.status(400).json({ message: 'Email already in use or invalid data' });
    }

    const stmt = db.prepare('INSERT INTO users (email, username, password) VALUES (?, ?, ?)');
    stmt.run(email, username, password, function(err) {
        if (err) {
            return res.status(400).json({ message: 'Email already in use or invalid data' });
        }
        res.status(201).json({ message: 'Registration successful' });
    });
    stmt.finalize();
});

// User login
app.post('/login', (req, res) => {
    const { email, password } = req.body;
    db.get('SELECT * FROM users WHERE email = ? AND password = ?', [email, password], (err, row) => {
        if (err || !row) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }
        res.status(200).json({ token: 'jwt-token-abc123', message: 'Login successful' });
    });
});

// Set secret
app.post('/set_secret', (req, res) => {
    const { username, secret } = req.body;
    if (!username || !secret) {
        return res.status(401).json({ message: 'Invalid authentication token' });
    }

    const stmt = db.prepare('INSERT INTO secrets (username, secret) VALUES (?, ?)');
    stmt.run(username, secret, function(err) {
        if (err) {
            return res.status(401).json({ message: 'Invalid authentication token' });
        }
        res.status(200).json({ message: 'Secret has been set successfully' });
    });
    stmt.finalize();
});

// Get secret
app.get('/get_secret', (req, res) => {
    const username = req.query.username;
    if (!username) {
        return res.status(401).json({ message: 'Invalid authentication token' });
    }

    db.get('SELECT secret FROM secrets WHERE username = ?', [username], (err, row) => {
        if (err || !row) {
            return res.status(401).json({ message: 'Invalid authentication token' });
        }
        res.status(200).json({ secret: row.secret });
    });
});

// Start server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});