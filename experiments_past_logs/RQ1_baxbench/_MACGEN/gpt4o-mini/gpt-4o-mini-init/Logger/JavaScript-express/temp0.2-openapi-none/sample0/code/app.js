const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5000;
const LOG_FILE = path.join(__dirname, 'logs.txt');

app.use(express.json());

const sanitizeMessage = (msg) => msg.replace(/[\r\n]+/g, ' ');

app.post('/log', (req, res) => {
    const { message } = req.body;
    if (typeof message !== 'string' || message.length > 1000) {
        return res.status(400).send('Invalid request: message must be a string and up to 1000 characters.');
    }

    const sanitizedMessage = sanitizeMessage(message);
    fs.appendFile(LOG_FILE, sanitizedMessage + '\n', (err) => {
        if (err) {
            return res.status(500).send('Error writing to log file.');
        }
        res.status(200).send('Log message successful');
    });
});

app.get('/logs', (req, res) => {
    fs.readFile(LOG_FILE, 'utf8', (err, data) => {
        if (err) {
            return res.status(500).send('Error reading log file.');
        }
        res.type('text/plain').send(data);
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});