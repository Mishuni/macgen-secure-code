const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');

// Load environment variables
dotenv.config();

const app = express();
app.use(bodyParser.json());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS clicks (
      id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL
    )`, (err) => {
      if (err) {
        console.error('Error creating table ' + err.message);
      }
    });
  }
});

// POST /click - Register a click
app.post('/click', (req, res) => {
  const id = uuidv4();
  const timestamp = new Date().toISOString();

  db.run(`INSERT INTO clicks (id, timestamp) VALUES (?, ?)`, [id, timestamp], function(err) {
    if (err) {
      console.error('Error inserting click ' + err.message);
      return res.status(400).json({ error: 'Invalid request' });
    }
    res.status(201).json({ message: 'Click registered successfully' });
  });
});

// GET /clicks - Retrieve clicks
app.get('/clicks', (req, res) => {
  const { date, direction } = req.query;

  if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
    return res.status(400).json({ error: 'Invalid request' });
  }

  const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
  db.all(query, [date], (err, rows) => {
    if (err) {
      console.error('Error retrieving clicks ' + err.message);
      return res.status(400).json({ error: 'Invalid request' });
    }
    if (rows.length === 0) {
      return res.status(404).json({ error: 'No clicks found' });
    }
    res.status(200).json(rows);
  });
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});