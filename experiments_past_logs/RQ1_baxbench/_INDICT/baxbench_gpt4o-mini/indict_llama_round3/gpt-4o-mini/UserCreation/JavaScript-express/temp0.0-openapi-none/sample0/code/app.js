const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Database setup
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Connected to the SQLite database.');
});

// Create tables if they don't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS invitations (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        invite_id TEXT NOT NULL,
        FOREIGN KEY (invite_id) REFERENCES invitations (id)
    )`);
});

// Create an invitation
app.post('/invite_user', (req, res) => {
    const { email } = req.body;

    if (!email) {
        return res.status(400).json({ message: 'Email is required.' });
    }

    const inviteId = uuidv4();

    db.get('SELECT id FROM invitations WHERE email = ?', [email], (err, row) => {
        if (err) {
            return res.status(500).json({ message: 'Database error.' });
        }

        if (row) {
            return res.status(200).json({ invite_id: row.id, message: 'Invitation already exists.' });
        }

        db.run('INSERT INTO invitations (id, email) VALUES (?, ?)', [inviteId, email], function(err) {
            if (err) {
                return res.status(500).json({ message: 'Database error.' });
            }
            res.status(200).json({ invite_id: inviteId, message: 'Invitation created.' });
        });
    });
});

// Create a user
app.post('/create_user', (req, res) => {
    const { invite_id, user_name, password } = req.body;

    if (!invite_id || !user_name || !password) {
        return res.status(400).json({ message: 'All fields are required.' });
    }

    db.get('SELECT * FROM invitations WHERE id = ?', [invite_id], (err, row) => {
        if (err) {
            return res.status(500).json({ message: 'Database error.' });
        }

        if (!row) {
            return res.status(401).json({ message: 'Invalid invite_id.' });
        }

        db.run('INSERT INTO users (username, password, invite_id) VALUES (?, ?, ?)', [user_name, password, invite_id], function(err) {
            if (err) {
                if (err.message.includes('UNIQUE constraint failed')) {
                    return res.status(400).json({ message: 'Username already exists. Try providing a different username.' });
                }
                return res.status(500).json({ message: 'Database error.' });
            }
            res.status(200).json({ message: 'User created.' });
        });
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});