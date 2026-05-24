const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

// Middleware
app.use(bodyParser.json());
app.use(cookieParser());

// Create messages table if it doesn't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        username TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )`);
});

// GET /messages
app.get('/messages', (req, res) => {
    const limit = parseInt(req.query.limit) || 10;
    const offset = parseInt(req.query.offset) || 0;
    const sort = req.query.sort === 'ASC' ? 'ASC' : 'DESC';

    db.all(`SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`, [limit, offset], (err, rows) => {
        if (err) {
            return res.status(500).send('An error occurred while retrieving messages.');
        }
        res.status(200).json(rows);
    });
});

// POST /messages
app.post('/messages', (req, res) => {
    const { content, username } = req.body;

    if (typeof content !== 'string' || typeof username !== 'string') {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO messages (content, username) VALUES (?, ?)`, [content, username], function(err) {
        if (err) {
            return res.status(500).send('An error occurred while posting the message.');
        }
        res.status(200).send('Message posted successfully.');
    });
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

// Start server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});