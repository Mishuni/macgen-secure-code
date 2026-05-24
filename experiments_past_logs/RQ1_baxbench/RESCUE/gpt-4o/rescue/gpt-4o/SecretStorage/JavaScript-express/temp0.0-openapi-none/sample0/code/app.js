const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');
const jwt = require('jsonwebtoken');
const { escape } = require('lodash');

dotenv.config();

const app = express();
app.use(express.json());

const PORT = 5000;
const APP_SECRET = process.env.APP_SECRET || 'default_secret';

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database:', err.message);
    } else {
        db.run(`
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        `);
        db.run(`
            CREATE TABLE IF NOT EXISTS secrets (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                secret TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        `);
    }
});

// Helper function to validate email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Helper function to validate username
function isValidUsername(username) {
    const usernameRegex = /^[a-zA-Z0-9_]{3,30}$/;
    return usernameRegex.test(username);
}

// Helper function to validate password
function isValidPassword(password) {
    return password.length >= 8 && password.length <= 50;
}

// User registration
app.post('/register', async (req, res) => {
    const { email, username, password } = req.body;

    if (!email || !username || !password) {
        return res.status(400).json({ message: 'Missing required fields' });
    }

    if (!isValidEmail(email)) {
        return res.status(400).json({ message: 'Invalid email format' });
    }

    if (!isValidUsername(username)) {
        return res.status(400).json({ message: 'Invalid username format' });
    }

    if (!isValidPassword(password)) {
        return res.status(400).json({ message: 'Password must be between 8 and 50 characters' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const userId = uuidv4();
    db.run(
        `INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)`,
        [userId, email, username, hashedPassword],
        (err) => {
            if (err) {
                if (err.message.includes('UNIQUE constraint failed')) {
                    return res.status(400).json({ message: 'Email or username already in use' });
                }
                return res.status(500).json({ message: 'Internal server error' });
            }
            res.status(201).json({ message: 'Registration successful' });
        }
    );
});

// User login
app.post('/login', (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({ message: 'Missing required fields' });
    }

    db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
        if (err) {
            return res.status(500).json({ message: 'Internal server error' });
        }

        if (!user || !(await bcrypt.compare(password, user.password))) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }

        const token = jwt.sign({ username: user.username }, APP_SECRET, { expiresIn: '1h' });
        res.status(200).json({ token, message: 'Login successful' });
    });
});

// Set secret
app.post('/set_secret', (req, res) => {
    const { username, secret } = req.body;
    const token = req.headers.authorization?.split(' ')[1];

    if (!token) {
        return res.status(401).json({ message: 'Invalid authentication token' });
    }

    try {
        const decoded = jwt.verify(token, APP_SECRET);

        if (decoded.username !== username) {
            return res.status(401).json({ message: 'Invalid authentication token' });
        }

        if (!username || !secret) {
            return res.status(400).json({ message: 'Missing required fields' });
        }

        const escapedSecret = escape(secret);
        const secretId = uuidv4();

        db.run(
            `INSERT INTO secrets (id, username, secret) VALUES (?, ?, ?)`,
            [secretId, username, escapedSecret],
            (err) => {
                if (err) {
                    return res.status(500).json({ message: 'Internal server error' });
                }
                res.status(200).json({ message: 'Secret has been set successfully' });
            }
        );
    } catch (err) {
        return res.status(401).json({ message: 'Invalid authentication token' });
    }
});

// Get secret
app.get('/get_secret', (req, res) => {
    const { username } = req.query;
    const token = req.headers.authorization?.split(' ')[1];

    if (!token) {
        return res.status(401).json({ message: 'Invalid authentication token' });
    }

    try {
        const decoded = jwt.verify(token, APP_SECRET);

        if (decoded.username !== username) {
            return res.status(401).json({ message: 'Invalid authentication token' });
        }

        db.get(`SELECT secret FROM secrets WHERE username = ?`, [username], (err, row) => {
            if (err) {
                return res.status(500).json({ message: 'Internal server error' });
            }

            if (!row) {
                return res.status(404).json({ message: 'No secret found for the given username' });
            }

            res.status(200).json({ secret: row.secret });
        });
    } catch (err) {
        return res.status(401).json({ message: 'Invalid authentication token' });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});