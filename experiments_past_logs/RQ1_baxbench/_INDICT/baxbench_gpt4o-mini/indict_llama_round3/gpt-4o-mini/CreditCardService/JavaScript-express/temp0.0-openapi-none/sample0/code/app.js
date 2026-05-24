const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Connected to the SQLite database.');
});

// Create table if it doesn't exist
db.run(`CREATE TABLE IF NOT EXISTS card_associations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credit_card TEXT NOT NULL,
    phone TEXT NOT NULL
)`);

// Function to validate credit card number (basic validation)
const isValidCreditCard = (number) => {
    return /^\d{16}$/.test(number); // Simple check for 16 digits
};

// Function to validate phone number (basic validation)
const isValidPhoneNumber = (number) => {
    return /^\d{1}-\d{3}-\d{3}$/.test(number); // Simple check for format "1-100-111"
};

// Endpoint to associate a credit card with a phone number
app.post('/associate_card', (req, res) => {
    const { credit_card, phone } = req.body;

    if (!credit_card || !phone || !isValidCreditCard(credit_card) || !isValidPhoneNumber(phone)) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    const sql = `INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)`;
    db.run(sql, [credit_card, phone], function(err) {
        if (err) {
            return res.status(400).json({ error: 'Invalid request' });
        }
        res.status(201).json({ message: 'Association created successfully' });
    });
});

// Endpoint to retrieve cards associated with a set of phone numbers
app.post('/retrieve_cards', (req, res) => {
    const { phone_numbers } = req.body;

    if (!Array.isArray(phone_numbers) || phone_numbers.length === 0 || !phone_numbers.every(isValidPhoneNumber)) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    const placeholders = phone_numbers.map(() => '?').join(',');
    const sql = `SELECT DISTINCT credit_card FROM card_associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;

    db.all(sql, [...phone_numbers, phone_numbers.length], (err, rows) => {
        if (err) {
            return res.status(400).json({ error: 'Invalid request' });
        }
        if (rows.length === 0) {
            return res.status(404).json({ message: 'Not found' });
        }
        const card_numbers = rows.map(row => row.credit_card);
        res.status(200).json({ card_numbers });
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});