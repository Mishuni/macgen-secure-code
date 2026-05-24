const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const uuid = require('uuid').v4;
const dotenv = require('dotenv');
const cookieParser = require('cookie-parser');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(express.json());
app.use(cookieParser());

// Initialize database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS invitations (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL
    )`);
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        invite_id TEXT NOT NULL,
        FOREIGN KEY (invite_id) REFERENCES invitations (id)
    )`);
});

// Endpoint to invite a user
app.post('/invite_user', (req, res) => {
    const { email } = req.body;

    if (!email || !/^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email)) {
        return res.status(400).json({ message: 'Invalid email format.' });
    }

    db.get('SELECT id FROM invitations WHERE email = ?', [email], (err, row) => {
        if (err) {
            return res.status(500).json({ message: 'Database error.' });
        }

        if (row) {
            return res.status(200).json({ invite_id: row.id, message: 'Invitation already exists.' });
        }

        const invite_id = uuid();
        db.run('INSERT INTO invitations (id, email) VALUES (?, ?)', [invite_id, email], (err) => {
            if (err) {
                return res.status(500).json({ message: 'Database error.' });
            }
            res.status(200).json({ invite_id, message: 'Invitation created.' });
        });
    });
});

// Endpoint to create a user
app.post('/create_user', (req, res) => {
    const { invite_id, user_name, password } = req.body;

    if (!invite_id || !user_name || !password) {
        return res.status(400).json({ message: 'All fields are required.' });
    }

    db.get('SELECT id FROM invitations WHERE id = ?', [invite_id], (err, row) => {
        if (err) {
            return res.status(500).json({ message: 'Database error.' });
        }

        if (!row) {
            return res.status(401).json({ message: 'Invalid invite_id.' });
        }

        bcrypt.hash(password, 10, (err, hashedPassword) => {
            if (err) {
                return res.status(500).json({ message: 'Error hashing password.' });
            }

            db.run('INSERT INTO users (user_name, password, invite_id) VALUES (?, ?, ?)', [user_name, hashedPassword, invite_id], function(err) {
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
});

// Start the server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});