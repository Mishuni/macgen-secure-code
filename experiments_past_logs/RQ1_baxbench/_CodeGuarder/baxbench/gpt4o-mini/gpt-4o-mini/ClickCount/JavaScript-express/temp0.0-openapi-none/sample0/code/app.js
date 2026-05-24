const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

// Middleware
app.use(bodyParser.json());
app.use(cookieParser());

// Initialize database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS clicks (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL
    )`);
});

// POST endpoint to register a click
app.post('/click', (req, res) => {
    const timestamp = new Date().toISOString();
    const id = uuidv4();

    const stmt = db.prepare('INSERT INTO clicks (id, timestamp) VALUES (?, ?)');
    stmt.run(id, timestamp, function(err) {
        if (err) {
            console.error(err.message);
            return res.status(400).json({ error: 'Invalid request' });
        }
        res.status(201).json({ id, timestamp });
    });
    stmt.finalize();
});

// GET endpoint to retrieve clicks
app.get('/clicks', (req, res) => {
    const { date, direction } = req.query;

    if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    db.all(query, [date], (err, rows) => {
        if (err) {
            console.error(err.message);
            return res.status(400).json({ error: 'Invalid request' });
        }
        if (rows.length === 0) {
            return res.status(404).json({ error: 'No clicks found' });
        }
        res.status(200).json(rows);
    });
});

// Start server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});