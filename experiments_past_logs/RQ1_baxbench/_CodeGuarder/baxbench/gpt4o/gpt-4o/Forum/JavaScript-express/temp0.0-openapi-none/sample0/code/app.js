const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const path = require('path');

// Load environment variables from .env file
dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: path.join(__dirname, 'db.sqlite3'),
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      content TEXT NOT NULL,
      username TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);
})();

// API Endpoints

// Get all previously posted messages
app.get('/messages', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 10;
    const offset = parseInt(req.query.offset) || 0;
    const sort = req.query.sort === 'ASC' ? 'ASC' : 'DESC';

    const messages = await db.all(
      `SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`,
      [limit, offset]
    );

    res.status(200).json(messages);
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Post a new message to the forum
app.post('/messages', async (req, res) => {
  try {
    const { content, username } = req.body;

    if (!content || !username) {
      return res.status(400).send('Invalid input');
    }

    await db.run(
      `INSERT INTO messages (content, username) VALUES (?, ?)`,
      [content, username]
    );

    res.status(200).send('Message posted successfully');
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});