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

    if (!serviceId || !token) {
        return res.status(400).json({ error: 'Invalid request payload.' });
    }

    const query = `INSERT INTO services (serviceId, token, lastNotification) 
                   VALUES (?, ?, CURRENT_TIMESTAMP) 
                   ON CONFLICT(serviceId) 
                   DO UPDATE SET lastNotification = CURRENT_TIMESTAMP, token = ?`;

    db.run(query, [serviceId, token, token], function(err) {
        if (err) {
            return res.status(500).json({ error: 'Internal server error.' });
        }
        res.status(200).json({ message: 'Heartbeat registered successfully.' });
    });
});

// Endpoint to get overview of registered services
app.post('/services', (req, res) => {
    const { token } = req.body;

    if (!token) {
        return res.status(400).json({ error: 'Invalid request payload.' });
    }

    const query = `SELECT serviceId, lastNotification FROM services WHERE token = ?`;

    db.all(query, [token], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Internal server error.' });
        }
        res.status(200).json(rows);
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});