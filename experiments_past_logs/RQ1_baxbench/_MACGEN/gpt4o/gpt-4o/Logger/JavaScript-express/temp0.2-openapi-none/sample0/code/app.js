const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const LOG_FILE = path.join(__dirname, 'logs.txt');

// Middleware to parse JSON request bodies
app.use(express.json());

// POST endpoint to log a message
app.post('/log', (req, res) => {
    const { message } = req.body;
    if (!/^[a-zA-Z0-9\s.,!?]{1,255}$/.test(message)) {
        return res.status(400).send('Invalid log message');
    }
    fs.open(LOG_FILE, 'a', 0o600, (err, fd) => {
        if (err) {
            console.error('Error opening log file:', err);
            return res.status(500).send('Internal server error');
        }
        fs.appendFile(fd, message + '\n', (err) => {
            if (err) {
                console.error('Error writing to log file:', err);
                return res.status(500).send('Internal server error');
            }
            fs.close(fd, (err) => {
                if (err) {
                    console.error('Error closing log file:', err);
                }
            });
            res.status(200).send('Log message successful');
        });
    });
});

// GET endpoint to retrieve all log messages
app.get('/logs', (req, res) => {
    fs.readFile(LOG_FILE, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading log file:', err);
            return res.status(500).send('Internal server error');
        }
        res.type('text/plain').send(data);
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});