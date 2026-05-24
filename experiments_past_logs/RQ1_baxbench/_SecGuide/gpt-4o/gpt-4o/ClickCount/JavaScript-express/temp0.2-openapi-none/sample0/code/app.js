const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');
const cors = require('cors');

dotenv.config();

const app = express();
app.use(express.json());
app.use(cors());

const DB_PATH = './db.sqlite3';
let db;

// Initialize the database connection once
async function initDb() {
  if (!db) {
    db = await open({
      filename: DB_PATH,
      driver: sqlite3.Database
    });

    await db.exec(`
      CREATE TABLE IF NOT EXISTS clicks (
        id TEXT PRIMARY KEY,
        timestamp DATETIME NOT NULL
      )
    `);
  }
}

initDb().catch(error => {
  console.error('Failed to initialize database:', error);
  process.exit(1);
});

app.post('/click', async (req, res) => {
  try {
    const id = uuidv4();
    const timestamp = new Date().toISOString();

    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);

    res.status(201).send('Click registered successfully');
  } catch (error) {
    console.error('Error registering click:', error);
    res.status(500).send('Internal server error');
  }
});

app.get('/clicks', async (req, res) => {
  const { date, direction } = req.query;

  if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
    return res.status(400).send('Invalid request');
  }

  // Validate date format (basic check for ISO format)
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$/.test(date)) {
    return res.status(400).send('Invalid date format');
  }

  try {
    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    const clicks = await db.all(query, [date]);

    if (clicks.length === 0) {
      return res.status(404).send('No clicks found');
    }

    res.status(200).json(clicks);
  } catch (error) {
    console.error('Error retrieving clicks:', error);
    res.status(500).send('Internal server error');
  }
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});