const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const validator = require('validator');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(helmet()); // Use Helmet to secure Express apps by setting various HTTP headers
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

// Rate limiting middleware
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Get all messages
app.get('/messages', (req, res) => {
    const limit = Math.min(parseInt(req.query.limit) || 10, 100); // Limit max to 100
    const offset = Math.max(parseInt(req.query.offset) || 0, 0); // Ensure offset is non-negative
    const sort = ['ASC', 'DESC'].includes(req.query.sort) ? req.query.sort : 'DESC'; // Validate sort parameter

    db.all(`SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`, [limit, offset], (err, rows) => {
        if (err) {
            console.error(err); // Log the error for debugging
            return res.status(500).send('Internal Server Error');
        }
        res.status(200).send(rows);
    });
});

// Post a new message
app.post('/messages', (req, res) => {
    const { content, username } = req.body;

    // Input validation
    if (!content || !username || content.length > 500 || username.length > 100 || 
        !validator.isAlphanumeric(username) || validator.contains(content, '<') || validator.contains(content, '>')) {
        return res.status(400).send('Invalid input');
    }

    const stmt = db.prepare(`INSERT INTO messages (content, username) VALUES (?, ?)`);
    stmt.run(content, username, function(err) {
        if (err) {
            console.error(err); // Log the error for debugging
            return res.status(500).send('Internal Server Error');
        }
        res.status(200).send({ id: this.lastID });
    });
    stmt.finalize();
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});