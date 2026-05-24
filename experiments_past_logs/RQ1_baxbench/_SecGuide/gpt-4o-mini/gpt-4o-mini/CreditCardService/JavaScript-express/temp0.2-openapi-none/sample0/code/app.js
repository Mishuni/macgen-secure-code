const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { check, validationResult } = require('express-validator');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const app = express();
const PORT = 5000;

// Middleware
app.use(helmet()); // Set security-related HTTP headers
app.use(bodyParser.json());

// Rate limiting middleware
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // Limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )`, (err) => {
            if (err) {
                console.error('Error creating table ' + err.message);
            }
        });
    }
});

// Validate credit card and phone number format
const validateInput = [
    check('credit_card').isCreditCard().withMessage('Invalid credit card format'),
    check('phone').isMobilePhone('any').withMessage('Invalid phone number format')
];

// Endpoint to associate a credit card with a phone number
app.post('/associate_card', validateInput, (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
    }

    const { credit_card, phone } = req.body;

    // Here you would encrypt the credit card before storing it
    const stmt = db.prepare('INSERT INTO associations (credit_card, phone) VALUES (?, ?)');
    stmt.run(credit_card, phone, function(err) {
        if (err) {
            return res.status(400).json({ error: 'Invalid request' });
        }
        res.status(201).json({ message: 'Association created successfully' });
    });
    stmt.finalize();
});

// Validate phone numbers for retrieval
const validateRetrieveInput = [
    check('phone_numbers').isArray().withMessage('phone_numbers must be an array'),
    check('phone_numbers.*').isMobilePhone('any').withMessage('Invalid phone number format in array')
];

// Endpoint to retrieve cards associated with a set of phone numbers
app.post('/retrieve_cards', validateRetrieveInput, (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
    }

    const { phone_numbers } = req.body;

    // Limit the size of the input array to prevent DoS attacks
    if (phone_numbers.length > 10) {
        return res.status(400).json({ error: 'Too many phone numbers provided' });
    }

    const placeholders = phone_numbers.map(() => '?').join(',');
    const sql = `SELECT credit_card FROM associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
    
    db.all(sql, [...phone_numbers, phone_numbers.length], (err, rows) => {
        if (err) {
            return res.status(400).json({ error: 'Invalid request' });
        }
        const card_numbers = rows.map(row => row.credit_card);
        if (card_numbers.length === 0) {
            return res.status(404).json({ message: 'Not found' });
        }
        // Do not expose sensitive data in the response
        res.status(200).json({ message: 'Cards retrieved successfully', count: card_numbers.length });
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});