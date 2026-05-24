const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());

// Create the database table if it doesn't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS card_associations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        credit_card TEXT NOT NULL,
        phone TEXT NOT NULL
    )`);
});

// Endpoint to associate a credit card with a phone number
app.post('/associate_card', (req, res) => {
    const { credit_card, phone } = req.body;

    // Input validation
    if (typeof credit_card !== 'string' || typeof phone !== 'string' || 
        !/^\d{16}$/.test(credit_card) || !/^\d{1}-\d{3}-\d{3}$/.test(phone)) {
        return res.status(400).json({ message: 'Invalid request' });
    }

    const stmt = db.prepare('INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)');
    stmt.run(credit_card, phone, function(err) {
        if (err) {
            return res.status(400).json({ message: 'Invalid request' });
        }
        res.status(201).json({ message: 'Association created successfully' });
    });
    stmt.finalize();
});

// Endpoint to retrieve credit cards associated with phone numbers
app.post('/retrieve_cards', (req, res) => {
    const { phone_numbers } = req.body;

    // Input validation
    if (!Array.isArray(phone_numbers) || phone_numbers.length === 0 || 
        !phone_numbers.every(phone => typeof phone === 'string' && /^\d{1}-\d{3}-\d{3}$/.test(phone))) {
        return res.status(400).json({ message: 'Invalid request' });
    }

    const placeholders = phone_numbers.map(() => '?').join(',');
    const query = `SELECT credit_card FROM card_associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
    
    db.all(query, [...phone_numbers, phone_numbers.length], (err, rows) => {
        if (err) {
            return res.status(400).json({ message: 'Invalid request' });
        }
        const card_numbers = rows.map(row => row.credit_card);
        if (card_numbers.length === 0) {
            return res.status(404).json({ message: 'Not found' });
        }
        res.status(200).json({ card_numbers });
    });
});

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});