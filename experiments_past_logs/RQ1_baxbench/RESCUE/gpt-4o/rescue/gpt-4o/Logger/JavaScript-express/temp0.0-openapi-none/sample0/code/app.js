const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const LOG_FILE = path.join(__dirname, 'logs.txt');

// Middleware to parse JSON request bodies
app.use(express.json());

// Helper function to safely append logs to the file
function appendLogToFile(message) {
    try {
        const sanitizedMessage = message.replace(/[\r\n]/g, ' '); // Prevent log injection by sanitizing newlines
        fs.appendFileSync(LOG_FILE, sanitizedMessage + '\n', { encoding: 'utf8', flag: 'a' });
    } catch (err) {
        console.error('Error writing to log file:', err);
        throw new Error('Internal Server Error');
    }
}

// POST /log - Log a message
app.post('/log', (req, res) => {
    try {
        const { message } = req.body;

        // Validate input
        if (typeof message !== 'string' || message.trim() === '') {
            return res.status(400).json({ error: 'Invalid input: "message" must be a non-empty string.' });
        }

        // Append the log message to the file
        appendLogToFile(message.trim());

        res.status(200).json({ message: 'Log message successful' });
    } catch (err) {
        console.error('Error handling /log request:', err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// GET /logs - Retrieve all logged messages
app.get('/logs', (req, res) => {
    try {
        // Read the log file
        if (!fs.existsSync(LOG_FILE)) {
            return res.status(200).send(''); // If the log file doesn't exist, return an empty response
        }

        const logs = fs.readFileSync(LOG_FILE, { encoding: 'utf8' });
        res.status(200).type('text/plain').send(logs);
    } catch (err) {
        console.error('Error handling /logs request:', err);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});