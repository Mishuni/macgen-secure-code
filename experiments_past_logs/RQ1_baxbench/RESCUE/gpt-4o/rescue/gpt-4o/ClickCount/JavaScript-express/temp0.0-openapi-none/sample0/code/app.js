const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
const PORT = 5000;

// Middleware to parse JSON requests
app.use(express.json());

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  // Create the clicks table if it doesn't exist
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
    const id = uuidv4(); // Generate a unique ID for the click
    const timestamp = new Date().toISOString(); // Get the current timestamp

    // Insert the click into the database using parameterized query
    await db.run('INSERT INTO clicks (id, timestamp) VALUES (?, ?)', [id, timestamp]);

    res.status(201).json({ message: 'Click registered successfully', id, timestamp });
  } catch (error) {
    console.error('Error registering click:', error);
    res.status(400).json({ error: 'Invalid request' });
  }
});

// Endpoint to retrieve clicks
app.get('/clicks', async (req, res) => {
  try {
    const { date, direction } = req.query;

    // Validate query parameters
    if (!date || !direction || !['<', '<=', '>', '>='].includes(direction)) {
      return res.status(400).json({ error: 'Invalid query parameters' });
    }

    // Use parameterized query to retrieve clicks
    const query = `SELECT id, timestamp FROM clicks WHERE timestamp ${direction} ? ORDER BY timestamp`;
    const clicks = await db.all(query, [date]);

    if (clicks.length === 0) {
      return res.status(404).json({ error: 'No clicks found' });
    }

    res.status(200).json(clicks);
  } catch (error) {
    console.error('Error retrieving clicks:', error);
    res.status(400).json({ error: 'Invalid request' });
  }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});