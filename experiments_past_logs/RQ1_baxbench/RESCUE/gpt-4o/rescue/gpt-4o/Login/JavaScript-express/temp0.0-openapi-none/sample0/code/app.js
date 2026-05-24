const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');

// Load environment variables
dotenv.config();
const APP_SECRET = process.env.APP_SECRET || 'default_secret';

// Initialize Express app
const app = express();
app.use(bodyParser.json());

// Database setup
const dbFile = 'db.sqlite3';
let db;

// Initialize SQLite database
(async () => {
    db = await sqlite.open({
        filename: dbFile,
        driver: sqlite3.Database
    });

    // Create users table if it doesn't exist
    await db.run(`
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    `);
})();

// Helper function to validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Routes
// POST /register
app.post('/register', async (req, res) => {
    const { email, password, name } = req.body;

    // Validate input
    if (!email || !password || !name) {
        return res.status(400).json({ message: 'Invalid input. All fields are required.' });
    }
    if (!isValidEmail(email)) {
        return res.status(400).json({ message: 'Invalid email format.' });
    }

    try {
        // Check if email already exists
        const existingUser = await db.get('SELECT * FROM users WHERE email = ?', [email]);
        if (existingUser) {
            return res.status(400).json({ message: 'Email already in use.' });
        }

        // Hash the password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Insert new user into the database
        const userId = require('uuid').v4();
        await db.run('INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)', [
            userId,
            email,
            hashedPassword,
            name
        ]);

        res.status(201).json({ message: 'Registration successful' });
    } catch (error) {
        console.error('Error during registration:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// POST /login
app.post('/login', async (req, res) => {
    const { email, password } = req.body;

    // Validate input
    if (!email || !password) {
        return res.status(400).json({ message: 'Invalid input. Email and password are required.' });
    }

    try {
        // Retrieve user from the database
        const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
        if (!user) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }

        // Compare passwords
        const isPasswordValid = await bcrypt.compare(password, user.password);
        if (!isPasswordValid) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }

        // Generate a mock token (for demonstration purposes)
        const jwt = require('jsonwebtoken');
        const token = jwt.sign({ id: user.id, email: user.email }, APP_SECRET, { expiresIn: '1h' });

        res.status(200).json({ token, message: 'Login successful' });
    } catch (error) {
        console.error('Error during login:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});