const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const dotenv = require('dotenv');
const { escape } = require('html-escaper');
const helmet = require('helmet');
const cors = require('cors');

dotenv.config();

const app = express();
app.use(express.json());
app.use(helmet());
app.use(cors());

const PORT = process.env.PORT || 5000;
const DB_FILE = process.env.DB_FILE || 'db.sqlite3';

let db;

// Initialize the SQLite database
(async () => {
  db = await sqlite.open({
    filename: DB_FILE,
    driver: sqlite3.Database
  });

  await db.run(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      content TEXT NOT NULL,
      username TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);
})();

// Validate input
function validateInput(content, username) {
  const maxLength = 255;
  const isValidString = (str) => typeof str === 'string' && str.length > 0 && str.length <= maxLength;
  return isValidString(content) && isValidString(username);
}

// Sanitize input
function sanitizeInput(input) {
  return input.replace(/<[^>]*>?/gm, '');
}

// Get all previously posted messages
app.get('/messages', async (req, res) => {
  try {
    const limit = Math.min(parseInt(req.query.limit) || 10, 100); // Limit to a maximum of 100
    const offset = parseInt(req.query.offset) || 0;
    const sort = req.query.sort && req.query.sort.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

    const messages = await db.all(`
      SELECT * FROM messages
      ORDER BY created_at ${sort}
      LIMIT ? OFFSET ?
    `, [limit, offset]);

    const escapedMessages = messages.map(msg => ({
      ...msg,
      content: escape(msg.content),
      username: escape(msg.username)
    }));

    res.status(200).send(escapedMessages);
  } catch (error) {
    console.error('Error fetching messages:', error.message);
    res.status(500).send('Internal Server Error');
  }
});

// Post a new message to the forum
app.post('/messages', async (req, res) => {
  try {
    let { content, username } = req.body;

    if (!validateInput(content, username)) {
      return res.status(400).send('Invalid input');
    }

    content = sanitizeInput(content);
    username = sanitizeInput(username);

    await db.run(`
      INSERT INTO messages (content, username)
      VALUES (?, ?)
    `, [content, username]);

    res.status(200).send('Message posted successfully');
  } catch (error) {
    console.error('Error posting message:', error.message);
    res.status(500).send('Internal Server Error');
  }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});