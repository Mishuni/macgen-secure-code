const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 5000;
const LOG_FILE_PATH = path.join(__dirname, 'logs.txt');

// Middleware to parse JSON bodies
app.use(express.json());

// POST endpoint to log a message
app.post('/log', (req, res) => {
    const { message } = req.body;

    // Validate input
    if (typeof message !== 'string' || message.trim() === '') {
        return res.status(400).send('Invalid log message');
    }

    // Sanitize the message to prevent injection attacks
    const sanitizedMessage = message.replace(/[\r\n]+/g, ' ').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // Append the sanitized message to the log file
    fs.appendFile(LOG_FILE_PATH, sanitizedMessage + '\n', (err) => {
        if (err) {
            console.error('Error writing to log file:', err);
            return res.status(500).send('Unable to log message');
        }
        res.status(200).send('Log message successful');
    });
});

// GET endpoint to retrieve logs
app.get('/logs', (req, res) => {
    fs.readFile(LOG_FILE_PATH, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading log file:', err);
            return res.status(500).send('Unable to retrieve logs');
        }
        // Send logs as plain text
        res.type('text/plain').send(data);
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});