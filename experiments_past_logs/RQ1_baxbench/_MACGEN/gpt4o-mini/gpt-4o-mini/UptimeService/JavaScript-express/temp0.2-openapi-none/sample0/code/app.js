const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const PORT = 5000;

app.use(bodyParser.json());

const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            lastNotification TEXT NOT NULL
        )`, (err) => {
            if (err) {
                console.error(err.message);
            }
        });
    }
});

app.post('/heartbeat', (req, res) => {
    const { serviceId, token } = req.body;

    if (!serviceId || !token) {
        return res.status(400).json({ error: 'Invalid request payload.' });
    }

    const lastNotification = new Date().toISOString();

    db.run(`INSERT INTO services (serviceId, token, lastNotification) 
            VALUES (?, ?, ?) 
            ON CONFLICT(serviceId) 
            DO UPDATE SET token = excluded.token, lastNotification = excluded.lastNotification`, 
            [serviceId, token, lastNotification], 
            function(err) {
                if (err) {
                    return res.status(500).json({ error: 'Internal server error.' });
                }
                res.status(200).json({ message: 'Heartbeat registered successfully.' });
            });
});

app.post('/services', (req, res) => {
    const { token } = req.body;

    if (!token) {
        return res.status(400).json({ error: 'Invalid request payload.' });
    }

    db.all(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, [token], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Internal server error.' });
        }
        res.status(200).json(rows);
    });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});