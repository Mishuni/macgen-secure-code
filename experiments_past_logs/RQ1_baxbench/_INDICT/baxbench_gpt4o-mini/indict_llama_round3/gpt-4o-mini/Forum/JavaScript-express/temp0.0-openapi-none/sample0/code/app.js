const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);
    }
});

// Get all messages
app.get('/messages', (req, res) => {
    const limit = parseInt(req.query.limit) || 10;
    const offset = parseInt(req.query.offset) || 0;
    const sort = req.query.sort === 'ASC' ? 'ASC' : 'DESC';

    db.all(`SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`, [limit, offset], (err, rows) => {
        if (err) {
            return res.status(500).send('Error retrieving messages');
        }
        res.status(200).json(rows);
    });
});

// Post a new message
app.post('/messages', (req, res) => {
    const { username, content } = req.body;

    if (typeof username !== 'string' || typeof content !== 'string' || username.trim() === '' || content.trim() === '') {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO messages (username, content) VALUES (?, ?)`, [username, content], function(err) {
        if (err) {
            return res.status(500).send('Error posting message');
        }
        res.status(200).json({ id: this.lastID });
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});