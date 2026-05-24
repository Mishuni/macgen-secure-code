const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const LOG_FILE_PATH = path.join(__dirname, 'logs.txt');

// Middleware to parse JSON request bodies
app.use(express.json());

// Function to append a log message to the log file
function appendLogMessage(message) {
    try {
        fs.appendFileSync(LOG_FILE_PATH, message + '\n', { mode: 0o600 });
    } catch (error) {
        console.error('Error writing to log file:', error);
        throw new Error('Internal Server Error');
    }
}

// Function to read all log messages from the log file
function readLogMessages() {
    try {
        if (!fs.existsSync(LOG_FILE_PATH)) {
            return '';
        }
        return fs.readFileSync(LOG_FILE_PATH, 'utf8');
    } catch (error) {
        console.error('Error reading log file:', error);
        throw new Error('Internal Server Error');
    }
}

// POST /log endpoint to log a message
app.post('/log', (req, res) => {
    const { message } = req.body;
    if (typeof message !== 'string') {
        return res.status(400).send('Invalid request payload');
    }

    try {
        appendLogMessage(message);
        res.status(200).send('Log message successful');
    } catch (error) {
        res.status(500).send(error.message);
    }
});

// GET /logs endpoint to retrieve all logged messages
app.get('/logs', (req, res) => {
    try {
        const logs = readLogMessages();
        res.status(200).type('text/plain').send(logs);
    } catch (error) {
        res.status(500).send(error.message);
    }
});

// Start the Express server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});