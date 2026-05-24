const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const { escape } = require('querystring');

// Load environment variables
dotenv.config();

const app = express();
const PORT = 5000;

// Middleware to parse JSON requests
app.use(express.json());

// Initialize SQLite database
let db;
(async () => {
    db = await open({
        filename: './db.sqlite3',
        driver: sqlite3.Database
    });

    // Create tables if they don't exist
    await db.exec(`
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serviceId TEXT NOT NULL,
            token TEXT NOT NULL,
            lastNotification TEXT NOT NULL
        );
    `);
})();

// Helper function to validate input
function validateInput(input, requiredFields) {
    for (const field of requiredFields) {
        if (!input[field] || typeof input[field] !== 'string' || input[field].trim() === '') {
            return false;
        }
    }
    return true;
}

// POST /heartbeat - Register a heartbeat for a service
app.post('/heartbeat', async (req, res) => {
    try {
        const { serviceId, token } = req.body;

        // Validate input
        if (!validateInput(req.body, ['serviceId', 'token'])) {
            return res.status(400).json({ error: 'Invalid request payload.' });
        }

        const sanitizedServiceId = escape(serviceId.trim());
        const sanitizedToken = escape(token.trim());
        const currentTime = new Date().toISOString();

        // Check if the service already exists
        const existingService = await db.get(
            'SELECT * FROM services WHERE serviceId = ? AND token = ?',
            [sanitizedServiceId, sanitizedToken]
        );

        if (existingService) {
            // Update the last notification time
            await db.run(
                'UPDATE services SET lastNotification = ? WHERE serviceId = ? AND token = ?',
                [currentTime, sanitizedServiceId, sanitizedToken]
            );
        } else {
            // Insert a new service record
            await db.run(
                'INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)',
                [sanitizedServiceId, sanitizedToken, currentTime]
            );
        }

        res.status(200).json({ message: 'Heartbeat registered successfully.' });
    } catch (error) {
        console.error('Error in /heartbeat:', error);
        res.status(500).json({ error: 'Internal server error.' });
    }
});

// POST /services - Get overview of registered services
app.post('/services', async (req, res) => {
    try {
        const { token } = req.body;

        // Validate input
        if (!validateInput(req.body, ['token'])) {
            return res.status(400).json({ error: 'Invalid request payload.' });
        }

        const sanitizedToken = escape(token.trim());

        // Retrieve services associated with the token
        const services = await db.all(
            'SELECT serviceId, lastNotification FROM services WHERE token = ?',
            [sanitizedToken]
        );

        res.status(200).json(services);
    } catch (error) {
        console.error('Error in /services:', error);
        res.status(500).json({ error: 'Internal server error.' });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});