const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(express.json());

const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS clicks (
      id TEXT PRIMARY KEY,
      timestamp TEXT NOT NULL
    )
  `);
})();

// Endpoint to register a click
app.post('/click', async (req, res) => {
  try {
    const id = uuidv4();
    const timestamp = new Date().toISOString();

    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);

    res.status(201).send('Click registered successfully');
  } catch (error) {
    console.error('Error registering click:', error);
    res.status(400).send('Invalid request');
  }
});

// Endpoint to retrieve clicks
app.get('/clicks', async (req, res) => {
  const { date, direction } = req.query;

  if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
    return res.status(400).send('Invalid request');
  }

  try {
    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    const clicks = await db.all(query, [`${date}T00:00:00.000Z`]);

    if (clicks.length === 0) {
      return res.status(404).send('No clicks found');
    }

    res.status(200).json(clicks);
  } catch (error) {
    console.error('Error retrieving clicks:', error);
    res.status(400).send('Invalid request');
  }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});