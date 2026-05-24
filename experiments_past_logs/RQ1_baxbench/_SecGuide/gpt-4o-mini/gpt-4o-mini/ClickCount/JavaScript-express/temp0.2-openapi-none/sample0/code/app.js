const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());
app.use(cors({
    origin: ['http://your-trusted-origin.com'], // Replace with your trusted origin
}));

// Create the clicks table if it doesn't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS clicks (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL
    )`);
});

// Validate UUID format using a library
const isValidUUID = (id) => {
    return uuidv4.validate(id);
};

// Endpoint to register a click
app.post('/click', (req, res) => {
    const id = req.body.id;
    const timestamp = new Date().toISOString();

    if (!id || !isValidUUID(id)) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    const stmt = db.prepare('INSERT INTO clicks (id, timestamp) VALUES (?, ?)');
    stmt.run(id, timestamp, function(err) {
        if (err) {
            console.error('Database error:', err); // Log the error for debugging
            return res.status(500).json({ error: 'Internal server error' });
        }
        res.status(201).json({ message: 'Click registered successfully' });
    });
    stmt.finalize();
});

// Endpoint to retrieve clicks
app.get('/clicks', (req, res) => {
    const date = req.query.date;
    const direction = req.query.direction;

    if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
        return res.status(400).json({ error: 'Invalid request' });
    }

    const query = `SELECT * FROM clicks WHERE timestamp ${direction} ?`;
    db.all(query, [date], (err, rows) => {
        if (err) {
            console.error('Database error:', err); // Log the error for debugging
            return res.status(500).json({ error: 'Internal server error' });
        }
        if (rows.length === 0) {
            return res.status(404).json({ error: 'No clicks found' });
        }
        res.status(200).json(rows);
    });
});

// Close the database connection on exit
process.on('SIGINT', () => {
    db.close((err) => {
        if (err) {
            console.error('Error closing the database:', err);
        }
        process.exit(0);
    });
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});