const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const cors = require('cors');
const { body, validationResult } = require('express-validator');

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());
app.use(cors({
    origin: ['https://trusted-origin.com'], // Replace with your trusted origins
    methods: ['POST'],
    allowedHeaders: ['Content-Type']
}));

// Create the services table if it doesn't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS services (
        serviceId TEXT PRIMARY KEY,
        token TEXT NOT NULL,
        lastNotification DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
});

// Endpoint to register a heartbeat for a service
app.post('/heartbeat', [
    body('serviceId').isLength({ min: 1, max: 50 }).matches(/^[a-zA-Z0-9_-]+$/),
    body('token').isLength({ min: 1, max: 100 }).matches(/^[a-zA-Z0-9_-]+$/)
], (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ error: 'Invalid request payload.' });
    }

    const { serviceId, token } = req.body;

    const query = `INSERT INTO services (serviceId, token, lastNotification) 
                   VALUES (?, ?, CURRENT_TIMESTAMP) 
                   ON CONFLICT(serviceId) 
                   DO UPDATE SET lastNotification = CURRENT_TIMESTAMP, token = ?`;

    db.run(query, [serviceId, token, token], function(err) {
        if (err) {
            console.error(err); // Log error internally
            return res.status(500).json({ error: 'Internal server error.' });
        }
        res.status(200).json({ message: 'Heartbeat registered successfully.' });
    });
});

// Endpoint to get an overview of registered services
app.post('/services', [
    body('token').isLength({ min: 1, max: 100 }).matches(/^[a-zA-Z0-9_-]+$/)
], (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ error: 'Invalid request payload.' });
    }

    const { token } = req.body;

    const query = `SELECT serviceId, lastNotification FROM services WHERE token = ?`;

    db.all(query, [token], (err, rows) => {
        if (err) {
            console.error(err); // Log error internally
            return res.status(500).json({ error: 'Internal server error.' });
        }
        res.status(200).json(rows);
    });
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});