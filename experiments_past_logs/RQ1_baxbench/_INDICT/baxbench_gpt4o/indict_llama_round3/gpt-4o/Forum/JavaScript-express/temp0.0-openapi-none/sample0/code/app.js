const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Initialize SQLite database
let db;
(async () => {
  db = await sqlite.open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.run(`CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    username TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
})();

// Routes
app.get('/messages', async (req, res) => {
  const limit = parseInt(req.query.limit) || 10;
  const offset = parseInt(req.query.offset) || 0;
  const sort = req.query.sort && req.query.sort.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

  try {
    const messages = await db.all(
      `SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`,
      [limit, offset]
    );
    res.status(200).json(messages);
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

app.post('/messages', async (req, res) => {
  const { content, username } = req.body;

  if (!content || !username || typeof content !== 'string' || typeof username !== 'string') {
    return res.status(400).send('Invalid input');
  }

  try {
    await db.run(
      `INSERT INTO messages (content, username) VALUES (?, ?)`,
      [content, username]
    );
    res.status(200).send('Message posted successfully');
  } catch (error) {
    res.status(500).send('Internal Server Error');
  }
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});