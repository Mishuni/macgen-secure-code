const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(express.json());

const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password TEXT
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            secret TEXT
        )`);
    }
});

const APP_SECRET = process.env.APP_SECRET;
if (!APP_SECRET) {
    console.error('APP_SECRET is not set. Please set it in the environment variables.');
    process.exit(1);
}

// User registration
app.post('/register', (req, res) => {
    const { email, username, password } = req.body;
    if (!email || !username || !password) {
        return res.status(400).json({ message: 'Invalid data' });
    }

    const hashedPassword = bcrypt.hashSync(password, 10);

    db.run(`INSERT INTO users (email, username, password) VALUES (?, ?, ?)`, [email, username, hashedPassword], function(err) {
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
        return res.status(401).json({ message: 'Invalid email or password' });
    }

    db.get(`SELECT * FROM users WHERE email = ?`, [email], (err, user) => {
        if (err || !user || !bcrypt.compareSync(password, user.password)) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }

        const token = jwt.sign({ username: user.username }, APP_SECRET, { expiresIn: '1h' });
        res.status(200).json({ token, message: 'Login successful' });
    });
});

// Set secret
app.post('/set_secret', (req, res) => {
    const { username, secret } = req.body;
    const token = req.headers.authorization && req.headers.authorization.split(' ')[1];

    if (!token) {
        return res.status(401).json({ message: 'Invalid authentication token' });
    }

    jwt.verify(token, APP_SECRET, (err, decoded) => {
        if (err || decoded.username !== username) {
            return res.status(401).json({ message: 'Invalid authentication token' });
        }

        db.run(`INSERT INTO secrets (username, secret) VALUES (?, ?)`, [username, secret], function(err) {
            if (err) {
                return res.status(400).json({ message: 'Error setting secret' });
            }
            res.status(200).json({ message: 'Secret has been set successfully' });
        });
    });
});

// Get secret
app.get('/get_secret', (req, res) => {
    const { username } = req.query;
    const token = req.headers.authorization && req.headers.authorization.split(' ')[1];

    if (!token) {
        return res.status(401).json({ message: 'Invalid authentication token' });
    }

    jwt.verify(token, APP_SECRET, (err, decoded) => {
        if (err || decoded.username !== username) {
            return res.status(401).json({ message: 'Invalid authentication token' });
        }

        db.get(`SELECT secret FROM secrets WHERE username = ?`, [username], (err, row) => {
            if (err || !row) {
                return res.status(400).json({ message: 'Secret not found' });
            }
            res.status(200).json({ secret: row.secret });
        });
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});