const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');
const bcrypt = require('bcrypt');

dotenv.config();

const app = express();
app.use(express.json());

// Database setup
let db;
(async () => {
    db = await open({
        filename: './db.sqlite3',
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS invitations (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            invite_id TEXT NOT NULL,
            FOREIGN KEY (invite_id) REFERENCES invitations (id)
        );
    `);
})();

// Helper function to validate email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Route to create an invitation
app.post('/invite_user', async (req, res) => {
    const { email } = req.body;

    if (!email || !isValidEmail(email)) {
        return res.status(400).json({ message: 'Invalid email format' });
    }

    try {
        // Check if an invitation already exists for the email
        const existingInvite = await db.get('SELECT id FROM invitations WHERE email = ?', [email]);

        if (existingInvite) {
            return res.status(200).json({
                invite_id: existingInvite.id,
                message: 'Invitation already exists for this email'
            });
        }

        // Create a new invitation
        const inviteId = uuidv4();
        await db.run('INSERT INTO invitations (id, email) VALUES (?, ?)', [inviteId, email]);

        return res.status(200).json({
            invite_id: inviteId,
            message: 'Invitation created successfully'
        });
    } catch (error) {
        console.error('Error creating invitation:', error);
        return res.status(500).json({ message: 'Internal server error' });
    }
});

// Route to create a user
app.post('/create_user', async (req, res) => {
    const { invite_id, user_name, password } = req.body;

    if (!invite_id || !user_name || !password) {
        return res.status(400).json({ message: 'Missing required fields' });
    }

    try {
        // Check if the invitation exists
        const invitation = await db.get('SELECT id FROM invitations WHERE id = ?', [invite_id]);

        if (!invitation) {
            return res.status(401).json({ message: 'Invalid invite_id' });
        }

        // Check if the username already exists
        const existingUser = await db.get('SELECT id FROM users WHERE username = ?', [user_name]);

        if (existingUser) {
            return res.status(400).json({ message: 'Username already exists. Try providing different username.' });
        }

        // Hash the password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Create the user
        await db.run(
            'INSERT INTO users (username, password, invite_id) VALUES (?, ?, ?)',
            [user_name, hashedPassword, invite_id]
        );

        return res.status(200).json({ message: 'User created successfully' });
    } catch (error) {
        console.error('Error creating user:', error);
        return res.status(500).json({ message: 'Internal server error' });
    }
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});