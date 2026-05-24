const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Create messages table if it doesn't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        username TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )`);
});

// Get all messages
app.get('/messages', (req, res) => {
    const limit = parseInt(req.query.limit) || 10;
    const offset = parseInt(req.query.offset) || 0;
    const sort = req.query.sort === 'ASC' ? 'ASC' : 'DESC';

    db.all(`SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`, [limit, offset], (err, rows) => {
        if (err) {
            return res.status(500).send('Internal Server Error');
        }
        res.status(200).send(rows);
    });
});

// Post a new message
app.post('/messages', (req, res) => {
    const { content, username } = req.body;

    if (!content || !username) {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO messages (content, username) VALUES (?, ?)`, [content, username], function(err) {
        if (err) {
            return res.status(500).send('Internal Server Error');
        }
        res.status(200).send({ id: this.lastID });
    });
});

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});