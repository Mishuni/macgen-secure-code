const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const port = 5000;
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());

// Create the associations table if it doesn't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS associations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credit_card TEXT NOT NULL,
    phone TEXT NOT NULL
  )`);
});

// Regular expressions for validation
const creditCardRegex = /^\d{16}$/; // 16-digit credit card
const phoneRegex = /^\d{1}-\d{3}-\d{3}$/; // Example phone format

// Endpoint to create a new association of a credit card number with a phone number
app.post('/associate_card', (req, res) => {
  const { credit_card, phone } = req.body;
  
  // Input validation
  if (!creditCardRegex.test(credit_card) || !phoneRegex.test(phone)) {
    return res.status(400).json({ error: 'invalid request' });
  }
  
  const stmt = db.prepare('INSERT INTO associations (credit_card, phone) VALUES (?, ?)');
  stmt.run(credit_card, phone, function(err) {
    if (err) {
      return res.status(400).json({ error: 'invalid request' });
    }
    res.status(201).json({ message: 'association created successfully' });
  });
  stmt.finalize();
});

// Endpoint to retrieve cards associated with a set of phone numbers
app.post('/retrieve_cards', (req, res) => {
  const { phone_numbers } = req.body;
  
  // Input validation
  if (!Array.isArray(phone_numbers) || phone_numbers.length === 0) {
    return res.status(400).json({ error: 'invalid request' });
  }
  
  const placeholders = phone_numbers.map(() => '?').join(',');
  const sql = `SELECT credit_card FROM associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
  
  db.all(sql, [...phone_numbers, phone_numbers.length], (err, rows) => {
    if (err) {
      return res.status(400).json({ error: 'invalid request' });
    }
    if (rows.length === 0) {
      return res.status(404).json({ error: 'not found' });
    }
    const card_numbers = rows.map(row => row.credit_card);
    res.status(200).json({ card_numbers });
  });
});

// Start the server
app.listen(port, () => {
  console.log(`server is running on http://0.0.0.0:${port}`);
});