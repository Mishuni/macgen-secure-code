const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const LOG_FILE_PATH = path.join(__dirname, 'logs.txt');

app.use(express.json());

app.post('/log', (req, res) => {
    const { message } = req.body;

    // Validate the message property
    if (typeof message !== 'string' || message.trim() === '') {
        return res.status(400).send('Invalid message format');
    }

    // Append the log message to the file
    fs.appendFile(LOG_FILE_PATH, message.trim() + '\n', (err) => {
        if (err) {
            return res.status(500).send('Error logging message');
        }
        res.status(200).send('Log message successful');
    });
});

app.get('/logs', (req, res) => {
    // Read the log file
    fs.readFile(LOG_FILE_PATH, 'utf8', (err, data) => {
        if (err) {
            return res.status(500).send('Error retrieving logs');
        }
        res.type('text/plain').send(data);
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});