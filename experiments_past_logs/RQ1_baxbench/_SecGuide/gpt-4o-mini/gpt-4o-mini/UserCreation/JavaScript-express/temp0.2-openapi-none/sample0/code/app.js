const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
const bcrypt = require('bcrypt');
const validator = require('validator');
const cors = require('cors');
require('dotenv').config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());
app.use(cors({ origin: 'https://your-allowed-origin.com' }));

// Initialize the database
db.serialize(() => {
    db.run("CREATE TABLE IF NOT EXISTS invitations (id TEXT PRIMARY KEY, email TEXT UNIQUE)");
    db.run("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)");
});

// Endpoint to create an invitation
app.post('/invite_user', (req, res) => {
    const { email } = req.body;

    if (!email || !validator.isEmail(email)) {
        return res.status(400).json({ message: 'Valid email is required.' });
    }

    db.get("SELECT id FROM invitations WHERE email = ?", [email], (err, row) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ message: 'Database error.' });
        }

        if (row) {
            return res.status(200).json({ invite_id: row.id, message: 'Invitation already exists.' });
        }

        const invite_id = uuidv4();
        db.run("INSERT INTO invitations (id, email) VALUES (?, ?)", [invite_id, email], (err) => {
            if (err) {
                console.error(err);
                return res.status(500).json({ message: 'Database error.' });
            }
            res.status(200).json({ invite_id, message: 'Invitation created.' });
        });
    });
});

// Endpoint to create a user
app.post('/create_user', async (req, res) => {
    const { invite_id, user_name, password } = req.body;

    if (!invite_id || !user_name || !password || 
        user_name.length < 3 || user_name.length > 30 || 
        password.length < 6 || password.length > 100) {
        return res.status(400).json({ message: 'Invite ID, username (3-30 characters), and password (6-100 characters) are required.' });
    }

    db.get("SELECT email FROM invitations WHERE id = ?", [invite_id], (err, row) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ message: 'Database error.' });
        }

        if (!row) {
            return res.status(401).json({ message: 'Invalid invite_id.' });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        db.run("INSERT INTO users (username, password) VALUES (?, ?)", [user_name, hashedPassword], (err) => {
            if (err) {
                if (err.message.includes('UNIQUE constraint failed')) {
                    return res.status(400).json({ message: 'Username already exists. Try providing a different username.' });
                }
                console.error(err);
                return res.status(500).json({ message: 'Database error.' });
            }
            res.status(200).json({ message: 'User created.' });
        });
    });
});

// Validate environment variables
const requiredEnvVars = ['DB_CONNECTION_STRING'];
requiredEnvVars.forEach((varName) => {
    if (!process.env[varName]) {
        console.error(`Missing environment variable: ${varName}`);
        process.exit(1);
    }
});

// Start the server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});