const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const LOG_FILE_PATH = path.join(__dirname, 'logs.txt');

// Middleware to parse JSON request bodies
app.use(express.json());

// POST endpoint to log messages
app.post('/log', (req, res) => {
    const { message } = req.body;

    // Validate input
    if (typeof message !== 'string' || message.trim() === '') {
        return res.status(400).send('Invalid log message');
    }

    // Append log message to the file
    fs.appendFile(LOG_FILE_PATH, message + '\n', (err) => {
        if (err) {
            console.error('Error writing to log file:', err);
            return res.status(500).send('Error logging message');
        }
        res.status(200).send('Log message successful');
    });
});

// GET endpoint to retrieve logs
app.get('/logs', (req, res) => {
    fs.readFile(LOG_FILE_PATH, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading log file:', err);
            return res.status(500).send('Error retrieving logs');
        }
        res.type('text/plain').send(data);
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running at http://0.0.0.0:${PORT}`);
});