const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());

// Create tables if they don't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS USERS (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        EMAIL TEXT UNIQUE NOT NULL,
        USERNAME TEXT UNIQUE NOT NULL,
        PASSWORD TEXT NOT NULL
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS SECRETS (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        USERNAME TEXT NOT NULL,
        SECRET TEXT NOT NULL,
        FOREIGN KEY (USERNAME) REFERENCES USERS (USERNAME)
    )`);
});

// User registration
app.post('/register', (req, res) => {
    const { email, username, password } = req.body;
    const hashedPassword = bcrypt.hashSync(password, 10);

    const query = `INSERT INTO USERS (EMAIL, USERNAME, PASSWORD) VALUES (?, ?, ?)`;
    db.run(query, [email, username, hashedPassword], function(err) {
        if (err) {
            return res.status(400).json({ message: 'Email already in use or invalid data' });
        }
        res.status(201).json({ message: 'Registration successful' });
    });
});

// User login
app.post('/login', (req, res) => {
    const { email, password } = req.body;

    const query = `SELECT * FROM USERS WHERE EMAIL = ?`;
    db.get(query, [email], (err, user) => {
        if (err || !user || !bcrypt.compareSync(password, user.PASSWORD)) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }
        const token = jwt.sign({ username: user.USERNAME }, process.env.APP_SECRET);
        res.status(200).json({ token, message: 'Login successful' });
    });
});

// Set secret
app.post('/set_secret', (req, res) => {
    const { username, secret } = req.body;

    const query = `INSERT INTO SECRETS (USERNAME, SECRET) VALUES (?, ?)`;
    db.run(query, [username, secret], function(err) {
        if (err) {
            return res.status(401).json({ message: 'Invalid authentication token' });
        }
        res.status(200).json({ message: 'Secret has been set successfully' });
    });
});

// Get secret
app.get('/get_secret', (req, res) => {
    const username = req.query.username;

    const query = `SELECT SECRET FROM SECRETS WHERE USERNAME = ?`;
    db.get(query, [username], (err, row) => {
        if (err || !row) {
            return res.status(401).json({ message: 'Invalid authentication token' });
        }
        res.status(200).json({ secret: row.SECRET });
    });
});

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});