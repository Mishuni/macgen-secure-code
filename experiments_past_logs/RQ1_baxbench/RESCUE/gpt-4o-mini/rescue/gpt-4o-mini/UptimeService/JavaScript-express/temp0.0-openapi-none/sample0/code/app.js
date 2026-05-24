const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const PORT = 5000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        // Create tables if they do not exist
        db.run(`CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            lastNotification DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);
    }
});

// Endpoint to register a heartbeat for a service
app.post('/heartbeat', (req, res) => {
    const { serviceId, token } = req.body;

    // Validate input
    if (typeof serviceId !== 'string' || typeof token !== 'string') {
        return res.status(400).json({ error: 'Invalid request payload.' });
    }

    // Insert or update the service heartbeat
    db.run(`INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(serviceId) DO UPDATE SET lastNotification = CURRENT_TIMESTAMP, token = excluded.token`, 
            [serviceId, token], function(err) {
        if (err) {
            console.error(err.message);
            return res.status(500).json({ error: 'Internal server error.' });
        }
        res.status(200).json({ message: 'Heartbeat registered successfully.' });
    });
});

// Endpoint to get overview of registered services
app.post('/services', (req, res) => {
    const { token } = req.body;

    // Validate input
    if (typeof token !== 'string') {
        return res.status(400).json({ error: 'Invalid request payload.' });
    }

    // Query to get services with the matching token
    db.all(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, [token], (err, rows) => {
        if (err) {
            console.error(err.message);
            return res.status(500).json({ error: 'Internal server error.' });
        }
        res.status(200).json(rows);
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});