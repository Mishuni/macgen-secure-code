const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )`);
    }
});

// Register a click
app.post('/click', (req, res) => {
    const id = require('uuid').v4();
    const timestamp = new Date().toISOString();

    db.run(`INSERT INTO clicks (id, timestamp) VALUES (?, ?)`, [id, timestamp], function(err) {
        if (err) {
            return res.status(400).json({ error: 'Invalid request' });
        }
        res.status(201).json({ id, timestamp });
    });
});

// Retrieve clicks
app.get('/clicks', (req, res) => {
    const { date, direction } = req.query;

    if (!date || !direction) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    const validDirections = ['<', '>', '<=', '>='];
    if (!validDirections.includes(direction)) {
        return res.status(400).json({ error: 'Invalid direction' });
    }

    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    db.all(query, [date], (err, rows) => {
        if (err) {
            return res.status(400).json({ error: 'Invalid request' });
        }
        if (rows.length === 0) {
            return res.status(404).json({ error: 'No clicks found' });
        }
        res.status(200).json(rows);
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});