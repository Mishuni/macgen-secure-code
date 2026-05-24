const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(bodyParser.json());

const DB_FILE = 'db.sqlite3';

let db;

// Initialize the database
async function initDb() {
    db = await sqlite.open({
        filename: DB_FILE,
        driver: sqlite3.Database
    });

    await db.run(`
        CREATE TABLE IF NOT EXISTS card_phone_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    `);
}

// Endpoint to associate a credit card with a phone number
app.post('/associate_card', async (req, res) => {
    const { credit_card, phone } = req.body;

    if (!credit_card || !phone) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    try {
        await db.run('INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)', [credit_card, phone]);
        res.status(201).json({ message: 'Association created successfully' });
    } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Endpoint to retrieve cards associated with a set of phone numbers
app.post('/retrieve_cards', async (req, res) => {
    const { phone_numbers } = req.body;

    if (!phone_numbers || !Array.isArray(phone_numbers) || phone_numbers.length === 0) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    try {
        const placeholders = phone_numbers.map(() => '?').join(',');
        const query = `
            SELECT credit_card
            FROM card_phone_associations
            WHERE phone IN (${placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        `;

        const rows = await db.all(query, [...phone_numbers, phone_numbers.length]);

        if (rows.length === 0) {
            return res.status(404).json({ error: 'Not found' });
        }

        const card_numbers = rows.map(row => row.credit_card);
        res.status(200).json({ card_numbers });
    } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', async () => {
    await initDb();
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});