const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const https = require('https');
const fs = require('fs');
const path = require('path');

dotenv.config();

const app = express();
app.use(bodyParser.json());

const DB_PATH = process.env.DB_PATH || './db.sqlite3';
let db;

// Initialize the database connection once
async function initDb() {
  if (!db) {
    db = await sqlite.open({
      filename: DB_PATH,
      driver: sqlite3.Database
    });

    await db.run(`
      CREATE TABLE IF NOT EXISTS card_associations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        credit_card TEXT NOT NULL,
        phone TEXT NOT NULL
      )
    `);
  }
}

initDb().catch(error => {
  console.error('Failed to initialize database:', error);
  process.exit(1);
});

// Validate credit card and phone number formats
function validateInput(credit_card, phone) {
  const creditCardRegex = /^[0-9]{13,19}$/; // More robust regex for credit card numbers
  const phoneRegex = /^[0-9]{10,15}$/; // More robust regex for phone numbers

  return creditCardRegex.test(credit_card) && phoneRegex.test(phone);
}

app.post('/associate_card', async (req, res) => {
  const { credit_card, phone } = req.body;

  if (!credit_card || !phone || !validateInput(credit_card, phone)) {
    return res.status(400).json({ error: 'Invalid request' });
  }

  try {
    await db.run('INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)', [credit_card, phone]);
    res.status(201).json({ message: 'Association created successfully' });
  } catch (error) {
    console.error('Error associating card:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/retrieve_cards', async (req, res) => {
  const phone_numbers = req.query.phone_numbers;

  if (!Array.isArray(phone_numbers) || phone_numbers.length === 0 || !phone_numbers.every(phone => /^[0-9]{10,15}$/.test(phone))) {
    return res.status(400).json({ error: 'Invalid request' });
  }

  try {
    const placeholders = phone_numbers.map(() => '?').join(',');
    const query = `
      SELECT credit_card FROM card_associations
      WHERE phone IN (${placeholders})
      GROUP BY credit_card
      HAVING COUNT(DISTINCT phone) = ?
    `;
    const cards = await db.all(query, [...phone_numbers, phone_numbers.length]);

    if (cards.length === 0) {
      return res.status(404).json({ error: 'Not found' });
    }

    res.status(200).json({ card_numbers: cards.map(card => card.credit_card) });
  } catch (error) {
    console.error('Error retrieving cards:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Load SSL certificates
const options = {
  key: fs.readFileSync(process.env.SSL_KEY_PATH || path.join(__dirname, 'private.key')),
  cert: fs.readFileSync(process.env.SSL_CERT_PATH || path.join(__dirname, 'certificate.crt'))
};

const PORT = process.env.PORT || 5000;
https.createServer(options, app).listen(PORT, () => {
  console.log(`Server running on https://localhost:${PORT}`);
});