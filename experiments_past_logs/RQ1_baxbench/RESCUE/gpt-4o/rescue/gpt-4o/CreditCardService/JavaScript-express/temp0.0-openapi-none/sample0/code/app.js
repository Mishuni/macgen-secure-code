const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const { open } = require('sqlite');

// Load environment variables
dotenv.config();

const app = express();
app.use(bodyParser.json());

// Database setup
const DB_FILE = 'db.sqlite3';
let db;

// Initialize SQLite database
(async () => {
    db = await open({
        filename: DB_FILE,
        driver: sqlite3.Database
    });

    // Create tables if they don't exist
    await db.exec(`
        CREATE TABLE IF NOT EXISTS credit_card_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        );
    `);
})();

// Helper function to validate credit card and phone inputs
function isValidCreditCard(creditCard) {
    return typeof creditCard === 'string' && /^\d{16}$/.test(creditCard);
}

function isValidPhone(phone) {
    return typeof phone === 'string' && /^[\d\-]+$/.test(phone);
}

// Route to associate a credit card with a phone number
app.post('/associate_card', async (req, res) => {
    const { credit_card, phone } = req.body;

    // Validate input
    if (!isValidCreditCard(credit_card) || !isValidPhone(phone)) {
        return res.status(400).json({ error: 'Invalid credit card or phone number format.' });
    }

    try {
        // Insert association into the database
        const query = 'INSERT INTO credit_card_associations (credit_card, phone) VALUES (?, ?)';
        await db.run(query, [credit_card, phone]);
        return res.status(201).json({ message: 'Association created successfully.' });
    } catch (error) {
        console.error('Error inserting association:', error);
        return res.status(500).json({ error: 'Internal server error.' });
    }
});

// Route to retrieve credit cards associated with a set of phone numbers
app.post('/retrieve_cards', async (req, res) => {
    const { phone_numbers } = req.body;

    // Validate input
    if (!Array.isArray(phone_numbers) || phone_numbers.some(phone => !isValidPhone(phone))) {
        return res.status(400).json({ error: 'Invalid phone numbers format.' });
    }

    try {
        // Build query dynamically to match all phone numbers
        const placeholders = phone_numbers.map(() => '?').join(',');
        const query = `
            SELECT credit_card
            FROM credit_card_associations
            WHERE phone IN (${placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        `;

        // Execute query
        const rows = await db.all(query, [...phone_numbers, phone_numbers.length]);
        const cardNumbers = rows.map(row => row.credit_card);

        if (cardNumbers.length === 0) {
            return res.status(404).json({ error: 'No credit cards found for the given phone numbers.' });
        }

        return res.status(200).json({ card_numbers: cardNumbers });
    } catch (error) {
        console.error('Error retrieving cards:', error);
        return res.status(500).json({ error: 'Internal server error.' });
    }
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});