const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');

// Load environment variables from .env file
dotenv.config();

const app = express();
app.use(bodyParser.json());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS card_associations (
      id TEXT PRIMARY KEY,
      credit_card TEXT NOT NULL,
      phone TEXT NOT NULL
    )`, (err) => {
      if (err) {
        console.error('Error creating table ' + err.message);
      }
    });
  }
});

// Endpoint to associate a credit card with a phone number
app.post('/associate_card', (req, res) => {
  const { credit_card, phone } = req.body;

  if (!credit_card || !phone) {
    return res.status(400).json({ error: 'Invalid request' });
  }

  const id = uuidv4();
  const query = `INSERT INTO card_associations (id, credit_card, phone) VALUES (?, ?, ?)`;

  db.run(query, [id, credit_card, phone], function(err) {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }
    res.status(201).json({ message: 'Association created successfully' });
  });
});

// Endpoint to retrieve cards associated with a set of phone numbers
app.post('/retrieve_cards', (req, res) => {
  const { phone_numbers } = req.body;

  if (!Array.isArray(phone_numbers) || phone_numbers.length === 0) {
    return res.status(400).json({ error: 'Invalid request' });
  }

  const placeholders = phone_numbers.map(() => '?').join(',');
  const query = `
    SELECT credit_card
    FROM card_associations
    WHERE phone IN (${placeholders})
    GROUP BY credit_card
    HAVING COUNT(DISTINCT phone) = ?
  `;

  db.all(query, [...phone_numbers, phone_numbers.length], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }
    if (rows.length === 0) {
      return res.status(404).json({ error: 'Not found' });
    }
    const card_numbers = rows.map(row => row.credit_card);
    res.status(200).json({ card_numbers });
  });
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});