const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(express.json());

const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL,
            UNIQUE(credit_card, phone)
        )`, (err) => {
            if (err) {
                console.error('Error creating table ' + err.message);
            }
        });
    }
});

app.post('/associate_card', (req, res) => {
    const { credit_card, phone } = req.body;

    if (!credit_card || !phone) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    const sql = 'INSERT INTO associations (credit_card, phone) VALUES (?, ?)';
    db.run(sql, [credit_card, phone], function(err) {
        if (err) {
            return res.status(400).json({ error: 'Invalid request' });
        }
        res.status(201).json({ message: 'Association created successfully' });
    });
});

app.post('/retrieve_cards', (req, res) => {
    const { phone_numbers } = req.body;

    if (!Array.isArray(phone_numbers) || phone_numbers.length === 0) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    const placeholders = phone_numbers.map(() => '?').join(',');
    const sql = `SELECT credit_card FROM associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
    
    db.all(sql, [...phone_numbers, phone_numbers.length], (err, rows) => {
        if (err) {
            return res.status(400).json({ error: 'Invalid request' });
        }
        if (rows.length === 0) {
            return res.status(404).json({ error: 'Not found' });
        }
        const card_numbers = rows.map(row => row.credit_card);
        res.status(200).json({ card_numbers });
    });
});

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});