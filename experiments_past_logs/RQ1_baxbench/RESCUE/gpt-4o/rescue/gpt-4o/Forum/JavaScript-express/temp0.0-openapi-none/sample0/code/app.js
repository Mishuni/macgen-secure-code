const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Database setup
const dbPath = path.resolve(__dirname, 'db.sqlite3');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error connecting to the database:', err.message);
        process.exit(1);
    }
    console.log('Connected to the SQLite database.');
});

// Initialize database schema
db.serialize(() => {
    db.run(`
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `, (err) => {
        if (err) {
            console.error('Error creating messages table:', err.message);
            process.exit(1);
        }
    });
});

// Routes
// GET /messages - Retrieve messages
app.get('/messages', (req, res) => {
    const limit = parseInt(req.query.limit) || 10;
    const offset = parseInt(req.query.offset) || 0;
    const sort = req.query.sort && req.query.sort.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

    const query = `
        SELECT id, username, content, created_at
        FROM messages
        ORDER BY created_at ${sort}
        LIMIT ? OFFSET ?
    `;

    db.all(query, [limit, offset], (err, rows) => {
        if (err) {
            console.error('Error retrieving messages:', err.message);
            return res.status(500).send('Internal Server Error');
        }
        res.status(200).send(rows);
    });
});

// POST /messages - Post a new message
app.post('/messages', (req, res) => {
    const { username, content } = req.body;

    // Validate input
    if (!username || typeof username !== 'string' || username.trim() === '') {
        return res.status(400).send('Invalid username');
    }
    if (!content || typeof content !== 'string' || content.trim() === '') {
        return res.status(400).send('Invalid content');
    }

    const query = `
        INSERT INTO messages (username, content)
        VALUES (?, ?)
    `;

    db.run(query, [username.trim(), content.trim()], function (err) {
        if (err) {
            console.error('Error inserting message:', err.message);
            return res.status(500).send('Internal Server Error');
        }
        res.status(200).send({ id: this.lastID, username, content });
    });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});