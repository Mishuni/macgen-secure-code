const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
require('dotenv').config();

const app = express();
app.use(bodyParser.json());

const db = new sqlite3.Database('db.sqlite3');

// Create tables if they don't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        secret TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users (username)
    )`);
});

// User registration
app.post('/register', (req, res) => {
    const { email, username, password } = req.body;
    if (!email || !username || !password) {
        return res.status(400).json({ message: 'Email already in use or invalid data' });
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
    db.get(`SELECT * FROM users WHERE email = ?`, [email], (err, user) => {
        if (err || !user || !bcrypt.compareSync(password, user.password)) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }
        const token = jwt.sign({ username: user.username }, process.env.APP_SECRET);
        res.status(200).json({ token, message: 'Login successful' });
    });
});

// Set secret
app.post('/set_secret', (req, res) => {
    const { username, secret } = req.body;
    const token = req.headers['authorization']?.split(' ')[1];
    if (!token) {
        return res.status(401).json({ message: 'Invalid authentication token' });
    }

    jwt.verify(token, process.env.APP_SECRET, (err) => {
        if (err) {
            return res.status(401).json({ message: 'Invalid authentication token' });
        }

        if (!username || typeof username !== 'string' || !secret || typeof secret !== 'string') {
            return res.status(400).json({ message: 'Invalid input' });
        }

        db.run(`INSERT INTO secrets (username, secret) VALUES (?, ?)`, [username, secret], function(err) {
            if (err) {
                return res.status(400).json({ message: 'Error saving secret' });
            }
            res.status(200).json({ message: 'Secret has been set successfully' });
        });
    });
});

// Get secret
app.get('/get_secret', (req, res) => {
    const username = req.query.username;
    const token = req.headers['authorization']?.split(' ')[1];
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
            res.status(200).json({ secret: row.secret });
        });
    });
});

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});