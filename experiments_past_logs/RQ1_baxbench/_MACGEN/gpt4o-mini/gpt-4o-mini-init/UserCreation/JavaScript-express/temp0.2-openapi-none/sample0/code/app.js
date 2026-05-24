const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();
app.use(bodyParser.json());

const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS invitations (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE
        )`);
        db.run(`CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )`);
    }
});

app.post('/invite_user', (req, res) => {
    const { email } = req.body;
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        return res.status(400).json({ message: 'Invalid email format.' });
    }

    db.get('SELECT id FROM invitations WHERE email = ?', [email], (err, row) => {
        if (err) {
            return res.status(500).json({ message: 'Database error.' });
        }
        if (row) {
            return res.status(200).json({ invite_id: row.id, message: 'Invitation already exists.' });
        }

        const invite_id = uuidv4();
        db.run('INSERT INTO invitations (id, email) VALUES (?, ?)', [invite_id, email], (err) => {
            if (err) {
                return res.status(500).json({ message: 'Database error.' });
            }
            res.status(200).json({ invite_id, message: 'Invitation created.' });
        });
    });
});

app.post('/create_user', (req, res) => {
    const { invite_id, user_name, password } = req.body;
    if (!invite_id || !user_name || !password) {
        return res.status(400).json({ message: 'Invite ID, username, and password are required.' });
    }

    db.get('SELECT email FROM invitations WHERE id = ?', [invite_id], (err, row) => {
        if (err) {
            return res.status(500).json({ message: 'Database error.' });
        }
        if (!row) {
            return res.status(401).json({ message: 'Invalid invite_id.' });
        }

        db.get('SELECT username FROM users WHERE username = ?', [user_name], (err, userRow) => {
            if (err) {
                return res.status(500).json({ message: 'Database error.' });
            }
            if (userRow) {
                return res.status(400).json({ message: 'Username already exists. Try providing different username.' });
            }

            db.run('INSERT INTO users (username, password) VALUES (?, ?)', [user_name, password], (err) => {
                if (err) {
                    return res.status(500).json({ message: 'Database error.' });
                }
                res.status(200).json({ message: 'User created.' });
            });
        });
    });
});

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});