const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());

// Initialize the database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS invitations (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )`);
});

// Endpoint to invite a user
app.post('/invite_user', (req, res) => {
    const { email } = req.body;

    if (!email) {
        return res.status(400).json({ message: 'Email is required' });
    }

    const inviteId = uuidv4();

    db.serialize(() => {
        db.run(`INSERT INTO invitations (id, email) VALUES (?, ?)`, [inviteId, email], function(err) {
            if (err) {
                if (err.code === 'SQLITE_CONSTRAINT') {
                    // If the email already exists, retrieve the existing invite_id
                    db.get(`SELECT id FROM invitations WHERE email = ?`, [email], (err, row) => {
                        if (err) {
                            return res.status(500).json({ message: 'Database error' });
                        }
                        return res.json({ invite_id: row.id, message: 'Invitation already exists' });
                    });
                } else {
                    return res.status(500).json({ message: 'Database error' });
                }
            } else {
                return res.json({ invite_id: inviteId, message: 'Invitation created' });
            }
        });
    });
});

// Endpoint to create a user
app.post('/create_user', (req, res) => {
    const { invite_id, user_name, password } = req.body;

    if (!invite_id || !user_name || !password) {
        return res.status(400).json({ message: 'Invite ID, username, and password are required' });
    }

    db.get(`SELECT email FROM invitations WHERE id = ?`, [invite_id], (err, row) => {
        if (err || !row) {
            return res.status(401).json({ message: 'Invalid invite_id' });
        }

        db.run(`INSERT INTO users (user_name, password) VALUES (?, ?)`, [user_name, password], function(err) {
            if (err) {
                if (err.code === 'SQLITE_CONSTRAINT') {
                    return res.status(400).json({ message: 'Username already exists. Try providing a different username.' });
                }
                return res.status(500).json({ message: 'Database error' });
            }
            return res.json({ message: 'User created' });
        });
    });
});

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});