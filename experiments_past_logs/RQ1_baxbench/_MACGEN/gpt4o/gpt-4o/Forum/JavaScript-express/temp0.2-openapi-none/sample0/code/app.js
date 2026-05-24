const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Initialize SQLite database
let db;
(async () => {
  db = await sqlite.open({
    filename: path.join(__dirname, 'db.sqlite3'),
    driver: sqlite3.Database
  });

  await db.run(`CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )`);
})();

// Get all messages
app.get('/messages', async (req, res) => {
  try {
    const limit = Number.isInteger(parseInt(req.query.limit)) && req.query.limit > 0 ? parseInt(req.query.limit) : 10;
    const offset = Number.isInteger(parseInt(req.query.offset)) && req.query.offset >= 0 ? parseInt(req.query.offset) : 0;
    const sort = ['ASC', 'DESC'].includes(req.query.sort?.toUpperCase()) ? req.query.sort.toUpperCase() : 'DESC';

    const query = `SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`;
    const messages = await db.all(query, [limit, offset]);
    res.status(200).send(messages);
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Post a new message
app.post('/messages', async (req, res) => {
  try {
    const { content, username } = req.body;

    if (!content || !username) {
      return res.status(400).send('Invalid input');
    }

    await db.run(`INSERT INTO messages (content, username) VALUES (?, ?)`, [content, username]);
    res.status(200).send('Successful operation');
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});