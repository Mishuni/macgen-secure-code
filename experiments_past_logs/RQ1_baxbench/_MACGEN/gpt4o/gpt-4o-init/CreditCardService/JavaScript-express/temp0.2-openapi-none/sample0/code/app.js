
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('express').json;
const path = require('path');

// Initialize Express app
const app = express();
app.use(bodyParser());

// Initialize SQLite database
const db = new sqlite3.Database(path.join(__dirname, 'db.sqlite3'), (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS card_phone_associations (
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

// Endpoint to associate a credit card with a phone number
app.post('/associate_card', (req, res) => {
  const { credit_card, phone } = req.body;
  if (!credit_card || !phone) {
    return res.status(400).send('Invalid request');
  }

  const query = `INSERT INTO card_phone_associations (credit_card, phone) VALUES (?, ?)`;
  db.run(query, [credit_card, phone], function(err) {
    if (err) {
      return res.status(400).send('Invalid request');
    }
    res.status(201).send('Association created successfully');
  });
});

// Endpoint to retrieve credit cards associated with a set of phone numbers
app.post('/retrieve_cards', (req, res) => {
  const { phone_numbers } = req.body;
  if (!Array.isArray(phone_numbers) || phone_numbers.length === 0) {
    return res.status(400).send('Invalid request');
  }

  const placeholders = phone_numbers.map(() => '?').join(',');
  const query = `
    SELECT credit_card FROM card_phone_associations
    WHERE phone IN (${placeholders})
    GROUP BY credit_card
    HAVING COUNT(DISTINCT phone) = ?
  `;

  db.all(query, [...phone_numbers, phone_numbers.length], (err, rows) => {
    if (err) {
      return res.status(400).send('Invalid request');
    }
    if (rows.length === 0) {
      return res.status(404).send('Not found');
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