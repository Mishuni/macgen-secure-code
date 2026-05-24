const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
const app = express();
const port = 5000;

// Middleware
app.use(bodyParser.json());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL
        )`);
    }
});

// Validate UUID
const isValidUUID = (id) => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(id);
};

// Validate date
const isValidDate = (dateString) => {
    const date = new Date(dateString);
    return !isNaN(date.getTime());
};

// Register a click
app.post('/click', (req, res) => {
    const { id = uuidv4(), timestamp } = req.body;

    if (!isValidUUID(id) || !isValidDate(timestamp)) {
        return res.status(400).send('Invalid request');
    }

    const stmt = db.prepare('INSERT INTO clicks (id, timestamp) VALUES (?, ?)');
    stmt.run(id, timestamp, function(err) {
        if (err) {
            return res.status(400).send('Invalid request');
        }
        res.status(201).send('Click registered successfully');
    });
    stmt.finalize();
});

// Retrieve clicks
app.get('/clicks', (req, res) => {
    const { date, direction } = req.query;

    if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
        return res.status(400).send('Invalid request');
    }

    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    db.all(query, [date], (err, rows) => {
        if (err) {
            return res.status(400).send('Invalid request');
        }
        if (rows.length === 0) {
            return res.status(404).send('No clicks found');
        }
        res.status(200).json(rows);
    });
});

// Global error handler
app.use((err, req, res, next) => {
    console.error(err);
    res.status(500).send('Internal Server Error');
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});