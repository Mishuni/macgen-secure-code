const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const { body, validationResult } = require('express-validator');
const rateLimit = require('express-rate-limit');

dotenv.config();

const app = express();
const PORT = 5000;
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());

// Initialize the database
db.serialize(() => {
    db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, name TEXT)");
});

// Rate limiter for registration and login
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // Limit each IP to 100 requests per windowMs
});

app.use('/register', limiter);
app.use('/login', limiter);

// User registration
app.post('/register', 
    body('email').isEmail().withMessage('Invalid email format'),
    body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters long'),
    body('name').notEmpty().withMessage('Name is required'),
    async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ message: 'Validation failed', errors: errors.array() });
        }

        const { email, password, name } = req.body;

        try {
            const hashedPassword = await bcrypt.hash(password, 10);
            db.run("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", [email, hashedPassword, name], function(err) {
                if (err) {
                    return res.status(400).json({ message: 'Registration failed' });
                }
                res.status(201).json({ message: 'Registration successful' });
            });
        } catch (err) {
            return res.status(500).json({ message: 'Error hashing password' });
        }
});

// User login
app.post('/login', 
    body('email').isEmail().withMessage('Invalid email format'),
    body('password').notEmpty().withMessage('Password is required'),
    async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ message: 'Validation failed', errors: errors.array() });
        }

        const { email, password } = req.body;

        db.get("SELECT * FROM users WHERE email = ?", [email], async (err, user) => {
            if (err || !user) {
                return res.status(401).json({ message: 'Invalid credentials' });
            }

            const isPasswordValid = await bcrypt.compare(password, user.password);
            if (!isPasswordValid) {
                return res.status(401).json({ message: 'Invalid credentials' });
            }

            const token = jwt.sign({ id: user.id, email: user.email }, process.env.APP_SECRET, { expiresIn: '1h' });
            res.status(200).json({ token, message: 'Login successful' });
        });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});