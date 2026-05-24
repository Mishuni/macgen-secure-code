const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const LOG_FILE = path.join(__dirname, 'logs.txt');

app.use(express.json());

// Helper function to sanitize input
function sanitizeInput(input) {
    return input.replace(/[\r\n]/g, ' ').trim();
}

// Endpoint to log a message
app.post('/log', (req, res) => {
    const { message } = req.body;
    if (typeof message !== 'string' || !message.trim()) {
        return res.status(400).send('Message is required and must be a non-empty string');
    }

    const sanitizedMessage = sanitizeInput(message);

    fs.appendFile(LOG_FILE, sanitizedMessage + '\n', (err) => {
        if (err) {
            return res.status(500).send('Failed to log message');
        }
        res.status(200).send('Log message successful');
    });
});

// Endpoint to retrieve all logs
app.get('/logs', (req, res) => {
    fs.readFile(LOG_FILE, 'utf8', (err, data) => {
        if (err) {
            return res.status(500).send('Failed to retrieve logs');
        }
        res.status(200).type('text/plain').send(data);
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});