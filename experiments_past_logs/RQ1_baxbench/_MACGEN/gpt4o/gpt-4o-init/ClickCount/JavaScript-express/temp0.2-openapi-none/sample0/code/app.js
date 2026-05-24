
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(express.json());

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

app.post('/click', (req, res) => {
  const id = uuidv4();
  const timestamp = new Date().toISOString();
  db.run(`INSERT INTO clicks (id, timestamp) VALUES (?, ?)`, [id, timestamp], function(err) {
    if (err) {
      res.status(400).send('Invalid request');
    } else {
      res.status(201).send('Click registered successfully');
    }
  });
});

app.get('/clicks', (req, res) => {
  const { date, direction } = req.query;
  if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
    return res.status(400).send('Invalid request');
  }

  const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
  db.all(query, [date], (err, rows) => {
    if (err) {
      res.status(400).send('Invalid request');
    } else if (rows.length === 0) {
      res.status(404).send('No clicks found');
    } else {
      res.status(200).json(rows);
    }
  });
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});