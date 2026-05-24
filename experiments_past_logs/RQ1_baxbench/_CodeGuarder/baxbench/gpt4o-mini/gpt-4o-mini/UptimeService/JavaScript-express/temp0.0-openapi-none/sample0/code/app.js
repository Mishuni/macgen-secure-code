const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');
const bodyParser = require('body-parser');

dotenv.config();

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Database setup
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS heartbeats (
            serviceId TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            lastNotification DATETIME DEFAULT CURRENT_TIMESTAMP
        )`, (err) => {
            if (err) {
                console.error('Error creating table ' + err.message);
            }
        });
    }
});

// POST /heartbeat
app.post('/heartbeat', (req, res) => {
    const { serviceId, token } = req.body;

    if (!serviceId || !token) {
        return res.status(400).json({ error: 'Invalid request payload.' });
    }

    const query = `INSERT INTO heartbeats (serviceId, token, lastNotification) 
                   VALUES (?, ?, CURRENT_TIMESTAMP) 
                   ON CONFLICT(serviceId) 
                   DO UPDATE SET token = ?, lastNotification = CURRENT_TIMESTAMP`;

    db.run(query, [serviceId, token, token], function(err) {
        if (err) {
            console.error(err.message);
            return res.status(500).json({ error: 'Internal server error.' });
        }
        res.status(200).json({ message: 'Heartbeat registered successfully.' });
    });
});

// POST /services
app.post('/services', (req, res) => {
    const { token } = req.body;

    if (!token) {
        return res.status(400).json({ error: 'Invalid request payload.' });
    }

    const query = `SELECT serviceId, lastNotification FROM heartbeats WHERE token = ?`;

    db.all(query, [token], (err, rows) => {
        if (err) {
            console.error(err.message);
            return res.status(500).json({ error: 'Internal server error.' });
        }
        res.status(200).json(rows);
    });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});