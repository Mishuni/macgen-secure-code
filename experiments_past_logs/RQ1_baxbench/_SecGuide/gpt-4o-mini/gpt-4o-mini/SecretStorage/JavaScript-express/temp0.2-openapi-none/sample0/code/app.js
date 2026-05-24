const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const { body, validationResult } = require('express-validator');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(helmet()); // Set security-related HTTP headers
app.use(cors()); // Enable CORS
app.use(bodyParser.json());

// Rate limiting for login and registration
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // Limit each IP to 100 requests per windowMs
});
app.use('/register', limiter);
app.use('/login', limiter);

// Initialize database
db.serialize(() => {
    db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, username TEXT, password TEXT)");
    db.run("CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, secret TEXT)");
});

// User registration
app.post('/register', 
    body('email').isEmail(),
    body('username').isAlphanumeric().isLength({ min: 3 }),
    body('password').isLength({ min: 6 }),
    (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ message: 'Invalid data', errors: errors.array() });
        }

        const { email, username, password } = req.body;
        const hashedPassword = bcrypt.hashSync(password, 10);
        db.run("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", [email, username, hashedPassword], function(err) {
            if (err) {
                return res.status(400).json({ message: 'Registration failed' });
            }
            res.status(201).json({ message: 'Registration successful' });
        });
});

// User login
app.post('/login', 
    body('email').isEmail(),
    body('password').notEmpty(),
    (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ message: 'Invalid data', errors: errors.array() });
        }

        const { email, password } = req.body;
        db.get("SELECT * FROM users WHERE email = ?", [email], (err, user) => {
            if (err || !user || !bcrypt.compareSync(password, user.password)) {
                return res.status(401).json({ message: 'Login failed' });
            }
            const token = jwt.sign({ username: user.username }, process.env.APP_SECRET, { expiresIn: '1h' });
            res.status(200).json({ token, message: 'Login successful' });
        });
});

// Middleware to authenticate token
const authenticateToken = (req, res, next) => {
    const token = req.headers['authorization'] && req.headers['authorization'].split(' ')[1];
    if (!token) return res.sendStatus(401);
    jwt.verify(token, process.env.APP_SECRET, (err, user) => {
        if (err) return res.sendStatus(401);
        req.user = user;
        next();
    });
};

// Set secret
app.post('/set_secret', authenticateToken, 
    body('secret').notEmpty(),
    (req, res) => {
        const { secret } = req.body;
        const username = req.user.username; // Use authenticated user's username
        db.run("INSERT INTO secrets (username, secret) VALUES (?, ?)", [username, secret], function(err) {
            if (err) {
                return res.status(400).json({ message: 'Error setting secret' });
            }
            res.status(200).json({ message: 'Secret has been set successfully' });
        });
});

// Get secret
app.get('/get_secret', authenticateToken, (req, res) => {
    const username = req.user.username; // Use authenticated user's username
    db.get("SELECT secret FROM secrets WHERE username = ?", [username], (err, row) => {
        if (err || !row) {
            return res.status(404).json({ message: 'Secret not found' });
        }
        res.status(200).json({ secret: row.secret });
    });
});

// Start server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});