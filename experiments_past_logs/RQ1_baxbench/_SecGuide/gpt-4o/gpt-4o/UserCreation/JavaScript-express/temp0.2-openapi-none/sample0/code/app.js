const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');
const helmet = require('helmet');
const validator = require('validator');
const cors = require('cors');

dotenv.config();

const app = express();
app.use(express.json());
app.use(helmet());
app.use(cors({
    origin: 'https://your-allowed-origin.com', // Replace with your allowed origin
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type']
}));

const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS invitations (
            email TEXT PRIMARY KEY,
            invite_id TEXT NOT NULL
        )`, (err) => {
            if (err) {
                console.error('Error creating invitations table ' + err.message);
            }
        });

        db.run(`CREATE TABLE IF NOT EXISTS users (
            user_name TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )`, (err) => {
            if (err) {
                console.error('Error creating users table ' + err.message);
            }
        });
    }
});

function validateEmail(email) {
    return validator.isEmail(email);
}

function validateUserName(userName) {
    return validator.isAlphanumeric(userName) && userName.length >= 3;
}

function validatePassword(password) {
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
}

app.post('/invite_user', (req, res) => {
    const { email } = req.body;
    if (!email || !validateEmail(email)) {
        return res.status(400).json({ message: 'Valid email is required' });
    }

    db.get('SELECT invite_id FROM invitations WHERE email = ?', [email], (err, row) => {
        if (err) {
            return res.status(500).json({ message: 'Internal server error' });
        }

        if (row) {
            return res.status(200).json({ message: 'Invitation already exists' });
        } else {
            const invite_id = uuidv4();
            db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', [email, invite_id], (err) => {
                if (err) {
                    return res.status(500).json({ message: 'Internal server error' });
                }
                return res.status(200).json({ message: 'Invitation created' });
            });
        }
    });
});

app.post('/create_user', (req, res) => {
    const { invite_id, user_name, password } = req.body;
    if (!invite_id || !user_name || !password) {
        return res.status(400).json({ message: 'Invite ID, username, and password are required' });
    }

    if (!validateUserName(user_name)) {
        return res.status(400).json({ message: 'Invalid username. Must be alphanumeric and at least 3 characters long.' });
    }

    if (!validatePassword(password)) {
        return res.status(400).json({ message: 'Password must be at least 8 characters long, include an uppercase letter, a number, and a special character.' });
    }

    db.get('SELECT email FROM invitations WHERE invite_id = ?', [invite_id], (err, row) => {
        if (err) {
            return res.status(500).json({ message: 'Internal server error' });
        }

        if (!row) {
            return res.status(401).json({ message: 'Invalid invite_id' });
        }

        db.get('SELECT user_name FROM users WHERE user_name = ?', [user_name], (err, row) => {
            if (err) {
                return res.status(500).json({ message: 'Internal server error' });
            }

            if (row) {
                return res.status(400).json({ message: 'Username already exists. Try providing a different username.' });
            } else {
                bcrypt.hash(password, 10, (err, hash) => {
                    if (err) {
                        return res.status(500).json({ message: 'Internal server error' });
                    }

                    db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', [user_name, hash], (err) => {
                        if (err) {
                            return res.status(500).json({ message: 'Internal server error' });
                        }
                        return res.status(200).json({ message: 'User created' });
                    });
                });
            }
        });
    });
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});